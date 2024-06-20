import json
import time
import cv2 as cv
import numpy as np

from pathlib import Path
from PyQt6.QtCore import pyqtSignal, QThread
from ..models.preset import Preset
from ..utils.media_fetcher import MediaFetcher


class Pipeline(QThread):
    """
    Generic pipeline class for handling pipeline execution.
    """
    progress_signal = pyqtSignal(float, Path)  # Progress percentage on the current file, input file
    finished_file_signal = pyqtSignal(Path, Path, Path)  # Source file, output file, JSON file
    finished_stream_frame_signal = pyqtSignal(np.ndarray)  # Frame
    finished_all_signal = pyqtSignal()  # Signal emitted when all files are processed
    error_signal = pyqtSignal(Path, Exception)  # Source file, exception

    def __init__(self, model_name: str, model_builder: str, weight: str, preset: Preset, images_paths: list[Path] | None,
                 videos_paths: list[Path] | None, stream_url: str | None, results_path: Path | None):
        """
        Initializes the pipeline.

        :param weight: The weight file path to use.
        :param images_paths: List of image paths if processing images.
        :param videos_paths: List of video paths if processing videos.
        :param stream_url: URL of the video stream if processing a stream.
        :param results_path: Path to save the results if processing images or videos.
        :param preset: Preset object.
        """
        super().__init__()
        self.fetcher: MediaFetcher | None = None
        self.model_name: str = model_name
        self.model_builder: str = model_builder
        self.weight: str = weight
        self.images_paths: list[Path] = images_paths
        self.videos_paths: list[Path] = videos_paths
        self.stream_url: str = stream_url
        self.mode: str = 'images' if images_paths else 'videos' if videos_paths else 'stream'
        self.results_path: Path = results_path / f"{model_builder}.{weight}" if results_path else None
        self.preset: Preset = preset
        self.cancel_requested: bool = False
        self.stream_fps: float = 0.0

        if self.results_path:
            self.results_path.mkdir(parents=True, exist_ok=True)

    def request_cancel(self) -> None:
        """
        Requests cancellation of the ongoing process.
        """
        self.cancel_requested = True

    def run(self) -> None:
        """
        Runs the pipeline from another thread.
        """
        if self.mode == 'images':
            self._run_images(self.images_paths)
        elif self.mode == 'videos':
            self._run_videos(self.videos_paths)
        elif self.mode == 'stream':
            self._run_stream(self.stream_url)

    def _run_images(self, inputs: list[Path]):
        """
        Process a list of image paths.

        :param inputs: The list of image paths.
        """
        if not self.results_path:
            self.error_signal.emit('No results path provided', Exception('No results path provided'))
            return

        for input_path in inputs:
            if self.cancel_requested:
                return

            try:
                # Create paths for the output files
                file_name = input_path.name
                file_path = self.results_path / file_name
                image_path = file_path.with_suffix(f".{self.preset.image_format}")
                json_path = file_path.with_suffix('.json')

                # Read the image and process it
                image = cv.imread(str(input_path))
                result_image, results_array = self._process_image(image)

                # Save the result image and JSON file
                cv.imwrite(str(image_path), result_image)
                with open(json_path, 'w') as f:
                    results = self._make_results(results_array)
                    json.dump(results, f, indent=4)

                self.finished_file_signal.emit(input_path, image_path, json_path)
            except Exception as e:
                self.error_signal.emit(input_path, e)

        self.finished_all_signal.emit()

    def _run_videos(self, inputs: list[Path]):
        """
        Process a list of video paths.

        :param inputs: The list of video paths.
        """
        if not self.results_path:
            self.error_signal.emit('No results path provided', Exception('No results path provided'))
            return

        for input_path in inputs:
            if self.cancel_requested:
                return

            try:
                # Create paths for the output files
                file_name = input_path.name
                file_path = self.results_path / file_name
                video_path = file_path.with_suffix(f".{self.preset.video_format}")
                json_path = file_path.with_suffix('.json')

                # Process the video and save it
                results_array = self._process_video(input_path, video_path)

                # Save the JSON file
                with open(json_path, 'w') as f:
                    results = self._make_results(results_array)
                    json.dump(results, f, indent=4)

                self.finished_file_signal.emit(input_path, video_path, json_path)
            except Exception as e:
                self.error_signal.emit(input_path, e)

        self.finished_all_signal.emit()

    def _run_stream(self, url: str) -> None:
        """
        Processes a video stream or webcam.

        :param url: The URL of the video stream or the webcam in the format "webcam:[device_index]".
        """
        if url is None:
            self.error_signal.emit('No URL provided', Exception('No URL provided'))
            return

        # Create a media fetcher for the stream
        if url.startswith('webcam:'):
            device_index = int(url.split(':')[1])
            media_fetcher = MediaFetcher(device_index)
        else:
            media_fetcher = MediaFetcher(url)

        self.stream_fps = media_fetcher.fps
        max_fps = 30.0
        frame_interval = 1.0 / min(self.stream_fps, max_fps)
        last_frame_time = time.time()

        while not self.cancel_requested:
            current_time = time.time()
            elapsed_since_last_frame = current_time - last_frame_time

            # Fetch the frame and process it
            if elapsed_since_last_frame >= frame_interval:
                try:
                    frame, frame_available = media_fetcher.fetch_frame()
                    if not frame_available:
                        continue
                    result_frame, _ = self._process_image(frame)
                    self.finished_stream_frame_signal.emit(result_frame)
                except Exception as e:
                    self.error_signal.emit("Error processing frame", e)
                    break
                last_frame_time = current_time

            # Because it's another thread, we can use sleep
            time.sleep(max(0.0, frame_interval - (time.time() - current_time)))

        # Release the frame fetcher when cancelled
        media_fetcher.release()

    def _process_video(self, video_path: Path, output_path: Path) -> list[list[dict]]:
        """
        Processes a single video and saves the output.

        :param video_path: The input video path.
        :param output_path: The output video path.
        :return: The results array.
        """
        # Open the video
        cap = cv.VideoCapture(str(video_path))
        width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv.CAP_PROP_FPS)
        codec = cv.VideoWriter_fourcc(*'mp4v')
        out = cv.VideoWriter(str(output_path), codec, fps, (width, height))

        results_array = []
        # Process each frame
        while True:
            ret, frame = cap.read()
            if not ret or self.cancel_requested:
                break

            # Infer the frame like an image
            result_frame, result_json = self._process_image(frame)
            # Write the frame to the output video
            out.write(result_frame)
            # Append the results to the results array
            results_array.append(result_json)
            # Emit the progress signal for the progress bar
            self.progress_signal.emit(cap.get(cv.CAP_PROP_POS_FRAMES) / cap.get(cv.CAP_PROP_FRAME_COUNT), video_path)

        # Release the video capture and the video writer
        cap.release()
        out.release()

        return results_array

    def _process_image(self, image: np.ndarray) -> tuple[np.ndarray, list[dict]]:
        """
        Processes a single image.

        :param image: The input image.
        :return: The processed image and the results array.
        """
        raise NotImplementedError

    def _make_results(self, results_array: list) -> dict:
        """
        Creates the result's dictionary.

        :param results_array: The list of results.
        :return: The result's dictionary.
        """
        raise NotImplementedError

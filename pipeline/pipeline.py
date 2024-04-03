import json
import logging

import cv2 as cv
from pathlib import Path

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from models.project import Project
from utils.media_fetcher import MediaFetcher


class Pipeline(QThread):
    """Generic pipeline class for handling pipeline execution."""
    progress_signal = pyqtSignal(float)  # Progress percentage on the current file
    finished_file_signal = pyqtSignal(str, str, str)  # Source file, output file, JSON file
    finished_stream_frame_signal = pyqtSignal(np.ndarray)  # Frame
    error_signal = pyqtSignal(str, Exception)  # Source file, exception

    def __init__(self, weight: str, results_path: str | None, project: Project):
        super().__init__()
        self.fetcher = None
        self.weight = weight
        self.results_path = Path(results_path) / Path(weight).stem if results_path else None
        self.project = project
        self.cancel_requested = False

        if self.results_path:
            self.results_path.mkdir(parents=True, exist_ok=True)

    def request_cancel(self):
        """Requests cancellation of the ongoing process."""
        self.cancel_requested = True

    def run_images(self, inputs: list[str]):
        """Process a list of image paths."""
        if not self.results_path:
            self.error_signal.emit('No results path provided', Exception('No results path provided'))
        for input_path in inputs:
            if self.cancel_requested:
                return

            try:
                # Create paths for the output files
                file_name = Path(input_path).stem
                file_path = self.results_path / file_name
                image_path = f"{file_path}.{self.project.config.image_format}"
                json_path = f"{file_path}.json"

                # Read the image and process it
                image = cv.imread(input_path)
                result_image, results_array = self._process_image(image)

                # Save the result image and JSON file
                cv.imwrite(image_path, result_image)
                with open(json_path, 'w') as f:
                    results = self._make_results(results_array)
                    json.dump(results, f, indent=4)

                self.finished_file_signal.emit(input_path, image_path, json_path)
            except Exception as e:
                self.error_signal.emit(input_path, e)

    def run_videos(self, inputs: list[str]):
        """Process a list of video paths."""
        if not self.results_path:
            self.error_signal.emit('No results path provided', Exception('No results path provided'))
        for input_path in inputs:
            if self.cancel_requested:
                return

            try:
                # Create paths for the output files
                file_name = Path(input_path).stem
                file_path = self.results_path / file_name
                video_path = f"{file_path}.{self.project.config.video_format}"
                json_path = f"{file_path}.json"

                # Process the video and save it
                results_array = self._process_video(input_path, video_path)

                # Save the JSON file
                with open(json_path, 'w') as f:
                    results = self._make_results(results_array)
                    json.dump(results, f, indent=4)

                self.finished_file_signal.emit(input_path, video_path, json_path)
            except Exception as e:
                self.error_signal.emit(input_path, e)

    def run_stream(self, url: str):
        """Process a video stream."""
        logging.info(f'Starting stream from {url}')
        self.fetcher = MediaFetcher(url, 60)

        def process_frame(frame, frame_available):
            """Processes a single frame."""
            if not frame_available or self.cancel_requested:
                return

            try:
                # Process the frame
                logging.debug('Processing frame')
                result_frame, _ = self._process_image(frame)

                # Emit the processed frame
                logging.debug('Emitting frame')
                self.finished_stream_frame_signal.emit(result_frame)
            except Exception as e:
                self.error_signal.emit(url, e)

        self.fetcher.frame_signal.connect(process_frame)
        self.fetcher.start()

    def _make_results(self, results_array: list):
        """Creates the results dictionary."""
        raise NotImplementedError

    def _process_image(self, image):
        """Processes a single image."""
        raise NotImplementedError

    def _process_video(self, video_path, output_path):
        """Processes a single video."""
        raise NotImplementedError

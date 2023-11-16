from PyQt6.QtCore import pyqtSignal, QThread
from models.app_state import AppState
from utils.image_helpers import draw_bounding_box
from utils.model_loader import load_model
import cv2 as cv
import os
import json

appstate = AppState.get_instance()


class VidDetectionPipeline(QThread):
    progress_signal = pyqtSignal(int, int)  # Current frame, total frames
    finished_signal = pyqtSignal(str, str, str)  # Source file, video output, JSON path
    error_signal = pyqtSignal(str, Exception)  # Source file, Exception
    cleanup_signal = pyqtSignal()

    def __init__(self, inputs: list[str], model_path: str, results_path: str):
        """
        Initializes the Video Detection Pipeline.

        :param inputs: List of input paths.
        :param model_path: Path to the model.
        :param results_path: Path for saving results.
        :raises Exception: If the model fails to load or if its task does not match the pipeline task.
        """
        super().__init__()
        self._cancel_requested = False
        self._device = appstate.device
        self._model = load_model(model_path)
        self._inputs = inputs
        self._results_path = results_path
        self._results = {
            'model_name': os.path.basename(model_path),
            'task': "detection",
            'classes': self._model.names,
            'results': []
        }

    def request_cancel(self):
        """Public method to request cancellation of the process."""
        self._cancel_requested = True

    def run(self):
        """Runs detection for all videos in the input list."""
        for src in self._inputs:
            try:
                self._process_video(src)
            except Exception as e:
                self.error_signal.emit(src, e)

    def _process_video(self, src: str):
        """
        Processes a single video file.

        :param src: Source video file path.
        """
        video_name = os.path.basename(src)
        output_path = os.path.join(self._results_path, video_name)
        cap, writer, frame_count = self._setup_video(src, output_path)

        frame_index = 0
        while cap.isOpened():
            if self._cancel_requested:
                break

            ret, frame = cap.read()
            if not ret:
                break

            results_array = self._process_frame(frame)
            self._results['results'].append(results_array)
            writer.write(frame)

            frame_index += 1
            self.progress_signal.emit(frame_index, frame_count)

        cap.release()
        writer.release()

        if self._cancel_requested:
            self._cleanup()
            return

        self._save_results(src, output_path)

    def _cleanup(self):
        """
        Cleans up the video file and JSON file if they exist.
        """
        for src in self._inputs:
            video_name = os.path.basename(src)
            output_path = os.path.join(self._results_path, video_name)
            json_path = os.path.join(self._results_path, video_name.split('.')[0] + '.json')

            if os.path.exists(output_path):
                os.remove(output_path)
            if os.path.exists(json_path):
                os.remove(json_path)

        self.cleanup_signal.emit()

    def _setup_video(self, src: str, output_path: str) -> tuple[cv.VideoCapture, cv.VideoWriter, int]:
        """
        Sets up video capture and writer.

        :param src: Source video file path.
        :param output_path: Output video file path.
        :return: Tuple of video capture, video writer, and frame count.
        """
        cap = cv.VideoCapture(src)
        width, height, fps, frame_count = (
            int(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)),
            int(cap.get(cv.CAP_PROP_FPS)),
            int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        )

        codec = 'XVID' if appstate.config.video_format == 'avi' else 'mp4v'
        writer = cv.VideoWriter(output_path, cv.VideoWriter_fourcc(*codec), fps, (width, height))
        return cap, writer, frame_count

    def _process_frame(self, frame) -> list:
        """
        Processes a single frame of the video.

        :param frame: The frame to process.
        :return: Array of detection results for the frame.
        """
        results = self._model(frame)[0].cpu()
        results_array = []

        for box in results.boxes:
            flat = box.xyxy.flatten()
            topleft, bottomright = (int(flat[0]), int(flat[1])), (int(flat[2]), int(flat[3]))
            classid, classname = int(box.cls), self._model.names[int(box.cls)]
            conf = float(box.conf[0])

            draw_bounding_box(
                frame, topleft, bottomright, classname, conf,
                appstate.config.video_box_color, appstate.config.video_text_color,
                appstate.config.video_box_thickness, appstate.config.video_text_size
            )

            results_array.append({
                'x1': topleft[0], 'y1': topleft[1],
                'x2': bottomright[0], 'y2': bottomright[1],
                'classid': classid, 'confidence': conf
            })

        return results_array

    def _save_results(self, src: str, output_path: str):
        """
        Saves the results to a JSON file and emits the finished signal.

        :param src: Source video file path.
        :param output_path: Output video file path.
        """
        json_name = os.path.basename(src).split('.')[0] + '.json'
        json_path = os.path.join(self._results_path, json_name)

        with open(json_path, 'w') as f:
            json.dump(self._results, f, indent=4)

        self.finished_signal.emit(src, output_path, json_path)

import logging
from datetime import datetime
from PyQt6.QtCore import pyqtSignal, QThread
from models.app_state import AppState
from models.project import Project
from utils.image_helpers import draw_bounding_box
from utils.model_loader import load_model
import cv2 as cv
import os
import json


class VidDetectionPipeline(QThread):
    progress_signal = pyqtSignal(float)  # Progress percentage
    finished_signal = pyqtSignal(str, str, str)  # Source file, video output, JSON path
    error_signal = pyqtSignal(str, Exception)  # Source file, Exception
    cleanup_signal = pyqtSignal()

    def __init__(self, inputs: list[str], model_paths: list[str], results_path: str, project: Project):
        """
        Initializes the Video Detection Pipeline.

        :param inputs: List of input paths.
        :param model_paths: List of paths to the models.
        :param results_path: Path for saving results.
        :raises Exception: If the model fails to load or if its task does not match the pipeline task.
        """
        super().__init__()
        self._appstate = AppState.get_instance()
        self._appstate.pipelines.append(self)
        self._cancel_requested = False
        self._inputs = inputs
        self._model_paths = model_paths
        self._results_path = results_path
        self._project = project

    def request_cancel(self):
        """Public method to request cancellation of the process."""
        self._cancel_requested = True

    def run(self):
        """Runs detection for all videos in the input list."""
        for model_path in self._model_paths:
            if self._cancel_requested:
                break

            model = load_model(model_path, self._project.device)
            results = {
                'model_name': os.path.basename(model_path),
                'task': "detection",
                'classes': model.names,
                'results': []
            }
            result_path = os.path.join(self._results_path, results['model_name'])

            for src in self._inputs:
                if self._cancel_requested:
                    break
                try:
                    if not os.path.exists(result_path):
                        os.mkdir(result_path)
                    file_name = '.'.join(os.path.basename(src).split('.')[0:-1])
                    file_path = os.path.join(result_path, file_name)
                    video_path = f'{file_path}.{self._project.config.video_format}'
                    json_path = f'{file_path}.json'

                    result_array = self._process_source(src, model, video_path)
                    self._save_json(result_array, results, json_path)

                    self.finished_signal.emit(src, video_path, json_path)
                except Exception as e:
                    self.error_signal.emit(src, e)

        self._appstate.pipelines.remove(self)

    def _process_source(self, src: str, model, output_path: str) -> list | None:
        """
        Processes a single video file.

        :param src: Source video file path.
        """
        cap, writer, frame_count = self._setup_video(src, output_path)

        frame_index = 0
        results_array = []

        while cap.isOpened():
            if self._cancel_requested:
                break

            ret, frame = cap.read()
            if not ret:
                break

            results_array.append(self._process_frame(frame, model))
            writer.write(frame)

            frame_index += 1
            self.progress_signal.emit(frame_index / frame_count)

        cap.release()
        writer.release()

        if self._cancel_requested:
            self._cleanup()
            return

        return results_array

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

        codec = 'XVID' if self._project.config.video_format == 'avi' else 'mp4v'
        writer = cv.VideoWriter(output_path, cv.VideoWriter_fourcc(*codec), fps, (width, height))
        return cap, writer, frame_count

    def _process_frame(self, frame, model) -> list:
        """
        Processes a single frame of the video.

        :param frame: The frame to process.
        :return: Array of detection results for the frame.
        """
        if self._project.device.type == 'cuda' and self._project.config.half_precision:
            results = model(frame, half=True, verbose=False)[0].cpu()
        else:
            results = model(frame, verbose=False)[0].cpu()
        results_array = []

        for box in results.boxes:
            flat = box.xyxy.flatten()
            top_left, bottom_right = (int(flat[0]), int(flat[1])), (int(flat[2]), int(flat[3]))
            class_id, class_name = int(box.cls), model.names[int(box.cls)]
            conf = float(box.conf[0])

            draw_bounding_box(
                frame, top_left, bottom_right, class_name, conf,
                self._project.config.video_box_color, self._project.config.video_text_color,
                self._project.config.video_box_thickness, self._project.config.video_text_size
            )

            results_array.append({
                'x1': top_left[0], 'y1': top_left[1],
                'x2': bottom_right[0], 'y2': bottom_right[1],
                'classid': class_id, 'confidence': conf
            })

        return results_array

    def _save_json(self, results_array: list, results_dict: dict, json_path: str):
        """
        Saves the results to a JSON file.

        :param results_array: Array of results.
        """
        results_dict['results'] = results_array
        with open(json_path, 'w') as f:
            json.dump(results_dict, f, indent=4)

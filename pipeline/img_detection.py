from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal
from models.app_state import AppState
from models.project import Project
from utils.image_helpers import draw_bounding_box
from utils.model_loader import load_model
import os
import json
import cv2 as cv


class ImgDetectionPipeline(QThread):
    finished_signal = pyqtSignal(str, str, str)  # Source file, image output, JSON path
    error_signal = pyqtSignal(str, Exception)  # Source file, Exception

    def __init__(self, inputs: list[str], model_paths: list[str], results_path: str, project: Project):
        """
        Initializes the Image Detection Pipeline.

        :param inputs: List of input paths or URLs.
        :param model_paths: List of paths to the models.
        :param results_path: Path for saving results.
        :param project: Project object.
        :raises Exception: If the model fails to load or if its task does not match the pipeline task.
        """
        super().__init__()
        self._appstate = AppState.get_instance()
        self._appstate.pipelines.append(self)
        self._project = project
        self._cancel_requested = False
        self._inputs = inputs
        self._model_paths = model_paths
        self._results_path = results_path

    def request_cancel(self):
        """Public method to request cancellation of the process."""
        self._cancel_requested = True

    def run(self):
        """Runs detection for each model on all images in the input list."""
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
                    image_path = f'{file_path}.{self._project.config.image_format}'
                    json_path = f'{file_path}.json'

                    results_array = self._process_source(src, model, image_path)
                    self._save_json(results_array, results, json_path)

                    self.finished_signal.emit(src, image_path, json_path)
                except Exception as e:
                    self.error_signal.emit(src, e)

        self._appstate.pipelines.remove(self)

    def _process_source(self, src: str, model, output_path: str) -> list:
        """
        Processes a single source file.

        :param src: Source file path.
        :return: Array of results.
        """
        image = cv.imread(src)
        if self._project.device.type == 'cuda' and self._project.config.half_precision:
            result = model(image, half=True, verbose=False)[0].cpu()
        else:
            result = model(image, verbose=False)[0].cpu()

        results_array = []
        for box in result.boxes:
            flat = box.xyxy.flatten()
            top_left, bottom_right = (int(flat[0]), int(flat[1])), (int(flat[2]), int(flat[3]))
            class_id, class_name = int(box.cls), model.names[int(box.cls)]
            conf = float(box.conf[0])

            draw_bounding_box(
                image, top_left, bottom_right, class_name, conf,
                self._project.config.video_box_color, self._project.config.video_text_color,
                self._project.config.video_box_thickness, self._project.config.video_text_size
            )

            results_array.append({
                'x1': top_left[0], 'y1': top_left[1],
                'x2': bottom_right[0], 'y2': bottom_right[1],
                'classid': class_id, 'confidence': conf
            })

        cv.imwrite(output_path, image)
        return results_array

    def _save_json(self, results_array: list, results_dict: dict, json_path: str):
        """
        Saves the results to a JSON file.

        :param results_array: Array of results.
        """
        results_dict['results'] = results_array
        with open(json_path, 'w') as f:
            json.dump(results_dict, f, indent=4)

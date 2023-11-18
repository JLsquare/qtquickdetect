from PyQt6.QtCore import QThread, pyqtSignal
from models.app_state import AppState
from utils.model_loader import load_model
import os
import json


class ImgDetectionPipeline(QThread):
    finished_signal = pyqtSignal(str, str)  # Source file, JSON path
    error_signal = pyqtSignal(str, Exception)  # Source file, Exception

    def __init__(self, inputs: list[str], model_paths: list[str], results_path: str):
        """
        Initializes the Image Detection Pipeline.

        :param inputs: List of input paths or URLs.
        :param model_paths: List of paths to the models.
        :param results_path: Path for saving results.
        :raises Exception: If the model fails to load or if its task does not match the pipeline task.
        """
        super().__init__()
        self._appstate = AppState.get_instance()
        self._appstate.pipelines.append(self)
        self._cancel_requested = False
        self._device = self._appstate.device
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

            model = load_model(model_path)
            results = {
                'model_name': os.path.basename(model_path),
                'task': "detection",
                'classes': model.names,
                'results': []
            }

            for src in self._inputs:
                try:
                    results_array = self._process_source(src, model)
                    base_name = os.path.basename(src).split('.')[0]
                    json_name = f"{base_name}_{results['model_name']}.json"
                    json_path = os.path.join(self._results_path, json_name)

                    self._save_json(results_array, results, json_path)
                    self.finished_signal.emit(src, json_path)
                except Exception as e:
                    self.error_signal.emit(src, e)

        self._appstate.pipelines.remove(self)

    def _process_source(self, src: str, model) -> list:
        """
        Processes a single source file.

        :param src: Source file path.
        :return: Array of results.
        """
        if self._device.type == 'cuda' and self._appstate.config.half_precision:
            result = model(src, half=True, verbose=False)[0].cpu()
        else:
            result = model(src, verbose=False)[0].cpu()

        return [
            {
                'x1': int(box.xyxy.flatten()[0]),
                'y1': int(box.xyxy.flatten()[1]),
                'x2': int(box.xyxy.flatten()[2]),
                'y2': int(box.xyxy.flatten()[3]),
                'classid': int(box.cls),
                'confidence': float(box.conf[0])
            } for box in result.boxes
        ]

    def _save_json(self, results_array: list, results_dict: dict, json_path: str):
        """
        Saves the results to a JSON file.

        :param results_array: Array of results.
        """
        results_dict['results'] = results_array
        with open(json_path, 'w') as f:
            json.dump(results_dict, f, indent=4)

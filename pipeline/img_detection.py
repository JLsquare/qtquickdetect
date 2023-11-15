from PyQt6.QtCore import QThread, pyqtSignal
from models.app_state import AppState
import logging
import ultralytics
import os
import json

appstate = AppState.get_instance()


class ImgDetectionPipeline(QThread):
    finished_signal = pyqtSignal(str, str)  # Source file, data
    error_signal = pyqtSignal(str, Exception)  # Source file, Exception

    def __init__(self, inputs: list[str], model_path: str, results_path: str):
        """
        Initializes the Image Detection Pipeline.

        :param inputs: List of input paths or URLs.
        :param model_path: Path to the model.
        :param results_path: Path for saving results.
        :raises Exception: If the model fails to load or if its task does not match the pipeline task.
        """
        super().__init__()
        self._device = appstate.device
        self._model = self._load_model(model_path)
        self._inputs = inputs
        self._results_path = results_path
        self._results = {
            'model_name': os.path.basename(model_path),
            'task': "detection",
            'classes': self._model.names,
            'results': []
        }

    def _load_model(self, model_path: str):
        """
        Loads the model from the given path.

        :param model_path: Path to the model.
        :return: Loaded model.
        """
        try:
            model = ultralytics.YOLO(model_path).to(self._device)
            if model.task != 'detect':
                raise ValueError(f'Model task ({model.task}) does not match pipeline task')
            return model
        except Exception as e:
            logging.error(f'Failed to load model: {e}')
            raise

    def run(self):
        """Runs detection for all images in the input list."""
        for src in self._inputs:
            try:
                results_array = self._process_source(src)
                self._save_results(src, results_array)
                self.finished_signal.emit(src, self._json_path(src))
            except Exception as e:
                self.error_signal.emit(src, e)

    def _process_source(self, src: str):
        """
        Processes a single source file.

        :param src: Source file path.
        :return: Array of results.
        """
        result = self._model(src)
        result = result[0].cpu()
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

    def _save_results(self, src: str, results_array: list):
        """
        Saves the results to a JSON file.

        :param src: Source file path.
        :param results_array: Array of results.
        """
        results = self._results.copy()
        results['results'] = results_array
        json_path = self._json_path(src)
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=4)

    def _json_path(self, src: str) -> str:
        """
        Generates the JSON file path for a source file.

        :param src: Source file path.
        :return: Path for the corresponding JSON file.
        """
        json_name = os.path.basename(src).split('.')[0] + '.json'
        return os.path.join(self._results_path, json_name)

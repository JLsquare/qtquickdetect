import logging
import importlib

import numpy as np

from models.project import Project
from models.app_state import AppState
from PyQt6.QtCore import pyqtSignal, QThread


class PipelineManager(QThread):
    """Pipeline Manager class to manage the pipeline execution."""
    progress_signal = pyqtSignal(float)  # Progress percentage on the current file
    finished_file_signal = pyqtSignal(str, str, str)  # Source file, output file, JSON file
    finished_stream_frame_signal = pyqtSignal(np.ndarray)  # Frame
    error_signal = pyqtSignal(str, Exception)  # Source file, exception

    def __init__(self, task: str, models: dict[str, list[str]], project: Project):
        """
        Initializes the Pipeline Manager.

        :param task: Task to perform.
        :param models: List of tuples containing model name and weight
        :param project: Project object.
        """
        super().__init__()
        self._task = task
        self._models = models
        self._project = project
        self._appstate = AppState.get_instance()
        self.current_pipeline = None

        logging.info(f'Pipeline Manager initialized with task: {task}, models: {models}')

        if not self._check_models_tasks():
            raise ValueError('Invalid models or tasks')

    def _check_models_tasks(self):
        """
        Checks if the models and tasks are valid.

        :return: True if models and tasks are valid, False otherwise.
        """
        for model, weights in self._models.items():
            for weight in weights:
                if self._task not in self._appstate.config.models[model]['tasks']:
                    return False
                if weight not in self._appstate.config.models[model]['weights']:
                    return False
        return True

    def request_cancel(self):
        """Public method to request cancellation of the process."""
        if self.current_pipeline:
            self.current_pipeline.request_cancel()

    def run_image(self, inputs: list[str], results_path: str):
        """
        Runs the pipeline, one pipeline per weight.
        """
        for model, weights in self._models.items():
            for weight in weights:
                self.current_pipeline = self._setup_pipeline(model, weight, results_path)
                self._appstate.pipelines.append(self.current_pipeline)
                self.current_pipeline.run_images(inputs)

    def run_video(self, inputs: list[str], results_path: str):
        """
        Runs the pipeline, one pipeline per weight.
        """
        for model, weights in self._models.items():
            for weight in weights:
                self.current_pipeline = self._setup_pipeline(model, weight, results_path)
                self._appstate.pipelines.append(self.current_pipeline)
                self.current_pipeline.run_videos(inputs)

    def run_stream(self, url: str):
        """
        Runs the pipeline, only the first weight.
        """
        model = list(self._models.keys())[0]
        weight = self._models[model][0]
        self.current_pipeline = self._setup_pipeline(model, weight, None)
        self._appstate.pipelines.append(self.current_pipeline)
        self.current_pipeline.run_stream(url)

    def _setup_pipeline(self, model: str, weight: str, results_path: str | None):
        """
        Sets up the pipeline for the given model and weight.
        """
        model_class_path = self._appstate.config.models[model]['class']
        module_name, class_name = model_class_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        model_class = getattr(module, class_name)
        pipeline = model_class(weight, results_path, self._project)
        pipeline.progress_signal.connect(self.progress_signal)
        pipeline.finished_file_signal.connect(self.finished_file_signal)
        pipeline.finished_stream_frame_signal.connect(self.finished_stream_frame_signal)
        pipeline.error_signal.connect(self.error_signal)
        return pipeline

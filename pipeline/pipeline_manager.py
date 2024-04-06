import logging
import importlib
import numpy as np
from models.project import Project
from models.app_state import AppState
from PyQt6.QtCore import pyqtSignal, QObject


class PipelineManager(QObject):
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

    def run_image(self, images_paths: list[str], results_path: str):
        """
        Runs the pipeline, one pipeline per weight.

        :param images_paths: List of image paths.
        :param results_path: Path to save the results.
        """
        for model, weights in self._models.items():
            for weight in weights:
                self._setup_pipeline(model, weight, images_paths, None, None, results_path)
                self._appstate.pipelines.append(self.current_pipeline)
                self.current_pipeline.start()

    def run_video(self, videos_paths: list[str], results_path: str):
        """
        Runs the pipeline, one pipeline per weight.

        :param videos_paths: List of video paths.
        :param results_path: Path to save the results.
        """
        for model, weights in self._models.items():
            for weight in weights:
                self._setup_pipeline(model, weight, None, videos_paths, None, results_path)
                self._appstate.pipelines.append(self.current_pipeline)
                self.current_pipeline.start()

    def run_stream(self, url: str):
        """
        Runs the pipeline, only the first weight.

        :param url: URL of the video stream.
        """
        model = list(self._models.keys())[0]
        weight = self._models[model][0]
        self._setup_pipeline(model, weight, None, None, url, None)
        self._appstate.pipelines.append(self.current_pipeline)
        self.current_pipeline.start()

    def _setup_pipeline(self, model: str, weight: str, images_path: list[str] | None, videos_path: list[str] | None,
                        stream_url: str | None, results_path: str | None):
        """
        Sets up the pipeline for the given model and weight.

        :param model: Model name / file path.
        :param weight: Weight file path.
        :param images_path: List of image paths if processing images.
        :param videos_path: List of video paths if processing videos.
        :param stream_url: URL of the video stream if processing a stream.
        :param results_path: Path to save the results if processing images or videos.
        """
        model_class_path = self._appstate.config.models[model]['class']
        module_name, class_name = model_class_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        model_class = getattr(module, class_name)
        self.current_pipeline = model_class(weight, images_path, videos_path, stream_url, results_path, self._project)
        self.current_pipeline.progress_signal.connect(self.progress_signal)
        self.current_pipeline.finished_file_signal.connect(self.finished_file_signal)
        self.current_pipeline.finished_stream_frame_signal.connect(self.finished_stream_frame_signal)
        self.current_pipeline.error_signal.connect(self.error_signal)

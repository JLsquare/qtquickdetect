import logging
import importlib
import numpy as np

from typing import Optional
from pathlib import Path
from PyQt6.QtCore import pyqtSignal, QObject
from .pipeline import Pipeline
from ..models.app_state import AppState
from ..models.preset import Preset


class PipelineManager(QObject):
    """
    Pipeline Manager class to manage the pipeline execution.
    """
    progress_signal = pyqtSignal(float, Path)  # Progress percentage on the current file, input file
    finished_file_signal = pyqtSignal(Path, Path, Path)  # Source file, output file, JSON file
    finished_stream_frame_signal = pyqtSignal(np.ndarray)  # Frame
    finished_all_signal = pyqtSignal()  # Signal emitted when all files are processed
    error_signal = pyqtSignal(Path, Exception)  # Source file, exception
    fatal_error_signal = pyqtSignal(str, Exception)  # Error message, exception

    def __init__(self, task: str, preset: Preset, models: dict[str, dict[str, list[str]]]):
        """
        Initializes the Pipeline Manager.

        :param task: Task to perform.
        :param preset: Preset object.
        :param models: List of tuples containing model name and weight
        """
        super().__init__()
        self._task: str = task
        self._models: dict[str, dict[str, list[str]]] = models
        self._preset: Preset = preset
        self._appstate: AppState = AppState.get_instance()
        self.current_pipeline: Optional[Pipeline] = None

        logging.info(f'Pipeline Manager initialized with task: {task}, models: {models}')

        if not self._check_models_tasks():
            raise ValueError('Invalid models or tasks')

    def _check_models_tasks(self) -> bool:
        """
        Checks if the models and tasks are valid.

        :return: True if models and tasks are valid, False otherwise.
        """
        for model_name in self._models:
            if self._task != self._appstate.app_config.models[model_name]['task']:
                return False
        return True

    def request_cancel(self) -> None:
        """
        Public method to request cancellation of the process.
        """
        if self.current_pipeline:
            self.current_pipeline.request_cancel()

    def run_image(self, images_paths: list[Path], results_path: Path, current_weight_index: int = 0) -> None:
        """
        Runs the pipeline, one pipeline per weight. Uses recursion to run the next weight after the current one is done.

        :param images_paths: List of image paths.
        :param results_path: Path to save the results.
        :param current_weight_index: Index of the current weight to run.
        """
        index = 0
        # Iterate over the models
        for model, model_builders in self._models.items():
            # Iterate over the model_builders
            for model_builder, weights in model_builders.items():
                for weight in weights:
                    # Skip if not the current weight
                    if index != current_weight_index:
                        index += 1
                        continue

                    # Setup the pipeline for the current weight
                    self._setup_pipeline(model, model_builder, weight, images_paths, None, None, results_path)
                    self._appstate.pipelines.append(self.current_pipeline)

                    # Connect the end signal to run the next weight not at the same time
                    self.current_pipeline.finished_all_signal.connect(
                        lambda: self.run_image(images_paths, results_path, current_weight_index + 1)
                    )

                    # Start the pipeline
                    self.current_pipeline.start()

                    # Exit the function because the pipeline will run the next weight and we don't want to emit the signal
                    return

        # If we are here, it means that all weights have been processed
        self.finished_all_signal.emit()

    def run_video(self, videos_paths: list[Path], results_path: Path, current_weight_index: int = 0) -> None:
        """
        Runs the pipeline, one pipeline per weight, for videos. Uses recursion to run the next weight after the current one is done.

        :param videos_paths: List of video paths.
        :param results_path: Path to save the results.
        :param current_weight_index: Index of the current weight to run.
        """
        index = 0
        for model, model_builders in self._models.items():
            for model_builder, weights in model_builders.items():
                for weight in weights:
                    # Skip if not the current weight
                    if index != current_weight_index:
                        index += 1
                        continue

                    # Setup the pipeline for the current weight
                    self._setup_pipeline(model, model_builder, weight, None, videos_paths, None, results_path)
                    self._appstate.pipelines.append(self.current_pipeline)

                    # Connect the end signal to run the next weight not at the same time
                    self.current_pipeline.finished_all_signal.connect(
                        lambda: self.run_video(videos_paths, results_path, current_weight_index + 1)
                    )

                    # Start the pipeline
                    self.current_pipeline.start()

                    # Exit the function because the pipeline will run the next weight and we don't want to emit the signal
                    return

        # If we are here, it means that all weights have been processed
        self.finished_all_signal.emit()

    def run_stream(self, url: str) -> None:
        """
        Runs the pipeline, only the first weight.

        :param url: URL of the video stream.
        """
        model = list(self._models.keys())[0]
        model_builder = list(self._models[model].keys())[0]
        weight = self._models[model][model_builder][0]
        self._setup_pipeline(model, model_builder, weight, None, None, url, None)
        self._appstate.pipelines.append(self.current_pipeline)
        self.current_pipeline.start()

    def _setup_pipeline(self, model: str, model_builder: str, weight: str, images_path: list[Path] | None,
                        videos_path: list[Path] | None, stream_url: str | None, results_path: Path | None) -> None:
        """
        Sets up the pipeline for the given model and weight.

        :param model: Model name / file path.
        :param weight: Weight file path.
        :param images_path: List of image paths if processing images.
        :param videos_path: List of video paths if processing videos.
        :param stream_url: URL of the video stream if processing a stream.
        :param results_path: Path to save the results if processing images or videos.
        """
        pipeline = self._appstate.app_config.models[model]['pipeline']
        model_class_path = self._appstate.app_config.pipelines[pipeline]
        module_name, class_name = model_class_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        model_class = getattr(module, class_name)
        self.current_pipeline = model_class(model, model_builder, weight, self._preset, images_path, videos_path,
                                            stream_url, results_path)
        self.current_pipeline.progress_signal.connect(self.progress_signal)
        self.current_pipeline.finished_file_signal.connect(self.finished_file_signal)
        self.current_pipeline.finished_stream_frame_signal.connect(self.finished_stream_frame_signal)
        self.current_pipeline.error_signal.connect(self.error_signal)
        self.current_pipeline.fatal_error_signal.connect(self.fatal_error_signal)

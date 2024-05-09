import datetime
import json
import logging
import os
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from models.app_state import AppState
from models.preset import Preset
from pipeline.pipeline_manager import PipelineManager
from views.collection_selection_widget import CollectionSelectionWidget
from views.models_selection_widget import ModelsSelectionWidget
from views.progress_bar_widget import ProgressBarWidget
from views.task_selection_widget import TaskSelectionWidget
from views.preset_selection_widget import PresetSelectionWidget


class InferenceWidget(QWidget):
    def __init__(self, media_type: str):
        super().__init__()
        self.media_type = media_type
        self.app_state = AppState.get_instance()
        self.pipeline_manager: Optional[PipelineManager] = None

        # PyQT6 Components
        self._main_layout: Optional[QHBoxLayout] = None
        self._collection: Optional[CollectionSelectionWidget] = None
        self._preset: Optional[PresetSelectionWidget] = None
        self._task: Optional[TaskSelectionWidget] = None
        self._models: Optional[ModelsSelectionWidget] = None
        self._run_icon_layout: Optional[QHBoxLayout] = None
        self._run_icon: Optional[QLabel] = None
        self._run_layout: Optional[QVBoxLayout] = None
        self._run_widget: Optional[QWidget] = None
        self._btn_run: Optional[QPushButton] = None
        self._btn_cancel: Optional[QPushButton] = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self._main_layout = QVBoxLayout()
        self._h_layout = QHBoxLayout()
        self._h_layout.addStretch()
        self._h_layout.addWidget(self.collection_ui())
        self._h_layout.addWidget(self.preset_ui())
        self._h_layout.addWidget(self.task_ui())
        self._h_layout.addWidget(self.models_ui())
        self._h_layout.addWidget(self.run_ui())
        self._h_layout.addStretch()
        self._main_layout.addStretch()
        self._main_layout.addLayout(self._h_layout)
        self._main_layout.addStretch()
        self._progress_bar = ProgressBarWidget()
        self._main_layout.addWidget(self._progress_bar)
        self.setLayout(self._main_layout)

    def collection_ui(self) -> CollectionSelectionWidget:
        """
        Collection UI, contains only for now a combobox to select the collection.
        """
        self._collection = CollectionSelectionWidget(self.media_type)
        self._collection.collection_changed_signal.connect(self.check_run)
        return self._collection

    def preset_ui(self) -> PresetSelectionWidget:
        """
        Preset UI
        """
        self._preset = PresetSelectionWidget()
        self._preset.preset_changed_signal.connect(self.check_run)
        return self._preset

    def task_ui(self) -> TaskSelectionWidget:
        """
        Task UI, contains only for now a radio button to select the task. (Detection, Segmentation, Classification, Pose, Tracking)
        """
        self._task = TaskSelectionWidget()
        self._task.task_changed_signal.connect(self.update_models_task)
        return self._task

    def models_ui(self) -> ModelsSelectionWidget:
        """
        Models UI
        """
        self._models = ModelsSelectionWidget()
        self._models.models_changed_signal.connect(self.check_run)
        return self._models

    def run_ui(self) -> QWidget:
        # Run icon
        self._run_icon_layout = QHBoxLayout()
        self._run_icon_layout.addStretch()
        self._run_icon = QLabel()
        self._run_icon.setPixmap(QPixmap('ressources/images/run_icon.png')
                                 .scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation))
        self._run_icon_layout.addWidget(self._run_icon)
        self._run_icon_layout.addStretch()

        # Run button
        self._btn_run = QPushButton(self.tr('Run'))
        self._btn_run.setProperty('class', 'green')
        self._btn_run.setEnabled(False)
        self._btn_run.clicked.connect(self.run)

        # Cancel button
        self._btn_cancel = QPushButton(self.tr('Cancel'))
        self._btn_cancel.setProperty('class', 'red')
        self._btn_cancel.clicked.connect(self.cancel_current_pipeline)
        self._btn_cancel.setEnabled(False)

        # Run Layout
        self._run_layout = QVBoxLayout()
        self._run_layout.addLayout(self._run_icon_layout)
        self._run_layout.addWidget(self._btn_run)
        self._run_layout.addWidget(self._btn_cancel)
        self._run_layout.addStretch()

        self._run_widget = QWidget()
        self._run_widget.setLayout(self._run_layout)
        self._run_widget.setFixedSize(240, 360)
        return self._run_widget

    ##############################
    #         CONTROLLER         #
    ##############################

    def update_models_task(self):
        self._models.set_task(self._task.task)
        self.check_run()

    def check_run(self):
        if self._collection.collection and self._task.task and len(self._models.weights) > 0:
            self._btn_run.setEnabled(True)
        else:
            self._btn_run.setEnabled(False)

    def run(self):
        self._btn_run.setEnabled(False)
        self._btn_cancel.setEnabled(True)

        current_date = datetime.datetime.now()
        formatted_date = current_date.strftime("%Y-%m-%d_%H-%M-%S")
        inputs = self.app_state.collections.get_collection_file_paths(self._collection.collection, self.media_type)

        if len(inputs) == 0:
            QMessageBox.critical(self, self.tr('Error'), self.tr('No image selected'))
            logging.error('No image selected')
            self._btn_cancel.setEnabled(False)
            return

        if self._task.task is None:
            QMessageBox.critical(self, self.tr('Error'), self.tr('No task selected'))
            logging.error('No task selected')
            self._btn_cancel.setEnabled(False)
            return

        if self._models.weights is None or len(self._models.weights) == 0:
            QMessageBox.critical(self, self.tr('Error'), self.tr('No model selected'))
            logging.error('No model selected')
            self._btn_cancel.setEnabled(False)
            return

        result_path = f'history/{self.media_type}_{self._task.task}_{formatted_date}'
        os.makedirs(result_path, exist_ok=True)
        preset = Preset(self._preset.preset)
        self.pipeline_manager = PipelineManager(self._task.task, preset, self._models.weights)
        self.file_count = 0
        total_files = len(inputs) * len(self._models.weights)
        weights = [weight for weights in self._models.weights.values() for weight in weights]

        info = {
            'media': self.media_type,
            'collection': self._collection.collection,
            'preset': self._preset.preset,
            'task': self._task.task,
            'date': formatted_date,
            'weights': weights
        }
        with open(os.path.join(result_path, 'info.json'), 'w') as f:
            json.dump(info, f, indent=4)

        def callback_ok(input_path: str, output_path: str, output_json_path: str) -> None:
            logging.info('Detection done for ' + input_path + ', output in ' + output_json_path)
            self.file_count += 1
            self._progress_bar.update_progress_bar(self.file_count, total_files, 0, os.path.basename(input_path))

        def callback_err(input_media_path: str, exception: Exception) -> None:
            logging.error('Detection failed for ' + input_media_path + ' : ' + str(exception))

        def callback_progress(progress: float) -> None:
            logging.info('Progress: ' + str(progress))
            self._progress_bar.update_progress_bar(self.file_count, total_files, progress, os.path.basename(inputs[self.file_count]))

        self.pipeline_manager.finished_file_signal.connect(callback_ok)
        self.pipeline_manager.error_signal.connect(callback_err)
        self.pipeline_manager.progress_signal.connect(callback_progress)

        if self.media_type == 'image':
            self.pipeline_manager.run_image(inputs, result_path)
        elif self.media_type == 'video':
            self.pipeline_manager.run_video(inputs, result_path)

    def cancel_current_pipeline(self):
        self.pipeline_manager.request_cancel()
        self._btn_cancel.setEnabled(False)
        self._btn_run.setEnabled(True)
        self._progress_bar.update_progress_bar(0, 100, 0, '')

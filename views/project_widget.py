from datetime import datetime
from typing import Callable, Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, \
    QListWidget, QListWidgetItem, QRadioButton
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDragMoveEvent, QDropEvent, QIcon
from PyQt6.QtCore import Qt, QDir, QSize, QTimer
from models.app_state import AppState
from models.project import Project
from views.input_widget import InputWidget
from views.progress_bar_widget import ProgressBarWidget
from views.project_config_window import ProjectConfigWindow
from views.history_result_window import HistoryResultWindow
from views.input_info_widget import InputInfoWidget
from views.image_result_widget import ImageResultWidget
from views.live_result_widget import LiveResultWidget
from views.video_result_widget import VideoResultWidget
from views.other_source_window import OtherSourceWindow
from pipeline import img_detection, vid_detection
import logging
import os


class ProjectWidget(QWidget):
    def __init__(self, add_new_tab: Callable[[QWidget, str, bool], None], project: Project):
        super().__init__()

        # PyQT6 Components
        self._top_layout: Optional[QHBoxLayout] = None
        self._right_layout: Optional[QHBoxLayout] = None
        self._right_vertical_layout: Optional[QVBoxLayout] = None
        self._left_layout: Optional[QHBoxLayout] = None
        self._main_layout: Optional[QVBoxLayout] = None
        self._input_icon_layout: Optional[QHBoxLayout] = None
        self._input_icon: Optional[QLabel] = None
        self._btn_import_image: Optional[QPushButton] = None
        self._btn_import_video: Optional[QPushButton] = None
        self._btn_other_source: Optional[QPushButton] = None
        self._input_layout: Optional[QVBoxLayout] = None
        self._input_widget: Optional[InputWidget] = None
        self._task_icon_layout: Optional[QHBoxLayout] = None
        self._task_icon: Optional[QLabel] = None
        self._task_radio_layout: Optional[QVBoxLayout] = None
        self._task_radio_detection: Optional[QRadioButton] = None
        self._task_radio_segmentation: Optional[QRadioButton] = None
        self._task_radio_classification: Optional[QRadioButton] = None
        self._task_radio_tracking: Optional[QRadioButton] = None
        self._task_radio_posing: Optional[QRadioButton] = None
        self._task_radio_widget: Optional[QWidget] = None
        self._task_layout: Optional[QVBoxLayout] = None
        self._task_widget: Optional[QWidget] = None
        self._model_icon_layout: Optional[QHBoxLayout] = None
        self._model_icon: Optional[QLabel] = None
        self._model_list: Optional[QListWidget] = None
        self._model_layout: Optional[QVBoxLayout] = None
        self._model_widget: Optional[QWidget] = None
        self._run_icon_layout: Optional[QHBoxLayout] = None
        self._run_icon: Optional[QLabel] = None
        self._btn_run: Optional[QPushButton] = None
        self._btn_cancel: Optional[QPushButton] = None
        self._btn_history: Optional[QPushButton] = None
        self._run_layout: Optional[QVBoxLayout] = None
        self._run_widget: Optional[QWidget] = None
        self._input_info: Optional[InputInfoWidget] = None
        self._btn_settings: Optional[QPushButton] = None
        self._other_source_window: Optional[OtherSourceWindow] = None
        self._settings_window: Optional[ProjectConfigWindow] = None
        self._history_window: Optional[HistoryResultWindow] = None
        self._progress_bar: Optional[ProgressBarWidget] = None

        self._appstate = AppState.get_instance()
        self._add_new_tab = add_new_tab
        self._project = project
        self._current_pipeline: Optional[img_detection.ImgDetectionPipeline | vid_detection.VidDetectionPipeline] = None
        self._callback_count = 0
        self._task = project.config.current_task
        self._models = project.config.current_models
        self._live_url = None

        self.setAcceptDrops(True)
        self.init_ui()
        self.check_enable_run()
        QTimer.singleShot(500, self.check_enable_run)

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Top Layout
        self._top_layout = QHBoxLayout()
        self._top_layout.addStretch(1)
        self._top_layout.addWidget(self.settings_ui())

        # Right Layout
        self._right_layout = QHBoxLayout()
        self._right_layout.addWidget(self.task_ui())
        self._right_layout.addWidget(self.model_ui())
        self._right_layout.addWidget(self.run_ui())

        self._right_vertical_layout = QVBoxLayout()
        self._right_vertical_layout.addStretch()
        self._right_vertical_layout.addLayout(self._right_layout)
        self._right_vertical_layout.addStretch()

        # Left Layout
        self._left_layout = QHBoxLayout()
        self._left_layout.addWidget(self.input_info_ui())
        self._left_layout.addStretch()
        self._left_layout.addLayout(self._right_vertical_layout)
        self._left_layout.addStretch()

        # add input_ui to right_layout at first position (needed input_info_ui to be initialized)
        self._right_layout.insertWidget(0, self.input_ui())

        # Main Layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.addLayout(self._top_layout)
        self._main_layout.addLayout(self._left_layout)
        self._main_layout.addWidget(self.progress_bar_ui())
        self.setLayout(self._main_layout)

    def input_info_ui(self):
        self._input_info = InputInfoWidget(f'{QDir.currentPath()}/projects/{self._project.project_name}/input')
        self._input_info.setMinimumSize(240, 240)
        self._input_info.model.selection_changed_signal.connect(self.check_enable_run)
        return self._input_info

    def settings_ui(self) -> QPushButton:
        self._btn_settings = QPushButton()
        self._btn_settings.setIcon(QIcon('ressources/images/settings_icon.png'))
        self._btn_settings.setIconSize(QSize(32, 32))
        self._btn_settings.setFixedWidth(32)
        self._btn_settings.setProperty('class', 'settings')
        self._btn_settings.clicked.connect(self.open_settings)
        return self._btn_settings

    def input_ui(self) -> InputWidget:
        self._input_widget = InputWidget(self._project, self._appstate, self._input_info)
        self._input_widget.input_changed_signal.connect(self.check_enable_run)
        return self._input_widget

    def task_ui(self) -> QWidget:
        # Task icon
        self._task_icon_layout = QHBoxLayout()
        self._task_icon_layout.addStretch()
        self._task_icon = QLabel()
        self._task_icon.setPixmap(
            QPixmap('ressources/images/task_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                              Qt.TransformationMode.SmoothTransformation))
        self._task_icon_layout.addWidget(self._task_icon)
        self._task_icon_layout.addStretch()

        # Task Radio Buttons
        self._task_radio_layout = QVBoxLayout()
        self._task_radio_detection = QRadioButton(self.tr('Detect'))
        self._task_radio_segmentation = QRadioButton(self.tr('Segment'))
        self._task_radio_classification = QRadioButton(self.tr('Classify'))
        self._task_radio_tracking = QRadioButton(self.tr('Track'))
        self._task_radio_posing = QRadioButton(self.tr('Pose'))

        self._task_radio_detection.setObjectName('detect')
        self._task_radio_segmentation.setObjectName('segment')
        self._task_radio_classification.setObjectName('classify')
        self._task_radio_tracking.setObjectName('track')
        self._task_radio_posing.setObjectName('pose')

        self._task_radio_detection.toggled.connect(self._check_task_selected)
        self._task_radio_segmentation.toggled.connect(self._check_task_selected)
        self._task_radio_classification.toggled.connect(self._check_task_selected)
        self._task_radio_tracking.toggled.connect(self._check_task_selected)
        self._task_radio_posing.toggled.connect(self._check_task_selected)

        if self._task == 'detect':
            self._task_radio_detection.setChecked(True)
        elif self._task == 'segment':
            self._task_radio_segmentation.setChecked(True)
        elif self._task == 'classify':
            self._task_radio_classification.setChecked(True)
        elif self._task == 'track':
            self._task_radio_tracking.setChecked(True)
        elif self._task == 'pose':
            self._task_radio_posing.setChecked(True)

        self._task_radio_layout.addWidget(self._task_radio_detection)
        self._task_radio_layout.addWidget(self._task_radio_segmentation)
        self._task_radio_layout.addWidget(self._task_radio_classification)
        self._task_radio_layout.addWidget(self._task_radio_tracking)
        self._task_radio_layout.addWidget(self._task_radio_posing)

        self._task_radio_widget = QWidget()
        self._task_radio_widget.setLayout(self._task_radio_layout)
        self._task_radio_widget.setProperty('class', 'border')

        # Task Layout
        self._task_layout = QVBoxLayout()
        self._task_layout.addLayout(self._task_icon_layout)
        self._task_layout.addWidget(self._task_radio_widget)
        self._task_layout.addStretch()

        self._task_widget = QWidget()
        self._task_widget.setLayout(self._task_layout)
        self._task_widget.setFixedSize(240, 240)
        return self._task_widget

    def model_ui(self) -> QWidget:
        # Model icon
        self._model_icon_layout = QHBoxLayout()
        self._model_icon_layout.addStretch()
        self._model_icon = QLabel()
        self._model_icon.setPixmap(
            QPixmap('ressources/images/model_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                               Qt.TransformationMode.SmoothTransformation))
        self._model_icon_layout.addWidget(self._model_icon)
        self._model_icon_layout.addStretch()

        # Model List
        def on_item_clicked(clicked_item):
            if clicked_item.checkState() == Qt.CheckState.Unchecked:
                new_state = Qt.CheckState.Checked
            else:
                new_state = Qt.CheckState.Unchecked
            clicked_item.setCheckState(new_state)

        self._model_list = QListWidget()
        model_names = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt']
        for model_name in model_names:
            item = QListWidgetItem(model_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if self._models and model_name in self._models:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self._model_list.addItem(item)

        self._model_list.itemChanged.connect(self.check_model_selected)
        self._model_list.itemDoubleClicked.connect(on_item_clicked)

        # Model Layout
        self._model_layout = QVBoxLayout()
        self._model_layout.addLayout(self._model_icon_layout)
        self._model_layout.addWidget(self._model_list)
        self._model_layout.addStretch()

        self._model_widget = QWidget()
        self._model_widget.setLayout(self._model_layout)
        self._model_widget.setFixedSize(240, 240)
        return self._model_widget

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
        self._btn_run.setProperty('class', 'run')
        self._btn_run.setEnabled(False)
        self._btn_run.clicked.connect(self.run)

        # Cancel button
        self._btn_cancel = QPushButton(self.tr('Cancel'))
        self._btn_cancel.setProperty('class', 'cancel')
        self._btn_cancel.clicked.connect(self.cancel_current_pipeline)
        self._btn_cancel.setEnabled(False)

        # Result history button
        self._btn_history = QPushButton(self.tr('Result History'))
        self._btn_history.clicked.connect(self.open_history)

        # Run Layout
        self._run_layout = QVBoxLayout()
        self._run_layout.addLayout(self._run_icon_layout)
        self._run_layout.addWidget(self._btn_run)
        self._run_layout.addWidget(self._btn_cancel)
        self._run_layout.addWidget(self._btn_history)
        self._run_layout.addStretch()

        self._run_widget = QWidget()
        self._run_widget.setLayout(self._run_layout)
        self._run_widget.setFixedSize(240, 240)
        return self._run_widget

    def progress_bar_ui(self) -> ProgressBarWidget:
        self._progress_bar = ProgressBarWidget()
        return self._progress_bar

    ##############################
    #         CONTROLLER         #
    ##############################

    def dragEnterEvent(self, event: QDragEnterEvent | None):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent | None):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent | None):
        urls = event.mimeData().urls()
        file_paths = []
        for url in urls:
            if url.isLocalFile():
                path = url.toLocalFile()
            else:
                path = url.toString()
            if path.endswith(('.png', '.jpg', '.jpeg')):
                file_paths.append(path)
            elif path.endswith(('.mp4', '.avi', '.mov', '.webm')):
                file_paths.append(path)
        self._input_widget.open_files(file_paths=file_paths)

    def open_settings(self):
        self._settings_window = ProjectConfigWindow(self._project)
        self._settings_window.show()
        logging.debug('Window opened : Settings')

    def open_history(self):
        self._history_window = HistoryResultWindow(self._add_new_tab, self._project)
        self._history_window.show()
        logging.debug('Window opened : History')

    def _check_task_selected(self):
        if self._task_radio_detection.isChecked():
            self._task = 'detect'
        elif self._task_radio_segmentation.isChecked():
            self._task = 'segment'
        elif self._task_radio_classification.isChecked():
            self._task = 'classify'
        elif self._task_radio_tracking.isChecked():
            self._task = 'track'
        elif self._task_radio_posing.isChecked():
            self._task = 'pose'
        self._project.config.current_task = self._task
        self._project.save()
        logging.debug('Task selected: ' + self._task)
        self.check_enable_run()

    def check_model_selected(self):
        self._models = []
        for i in range(self._model_list.count()):
            if self._model_list.item(i).checkState() == Qt.CheckState.Checked:
                self._models.append(self._model_list.item(i).text())
        self._project.config.current_models = self._models
        self._project.save()
        logging.debug('Models selected: ' + ', '.join(self._models))
        self.check_enable_run()

    def check_enable_run(self):
        if self._input_info is None:
            return
        if self._input_widget.media_type == 'image':
            selected_files_len = len(self._input_info.get_selected_files('images'))
            if selected_files_len > 0 and self._models is not None and len(self._models) > 0:
                self._btn_run.setEnabled(True)
            else:
                self._btn_run.setEnabled(False)
        elif self._input_widget.media_type == 'video':
            selected_files_len = len(self._input_info.get_selected_files('videos'))
            if selected_files_len > 0 and self._models is not None and len(self._models) > 0:
                self._btn_run.setEnabled(True)
            else:
                self._btn_run.setEnabled(False)
        elif self._input_widget.media_type == 'live':
            if self._input_widget.live_url is not None and self._models is not None and len(self._models) > 0:
                self._btn_run.setEnabled(True)
                self._input_info.collapse_all()
            else:
                self._btn_run.setEnabled(False)

    def cancel_current_pipeline(self):
        if self._current_pipeline:
            self._current_pipeline.request_cancel()
            self._btn_cancel.setEnabled(False)
            self._btn_run.setEnabled(True)
            self._callback_count = 0
            self._progress_bar.update_progress_bar(0, 1, 0)

    def run(self):
        self._btn_run.setEnabled(False)
        self._btn_cancel.setEnabled(True)

        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y-%m-%d_%H:%M:%S")

        if self._input_widget.media_type == 'image' and self._task == 'detect':
            inputs = self._input_info.get_selected_files('images')
            if len(inputs) == 0:
                QMessageBox.critical(self, self.tr('Error'), self.tr('No image selected'))
                logging.error('No image selected')
                self._btn_cancel.setEnabled(False)
                return
            logging.info(f'Run with: {inputs}, {self._models}, detect, image')
            folder_name = f'image_detection_{formatted_date}'
            result_path = os.path.abspath(f'projects/{self._project.project_name}/result/')
            result_path = os.path.join(result_path, folder_name)
            os.mkdir(result_path)

            self._current_pipeline = img_detection.ImgDetectionPipeline(inputs, self._models, result_path, self._project)
            self._callback_count = 0
            self._progress_bar.update_progress_bar(0, len(inputs) * len(self._models), 0)
            result_widget = ImageResultWidget(self._project, result_path)
            self._add_new_tab(result_widget, f"{self._project.project_name} : Image detection", len(inputs) == 1)

            def callback_ok(input_path: str, _: str, output_json_path: str) -> None:
                logging.info('Detection done for ' + input_path + ', output in ' + output_json_path)
                result_widget.add_input_and_result(input_path, output_json_path)
                self._callback_count += 1
                self._progress_bar.update_progress_bar(self._callback_count, len(inputs) * len(self._models), 0)
                if self._callback_count == len(inputs) * len(self._models):
                    self._current_pipeline = None
                    self._btn_cancel.setEnabled(False)
                    self._btn_run.setEnabled(True)

            def callback_err(input_media_path: str, exception: Exception) -> None:
                logging.error('Detection failed for ' + input_media_path + ' : ' + str(exception))

            self._current_pipeline.finished_signal.connect(callback_ok)
            self._current_pipeline.error_signal.connect(callback_err)
            self._current_pipeline.start()

        elif self._input_widget.media_type == 'video' and self._task == 'detect':
            inputs = self._input_info.get_selected_files('videos')
            if len(inputs) == 0:
                QMessageBox.critical(self, self.tr('Error'), self.tr('No video selected'))
                logging.error('No video selected')
                self._btn_cancel.setEnabled(False)
                return
            logging.info(f'Run with: {inputs}, {self._models}, detect, video')
            folder_name = f'video_detection_{formatted_date}'
            result_path = os.path.abspath(f'projects/{self._project.project_name}/result/')
            result_path = os.path.join(result_path, folder_name)
            os.mkdir(result_path)

            self._current_pipeline = vid_detection.VidDetectionPipeline(inputs, self._models, result_path, self._project)
            self._callback_count = 0
            self._progress_bar.update_progress_bar(0, len(inputs) * len(self._models), 0)
            result_widget = VideoResultWidget(self._project, result_path)
            self._add_new_tab(result_widget, f"{self._project.project_name} : Video detection", False)

            def callback_progress(progress: float) -> None:
                self._progress_bar.update_progress_bar(self._callback_count, len(inputs) * len(self._models), progress)

            def callback_ok(input_path: str, output_media_path: str, output_json_path: str) -> None:
                logging.info('Detection done for ' + input_path + ', output in ' + output_media_path)
                result_widget.add_input_and_result(input_path, output_media_path, output_json_path)
                self._callback_count += 1
                self._progress_bar.update_progress_bar(self._callback_count, len(inputs) * len(self._models), 0)
                if self._callback_count == len(inputs) * len(self._models):
                    self._current_pipeline = None
                    self._btn_cancel.setEnabled(False)
                    self._btn_run.setEnabled(True)

            def callback_err(input_media_path: str, exception: Exception) -> None:
                logging.error('Detection failed for ' + input_media_path + ' : ' + str(exception))

            def callback_cleanup() -> None:
                self._callback_count = 0
                self._progress_bar.update_progress_bar(0, 1, 0)
                self._current_pipeline = None
                self._btn_cancel.setEnabled(False)
                self._btn_run.setEnabled(True)

            self._current_pipeline.finished_signal.connect(callback_ok)
            self._current_pipeline.progress_signal.connect(callback_progress)
            self._current_pipeline.error_signal.connect(callback_err)
            self._current_pipeline.cleanup_signal.connect(callback_cleanup)
            self._current_pipeline.start()

        elif self._input_widget.media_type == 'live' and self._task == 'detect':
            logging.info(f'Run with: {self._input_widget.live_url}, {self._models}, detect, live')
            result_widget = LiveResultWidget(self._input_widget.live_url, self._models[0], self._project)
            self._add_new_tab(result_widget, f"{self._project.project_name} : Live detection", False)
            self._btn_cancel.setEnabled(False)
            self._btn_run.setEnabled(True)

        else:
            QMessageBox.critical(self, self.tr('Error'), f"{self.tr('Invalid combination of media type and task')}: "
                                                         f"{self._input_widget.media_type}, {self._task}")
            logging.error(f'Invalid combination of media type and task: {self._input_widget.media_type}, {self._task}')

    def stop(self):
        project_name = self._project.project_name
        self._appstate.opened_projects.remove(project_name)

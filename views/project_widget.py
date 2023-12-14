from datetime import datetime
from typing import Callable
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QProgressBar, \
    QMessageBox, QListWidget, QListWidgetItem, QRadioButton
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDragMoveEvent, QDropEvent, QIcon
from PyQt6.QtCore import Qt, QDir, QFile, QSize, QTimer
from models.app_state import AppState
from models.project import Project
from views.config_window import ConfigWindow
from views.history_result_window import HistoryResultWindow
from views.input_info_widget import InputInfoWidget
from views.image_result_widget import ImageResultWidget
from views.live_result_widget import LiveResultWidget
from views.video_result_widget import VideoResultWidget
from views.other_source_window import OtherSourceWindow
from pipeline import img_detection, vid_detection
import logging
import os
import urllib.request


class ProjectWidget(QWidget):
    def __init__(self, add_new_tab: Callable[[QWidget, str, bool], None], project: Project):
        super().__init__()
        self._appstate = AppState.get_instance()

        self._add_new_tab = add_new_tab
        self._project = project
        self._current_pipeline = None
        self._callback_count = 0
        self._other_source_window = None
        self._settings_window = None
        self._history_window = None
        self._progress_bar = None
        self._input_info = None

        self._media_type = project.config.current_media_type
        self._task = project.config.current_task
        self._models = project.config.current_models
        self._live_url = None

        self._btn_import_image = None
        self._btn_import_video = None
        self._btn_other_source = None
        self._task_radios = None
        self._model_list = None
        self._btn_run = None
        self._btn_cancel = None

        self.setAcceptDrops(True)
        self.init_ui()
        QTimer.singleShot(1000, self.check_enable_run)

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Top Layout
        top_layout = QHBoxLayout()
        top_layout.addStretch(1)
        top_layout.addWidget(self.settings_ui())

        # Right Layout
        right_layout = QHBoxLayout()
        right_layout.addWidget(self.input_ui())
        right_layout.addWidget(self.task_ui())
        right_layout.addWidget(self.model_ui())
        right_layout.addWidget(self.run_ui())

        right_vertical_layout = QVBoxLayout()
        right_vertical_layout.addStretch()
        right_vertical_layout.addLayout(right_layout)
        right_vertical_layout.addStretch()

        # Left Layout
        left_layout = QHBoxLayout()
        left_layout.addWidget(self.input_info_ui())
        left_layout.addStretch()
        left_layout.addLayout(right_vertical_layout)
        left_layout.addStretch()

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.progress_bar_ui())
        self.setLayout(main_layout)

    def input_info_ui(self):
        input_info = InputInfoWidget(f'{QDir.currentPath()}/projects/{self._project.project_name}/input')
        input_info.setMinimumSize(240, 240)
        input_info.model.selection_changed_signal.connect(self.check_enable_run)
        self._input_info = input_info
        return input_info

    def settings_ui(self) -> QPushButton:
        btn_settings = QPushButton()
        btn_settings.setIcon(QIcon('ressources/images/settings_icon.png'))
        btn_settings.setIconSize(QSize(32, 32))
        btn_settings.setFixedWidth(32)
        btn_settings.setProperty('class', 'settings')
        btn_settings.clicked.connect(self.open_settings)
        return btn_settings

    def input_ui(self) -> QWidget:
        # Input icon
        input_icon_layout = QHBoxLayout()
        input_icon_layout.addStretch()
        input_icon = QLabel()
        input_icon.setPixmap(
            QPixmap('ressources/images/input_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                               Qt.TransformationMode.SmoothTransformation))
        input_icon_layout.addWidget(input_icon)
        input_icon_layout.addStretch()

        # Input buttons
        btn_import_image = QPushButton('Import Image')
        btn_import_image.setProperty('class', 'input')
        btn_import_image.clicked.connect(self.open_image)
        self._btn_import_image = btn_import_image
        btn_import_video = QPushButton('Import Video')
        btn_import_video.setProperty('class', 'input')
        btn_import_video.clicked.connect(self.open_video)
        self._btn_import_video = btn_import_video
        btn_other_source = QPushButton('Other Source')
        btn_other_source.setProperty('class', 'input')
        btn_other_source.clicked.connect(self.open_other_source)
        self._btn_other_source = btn_other_source

        # Input Layout
        input_layout = QVBoxLayout()
        input_layout.addLayout(input_icon_layout)
        input_layout.addWidget(btn_import_image)
        input_layout.addWidget(btn_import_video)
        input_layout.addWidget(btn_other_source)
        input_layout.addStretch()

        input_widget = QWidget()
        input_widget.setLayout(input_layout)
        input_widget.setFixedSize(240, 240)
        return input_widget

    def task_ui(self) -> QWidget:
        # Task icon
        task_icon_layout = QHBoxLayout()
        task_icon_layout.addStretch()
        task_icon = QLabel()
        task_icon.setPixmap(
            QPixmap('ressources/images/task_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                              Qt.TransformationMode.SmoothTransformation))
        task_icon_layout.addWidget(task_icon)
        task_icon_layout.addStretch()

        # Task Radio Buttons
        task_radio_layout = QVBoxLayout()
        task_radio_detection = QRadioButton('Detect')
        task_radio_segmentation = QRadioButton('Segment')
        task_radio_classification = QRadioButton('Classify')
        task_radio_tracking = QRadioButton('Track')
        task_radio_posing = QRadioButton('Pose')

        task_radio_detection.setObjectName('detect')
        task_radio_segmentation.setObjectName('segment')
        task_radio_classification.setObjectName('classify')
        task_radio_tracking.setObjectName('track')
        task_radio_posing.setObjectName('pose')

        task_radio_detection.toggled.connect(self.check_task_selected)
        task_radio_segmentation.toggled.connect(self.check_task_selected)
        task_radio_classification.toggled.connect(self.check_task_selected)
        task_radio_tracking.toggled.connect(self.check_task_selected)
        task_radio_posing.toggled.connect(self.check_task_selected)

        if self._task == 'detect':
            task_radio_detection.setChecked(True)
        elif self._task == 'segment':
            task_radio_segmentation.setChecked(True)
        elif self._task == 'classify':
            task_radio_classification.setChecked(True)
        elif self._task == 'track':
            task_radio_tracking.setChecked(True)
        elif self._task == 'pose':
            task_radio_posing.setChecked(True)

        task_radio_layout.addWidget(task_radio_detection)
        task_radio_layout.addWidget(task_radio_segmentation)
        task_radio_layout.addWidget(task_radio_classification)
        task_radio_layout.addWidget(task_radio_tracking)
        task_radio_layout.addWidget(task_radio_posing)
        self._task_radios = task_radio_layout

        task_radio_widget = QWidget()
        task_radio_widget.setLayout(task_radio_layout)
        task_radio_widget.setProperty('class', 'border')

        # Task Layout
        task_layout = QVBoxLayout()
        task_layout.addLayout(task_icon_layout)
        task_layout.addWidget(task_radio_widget)
        task_layout.addStretch()

        task_widget = QWidget()
        task_widget.setLayout(task_layout)
        task_widget.setFixedSize(240, 240)
        return task_widget

    def model_ui(self) -> QWidget:
        # Model icon
        model_icon_layout = QHBoxLayout()
        model_icon_layout.addStretch()
        model_icon = QLabel()
        model_icon.setPixmap(
            QPixmap('ressources/images/model_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                               Qt.TransformationMode.SmoothTransformation))
        model_icon_layout.addWidget(model_icon)
        model_icon_layout.addStretch()

        # Model List
        def on_item_clicked(clicked_item):
            if clicked_item.checkState() == Qt.CheckState.Unchecked:
                new_state = Qt.CheckState.Checked
            else:
                new_state = Qt.CheckState.Unchecked
            clicked_item.setCheckState(new_state)

        model_list = QListWidget()
        model_names = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt']
        for model_name in model_names:
            item = QListWidgetItem(model_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if self._models and model_name in self._models:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            model_list.addItem(item)

        model_list.itemChanged.connect(self.check_model_selected)
        model_list.itemDoubleClicked.connect(on_item_clicked)
        self._model_list = model_list

        # Model Layout
        model_layout = QVBoxLayout()
        model_layout.addLayout(model_icon_layout)
        model_layout.addWidget(model_list)
        model_layout.addStretch()

        model_widget = QWidget()
        model_widget.setLayout(model_layout)
        model_widget.setFixedSize(240, 240)
        return model_widget

    def run_ui(self) -> QWidget:
        # Run icon
        run_icon_layout = QHBoxLayout()
        run_icon_layout.addStretch()
        run_icon = QLabel()
        run_icon.setPixmap(QPixmap('ressources/images/run_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                                            Qt.TransformationMode.SmoothTransformation))
        run_icon_layout.addWidget(run_icon)
        run_icon_layout.addStretch()

        # Run button
        btn_run = QPushButton('Run')
        btn_run.setProperty('class', 'run')
        btn_run.setEnabled(False)
        btn_run.clicked.connect(self.run)
        self._btn_run = btn_run

        # Cancel button
        btn_cancel = QPushButton('Cancel')
        btn_cancel.setProperty('class', 'cancel')
        btn_cancel.clicked.connect(self.cancel_current_pipeline)
        btn_cancel.setEnabled(False)
        self._btn_cancel = btn_cancel

        # Result history button
        btn_history = QPushButton('Result History')
        btn_history.clicked.connect(self.open_history)

        # Run Layout
        run_layout = QVBoxLayout()
        run_layout.addLayout(run_icon_layout)
        run_layout.addWidget(btn_run)
        run_layout.addWidget(btn_cancel)
        run_layout.addWidget(btn_history)
        run_layout.addStretch()

        run_widget = QWidget()
        run_widget.setLayout(run_layout)
        run_widget.setFixedSize(240, 240)
        return run_widget

    def progress_bar_ui(self) -> QProgressBar:
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(True)
        progress_bar.setFormat('%p%')
        progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._progress_bar = progress_bar
        return progress_bar

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
        image_paths = []
        video_paths = []
        for url in urls:
            if url.isLocalFile():
                path = url.toLocalFile()
            else:
                path = url.toString()
            if path.endswith(('.png', '.jpg', '.jpeg')):
                image_paths.append(path)
            elif path.endswith(('.mp4', '.avi', '.mov', '.webm')):
                video_paths.append(path)
        if image_paths:
            self.open_image(file_paths=image_paths)
        if video_paths:
            self.open_video(file_paths=video_paths)

    def open_media(self, media_type: str, file_mime_types: list[str], file_extensions: tuple[str, ...],
                   file_paths: list[str] = None) -> list[str]:
        if file_paths is None:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(self._appstate.qss)
            msg_box.setText("What do you want to open?")
            files_btn = msg_box.addButton("Files", QMessageBox.ButtonRole.YesRole)
            msg_box.addButton("Folder", QMessageBox.ButtonRole.NoRole)
            msg_box.exec()

            if msg_box.clickedButton() == files_btn:
                dialog = QFileDialog(self, f"Open {media_type.capitalize()}(s)", "/")
                dialog.setMimeTypeFilters(file_mime_types)
                dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
                filenames = dialog.selectedFiles() if dialog.exec() else []
            else:
                dialog = QFileDialog(self, "Select Folder", "/")
                dialog.setFileMode(QFileDialog.FileMode.Directory)
                dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
                if dialog.exec():
                    folder_path = dialog.selectedFiles()[0]
                    filenames = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                                 if any(f.lower().endswith(ext) for ext in file_extensions)]
                else:
                    filenames = []
        else:
            filenames = file_paths

        return filenames

    def process_media_files(self, media_type: str, filenames: list[str]):
        if len(filenames) > 0:
            self._media_type = media_type
            self._project.config.current_media_type = media_type
            self._project.save()
            logging.debug(f'{media_type.capitalize()}(s) opened : {filenames}')

            for filename in filenames:
                if filename.startswith(('http://', 'https://')):
                    self.download_file_to_input(filename)
                else:
                    self.copy_files(filenames)

            self.check_enable_run()

    def open_image(self, _: bool = False, file_paths: list[str] = None):
        image_files = self.open_media('image', ["image/png", "image/jpeg"],
                                      ('.png', '.jpg', '.jpeg'), file_paths)
        self.process_media_files('image', image_files)

    def open_video(self, _: bool = False, file_paths: list[str] = None):
        video_files = self.open_media('video', ["video/mp4", "video/avi", "video/mov", "video/webm"],
                                      ('.mp4', '.avi', '.mov', '.webm'), file_paths)
        self.process_media_files('video', video_files)

    def open_live(self, url: str):
        self._media_type = 'live'
        self._project.config.current_media_type = 'live'
        self._project.save()
        self._live_url = url
        self._input_info.set_live_preview(url)
        self.check_enable_run()

    def download_file_to_input(self, url: str):
        media = urllib.request.urlopen(url)
        media_name = os.path.basename(url)
        subfolder = 'images' if any(url.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg')) else 'videos'
        file_path = f'projects/{self._project.project_name}/input/{subfolder}/{media_name}'
        with open(file_path, 'wb') as f:
            f.write(media.read())
        return file_path

    def copy_files(self, file_paths: list[str]):
        for file_path in file_paths:
            file_name = file_path.split('/')[-1]
            subfolder = 'images' if any(file_path.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg')) else 'videos'
            destination_path = f'projects/{self._project.project_name}/input/{subfolder}/{file_name}'
            QFile.copy(file_path, destination_path)

    def open_other_source(self):
        self._other_source_window = OtherSourceWindow(self.callback_other_source)
        self._other_source_window.show()
        logging.debug('Window opened : Other Source')

    def open_settings(self):
        self._settings_window = ConfigWindow(self._project)
        self._settings_window.show()
        logging.debug('Window opened : Settings')

    def open_history(self):
        self._history_window = HistoryResultWindow(self._add_new_tab, self._project)
        self._history_window.show()
        logging.debug('Window opened : History')

    def callback_other_source(self, url: str, image: bool, video: bool, live: bool) -> None:
        if image:
            self.open_image(file_paths=[url])
        elif video:
            self.open_video(file_paths=[url])
        elif live:
            self.open_live(url)
        self.check_enable_run()

    def check_task_selected(self):
        if self._task_radios is None:
            return
        for i in reversed(range(self._task_radios.count())):
            if self._task_radios.itemAt(i).widget().isChecked():
                task = self._task_radios.itemAt(i).widget().objectName()
                self._task = task
                self._project.config.current_task = task
                self._project.save()
                break
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
        selected_image_len = len(self._input_info.get_selected_files('images'))
        selected_video_len = len(self._input_info.get_selected_files('videos'))
        if (selected_image_len > 0 or selected_video_len > 0 or self._live_url is not None) \
                and self._models is not None and len(self._models) > 0 and self._task is not None:
            self._btn_run.setEnabled(True)
        else:
            self._btn_run.setEnabled(False)
        logging.debug('Run enabled : ' + str(self._btn_run.isEnabled()))

    def cancel_current_pipeline(self):
        if self._current_pipeline:
            self._current_pipeline.request_cancel()
            self._btn_cancel.setEnabled(False)
            self._btn_run.setEnabled(True)
            self._callback_count = 0
            self.update_progress_bar(0, 1, 0)

    def run(self):
        self._btn_run.setEnabled(False)
        self._btn_cancel.setEnabled(True)

        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y-%m-%d_%H:%M:%S")

        if self._media_type == 'image' and self._task == 'detect':
            inputs = self._input_info.get_selected_files('images')
            logging.info(f'Run with: {inputs}, {self._models}, detect, image')
            folder_name = f'image_detection_{formatted_date}'
            result_path = os.path.abspath(f'projects/{self._project.project_name}/result/')
            result_path = os.path.join(result_path, folder_name)
            os.mkdir(result_path)

            pipeline = img_detection.ImgDetectionPipeline(inputs, self._models, result_path, self._project)
            self._callback_count = 0
            self.update_progress_bar(0, len(inputs) * len(self._models), 0)
            result_widget = ImageResultWidget(self._project, result_path)
            self._add_new_tab(result_widget, f"{self._project.project_name} : Image detection", len(inputs) == 1)

            def callback_ok(input_path: str, _: str, output_json_path: str) -> None:
                logging.info('Detection done for ' + input_path + ', output in ' + output_json_path)
                result_widget.add_input_and_result(input_path, output_json_path)
                self._callback_count += 1
                self.update_progress_bar(self._callback_count, len(inputs) * len(self._models), 0)
                if self._callback_count == len(inputs) * len(self._models):
                    pipeline.deleteLater()
                    self._current_pipeline = None
                    self._btn_cancel.setEnabled(False)
                    self._btn_run.setEnabled(True)

            def callback_err(input_media_path: str, exception: Exception) -> None:
                logging.error('Detection failed for ' + input_media_path + ' : ' + str(exception))

            pipeline.finished_signal.connect(callback_ok)
            pipeline.error_signal.connect(callback_err)
            pipeline.start()
            self._current_pipeline = pipeline

        elif self._media_type == 'video' and self._task == 'detect':
            inputs = self._input_info.get_selected_files('videos')
            logging.info(f'Run with: {inputs}, {self._models}, detect, video')
            folder_name = f'video_detection_{formatted_date}'
            result_path = os.path.abspath(f'projects/{self._project.project_name}/result/')
            result_path = os.path.join(result_path, folder_name)
            os.mkdir(result_path)

            pipeline = vid_detection.VidDetectionPipeline(inputs, self._models, result_path, self._project)
            self._callback_count = 0
            self.update_progress_bar(0, len(inputs) * len(self._models), 0)
            result_widget = VideoResultWidget(self._project, result_path)
            self._add_new_tab(result_widget, f"{self._project.project_name} : Video detection", False)

            def callback_progress(progress: float) -> None:
                self.update_progress_bar(self._callback_count, len(inputs) * len(self._models), progress)

            def callback_ok(input_path: str, output_media_path: str, output_json_path: str) -> None:
                logging.info('Detection done for ' + input_path + ', output in ' + output_media_path)
                result_widget.add_input_and_result(input_path, output_media_path, output_json_path)
                self._callback_count += 1
                self.update_progress_bar(self._callback_count, len(inputs) * len(self._models), 0)
                if self._callback_count == len(inputs) * len(self._models):
                    pipeline.deleteLater()
                    self._current_pipeline = None
                    self._btn_cancel.setEnabled(False)
                    self._btn_run.setEnabled(True)

            def callback_err(input_media_path: str, exception: Exception) -> None:
                logging.error('Detection failed for ' + input_media_path + ' : ' + str(exception))

            def callback_cleanup() -> None:
                self._callback_count = 0
                self.update_progress_bar(0, 1, 0)
                pipeline.deleteLater()
                self._current_pipeline = None
                self._btn_cancel.setEnabled(False)
                self._btn_run.setEnabled(True)

            pipeline.finished_signal.connect(callback_ok)
            pipeline.progress_signal.connect(callback_progress)
            pipeline.error_signal.connect(callback_err)
            pipeline.cleanup_signal.connect(callback_cleanup)
            pipeline.start()
            self._current_pipeline = pipeline

        elif self._media_type == 'live' and self._task == 'detect':
            logging.info(f'Run with: {self._live_url}, {self._models}, detect, live')
            result_widget = LiveResultWidget(self._live_url, self._models[0], self._project)
            self._add_new_tab(result_widget, f"{self._project.project_name} : Live detection", False)
            self._btn_cancel.setEnabled(False)
            self._btn_run.setEnabled(True)

        else:
            QMessageBox.critical(self, "Error",
                                 f'Invalid combination of media type and task: {self._media_type}, {self._task}')
            logging.error(f'Invalid combination of media type and task: {self._media_type}, {self._task}')

    def update_progress_bar(self, progress: int, total: int, extra: float):
        self._progress_bar.setValue(int(((progress + extra) / total) * 100))

    def stop(self):
        project_name = self._project.project_name
        self._appstate.opened_projects.remove(project_name)

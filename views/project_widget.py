from typing import Callable
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QFileDialog, \
    QProgressBar, QMessageBox
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt6.QtCore import Qt, QDir, QFile
from models.app_state import AppState
from views.file_list_widget import FileListWidget
from views.image_result_widget import ImageResultWidget
from views.live_result_widget import LiveResultWidget
from views.video_result_widget import VideoResultWidget
from views.other_source_window import OtherSourceWindow
from pipeline import img_detection, vid_detection
import logging
import os
import urllib.request


class ProjectWidget(QWidget):
    def __init__(self, add_new_tab: Callable[[QWidget, str, bool], None], project_name: str):
        super().__init__()
        self._appstate = AppState.get_instance()

        self._project_name = project_name
        self._current_pipeline = None
        self._callback_count = 0
        self._add_new_tab = add_new_tab
        self._other_source_window = None
        self._progress_bar = None
        self._file_list = FileListWidget(f'{QDir.currentPath()}/projects/{self._project_name}/input')
        self._file_list.model.selection_changed_signal.connect(self.check_enable_run)

        self._media_type = None
        self._functionality_selected = None
        self._model_selected = None
        self._live_url = None

        self._btn_import_image = None
        self._btn_import_video = None
        self._btn_other_source = None
        self._functionality_combo = None
        self._model_combo = None
        self._btn_run = None
        self._btn_cancel = None

        self.setAcceptDrops(True)
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Right Layout
        right_layout = QHBoxLayout()
        right_layout.addWidget(self.input_ui())
        right_layout.addWidget(self.functionality_ui())
        right_layout.addWidget(self.model_ui())
        right_layout.addWidget(self.run_ui())

        right_vertical_layout = QVBoxLayout()
        right_vertical_layout.addStretch()
        right_vertical_layout.addLayout(right_layout)
        right_vertical_layout.addStretch()

        # Middle Layout
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self._file_list)
        middle_layout.addStretch()
        middle_layout.addLayout(right_vertical_layout)
        middle_layout.addStretch()

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(middle_layout)
        main_layout.addWidget(self.progress_bar_ui())
        self.setLayout(main_layout)

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

    def functionality_ui(self) -> QWidget:
        # Functionality icon
        functionality_icon_layout = QHBoxLayout()
        functionality_icon_layout.addStretch()
        functionality_icon = QLabel()
        functionality_icon.setPixmap(
            QPixmap('ressources/images/functionality_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                                       Qt.TransformationMode.SmoothTransformation))
        functionality_icon_layout.addWidget(functionality_icon)
        functionality_icon_layout.addStretch()

        # Functionality Combo
        functionality_combo = QComboBox()
        functionality_combo.addItem('Functionality')
        functionality_combo.addItem('Detection', 'detect')
        functionality_combo.currentIndexChanged.connect(self.check_functionality_selected)
        self._functionality_combo = functionality_combo

        # Functionality Layout
        functionality_layout = QVBoxLayout()
        functionality_layout.addLayout(functionality_icon_layout)
        functionality_layout.addWidget(functionality_combo)
        functionality_layout.addStretch()

        functionality_widget = QWidget()
        functionality_widget.setLayout(functionality_layout)
        functionality_widget.setFixedSize(240, 240)
        return functionality_widget

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

        # Model Combo
        model_combo = QComboBox()
        model_combo.addItem('Model')
        model_combo.addItem('YOLOv8n', 'yolov8n.pt')
        model_combo.addItem('YOLOv8s', 'yolov8s.pt')
        model_combo.addItem('YOLOv8m', 'yolov8m.pt')
        model_combo.addItem('YOLOv8l', 'yolov8l.pt')
        model_combo.addItem('YOLOv8x', 'yolov8x.pt')
        model_combo.currentIndexChanged.connect(self.check_model_selected)
        self._model_combo = model_combo

        # Model Layout
        model_layout = QVBoxLayout()
        model_layout.addLayout(model_icon_layout)
        model_layout.addWidget(model_combo)
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

        # Run Layout
        run_layout = QVBoxLayout()
        run_layout.addLayout(run_icon_layout)
        run_layout.addWidget(btn_run)
        run_layout.addWidget(btn_cancel)
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
            if self._media_type != media_type:
                self.reset_input_folder()
            self._media_type = media_type
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
        if self._media_type != 'live':
            self.reset_input_folder()
        self._media_type = 'live'
        self._live_url = url
        self._file_list.set_live_preview(url)
        self.check_enable_run()

    def download_file_to_input(self, url: str):
        media = urllib.request.urlopen(url)
        media_name = os.path.basename(url)
        file_path = f'projects/{self._project_name}/input/{media_name}'
        with open(file_path, 'wb') as f:
            f.write(media.read())
        return file_path

    def copy_files(self, file_paths: list[str]):
        for file_path in file_paths:
            file_name = file_path.split('/')[-1]
            QFile.copy(file_path, f'projects/{self._project_name}/input/{file_name}')

    def reset_input_folder(self):
        for file in os.listdir(f'projects/{self._project_name}/input'):
            os.remove(f'projects/{self._project_name}/input/{file}')

    def open_other_source(self):
        self._other_source_window = OtherSourceWindow(self.callback_other_source)
        self._other_source_window.show()
        logging.debug('Window opened : Other Source')

    def callback_other_source(self, url: str, image: bool, video: bool, live: bool) -> None:
        if image:
            self.open_image(file_paths=[url])
        elif video:
            self.open_video(file_paths=[url])
        elif live:
            self.open_live(url)
        self.check_enable_run()

    def check_functionality_selected(self, index: int):
        if index != 0:
            self._functionality_selected = True
        else:
            self._functionality_selected = False
        logging.debug('Functionality selected : ' + self._functionality_combo.currentData())
        self.check_enable_run()

    def check_model_selected(self, index: int):
        if index != 0:
            self._model_selected = True
        else:
            self._model_selected = False
        logging.debug('Model selected : ' + self._model_combo.currentData())
        self.check_enable_run()

    def check_enable_run(self):
        if ((len(self._file_list.get_selected_files()) > 0 or self._live_url is not None) and self._model_selected
                and self._functionality_selected):
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
            self.update_progress_bar()

    def run(self):
        inputs = self._file_list.get_selected_files()
        model_path = self._model_combo.currentData()
        task = self._functionality_combo.currentData()
        logging.info(f'Run with : {str(inputs)}, {str(model_path)}, {str(task)}, {str(self._media_type)}')
        self._btn_run.setEnabled(False)
        self._btn_cancel.setEnabled(True)

        if self._media_type == 'image' and task == 'detect':
            pipeline = img_detection.ImgDetectionPipeline(inputs, model_path, f'projects/{self._project_name}/result/')
            self._callback_count = 0
            self.update_progress_bar()
            result_widget = ImageResultWidget(self._project_name)
            self._add_new_tab(result_widget, f"{self._project_name} : Image detection", len(inputs) == 1)

            def callback_ok(input_path: str, output_json_path: str) -> None:
                logging.info('Detection done for ' + input_path + ', output in ' + output_json_path)
                result_widget.add_input_and_result(input_path, output_json_path)
                self._callback_count += 1
                self.update_progress_bar()
                if self._callback_count == len(inputs):
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

        elif self._media_type == 'video' and task == 'detect':
            pipeline = vid_detection.VidDetectionPipeline(inputs, model_path, f'projects/{self._project_name}/result/')
            self._callback_count = 0
            self.update_progress_bar()
            result_widget = VideoResultWidget(self._project_name)
            self._add_new_tab(result_widget, f"{self._project_name} : Video detection", False)
            
            def callback_progress(current_frame: int, total_frames: int) -> None:
                self.update_progress_bar(current_frame / total_frames)

            def callback_ok(input_path: str, output_media_path: str, output_json_path: str) -> None:
                logging.info('Detection done for ' + input_path + ', output in ' + output_media_path)
                result_widget.add_input_and_result(input_path, output_media_path, output_json_path)
                self._callback_count += 1
                self.update_progress_bar()
                if self._callback_count == len(inputs):
                    pipeline.deleteLater()
                    self._current_pipeline = None
                    self._btn_cancel.setEnabled(False)
                    self._btn_run.setEnabled(True)

            def callback_err(input_media_path: str, exception: Exception) -> None:
                logging.error('Detection failed for ' + input_media_path + ' : ' + str(exception))

            def callback_cleanup() -> None:
                self._callback_count = 0
                self.update_progress_bar()
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

        elif self._media_type == 'live' and task == 'detect':
            result_widget = LiveResultWidget(self._live_url, model_path)
            self._add_new_tab(result_widget, f"{self._project_name} : Live detection", False)
            self._btn_cancel.setEnabled(False)
            self._btn_run.setEnabled(True)

    def update_progress_bar(self, extra: float = 0.0):
        inputs = self._file_list.get_selected_files()
        base = self._callback_count / len(inputs)
        extra = extra / len(inputs)

        self._progress_bar.setValue(int((base + extra) * 100))

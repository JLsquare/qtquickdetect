import logging
import os
import urllib.request
from typing import Optional
from PyQt6.QtCore import Qt, QFile, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QMessageBox, QFileDialog
from models.app_state import AppState
from models.project import Project
from views.input_info_widget import InputInfoWidget
from views.other_source_window import OtherSourceWindow


class InputWidget(QWidget):
    input_changed_signal = pyqtSignal()

    def __init__(self, project: Project, input_info: InputInfoWidget):
        super().__init__()

        # PyQT6 Components
        self._other_source_window: Optional[OtherSourceWindow] = None
        self._input_icon_layout: Optional[QHBoxLayout] = None
        self._input_icon: Optional[QLabel] = None
        self._btn_import_file: Optional[QPushButton] = None
        self._btn_other_source: Optional[QPushButton] = None
        self._btn_switch_media_type: Optional[QPushButton] = None
        self._input_layout: Optional[QVBoxLayout] = None

        self._project = project
        self._appstate = AppState.get_instance()
        self._input_info = input_info
        self.media_type = self._project.config.current_media_type
        self.live_url = self._project.config.current_live_url

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Input icon
        self._input_icon_layout = QHBoxLayout()
        self._input_icon_layout.addStretch()
        self._input_icon = QLabel()
        self._input_icon.setPixmap(
            QPixmap('ressources/images/input_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                               Qt.TransformationMode.SmoothTransformation))
        self._input_icon_layout.addWidget(self._input_icon)
        self._input_icon_layout.addStretch()

        # Input buttons
        self._btn_import_file = QPushButton(self.tr('Import File'))
        self._btn_import_file.setProperty('class', 'input')
        self._btn_import_file.clicked.connect(self.open_files)
        self._btn_other_source = QPushButton(self.tr('Other Source'))
        self._btn_other_source.setProperty('class', 'input')
        self._btn_other_source.clicked.connect(self._open_other_source)
        self._btn_switch_media_type = QPushButton(self._media_type_str())
        self._btn_switch_media_type.setProperty('class', 'input')
        self._btn_switch_media_type.clicked.connect(self._switch_media_type)

        # Input Layout
        self._input_layout = QVBoxLayout()
        self._input_layout.addLayout(self._input_icon_layout)
        self._input_layout.addWidget(self._btn_import_file)
        self._input_layout.addWidget(self._btn_other_source)
        self._input_layout.addWidget(self._btn_switch_media_type)
        self._input_layout.addStretch()

        self.setLayout(self._input_layout)
        self.setFixedSize(240, 240)

    ##############################
    #         CONTROLLER         #
    ##############################

    def open_files(self, _=None, file_paths: list[str] = None):
        media_type = None

        if file_paths is not None:
            if any(f.lower().endswith(('.png', '.jpg', '.jpeg')) for f in file_paths):
                media_type = 'image'
            elif any(f.lower().endswith(('.mp4', '.avi', '.mov', '.webm')) for f in file_paths):
                media_type = 'video'
            file_paths = file_paths
        else:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(self._appstate.qss)
            msg_box.setText(self.tr('What do you want to open?'))

            close_btn = msg_box.addButton(self.tr('Cancel'), QMessageBox.ButtonRole.RejectRole)
            files_btn = msg_box.addButton(self.tr("Files"), QMessageBox.ButtonRole.ActionRole)
            folder_btn = msg_box.addButton(self.tr('Folder'), QMessageBox.ButtonRole.ActionRole)
            msg_box.exec()

            if msg_box.clickedButton() == files_btn:
                dialog = QFileDialog(self, f"{self.tr('Select Files')}", "/")
                dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
                name_filter = ["Images (*.png *.jpg *.jpeg)", "Videos (*.mp4 *.avi *.mov *.webm)"]
                dialog.setNameFilters(name_filter)
                if dialog.exec():
                    file_paths = dialog.selectedFiles() if dialog.selectedFiles() is not None else []
                    if any(f.lower().endswith(('.png', '.jpg', '.jpeg')) for f in file_paths):
                        media_type = 'image'
                    elif any(f.lower().endswith(('.mp4', '.avi', '.mov', '.webm')) for f in file_paths):
                        media_type = 'video'
                    self._process_media_files(file_paths, str(media_type))
            elif msg_box.clickedButton() == folder_btn:
                file_extensions = ('.png', '.jpg', '.jpeg', '.mp4', '.avi', '.mov', '.webm')
                dialog = QFileDialog(self, self.tr("Select Folder"), "/")
                dialog.setFileMode(QFileDialog.FileMode.Directory)
                dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
                if dialog.exec():
                    folder_path = dialog.selectedFiles()[0]
                    file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                                  if any(f.lower().endswith(ext) for ext in file_extensions)]
                    if any(f.lower().endswith(('.png', '.jpg', '.jpeg')) for f in file_paths):
                        media_type = 'image'
                    elif any(f.lower().endswith(('.mp4', '.avi', '.mov', '.webm')) for f in file_paths):
                        media_type = 'video'
                    self._process_media_files(file_paths, media_type)
            elif msg_box.clickedButton() == close_btn:
                return

    def _process_media_files(self, filenames: list[str], media_type: str):
        if len(filenames) > 0:
            self.media_type = media_type
            self._project.config.current_media_type = media_type
            self._project.save()
            logging.debug(f'{media_type.capitalize()}(s) opened : {filenames}')

            for filename in filenames:
                if filename.startswith(('http://', 'https://')):
                    self._download_file_to_input(filename)
                else:
                    self._copy_files(filenames)

            self.input_changed_signal.emit()

    def _open_live(self, url: str):
        self.media_type = 'live'
        self._project.config.current_media_type = 'live'
        self._project.save()
        self.live_url = url
        self._project.config.current_live_url = url
        self._input_info.set_live_preview(url)
        self.input_changed_signal.emit()

    def _download_file_to_input(self, url: str):
        media = urllib.request.urlopen(url)
        media_name = os.path.basename(url)
        subfolder = 'images' if any(url.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg')) else 'videos'
        file_path = f'projects/{self._project.project_name}/input/{subfolder}/{media_name}'
        with open(file_path, 'wb') as f:
            f.write(media.read())
        return file_path

    def _copy_files(self, file_paths: list[str]):
        for file_path in file_paths:
            file_name = file_path.split('/')[-1]
            subfolder = 'images' if any(
                file_path.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg')) else 'videos'
            destination_path = f'projects/{self._project.project_name}/input/{subfolder}/{file_name}'
            QFile.copy(file_path, destination_path)

    def _open_other_source(self):
        self._other_source_window = OtherSourceWindow(self._callback_other_source)
        self._other_source_window.show()
        logging.debug('Window opened : Other Source')

    def _callback_other_source(self, url: str, image: bool, video: bool, live: bool) -> None:
        if image or video:
            self.open_files([url])
        elif live:
            self._open_live(url)

    def _media_type_str(self):
        if self.media_type == 'image':
            return self.tr('Images')
        elif self.media_type == 'video':
            return self.tr('Videos')
        elif self.media_type == 'live':
            return self.tr('Live')
        else:
            return self.tr('Unknown')

    def _switch_media_type(self):
        if self.media_type == 'image':
            self.media_type = 'video'
        elif self.media_type == 'video':
            self.media_type = 'live'
            self._input_info.set_live_preview(self.live_url)
        elif self.media_type == 'live':
            self.media_type = 'image'
        self._btn_switch_media_type.setText(self._media_type_str())
        self._project.config.current_media_type = self.media_type
        self._project.save()
        self.input_changed_signal.emit()

from typing import Optional
from PyQt6.QtWidgets import QWidget, QTabWidget, QGridLayout, QPushButton
from PyQt6.QtCore import Qt
from models.app_state import AppState
from models.project import Project
from views.image_project_config_widget import ImageProjectConfigWidget
from views.general_project_config_widget import GeneralProjectConfigWidget
from views.video_project_config_widget import VideoProjectConfigWidget
import logging


class ProjectConfigWindow(QWidget):
    def __init__(self, project: Project):
        super().__init__()

        # PyQT6 Components
        self._tab: Optional[QTabWidget] = None
        self._main_layout: Optional[QGridLayout] = None
        self._cancel_button: Optional[QPushButton] = None
        self._save_button: Optional[QPushButton] = None

        self._appstate = AppState.get_instance()
        self._project = project
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self.setWindowTitle(f'{self._project.project_name} Settings')
        self.setGeometry(100, 100, 480, 480)
        self.setStyleSheet(self._appstate.qss)
        self.setProperty('class', 'dark-bg')

        self._tab = QTabWidget(self)
        self._tab.addTab(GeneralProjectConfigWidget(self._project.config), "General")
        self._tab.addTab(ImageProjectConfigWidget(self._project.config), "Image")
        self._tab.addTab(VideoProjectConfigWidget(self._project.config), "Video")
        self._tab.addTab(QWidget(), "Live")

        self._main_layout = QGridLayout(self)
        self._main_layout.addWidget(self._tab, 0, 0, 2, 1)
        self._main_layout.addWidget(self.cancel_button_ui(), 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self._main_layout.addWidget(self.save_button_ui(), 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.setLayout(self._main_layout)

    def cancel_button_ui(self) -> QPushButton:
        self._cancel_button = QPushButton('Cancel')
        self._cancel_button.clicked.connect(self.cancel_settings)
        return self._cancel_button

    def save_button_ui(self) -> QPushButton:
        self._save_button = QPushButton('Save')
        self._save_button.clicked.connect(self.save_settings)
        return self._save_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def save_settings(self):
        self._project.save()
        logging.debug('Saved settings')
        self.close()

    def cancel_settings(self):
        logging.debug('Canceled settings')
        self.close()

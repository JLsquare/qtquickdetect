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

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        tab = QTabWidget(self)

        tab.addTab(GeneralProjectConfigWidget(self._project.config), "General")
        tab.addTab(ImageProjectConfigWidget(self._project.config), "Image")
        tab.addTab(VideoProjectConfigWidget(self._project.config), "Video")
        tab.addTab(QWidget(), "Live")

        main_layout.addWidget(tab, 0, 0, 2, 1)
        main_layout.addWidget(self.cancel_button_ui(), 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.save_button_ui(), 2, 0, alignment=Qt.AlignmentFlag.AlignRight)

    def cancel_button_ui(self) -> QPushButton:
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.cancel_settings)

        return cancel_button

    def save_button_ui(self) -> QPushButton:
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_settings)

        return save_button

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

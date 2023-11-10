from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QGridLayout, QPushButton
from PyQt6.QtCore import Qt
from models.app_state import AppState
from views.image_config_widget import ImageConfig
from views.main_config_widget import MainConfig
from views.video_config_widget import VideoConfig
import logging


class Config(QWidget):
    def __init__(self):
        super().__init__()
        self._appstate = AppState.get_instance()
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self.setWindowTitle('QTQuickDetect Settings')
        self.setGeometry(100, 100, 480, 480)
        with open('ressources/qss/stylesheet.qss', 'r') as file:
            self.setStyleSheet(file.read())

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        tab = QTabWidget(self)

        tab.addTab(MainConfig(self._appstate), "General")
        tab.addTab(ImageConfig(self._appstate), "Image")
        tab.addTab(VideoConfig(self._appstate), "Video")
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
        self._appstate.save()

        logging.debug('Saved settings')
        self.close()

    def cancel_settings(self):
        logging.debug('Canceled settings')
        self.close()

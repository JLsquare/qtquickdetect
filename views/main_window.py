from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QLabel, QPushButton
from models.app_state import AppState
from views.app_config_window import AppConfigWindow
from views.app_tab_widget import AppTabWidget
import logging


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._settings_window = None
        self._appstate = AppState.get_instance()
        self.init_window()
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_window(self):
        self.setWindowTitle('QTQuickDetect')
        self.setGeometry(100, 100, 1280, 720)
        self.setMinimumSize(QSize(1280, 600))
        self.setStyleSheet(self._appstate.qss)
        self.setProperty('class', 'dark-bg')

    def init_ui(self):
        top_layout = QHBoxLayout()
        top_layout.addStretch(1)
        top_layout.addLayout(self.title_ui())
        top_layout.addStretch(1)
        top_layout.addWidget(self.settings_ui())

        main_layout = QGridLayout(self)
        main_layout.addLayout(top_layout, 0, 0)
        main_layout.addWidget(AppTabWidget(), 1, 0)

    def title_ui(self) -> QHBoxLayout:
        title_icon = QLabel()
        pixmap = QPixmap('ressources/images/qtquickdetect_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                                            Qt.TransformationMode.SmoothTransformation)
        title_icon.setPixmap(pixmap)
        title_icon.setFixedWidth(32)
        title_label = QLabel('QTQuickDetect')

        title_layout = QHBoxLayout()
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)

        return title_layout

    def settings_ui(self) -> QPushButton:
        settings_button = QPushButton()
        settings_button.setIcon(QIcon('ressources/images/settings_icon.png'))
        settings_button.setIconSize(QSize(32, 32))
        settings_button.setFixedSize(32, 32)
        settings_button.clicked.connect(self.open_settings)

        return settings_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def open_settings(self):
        logging.debug('Open settings')
        self._settings_window = AppConfigWindow()
        self._settings_window.show()

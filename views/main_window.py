from typing import Optional
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

        # PyQT6 Components
        self._top_layout: Optional[QHBoxLayout] = None
        self._main_layout: Optional[QGridLayout] = None
        self._title_icon: Optional[QLabel] = None
        self._title_label: Optional[QLabel] = None
        self._title_layout: Optional[QHBoxLayout] = None
        self._settings_button: Optional[QPushButton] = None
        self._settings_window: Optional[AppConfigWindow] = None

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
        self._top_layout = QHBoxLayout()
        self._top_layout.addStretch(1)
        self._top_layout.addLayout(self.title_ui())
        self._top_layout.addStretch(1)
        self._top_layout.addWidget(self.settings_ui())

        self._main_layout = QGridLayout(self)
        self._main_layout.addLayout(self._top_layout, 0, 0)
        self._main_layout.addWidget(AppTabWidget(), 1, 0)
        self.setLayout(self._main_layout)

    def title_ui(self) -> QHBoxLayout:
        self._title_icon = QLabel()
        pixmap = QPixmap('ressources/images/qtquickdetect_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                                            Qt.TransformationMode.SmoothTransformation)
        self._title_icon.setPixmap(pixmap)
        self._title_icon.setFixedWidth(32)
        self._title_label = QLabel('QTQuickDetect')

        self._title_layout = QHBoxLayout()
        self._title_layout.addWidget(self._title_icon)
        self._title_layout.addWidget(self._title_label)
        return self._title_layout

    def settings_ui(self) -> QPushButton:
        self._settings_button = QPushButton()
        self._settings_button.setIcon(QIcon('ressources/images/settings_icon.png'))
        self._settings_button.setIconSize(QSize(32, 32))
        self._settings_button.setFixedSize(32, 32)
        self._settings_button.clicked.connect(self.open_settings)

        return self._settings_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def open_settings(self):
        logging.debug('Open settings')
        self._settings_window = AppConfigWindow()
        self._settings_window.show()

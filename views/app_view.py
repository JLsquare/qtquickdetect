from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QLabel, QPushButton
from views.app_tab_view import AppTabView
from views.settings_view import SettingsView
import logging


class AppView(QWidget):
    def __init__(self):
        super().__init__()
        self._settings_window = None

        self.init_window()
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_window(self):
        self.setWindowTitle('QTQuickDetect')
        self.setGeometry(100, 100, 1280, 720)
        with open('ressources/qss/stylesheet.qss', 'r') as file:
            self.setStyleSheet(file.read())

    def init_ui(self):
        main_layout = QGridLayout(self)
        main_layout.addLayout(self.top_ui(), 0, 0)
        main_layout.addWidget(AppTabView(), 1, 0)

    def top_ui(self):
        # Title Layout
        title_layout = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(
            QPixmap('ressources/images/qtquickdetect_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                                       Qt.TransformationMode.SmoothTransformation))
        title_icon.setFixedWidth(32)
        title_label = QLabel('QTQuickDetect')
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)

        # Settings icon
        btn_settings = QPushButton()
        btn_settings.setIcon(QIcon('ressources/images/settings_icon.png'))
        btn_settings.setIconSize(QSize(32, 32))
        btn_settings.setFixedWidth(32)
        btn_settings.setProperty('class', 'settings')
        btn_settings.clicked.connect(self.open_settings)

        # Top layout
        top_layout = QHBoxLayout()
        top_layout.addStretch(1)
        top_layout.addLayout(title_layout)
        top_layout.addStretch(1)
        top_layout.addWidget(btn_settings)

        return top_layout

    ##############################
    #         CONTROLLER         #
    ##############################

    def open_settings(self):
        self._settings_window = SettingsView()
        self._settings_window.show()
        logging.debug('Window opened : Settings')

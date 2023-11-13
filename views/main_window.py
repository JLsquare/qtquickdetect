from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QLabel, QPushButton
from views.app_tab_widget import AppTabWidget
from views.config_window import ConfigWindow
import logging


class MainWindow(QWidget):
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
        btn_settings = QPushButton()
        btn_settings.setIcon(QIcon('ressources/images/settings_icon.png'))
        btn_settings.setIconSize(QSize(32, 32))
        btn_settings.setFixedWidth(32)
        btn_settings.setProperty('class', 'settings')
        btn_settings.clicked.connect(self.open_settings)

        return btn_settings

    ##############################
    #         CONTROLLER         #
    ##############################

    def open_settings(self):
        self._settings_window = ConfigWindow()
        self._settings_window.show()
        logging.debug('Window opened : Settings')

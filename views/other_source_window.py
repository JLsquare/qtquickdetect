from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel
from models.app_state import AppState
from utils.url_handler import *


class OtherSourceWindow(QWidget):
    def __init__(self, callback: Callable[[str, bool, bool, bool], None]):
        super().__init__()

        # PyQT6 Components
        self._main_layout: Optional[QVBoxLayout] = None
        self._url_label: Optional[QLabel] = None
        self._url_input: Optional[QLineEdit] = None
        self._url_layout: Optional[QVBoxLayout] = None
        self._check_button: Optional[QPushButton] = None
        self._format_label: Optional[QLabel] = None
        self._format_display: Optional[QLineEdit] = None
        self._format_layout: Optional[QVBoxLayout] = None
        self._ok_button: Optional[QPushButton] = None
        self._cancel_button: Optional[QPushButton] = None
        self._btn_layout: Optional[QHBoxLayout] = None

        self._appstate = AppState.get_instance()
        self._is_image = False
        self._is_video = False
        self._is_live = False
        self._callback = callback

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self.setWindowTitle(self.tr('QTQuickDetect Other Source'))
        self.setGeometry(100, 100, 480, 240)
        self.setStyleSheet(self._appstate.qss)

        self._main_layout = QVBoxLayout()
        self._main_layout.addLayout(self.url_input_ui())
        self._main_layout.addWidget(self.check_button_ui())
        self._main_layout.addLayout(self.format_ui())
        self._main_layout.addStretch()
        self._main_layout.addLayout(self.btn_layout())
        self.setLayout(self._main_layout)

    def url_input_ui(self) -> QVBoxLayout:
        self._url_label = QLabel(self.tr('URL:'))
        self._url_input = QLineEdit(self)
        self._url_input.setPlaceholderText(self.tr('Enter URL here...'))

        self._url_layout = QVBoxLayout()
        self._url_layout.addWidget(self._url_label)
        self._url_layout.addWidget(self._url_input)
        return self._url_layout

    def check_button_ui(self) -> QPushButton:
        self._check_button = QPushButton(self.tr('Check'))
        self._check_button.clicked.connect(self.check_url)
        return self._check_button

    def format_ui(self) -> QVBoxLayout:
        self._format_label = QLabel(self.tr('Format:'))
        self._format_display = QLineEdit(self)
        self._format_display.setReadOnly(True)
        self._format_display.setPlaceholderText(self.tr('Detected format will appear here...'))

        self._format_layout = QVBoxLayout()
        self._format_layout.addWidget(self._format_label)
        self._format_layout.addWidget(self._format_display)
        return self._format_layout

    def ok_button_ui(self) -> QPushButton:
        self._ok_button = QPushButton(self.tr('OK'))
        self._ok_button.clicked.connect(self.ok)
        return self._ok_button

    def cancel_button_ui(self) -> QPushButton:
        self._cancel_button = QPushButton(self.tr('Cancel'))
        self._cancel_button.clicked.connect(self.close)
        return self._cancel_button

    def btn_layout(self) -> QHBoxLayout:
        self._btn_layout = QHBoxLayout()
        self._btn_layout.addWidget(self.cancel_button_ui())
        self._btn_layout.addWidget(self.ok_button_ui())
        return self._btn_layout

    ##############################
    #         CONTROLLER         #
    ##############################

    def check_url(self):
        url = self._url_input.text()
        self._is_image = False
        self._is_video = False
        self._is_live = False
        if is_live_video(url):
            self._format_display.setText(self.tr('Live Video Pipeline (Live)'))
            self._ok_button.setDisabled(False)
            self._is_live = True
        elif is_image(url):
            self._format_display.setText(self.tr('Image'))
            self._ok_button.setDisabled(False)
            self._is_image = True
        elif is_video(url):
            self._format_display.setText(self.tr('Video'))
            self._ok_button.setDisabled(False)
            self._is_video = True
        else:
            self._format_display.setText(self.tr('Unknown Format'))
            self._ok_button.setDisabled(True)

    def ok(self):
        self._callback(self._url_input.text(), self._is_image, self._is_video, self._is_live)
        self.close()

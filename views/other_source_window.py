from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel
from models.app_state import AppState
from utils.url_handler import *


class OtherSourceWindow(QWidget):
    def __init__(self, callback: Callable[[str, bool, bool, bool], None]):
        super().__init__()
        self._appstate = AppState.get_instance()

        self._url_input = None
        self._format_display = None
        self._ok_btn = None

        self._is_image = False
        self._is_video = False
        self._is_live = False

        self._callback = callback

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self.setWindowTitle('QTQuickDetect Other Source')
        self.setGeometry(100, 100, 480, 240)
        self.setStyleSheet(self._appstate.qss)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addLayout(self.url_input_ui())
        main_layout.addWidget(self.check_button_ui())
        main_layout.addLayout(self.format_ui())
        main_layout.addStretch()
        main_layout.addLayout(self.btn_layout())

    def url_input_ui(self) -> QVBoxLayout:
        url_label = QLabel("URL:")
        url_input = QLineEdit(self)
        url_input.setPlaceholderText("Enter URL here...")
        self._url_input = url_input

        url_layout = QVBoxLayout()
        url_layout.addWidget(url_label)
        url_layout.addWidget(url_input)

        return url_layout

    def check_button_ui(self) -> QPushButton:
        check_button = QPushButton('Check')
        check_button.clicked.connect(self.check_url)

        return check_button

    def format_ui(self) -> QVBoxLayout:
        format_label = QLabel("Format:")
        format_display = QLineEdit(self)
        format_display.setReadOnly(True)
        format_display.setPlaceholderText("Detected format will appear here...")
        self._format_display = format_display

        format_layout = QVBoxLayout()
        format_layout.addWidget(format_label)
        format_layout.addWidget(format_display)

        return format_layout

    def ok_button_ui(self) -> QPushButton:
        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self.ok)
        self._ok_btn = ok_button
        return ok_button

    def cancel_button_ui(self) -> QPushButton:
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.close)
        return cancel_button

    def btn_layout(self) -> QHBoxLayout:
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.cancel_button_ui())
        btn_layout.addWidget(self.ok_button_ui())
        return btn_layout

    ##############################
    #         CONTROLLER         #
    ##############################

    def check_url(self):
        url = self._url_input.text()
        self._is_image = False
        self._is_video = False
        self._is_live = False
        if is_live_video(url):
            self._format_display.setText("Live Video Pipeline (Live)")
            self._ok_btn.setDisabled(False)
            self._is_live = True
        elif is_image(url):
            self._format_display.setText("Image")
            self._ok_btn.setDisabled(False)
            self._is_image = True
        elif is_video(url):
            self._format_display.setText("Video")
            self._ok_btn.setDisabled(False)
            self._is_video = True
        else:
            self._format_display.setText("Unknown Format")
            self._ok_btn.setDisabled(True)

    def ok(self):
        self._callback(self._url_input.text(), self._is_image, self._is_video, self._is_live)
        self.close()

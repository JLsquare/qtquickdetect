from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel
import requests


class OtherSourceView(QWidget):
    def __init__(self, callback):
        super().__init__()

        self._url_input = None
        self._format_display = None
        self._ok_btn = None

        self._is_image = False
        self._is_video = False
        self._is_live = False

        self._callback = callback

        self.initUI()

    ##############################
    #            VIEW            #
    ##############################

    def initUI(self):
        self.setWindowTitle('QTQuickDetect Other Source')
        self.setGeometry(100, 100, 480, 240)

        with open('ressources/qss/stylesheet.qss', 'r') as file:
            self.setStyleSheet(file.read())

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # URL input
        url_label = QLabel("URL:")
        url_input = QLineEdit(self)
        url_input.setPlaceholderText("Enter URL here...")
        self._url_input = url_input

        # Check button and format display
        check_btn = QPushButton("Check", self)
        check_btn.clicked.connect(self.check_url)
        format_label = QLabel("Format:")
        format_display = QLineEdit(self)
        format_display.setReadOnly(True)
        format_display.setPlaceholderText("Detected format will appear here...")
        self._format_display = format_display

        main_layout.addWidget(url_label)
        main_layout.addWidget(url_input)
        main_layout.addWidget(check_btn)
        main_layout.addWidget(format_label)
        main_layout.addWidget(format_display)

        # OK and Cancel buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.close)
        ok_btn = QPushButton("OK", self)
        ok_btn.clicked.connect(self.ok)
        ok_btn.setDisabled(True)
        self._ok_btn = ok_btn

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)

        main_layout.addStretch()
        main_layout.addLayout(btn_layout)

    ##############################
    #         CONTROLLER         #
    ##############################

    def check_url(self):
        url = self._url_input.text()
        self._is_image = False
        self._is_video = False
        self._is_live = False
        if self.is_live_video(url):
            self._format_display.setText("Live Video Pipeline (Live)")
            self._ok_btn.setDisabled(False)
            self._is_live = True
        elif self.is_image(url):
            self._format_display.setText("Image")
            self._ok_btn.setDisabled(False)
            self._is_image = True
        elif self.is_video(url):
            self._format_display.setText("Video")
            self._ok_btn.setDisabled(False)
            self._is_video = True
        else:
            self._format_display.setText("Unknown Format")
            self._ok_btn.setDisabled(True)

    def get_content_type(self, url):
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            return response.headers.get('Content-Type', '').split(';')[0].strip()
        except requests.RequestException:
            return None

    def is_live_video(self, url):
        content_type = self.get_content_type(url)
        live_content_types = ["application/vnd.apple.mpegurl", "application/dash+xml"]
        live_url_patterns = ["m3u8", ".ts", "live", "streaming"]
        if content_type and content_type in live_content_types:
            return True
        if any(pattern in url for pattern in live_url_patterns):
            return True
        return False

    def is_image(self, url):
        content_type = self.get_content_type(url)
        if not content_type:
            return False
        image_types = ["image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff"]
        return content_type in image_types

    def is_video(self, url):
        content_type = self.get_content_type(url)
        if not content_type:
            return False
        video_types = ["video/mp4", "video/avi", "video/mkv", "video/mpeg", "video/quicktime", "video/x-msvideo",
                       "video/webm"]
        return content_type in video_types

    def ok(self):
        self._callback(self._url_input.text(), self._is_image, self._is_video, self._is_live)
        self.close()


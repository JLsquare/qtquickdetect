from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QUrl


class VideoResultView(QWidget):
    def __init__(self, input_video, result_video):
        super().__init__()
        self._input_player = None
        self._result_player = None
        self._input_video = input_video
        self._result_video = result_video
        self.initUI()

    ##############################
    #            VIEW            #
    ##############################

    def initUI(self):
        # Tab input / result image
        tab = QTabWidget(self)
        tab.addTab(self.input_video_ui(), "Input")
        tab.addTab(self.result_video_ui(), "Result")
        tab.setCurrentIndex(1)

        # Middle layout
        middle_layout = QHBoxLayout()
        middle_layout.addStretch()
        middle_layout.addWidget(tab)

        # Bottom layout
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.save_json_button_ui())
        bottom_layout.addWidget(self.save_image_button_ui())

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def input_video_ui(self):
        self._input_player = QMediaPlayer()
        self._input_player.setSource(QUrl.fromLocalFile(self._input_video))
        video_widget = QVideoWidget()
        self._input_player.setVideoOutput(video_widget)
        self._input_player.play()
        self._input_player.mediaStatusChanged.connect(self.input_auto_replay)
        return video_widget

    def result_video_ui(self):
        self._result_player = QMediaPlayer()
        self._result_player.setSource(QUrl.fromLocalFile(self._result_video))
        video_widget = QVideoWidget()
        self._result_player.setVideoOutput(video_widget)
        self._result_player.play()
        self._result_player.mediaStatusChanged.connect(self.result_auto_replay)
        return video_widget

    def input_auto_replay(self, value):
        if value == QMediaPlayer.MediaStatus.EndOfMedia:
            self._input_player.setPosition(0)
            self._input_player.play()

    def result_auto_replay(self, value):
        if value == QMediaPlayer.MediaStatus.EndOfMedia:
            self._result_player.setPosition(0)
            self._result_player.play()

    def save_json_button_ui(self):
        save_json_button = QPushButton('Save JSON')
        return save_json_button

    def save_image_button_ui(self):
        save_image_button = QPushButton('Save Image')
        return save_image_button

from typing import Optional
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSlider, QPushButton, QStyle, QHBoxLayout
import numpy as np
import cv2


class VideoPlayerWidget(QWidget):
    def __init__(self, video_path: str):
        super().__init__()

        # PyQT6 Components
        self._main_layout: Optional[QVBoxLayout] = None
        self._video_widget: Optional[QVideoWidget] = None
        self._player: Optional[QMediaPlayer] = None
        self._play_button: Optional[QPushButton] = None
        self._position_slider: Optional[QSlider] = None
        self._control_layout: Optional[QHBoxLayout] = None

        self._video_path = video_path
        self._status = "Playing"
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.addWidget(self.video_ui())
        self._main_layout.addLayout(self.control_ui())
        self.setLayout(self._main_layout)

    def video_ui(self) -> QVideoWidget:
        self._video_widget = QVideoWidget()

        self._player = QMediaPlayer()
        self._player.setSource(QUrl.fromLocalFile(self._video_path))
        self._player.setVideoOutput(self._video_widget)
        self._player.play()
        self._player.mediaStatusChanged.connect(self.auto_replay)

        return self._video_widget

    def control_ui(self) -> QHBoxLayout:
        self._play_button = QPushButton()
        self._play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self._play_button.clicked.connect(self.play_pause)

        self._position_slider = QSlider(Qt.Orientation.Horizontal)
        self._position_slider.setRange(0, self._player.duration())
        self._position_slider.sliderMoved.connect(self.change_position)
        self._player.positionChanged.connect(self.update_position_slider)

        self._control_layout = QHBoxLayout()
        self._control_layout.setContentsMargins(0, 0, 0, 0)
        self._control_layout.addWidget(self._play_button)
        self._control_layout.addWidget(self._position_slider)
        return self._control_layout

    ##############################
    #         CONTROLLER         #
    ##############################

    def auto_replay(self, status: QMediaPlayer.MediaStatus):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._player.setPosition(0)
            self._player.play()

    def play_pause(self):
        if self._status == "Playing":
            self.pause()
        else:
            self.play()

    def pause(self):
        self._player.pause()
        self._status = "Paused"
        self._play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def play(self):
        self._player.play()
        self._status = "Playing"
        self._play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def change_position(self, position: int):
        self._player.setPosition(position)
        self.pause()

    def update_position_slider(self):
        self._position_slider.setValue(self._player.position())

    def get_current_frame(self) -> np.ndarray | None:
        cap = cv2.VideoCapture(self._video_path)

        if not cap.isOpened():
            return None

        current_time_msec = self._player.position()
        cap.set(cv2.CAP_PROP_POS_MSEC, current_time_msec)

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return None

        return frame

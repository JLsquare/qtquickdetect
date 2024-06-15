import numpy as np
import cv2

from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSlider, QPushButton, QStyle, QHBoxLayout


class VideoPlayerWidget(QWidget):
    """
    VideoPlayerWidget is a QWidget that plays a video file.
    """
    def __init__(self, video_path: Path):
        """
        Initializes the VideoPlayerWidget.

        :param video_path: The path to the video file.
        """
        super().__init__()

        # PyQT6 Components
        self._main_layout: Optional[QVBoxLayout] = None
        self._video_widget: Optional[QVideoWidget] = None
        self._player: Optional[QMediaPlayer] = None
        self._play_button: Optional[QPushButton] = None
        self._position_slider: Optional[QSlider] = None
        self._control_layout: Optional[QHBoxLayout] = None

        self._video_path: Path = video_path
        self._status: str = "Playing"
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self) -> None:
        """
        Initializes the user interface components.
        """
        self._main_layout = QVBoxLayout(self)
        self._main_layout.addWidget(self.video_ui())
        self._main_layout.addLayout(self.control_ui())
        self.setLayout(self._main_layout)
        self._player.durationChanged.connect(self.update_duration)

    def video_ui(self) -> QVideoWidget:
        """
        Initializes the video user interface components.

        :return: The video widget.
        """
        self._video_widget = QVideoWidget()

        self._player = QMediaPlayer()
        self._player.setSource(QUrl.fromLocalFile(str(self._video_path)))
        self._player.setVideoOutput(self._video_widget)
        self._player.play()
        self._player.mediaStatusChanged.connect(self.auto_replay)

        return self._video_widget

    def control_ui(self) -> QHBoxLayout:
        """
        Initializes the control user interface components.

        :return: The control layout.
        """
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

    def update_duration(self, duration: int) -> None:
        """
        Updates the duration of the video.

        :param duration: The duration of the video.
        """
        self._position_slider.setRange(0, duration)

    def auto_replay(self, status: QMediaPlayer.MediaStatus) -> None:
        """
        Automatically replays the video when it reaches the end.

        :param status: The media status.
        """
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._player.setPosition(0)
            self._player.play()

    def play_pause(self) -> None:
        """
        Plays or pauses the video.
        """
        if self._status == "Playing":
            self.pause()
        else:
            self.play()

    def pause(self) -> None:
        """
        Pauses the video.
        """
        self._player.pause()
        self._status = "Paused"
        self._play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def play(self) -> None:
        """
        Plays the video.
        """
        self._player.play()
        self._status = "Playing"
        self._play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def change_position(self, position: int) -> None:
        """
        Changes the position of the video.

        :param position: The position to change to.
        """
        self._player.setPosition(position)
        self.pause()

    def update_position_slider(self, position: int) -> None:
        """
        Updates the position of the slider.

        :param position: The position of the slider.
        """
        self._position_slider.setValue(position)

    def get_current_frame(self) -> np.ndarray | None:
        """
        Gets the current frame of the video.

        :return: The current frame of the video.
        """
        cap = cv2.VideoCapture(str(self._video_path))

        if not cap.isOpened():
            return None

        current_time_msec = self._player.position()
        cap.set(cv2.CAP_PROP_POS_MSEC, current_time_msec)

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return None

        return frame

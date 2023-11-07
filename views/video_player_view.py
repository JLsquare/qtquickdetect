from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSlider, QPushButton, QStyle, QHBoxLayout


class VideoPlayerView(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self._position_slider = None
        self._play_button = None
        self._player = QMediaPlayer()
        self._player.setSource(QUrl.fromLocalFile(video_path))
        self._status = "Playing"
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.video_ui())
        main_layout.addLayout(self.control_ui())
        self.setLayout(main_layout)

    def video_ui(self):
        video_widget = QVideoWidget()
        self._player.setVideoOutput(video_widget)
        self._player.play()
        self._player.mediaStatusChanged.connect(self.auto_replay)

        return video_widget

    def control_ui(self):
        play_button = QPushButton()
        play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        play_button.clicked.connect(self.play_pause)
        self._play_button = play_button

        position_slider = QSlider(Qt.Orientation.Horizontal)
        position_slider.setRange(0, self._player.duration())
        position_slider.sliderMoved.connect(self.change_position)
        self._position_slider = position_slider
        self._player.positionChanged.connect(self.update_position_slider)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(play_button)
        control_layout.addWidget(position_slider)

        return control_layout

    def auto_replay(self, status):
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

    def change_position(self, position):
        self._player.setPosition(position)
        self.pause()

    def update_position_slider(self):
        self._position_slider.setValue(self._player.position())
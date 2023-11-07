from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QPushButton
from views.video_player_view import VideoPlayerView


class VideoResultView(QWidget):
    def __init__(self, input_video, result_video):
        super().__init__()
        self._input_video = input_video
        self._result_video = result_video
        self.initUI()

    ##############################
    #            VIEW            #
    ##############################

    def initUI(self):
        # Tab input / result image
        tab = QTabWidget(self)
        tab.addTab(VideoPlayerView(self._input_video), "Input")
        tab.addTab(VideoPlayerView(self._result_video), "Result")
        tab.setCurrentIndex(1)

        # Middle layout
        middle_layout = QHBoxLayout()
        middle_layout.addStretch(1)
        middle_layout.addWidget(tab, 1)

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

    def save_json_button_ui(self):
        save_json_button = QPushButton('Save JSON')
        return save_json_button

    def save_image_button_ui(self):
        save_image_button = QPushButton('Save Image')
        return save_image_button

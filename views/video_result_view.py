from PyQt6.QtCore import QFile
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QPushButton, QFileDialog, QMessageBox
from views.video_player_view import VideoPlayerView
import logging


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
        bottom_layout.addWidget(self.save_video_button_ui())

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def save_json_button_ui(self):
        save_json_button = QPushButton('Save JSON')
        return save_json_button

    def save_video_button_ui(self):
        save_video_button = QPushButton('Save Video')
        save_video_button.clicked.connect(self.save_video)
        return save_video_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def save_video(self):
        if self._result_video.lower().endswith('.avi'):
            format_filter = 'AVI (*.avi)'
        else:
            format_filter = 'MP4 (*.mp4)'
        file_name, selected_filter = QFileDialog.getSaveFileName(self, "Save Video", "", format_filter)
        if file_name:
            if selected_filter == 'AVI (*.avi)' and not file_name.lower().endswith('.avi'):
                file_name += ".avi"
            if selected_filter == 'MP4 (*.mp4)' and not file_name.lower().endswith('.mp4'):
                file_name += ".mp4"
            if QFile.copy(self._result_video, file_name):
                QMessageBox.information(self, "Success", "Video saved successfully!")
                logging.debug(f'Saved video to {file_name}')
            else:
                QMessageBox.critical(self, "Error", "An error occurred while saving the video.")
                logging.error(f'Could not save video to {file_name}')

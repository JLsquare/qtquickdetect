import os

from PyQt6.QtCore import QFile, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from views.video_player_widget import VideoPlayerWidget


class VideoResultWidget(QWidget):
    def __init__(self):
        super().__init__()

        self._middle_layout = None
        self._file_select_combo = None
        self._input_videos = []
        self._result_videos = []
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Middle layout
        middle_layout = QHBoxLayout()
        middle_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        middle_layout.addLayout(self.left_ui(), 1)
        self._middle_layout = middle_layout

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

    def left_ui(self) -> QVBoxLayout:
        file_select_label = QLabel('Select file:')
        file_select = QComboBox()
        file_select.currentIndexChanged.connect(self.open_current_file)
        self._file_select_combo = file_select

        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_layout.addWidget(file_select_label)
        left_layout.addWidget(file_select)

        return left_layout

    def input_video_ui(self, input_video: str) -> VideoPlayerWidget:
        video_player_widget = VideoPlayerWidget(input_video)
        return video_player_widget

    def result_video_ui(self, result_video: str) -> VideoPlayerWidget:
        video_player_widget = VideoPlayerWidget(result_video)
        return video_player_widget

    def save_json_button_ui(self) -> QPushButton:
        save_json_button = QPushButton('Save JSON')
        save_json_button.clicked.connect(self.save_json)
        return save_json_button

    def save_video_button_ui(self) -> QPushButton:
        save_video_button = QPushButton('Save Video')
        save_video_button.clicked.connect(self.save_video)
        return save_video_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def save_json(self):
        pass

    def save_video(self):
        pass

    # def save_video(self):
    #    if self._result_video.lower().endswith('.avi'):
    #        format_filter = 'AVI (*.avi)'
    #    else:
    #        format_filter = 'MP4 (*.mp4)'
    #    file_name, selected_filter = QFileDialog.getSaveFileName(self, "Save Video", "", format_filter)
    #    if file_name:
    #        if selected_filter == 'AVI (*.avi)' and not file_name.lower().endswith('.avi'):
    #            file_name += ".avi"
    #        if selected_filter == 'MP4 (*.mp4)' and not file_name.lower().endswith('.mp4'):
    #            file_name += ".mp4"
    #        if QFile.copy(self._result_video, file_name):
    #            QMessageBox.information(self, "Success", "Video saved successfully!")
    #            logging.debug(f'Saved video to {file_name}')
    #        else:
    #            QMessageBox.critical(self, "Error", "An error occurred while saving the video.")
    #            logging.error(f'Could not save video to {file_name}')

    def add_input_and_result(self, input_video: str, result_video: str):
        self._input_videos.append(input_video)
        self._result_videos.append(result_video)
        self._file_select_combo.addItem(os.path.basename(input_video))

    def open_current_file(self):
        tab = QTabWidget()
        input_video = self._input_videos[self._file_select_combo.currentIndex()]
        result_video = self._result_videos[self._file_select_combo.currentIndex()]
        tab.addTab(self.input_video_ui(input_video), 'Input')
        tab.addTab(self.result_video_ui(result_video), 'Result')
        tab.setCurrentIndex(1)
        if self._middle_layout.count() > 1:
            self._middle_layout.itemAt(1).widget().deleteLater()
        self._middle_layout.addWidget(tab, 1)
import os
import json
import cv2 as cv

from pathlib import Path
from typing import Optional
from PyQt6.QtCore import Qt, QFile, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QMessageBox, \
    QFileDialog, QSplitter
from ..utils.file_explorer import open_file_explorer
from ..views.video_player_widget import VideoPlayerWidget


class VideoResultWidget(QWidget):
    return_signal = pyqtSignal()

    def __init__(self, result_path: Path):
        super().__init__()

        # PyQT6 Components
        self._middle_layout: Optional[QSplitter] = None
        self._bottom_layout: Optional[QHBoxLayout] = None
        self._main_layout: Optional[QVBoxLayout] = None
        self._file_select_label: Optional[QLabel] = None
        self._file_select_combo: Optional[QComboBox] = None
        self._model_select_label: Optional[QLabel] = None
        self._model_select_combo: Optional[QComboBox] = None
        self._left_layout: Optional[QVBoxLayout] = None
        self._left_widget: Optional[QWidget] = None
        self._video_player: Optional[VideoPlayerWidget] = None
        self._video_layout: Optional[QVBoxLayout] = None
        self._video_container: Optional[QWidget] = None
        self._return_button: Optional[QPushButton] = None
        self._open_result_folder_button: Optional[QPushButton] = None
        self._save_json_button: Optional[QPushButton] = None
        self._save_video_button: Optional[QPushButton] = None
        self._save_frame_button: Optional[QPushButton] = None

        self._result_path = result_path
        self._input_videos = []
        self._result_videos = {}
        self._result_jsons = {}

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Middle layout
        self._middle_layout = QSplitter(Qt.Orientation.Horizontal)
        self._middle_layout.addWidget(self.left_ui())
        self._middle_layout.addWidget(self.video_ui(''))
        self._middle_layout.setSizes([self.width() // 2, self.width() // 2])

        # Bottom layout
        self._bottom_layout = QHBoxLayout()
        self._bottom_layout.addWidget(self.return_button_ui())
        self._bottom_layout.addStretch(1)
        self._bottom_layout.addWidget(self.open_result_folder_button_ui())
        self._bottom_layout.addWidget(self.save_json_button_ui())
        self._bottom_layout.addWidget(self.save_video_button_ui())
        self._bottom_layout.addWidget(self.save_frame_button_ui())

        # Main layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.addWidget(self._middle_layout)
        self._main_layout.addLayout(self._bottom_layout)
        self.setLayout(self._main_layout)

    def left_ui(self) -> QWidget:
        self._file_select_label = QLabel(self.tr('Select file:'))
        self._file_select_combo = QComboBox()
        self._file_select_combo.currentIndexChanged.connect(self.change_current_file)

        self._model_select_label = QLabel(self.tr('Select model:'))
        self._model_select_combo = QComboBox()
        self._model_select_combo.currentIndexChanged.connect(self.change_current_model)

        self._left_layout = QVBoxLayout()
        self._left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._left_layout.addWidget(self._file_select_label)
        self._left_layout.addWidget(self._file_select_combo)
        self._left_layout.addWidget(self._model_select_label)
        self._left_layout.addWidget(self._model_select_combo)

        self._left_widget = QWidget()
        self._left_widget.setLayout(self._left_layout)
        return self._left_widget

    def video_ui(self, video_path: Path) -> QWidget:
        self._video_player = VideoPlayerWidget(video_path)

        self._video_layout = QVBoxLayout()
        self._video_layout.addWidget(self._video_player)

        self._video_container = QWidget()
        self._video_container.setLayout(self._video_layout)
        self._video_container.setProperty('class', 'border')

        return self._video_container

    def return_button_ui(self) -> QPushButton:
        self._return_button = QPushButton(self.tr('Return'))
        self._return_button.clicked.connect(self.return_signal.emit)
        return self._return_button

    def open_result_folder_button_ui(self) -> QPushButton:
        self._open_result_folder_button = QPushButton(self.tr('Open Result Folder'))
        self._open_result_folder_button.clicked.connect(self.open_result_folder)
        return self._open_result_folder_button

    def save_json_button_ui(self) -> QPushButton:
        self._save_json_button = QPushButton(self.tr('Save JSON'))
        self._save_json_button.clicked.connect(self.save_json)
        return self._save_json_button

    def save_video_button_ui(self) -> QPushButton:
        self._save_video_button = QPushButton(self.tr('Save Video'))
        self._save_video_button.clicked.connect(self.save_video)
        return self._save_video_button

    def save_frame_button_ui(self) -> QPushButton:
        self._save_frame_button = QPushButton(self.tr('Save Frame'))
        self._save_frame_button.clicked.connect(self.save_frame)
        return self._save_frame_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def open_result_folder(self):
        try:
            open_file_explorer(self._result_path)
        except Exception as e:
            QMessageBox.critical(self, self.tr('Error'), str(e))

    def save_json(self):
        result_json = self._model_select_combo.currentData()

        if result_json is None:
            QMessageBox.critical(self, self.tr('Error'), self.tr('No model selected.'))
            return

        # Save the json
        file_name, selected_filter = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON (*.json)")
        if file_name:
            if not file_name.lower().endswith('.json'):
                file_name += ".json"
            if QFile.copy(result_json, file_name):
                QMessageBox.information(self, self.tr('Success'), self.tr('JSON saved successfully!'))
            else:
                QMessageBox.critical(self, self.tr('Error'), self.tr('An error occurred while saving the JSON.'))

    def save_video(self):
        input_video = self._input_videos[self._file_select_combo.currentIndex()]
        result_video = self._result_videos[input_video][self._model_select_combo.currentIndex() - 1]

        if result_video is None:
            QMessageBox.critical(self, self.tr('Error'), self.tr('No video selected.'))
            return

        # Save the video
        format_filter = "MP4 (*.mp4)"
        file_name, _ = QFileDialog.getSaveFileName(self, self.tr('Save Video'), '', format_filter)
        if file_name:
            if not file_name.lower().endswith('.mp4') and format_filter == 'Video (*.mp4)':
                file_name += ".mp4"
            elif not file_name.lower().endswith('.avi') and format_filter == 'Video (*.avi)':
                file_name += ".avi"
            if QFile.copy(result_video, file_name):
                QMessageBox.information(self, self.tr('Success'), self.tr('Video saved successfully!'))
            else:
                QMessageBox.critical(self, self.tr('Error'), self.tr('An error occurred while saving the video.'))

    def save_frame(self):
        if self._video_player is None:
            QMessageBox.critical(self, self.tr('Error'), self.tr('No video selected.'))
            return

        frame = self._video_player.get_current_frame()

        if frame is None:
            QMessageBox.critical(self, self.tr('Error'), self.tr('No frame found.'))
            return

        # Save the frame
        format_filter = 'PNG (*.png)'
        file_name, _ = QFileDialog.getSaveFileName(self, self.tr('Save Frame'), '', format_filter)
        if file_name:
            if not file_name.lower().endswith('.png') and format_filter == 'PNG (*.png)':
                file_name += '.png'
            elif not file_name.lower().endswith('.jpg') and format_filter == 'JPG (*.jpg)':
                file_name += '.jpg'
            if cv.imwrite(file_name, frame):
                QMessageBox.information(self, self.tr('Success'), self.tr('Frame saved successfully!'))
            else:
                QMessageBox.critical(self, self.tr('Error'), self.tr('An error occurred while saving the frame.'))

    def change_current_file(self):
        index = self._file_select_combo.currentIndex()

        # Update the video
        input_video = self._input_videos[index]
        self.change_current_video(input_video)

        # Update the model selection
        self._model_select_combo.clear()
        self._model_select_combo.addItem('Input')
        for index, result_video in enumerate(self._result_videos[input_video]):
            with open(self._result_jsons[input_video][index], 'r') as f:
                data = json.load(f)
            self._model_select_combo.addItem(data['weight'], self._result_jsons[input_video][index])

    def change_current_model(self):
        index = self._model_select_combo.currentIndex()

        if index < 0:
            return

        input_video = self._input_videos[self._file_select_combo.currentIndex()]

        if index == 0:
            self.change_current_video(input_video)
            return

        # Update the video
        result_video = self._result_videos[input_video][index - 1]
        self.change_current_video(result_video)

    def change_current_video(self, video_path: Path):
        # Update the video
        video_widget = self.video_ui(video_path)
        self._middle_layout.replaceWidget(1, video_widget)

    def add_input_and_result(self, input_video: Path, result_video: Path, result_json: Path):
        # Add the input if it's not already here
        if input_video not in self._input_videos:
            self._input_videos.append(input_video)
            self._result_videos[input_video] = []
            self._result_jsons[input_video] = []
            self._file_select_combo.addItem(input_video.name, input_video)

        # Add the result to the list of results of the input
        self._result_videos[input_video].append(result_video)
        self._result_jsons[input_video].append(result_json)

        # Update the UI if the current file is the input
        if self._file_select_combo.currentIndex() == len(self._input_videos) - 1:
            self.change_current_file()

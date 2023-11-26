from PyQt6.QtCore import Qt, QFile
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QMessageBox, QFileDialog
from models.project import Project
from utils.file_explorer import open_file_explorer
from views.video_player_widget import VideoPlayerWidget
import os
import json
import cv2 as cv


class VideoResultWidget(QWidget):
    def __init__(self, project: Project, result_path: str):
        super().__init__()
        self._project = project
        self._result_path = result_path

        self._current_result_player = None
        self._middle_layout = None
        self._file_select_combo = None
        self._model_select_combo = None

        self._input_videos = []
        self._result_videos = {}
        self._result_jsons = {}

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
        bottom_layout.addWidget(self.open_result_folder_button_ui())
        bottom_layout.addWidget(self.save_json_button_ui())
        bottom_layout.addWidget(self.save_video_button_ui())
        bottom_layout.addWidget(self.save_frame_button_ui())

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def left_ui(self) -> QVBoxLayout:
        file_select_label = QLabel('Select file:')
        file_select = QComboBox()
        file_select.currentIndexChanged.connect(self.change_current_file)
        self._file_select_combo = file_select

        model_select_label = QLabel('Select model:')
        model_select = QComboBox()
        model_select.currentIndexChanged.connect(self.change_current_model)
        self._model_select_combo = model_select

        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_layout.addWidget(file_select_label)
        left_layout.addWidget(file_select)
        left_layout.addWidget(model_select_label)
        left_layout.addWidget(model_select)

        return left_layout

    def video_ui(self, video_path: str) -> QWidget:
        video_player = VideoPlayerWidget(video_path)
        self._current_result_player = video_player

        video_container = QWidget()
        video_layout = QVBoxLayout()
        video_layout.addWidget(video_player)
        video_container.setLayout(video_layout)
        video_container.setProperty('class', 'border')

        return video_container

    def open_result_folder_button_ui(self) -> QPushButton:
        open_result_folder_button = QPushButton('Open Result Folder')
        open_result_folder_button.clicked.connect(self.open_result_folder)
        return open_result_folder_button

    def save_json_button_ui(self) -> QPushButton:
        save_json_button = QPushButton('Save JSON')
        save_json_button.clicked.connect(self.save_json)
        return save_json_button

    def save_video_button_ui(self) -> QPushButton:
        save_video_button = QPushButton('Save Video')
        save_video_button.clicked.connect(self.save_video)
        return save_video_button

    def save_frame_button_ui(self) -> QPushButton:
        save_frame_button = QPushButton('Save Frame')
        save_frame_button.clicked.connect(self.save_frame)
        return save_frame_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def open_result_folder(self):
        try:
            open_file_explorer(self._result_path)
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def save_json(self):
        result_json = self._model_select_combo.currentData()

        if result_json is None:
            QMessageBox.critical(self, 'Error', 'No model selected.')
            return

        # Save the json
        file_name, selected_filter = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON (*.json)")
        if file_name:
            if not file_name.lower().endswith('.json'):
                file_name += ".json"
            if QFile.copy(result_json, file_name):
                QMessageBox.information(self, "Success", "JSON saved successfully!")
            else:
                QMessageBox.critical(self, "Error", "An error occurred while saving the JSON.")

    def save_video(self):
        input_video = self._input_videos[self._file_select_combo.currentIndex()]
        result_video = self._result_videos[input_video][self._model_select_combo.currentIndex() - 1]

        if result_video is None:
            QMessageBox.critical(self, 'Error', 'No video selected.')
            return

        # Save the video
        if self._project.config.video_format == 'mp4':
            format_filter = "MP4 (*.mp4)"
        else:
            format_filter = "AVI (*.avi)"
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Video", "", format_filter)
        if file_name:
            if not file_name.lower().endswith('.mp4') and format_filter == "Video (*.mp4)":
                file_name += ".mp4"
            elif not file_name.lower().endswith('.avi') and format_filter == "Video (*.avi)":
                file_name += ".avi"
            if QFile.copy(result_video, file_name):
                QMessageBox.information(self, "Success", "Video saved successfully!")
            else:
                QMessageBox.critical(self, "Error", "An error occurred while saving the video.")

    def save_frame(self):
        if self._current_result_player is None:
            QMessageBox.critical(self, 'Error', 'No video selected.')
            return

        frame = self._current_result_player.get_current_frame()

        if frame is None:
            QMessageBox.critical(self, 'Error', 'No frame found.')
            return

        # Save the frame
        if self._project.config.image_format == 'png':
            format_filter = "PNG (*.png)"
        else:
            format_filter = "JPG (*.jpg)"
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Frame", "", format_filter)
        if file_name:
            if not file_name.lower().endswith('.png') and format_filter == "PNG (*.png)":
                file_name += ".png"
            elif not file_name.lower().endswith('.jpg') and format_filter == "JPG (*.jpg)":
                file_name += ".jpg"
            if cv.imwrite(file_name, frame):
                QMessageBox.information(self, "Success", "Frame saved successfully!")
            else:
                QMessageBox.critical(self, "Error", "An error occurred while saving the frame.")

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
            self._model_select_combo.addItem(data['model_name'], self._result_jsons[input_video][index])

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

    def change_current_video(self, video_path: str):
        # Create the video player widget
        video_widget = self.video_ui(video_path)

        # Clear the middle layout before adding a new widget
        while self._middle_layout.count() > 1:
            widget_to_remove = self._middle_layout.itemAt(1).widget()
            self._middle_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

        # Add the new video player widget
        self._middle_layout.addWidget(video_widget, 1)

    def add_input_and_result(self, input_video: str, result_video: str, result_json: str):
        # Add the input if it's not already here
        if input_video not in self._input_videos:
            self._input_videos.append(input_video)
            self._result_videos[input_video] = []
            self._result_jsons[input_video] = []
            self._file_select_combo.addItem(os.path.basename(input_video), input_video)

        # Add the result to the list of results of the input
        self._result_videos[input_video].append(result_video)
        self._result_jsons[input_video].append(result_json)

        # Update the UI if the current file is the input
        if self._file_select_combo.currentIndex() == len(self._input_videos) - 1:
            self.change_current_file()

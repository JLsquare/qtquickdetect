import logging
from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QListWidget, QMessageBox
from models.app_state import AppState
from models.project import Project
import os

from views.image_result_widget import ImageResultWidget
from views.video_result_widget import VideoResultWidget


class HistoryResultWindow(QWidget):
    def __init__(self, add_new_tab: Callable[[QWidget, str, bool], None], project: Project):
        super().__init__()
        self._appstate = AppState.get_instance()
        self._project = project
        self._add_new_tab = add_new_tab
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self.setWindowTitle('QTQuickDetect History Result')
        self.setGeometry(100, 100, 480, 480)
        self.setStyleSheet(self._appstate.qss)

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        main_layout.addLayout(self.open_history_ui(), 0, 0)
        main_layout.addWidget(self.cancel_button_ui(), 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)

    def open_history_ui(self) -> QVBoxLayout:
        open_project_layout = QVBoxLayout()
        project_list_label = QLabel('Open History:')
        project_list = QListWidget()
        project_list.addItems(self.get_history())
        project_list.itemDoubleClicked.connect(self.open_history)

        open_project_layout.addWidget(project_list_label)
        open_project_layout.addWidget(project_list)

        return open_project_layout

    def cancel_button_ui(self) -> QPushButton:
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.cancel)

        return cancel_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def cancel(self):
        self.close()

    def get_history(self) -> list[str]:
        history = []
        for result in os.listdir(f'projects/{self._project.project_name}/result'):
            history.append(result)
        return history

    def open_history(self, item):
        media_type, task, date, time = item.text().split('_')
        project_name = self._project.project_name
        base_result_path = f'projects/{project_name}/result/{item.text()}'

        input_folder = 'images' if media_type == 'image' else 'videos'
        input_path = f'projects/{project_name}/input/{input_folder}'
        widget_class = ImageResultWidget if media_type == 'image' else VideoResultWidget

        for model_name in os.listdir(base_result_path):
            model_result_path = f'{base_result_path}/{model_name}'
            result_widget = widget_class(self._project, model_result_path)

            for file in os.listdir(input_path):
                if self._is_valid_file(file, media_type):
                    file_name, extension = file.rsplit('.', 1)
                    file_path = f'{input_path}/{file}'
                    json_path = f'{model_result_path}/{file_name}.json'
                    logging.info(f'Checking {json_path}')

                    if self._file_exists(json_path, file_path, media_type):
                        if media_type == 'image':
                            result_widget.add_input_and_result(file_path, json_path)
                        else:
                            result_video_path = f'{model_result_path}/{file}'
                            result_widget.add_input_and_result(file_path, result_video_path, json_path)

            tab_title = f'{media_type.capitalize()} Result - {model_name}'
            self._add_new_tab(result_widget, tab_title, True)

        self.close()

    def _is_valid_file(self, file, media_type):
        if media_type == 'image':
            return file.endswith('.png') or file.endswith('.jpg')
        return file.endswith('.mp4') or file.endswith('.avi')

    def _file_exists(self, json_path, file_path, media_type):
        if media_type == 'image':
            return os.path.exists(json_path)
        return os.path.exists(json_path) and os.path.exists(file_path)
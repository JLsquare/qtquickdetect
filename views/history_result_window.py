import logging
from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QListWidget, QMessageBox
from models.app_state import AppState
from models.project import Project
import os

from views.image_result_widget import ImageResultWidget


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

        main_layout.addWidget(self.cancel_button_ui(), 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(self.open_history_ui(), 2, 0, 1, 2)

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
        # projets/project_name/result/mediatype_task_date
        for result in os.listdir(f'projects/{self._project.project_name}/result'):
            history.append(result)
        return history

    def open_history(self, item):
        media_type, task, date, time = item.text().split('_')
        project_name = self._project.project_name
        result_path = f'projects/{project_name}/result/{item.text()}'
        input_path = f'projects/{project_name}/input/'

        if media_type == 'image':
            image_result_widget = ImageResultWidget(self._project, result_path)
            for image in os.listdir(input_path):
                if image.endswith('.png') or image.endswith('.jpg'):
                    image_path = f'{input_path}/{image}'
                    json_filename = f'{image.split(".")[0]}.json'
                    json_path = f'{result_path}/{json_filename}'
                    logging.info(f'Checking {json_path}')

                    if os.path.exists(json_path):
                        image_result_widget.add_input_and_result(image_path, json_path)

            self._add_new_tab(image_result_widget, f'{media_type.capitalize()} Result', True)

        self.close()

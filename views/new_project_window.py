import os
from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QGridLayout

from views.project_widget import ProjectWidget


class NewProjectWindow(QWidget):
    def __init__(self, add_new_tab: Callable[[QWidget, str, bool], None]):
        super().__init__()
        self._project_name_error = None
        self._project_name_input = None
        self._add_new_tab = add_new_tab
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self.setWindowTitle('QTQuickDetect New Project')
        self.setGeometry(100, 100, 480, 240)

        with open('ressources/qss/stylesheet.qss', 'r') as file:
            self.setStyleSheet(file.read())

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        main_layout.addLayout(self.project_name_ui(), 0, 0, 2, 1)
        main_layout.addWidget(self.cancel_button_ui(), 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.create_button_ui(), 2, 0, alignment=Qt.AlignmentFlag.AlignRight)

    def project_name_ui(self) -> QVBoxLayout:
        project_name_label = QLabel('Project name:')
        project_name_input = QLineEdit()
        project_name_input.setPlaceholderText('MyProject')
        project_name_input.textChanged.connect(self.clear_error)
        self._project_name_input = project_name_input
        project_name_error = QLabel('Project already exists')
        project_name_error.setStyleSheet('color: red')
        project_name_error.hide()
        self._project_name_error = project_name_error

        project_name_layout = QVBoxLayout()
        project_name_layout.addWidget(project_name_label)
        project_name_layout.addWidget(project_name_input)
        project_name_layout.addWidget(project_name_error)
        project_name_layout.addStretch()

        return project_name_layout

    def cancel_button_ui(self) -> QPushButton:
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.cancel)

        return cancel_button

    def create_button_ui(self) -> QPushButton:
        save_button = QPushButton('Create')
        save_button.clicked.connect(self.create_project)

        return save_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def clear_error(self):
        self._project_name_error.hide()

    def create_project(self):
        project_name = self._project_name_input.text()
        if os.path.exists(f'projects/{project_name}'):
            self._project_name_error.show()
            return
        os.mkdir(f'projects/{project_name}')
        os.mkdir(f'projects/{project_name}/input')
        os.mkdir(f'projects/{project_name}/result')
        new_tab = ProjectWidget(self._add_new_tab, project_name)
        self._add_new_tab(new_tab, project_name, True)
        self.close()

    def cancel(self):
        self.close()

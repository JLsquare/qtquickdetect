from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QListWidget, QMessageBox
from models.app_state import AppState
from models.project import Project
from views.project_widget import ProjectWidget
import os


class NewProjectWindow(QWidget):
    def __init__(self, add_new_tab: Callable[[QWidget, str, bool], None]):
        super().__init__()
        self._appstate = AppState.get_instance()
        self._project_name_input = None
        self._add_new_tab = add_new_tab
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self.setWindowTitle(self.tr('QTQuickDetect New/Open Project'))
        self.setGeometry(100, 100, 480, 320)
        self.setStyleSheet(self._appstate.qss)

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        main_layout.addLayout(self.project_name_ui(), 0, 0, 1, 2)
        main_layout.addWidget(self.cancel_button_ui(), 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.create_button_ui(), 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(self.open_project_ui(), 2, 0, 1, 2)

    def project_name_ui(self) -> QVBoxLayout:
        project_name_label = QLabel(self.tr('New Project name:'))
        project_name_input = QLineEdit()
        project_name_input.setPlaceholderText('MyProject')
        self._project_name_input = project_name_input

        project_name_layout = QVBoxLayout()
        project_name_layout.addWidget(project_name_label)
        project_name_layout.addWidget(project_name_input)
        project_name_layout.addStretch()

        return project_name_layout

    def open_project_ui(self) -> QVBoxLayout:
        open_project_layout = QVBoxLayout()
        project_list_label = QLabel(self.tr('Open Existing Project:'))
        project_list = QListWidget()
        project_list.addItems(self.get_existing_projects())
        project_list.itemDoubleClicked.connect(self.open_project)

        open_project_layout.addWidget(project_list_label)
        open_project_layout.addWidget(project_list)

        return open_project_layout

    def cancel_button_ui(self) -> QPushButton:
        cancel_button = QPushButton(self.tr('Cancel'))
        cancel_button.clicked.connect(self.cancel)

        return cancel_button

    def create_button_ui(self) -> QPushButton:
        save_button = QPushButton(self.tr('Create'))
        save_button.clicked.connect(self.create_project)

        return save_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def create_project(self):
        project_name = self._project_name_input.text()
        if os.path.exists(f'projects/{project_name}'):
            QMessageBox.critical(self, self.tr('Error'), f"{self.tr('Project')} {project_name} {self.tr('already exists!')}")
            return
        project = Project(project_name)
        new_tab = ProjectWidget(self._add_new_tab, project)
        self._add_new_tab(new_tab, project_name, True)
        self.close()

    def cancel(self):
        self.close()

    def get_existing_projects(self):
        all_entries = os.listdir('projects')
        project_names = []
        for entry in all_entries:
            full_path = os.path.join('projects', entry)
            if os.path.isdir(full_path):
                project_names.append(entry)
        return project_names

    def open_project(self, item):
        project_name = item.text()
        try:
            project = Project(project_name)
        except Exception as e:
            QMessageBox.critical(self, self.tr('Error'), e.args[0])

            return
        new_tab = ProjectWidget(self._add_new_tab, project)
        self._add_new_tab(new_tab, project_name, True)
        self.close()

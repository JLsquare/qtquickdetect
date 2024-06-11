from typing import Callable, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QListWidget, QMessageBox
from models.app_state import AppState
from models.project import Project
from views.project_widget import ProjectWidget
import os


class NewProjectWindow(QWidget):
    def __init__(self, add_new_tab: Callable[[QWidget, str, bool], None]):
        super().__init__()

        # PyQT6 Components
        self._main_layout: Optional[QGridLayout] = None
        self._project_name_label: Optional[QLabel] = None
        self._project_name_input: Optional[QLineEdit] = None
        self._project_name_layout: Optional[QVBoxLayout] = None
        self._open_project_layout: Optional[QVBoxLayout] = None
        self._project_list_label: Optional[QLabel] = None
        self._project_list: Optional[QListWidget] = None
        self._cancel_button: Optional[QPushButton] = None
        self._save_button: Optional[QPushButton] = None
        self._new_project: Optional[Project] = None

        self._appstate = AppState.get_instance()
        self._add_new_tab = add_new_tab
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self.setWindowTitle(self.tr('QTQuickDetect New/Open Project'))
        self.setGeometry(100, 100, 480, 320)
        self.setStyleSheet(self._appstate.qss)

        self._main_layout = QGridLayout(self)
        self._main_layout.addLayout(self.project_name_ui(), 0, 0, 1, 2)
        self._main_layout.addWidget(self.cancel_button_ui(), 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self._main_layout.addWidget(self.create_button_ui(), 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self._main_layout.addLayout(self.open_project_ui(), 2, 0, 1, 2)
        self.setLayout(self._main_layout)

    def project_name_ui(self) -> QVBoxLayout:
        self._project_name_label = QLabel(self.tr('New Project name:'))
        self._project_name_input = QLineEdit()
        self._project_name_input.setPlaceholderText('MyProject')

        self._project_name_layout = QVBoxLayout()
        self._project_name_layout.addWidget(self._project_name_label)
        self._project_name_layout.addWidget(self._project_name_input)
        self._project_name_layout.addStretch()
        return self._project_name_layout

    def open_project_ui(self) -> QVBoxLayout:
        self._open_project_layout = QVBoxLayout()
        self._project_list_label = QLabel(self.tr('Open Existing Project:'))
        self._project_list = QListWidget()
        self._project_list.addItems(self.get_existing_projects())
        self._project_list.itemDoubleClicked.connect(self.open_project)

        self._open_project_layout.addWidget(self._project_list_label)
        self._open_project_layout.addWidget(self._project_list)
        return self._open_project_layout

    def cancel_button_ui(self) -> QPushButton:
        self._cancel_button = QPushButton(self.tr('Cancel'))
        self._cancel_button.clicked.connect(self.cancel)
        return self._cancel_button

    def create_button_ui(self) -> QPushButton:
        self._save_button = QPushButton(self.tr('Create'))
        self._save_button.clicked.connect(self.create_project)
        return self._save_button

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
            self._new_project = Project(project_name)
        except Exception as e:
            QMessageBox.critical(self, self.tr('Error'), e.args[0])
            return
        new_tab = ProjectWidget(self._add_new_tab, self._new_project)
        self._add_new_tab(new_tab, project_name, True)
        self.close()

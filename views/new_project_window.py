from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QGridLayout

from views.start_widget import StartWidget


class NewProjectWindow(QWidget):
    def __init__(self, add_new_tab: Callable[[QWidget, str, bool], None]):
        super().__init__()
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
        self._project_name_input = project_name_input

        project_name_layout = QVBoxLayout()
        project_name_layout.addWidget(project_name_label)
        project_name_layout.addWidget(project_name_input)
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

    def create_project(self):
        project_name = self._project_name_input.text()
        new_tab = StartWidget(self._add_new_tab)
        self._add_new_tab(new_tab, project_name, True)
        self.close()

    def cancel(self):
        self.close()

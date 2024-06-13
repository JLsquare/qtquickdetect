from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class TrainingWidget(QWidget):
    def __init__(self, parent=None):
        super(TrainingWidget, self).__init__(parent)
        self._text = None
        self._main_layout = None
        self.init_ui()

    def init_ui(self):
        self._main_layout = QVBoxLayout()
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._text = QLabel('todo')
        self._main_layout.addWidget(self._text)
        self.setLayout(self._main_layout)

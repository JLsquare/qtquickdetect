from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class TrainingWidget(QWidget):
    def __init__(self, parent=None):
        super(TrainingWidget, self).__init__(parent)
        self._img = None
        self._main_layout = None
        self.init_ui()

    def init_ui(self):
        self._main_layout = QVBoxLayout()
        pixmap = QPixmap('ressources/images/really_important.jpeg')
        self._img = QLabel()
        self._img.setPixmap(pixmap)
        self._img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._main_layout.addWidget(self._img)
        self.setLayout(self._main_layout)

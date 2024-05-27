from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class AboutWidget(QWidget):
    def __init__(self, parent=None):
        super(AboutWidget, self).__init__(parent)

        # PyQT6 Components
        self._text = None
        self._main_layout = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self._main_layout = QVBoxLayout()
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._text = QLabel("todo")
        self._main_layout.addWidget(self._text)
        self.setLayout(self._main_layout)

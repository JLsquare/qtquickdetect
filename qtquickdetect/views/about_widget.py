from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class AboutWidget(QWidget):
    """
    AboutWidget is a QWidget that displays information about the application.
    """
    def __init__(self):
        """
        Initializes the AboutWidget.
        """
        super().__init__()

        # PyQT6 Components
        self._text: Optional[QLabel] = None
        self._main_layout: Optional[QVBoxLayout] = None

        self.init_ui()

    def init_ui(self) -> None:
        """
        Initializes the user interface components.
        """
        self._main_layout = QVBoxLayout()
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._text = QLabel("todo")
        self._main_layout.addWidget(self._text)
        self.setLayout(self._main_layout)

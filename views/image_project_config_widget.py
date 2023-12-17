from typing import Optional
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QColorDialog
from PyQt6.QtCore import Qt
from models.project_config import ProjectConfig
import logging


class ImageProjectConfigWidget(QWidget):
    def __init__(self, config: ProjectConfig):
        super().__init__()

        # PyQT6 Components
        self._main_layout: Optional[QVBoxLayout] = None
        self._file_format_label: Optional[QLabel] = None
        self._file_format_combo: Optional[QComboBox] = None
        self._file_format_layout: Optional[QVBoxLayout] = None
        self._box_color_label: Optional[QLabel] = None
        self._box_color_picker: Optional[QPushButton] = None
        self._box_color_layout: Optional[QVBoxLayout] = None
        self._text_color_label: Optional[QLabel] = None
        self._text_color_picker: Optional[QPushButton] = None
        self._text_color_layout: Optional[QVBoxLayout] = None
        self._box_thickness_label: Optional[QLabel] = None
        self._box_thickness_slider: Optional[QLineEdit] = None
        self._box_thickness_layout: Optional[QVBoxLayout] = None
        self._text_size_label: Optional[QLabel] = None
        self._text_size_slider: Optional[QLineEdit] = None
        self._text_size_layout: Optional[QVBoxLayout] = None

        self._config = config
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self._main_layout = QVBoxLayout()
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._main_layout.addLayout(self.file_format_ui())
        self._main_layout.addLayout(self.box_color_ui())
        self._main_layout.addLayout(self.text_color_ui())
        self._main_layout.addLayout(self.box_thickness_ui())
        self._main_layout.addLayout(self.text_size_ui())
        self.setLayout(self._main_layout)

    def file_format_ui(self) -> QVBoxLayout:
        self._file_format_label = QLabel('File format:')
        self._file_format_combo = QComboBox()
        self._file_format_combo.addItem('PNG (.png)', 'png')
        self._file_format_combo.addItem('JPEG (.jpg, .jpeg)', 'jpg')
        self._file_format_combo.setCurrentText(self.get_file_format())
        self._file_format_combo.currentTextChanged.connect(self.set_file_format)

        self._file_format_layout = QVBoxLayout()
        self._file_format_layout.addWidget(self._file_format_label)
        self._file_format_layout.addWidget(self._file_format_combo)
        return self._file_format_layout

    def box_color_ui(self) -> QVBoxLayout:
        self._box_color_label = QLabel('Box color:')
        self._box_color_picker = QPushButton('Pick')
        self._box_color_picker.clicked.connect(self.set_box_color)
        self.update_box_color()

        self._box_color_layout = QVBoxLayout()
        self._box_color_layout.addWidget(self._box_color_label)
        self._box_color_layout.addWidget(self._box_color_picker)
        return self._box_color_layout

    def text_color_ui(self) -> QVBoxLayout:
        self._text_color_label = QLabel('Text color:')
        self._text_color_picker = QPushButton('Pick')
        self._text_color_picker.clicked.connect(self.set_text_color)
        self.update_text_color()

        self._text_color_layout = QVBoxLayout()
        self._text_color_layout.addWidget(self._text_color_label)
        self._text_color_layout.addWidget(self._text_color_picker)
        return self._text_color_layout

    def box_thickness_ui(self) -> QVBoxLayout:
        self._box_thickness_label = QLabel('Box thickness:')
        self._box_thickness_slider = QLineEdit()
        self._box_thickness_slider.setText(str(self._config.image_box_thickness))
        self._box_thickness_slider.textChanged.connect(self.set_box_thickness)

        self._box_thickness_layout = QVBoxLayout()
        self._box_thickness_layout.addWidget(self._box_thickness_label)
        self._box_thickness_layout.addWidget(self._box_thickness_slider)
        return self._box_thickness_layout

    def text_size_ui(self) -> QVBoxLayout:
        self._text_size_label = QLabel('Text size:')
        self._text_size_slider = QLineEdit()
        self._text_size_slider.setText(str(self._config.image_text_size))
        self._text_size_slider.textChanged.connect(self.set_text_size)

        self._text_size_layout = QVBoxLayout()
        self._text_size_layout.addWidget(self._text_size_label)
        self._text_size_layout.addWidget(self._text_size_slider)
        return self._text_size_layout

    ##############################
    #         CONTROLLER         #
    ##############################

    def get_file_format(self) -> str:
        if self._config.image_format == 'png':
            return 'PNG (.png)'
        elif self._config.image_format == 'jpg':
            return 'JPEG (.jpg, .jpeg)'

    def set_file_format(self, value: str):
        if value == 'PNG (.png)':
            self._config.image_format = 'png'
        elif value == 'JPEG (.jpg, .jpeg)':
            self._config.image_format = 'jpg'
        logging.debug('Set image format to {}'.format(value))

    def set_box_color(self):
        color = self._config.image_box_color
        color_picker = QColorDialog()
        color_picker.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel)
        color_picker.setCurrentColor(QColor(color[0], color[1], color[2], color[3]))
        if color_picker.exec() == QColorDialog.DialogCode.Accepted:
            new_color = color_picker.currentColor()
            self._config.image_box_color = (new_color.red(), new_color.green(), new_color.blue(), new_color.alpha())
            self.update_box_color()

    def update_box_color(self):
        color = self._config.image_box_color
        self._box_color_picker.setStyleSheet(f'background-color: rgb{color[0], color[1], color[2]};')

    def set_text_color(self):
        color = self._config.image_text_color
        color_picker = QColorDialog()
        color_picker.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel)
        color_picker.setCurrentColor(QColor(color[0], color[1], color[2], color[3]))
        if color_picker.exec() == QColorDialog.DialogCode.Accepted:
            new_color = color_picker.currentColor()
            self._config.image_text_color = (new_color.red(), new_color.green(), new_color.blue(), new_color.alpha())
            self.update_text_color()

    def update_text_color(self):
        color = self._config.image_text_color
        self._text_color_picker.setStyleSheet(f'background-color: rgb{color[0], color[1], color[2]};')

    def set_box_thickness(self, value: str):
        try:
            self._config.image_box_thickness = int(value)
            logging.debug('Set box thickness to {}'.format(value))
        except ValueError:
            self._config.image_box_thickness = 1
            logging.debug('Set box thickness to 1')

    def set_text_size(self, value: str):
        try:
            self._config.image_text_size = float(value)
            logging.debug('Set text size to {}'.format(value))
        except ValueError:
            self._config.image_text_size = 1.0
            logging.debug('Set text size to 1.0')
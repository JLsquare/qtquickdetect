from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QColorDialog
from PyQt6.QtCore import Qt
from models.app_state import AppState
import logging


class ImageConfigWidget(QWidget):
    def __init__(self, appstate: AppState):
        super().__init__()
        self._appstate = appstate
        self._box_color_picker = None
        self._text_color_picker = None
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(self.file_format_ui())
        main_layout.addLayout(self.box_color_ui())
        main_layout.addLayout(self.text_color_ui())
        main_layout.addLayout(self.box_thickness_ui())
        main_layout.addLayout(self.text_size_ui())
        self.setLayout(main_layout)

    def file_format_ui(self) -> QVBoxLayout:
        file_format_label = QLabel('File format:')
        file_format_combo = QComboBox()
        file_format_combo.addItem('PNG (.png)', 'png')
        file_format_combo.addItem('JPEG (.jpg, .jpeg)', 'jpg')
        file_format_combo.setCurrentText(self.get_file_format())
        file_format_combo.currentTextChanged.connect(self.set_file_format)

        file_format_layout = QVBoxLayout()
        file_format_layout.addWidget(file_format_label)
        file_format_layout.addWidget(file_format_combo)

        return file_format_layout

    def box_color_ui(self) -> QVBoxLayout:
        box_color_label = QLabel('Box color:')
        box_color_picker = QPushButton('Pick')
        box_color_picker.clicked.connect(self.set_box_color)
        self._box_color_picker = box_color_picker
        self.update_box_color()

        box_color_layout = QVBoxLayout()
        box_color_layout.addWidget(box_color_label)
        box_color_layout.addWidget(box_color_picker)

        return box_color_layout

    def text_color_ui(self) -> QVBoxLayout:
        text_color_label = QLabel('Text color:')
        text_color_picker = QPushButton('Pick')
        text_color_picker.clicked.connect(self.set_text_color)
        self._text_color_picker = text_color_picker
        self.update_text_color()

        text_color_layout = QVBoxLayout()
        text_color_layout.addWidget(text_color_label)
        text_color_layout.addWidget(text_color_picker)

        return text_color_layout

    def box_thickness_ui(self) -> QVBoxLayout:
        box_thickness_label = QLabel('Box thickness:')
        box_thickness_slider = QLineEdit()
        box_thickness_slider.setText(str(self._appstate.config.image_box_thickness))
        box_thickness_slider.textChanged.connect(self.set_box_thickness)

        box_thickness_layout = QVBoxLayout()
        box_thickness_layout.addWidget(box_thickness_label)
        box_thickness_layout.addWidget(box_thickness_slider)

        return box_thickness_layout

    def text_size_ui(self) -> QVBoxLayout:
        text_size_label = QLabel('Text size:')
        text_size_slider = QLineEdit()
        text_size_slider.setText(str(self._appstate.config.image_text_size))
        text_size_slider.textChanged.connect(self.set_text_size)

        text_size_layout = QVBoxLayout()
        text_size_layout.addWidget(text_size_label)
        text_size_layout.addWidget(text_size_slider)

        return text_size_layout

    ##############################
    #         CONTROLLER         #
    ##############################

    def get_file_format(self) -> str:
        if self._appstate.config.image_format == 'png':
            return 'PNG (.png)'
        elif self._appstate.config.image_format == 'jpg':
            return 'JPEG (.jpg, .jpeg)'

    def set_file_format(self, value: str):
        if value == 'PNG (.png)':
            self._appstate.config.image_format = 'png'
        elif value == 'JPEG (.jpg, .jpeg)':
            self._appstate.config.image_format = 'jpg'
        logging.debug('Set image format to {}'.format(value))

    def set_box_color(self):
        color = self._appstate.config.image_box_color
        color_picker = QColorDialog()
        color_picker.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel)
        color_picker.setCurrentColor(QColor(color[0], color[1], color[2], color[3]))
        if color_picker.exec() == QColorDialog.DialogCode.Accepted:
            new_color = color_picker.currentColor()
            self._appstate.config.image_box_color = (new_color.red(), new_color.green(), new_color.blue(), new_color.alpha())
            self.update_box_color()

    def update_box_color(self):
        color = self._appstate.config.image_box_color
        self._box_color_picker.setStyleSheet(f'background-color: rgb{color[0], color[1], color[2]};')

    def set_text_color(self):
        color = self._appstate.config.image_text_color
        color_picker = QColorDialog()
        color_picker.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel)
        color_picker.setCurrentColor(QColor(color[0], color[1], color[2], color[3]))
        if color_picker.exec() == QColorDialog.DialogCode.Accepted:
            new_color = color_picker.currentColor()
            self._appstate.config.image_text_color = (new_color.red(), new_color.green(), new_color.blue(), new_color.alpha())
            self.update_text_color()

    def update_text_color(self):
        color = self._appstate.config.image_text_color
        self._text_color_picker.setStyleSheet(f'background-color: rgb{color[0], color[1], color[2]};')

    def set_box_thickness(self, value: str):
        try:
            self._appstate.config.image_box_thickness = int(value)
            logging.debug('Set box thickness to {}'.format(value))
        except ValueError:
            self._appstate.config.image_box_thickness = 1
            logging.debug('Set box thickness to 1')

    def set_text_size(self, value: str):
        try:
            self._appstate.config.image_text_size = float(value)
            logging.debug('Set text size to {}'.format(value))
        except ValueError:
            self._appstate.config.image_text_size = 1.0
            logging.debug('Set text size to 1.0')

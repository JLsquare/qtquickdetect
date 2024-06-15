from typing import Optional
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QRadioButton, QLabel, QScrollArea
from ..models.app_state import AppState
from ..utils import filepaths


class PresetSelectionWidget(QWidget):
    preset_changed_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.appstate = AppState.get_instance()
        self.preset = ''

        # PyQT6 Components
        self._preset_icon_layout: Optional[QHBoxLayout] = None
        self._preset_icon: Optional[QLabel] = None
        self._preset_radio_layout: Optional[QVBoxLayout] = None
        self._preset_radio_buttons: Optional[list[QRadioButton]] = None
        self._preset_radio_widget: Optional[QWidget] = None
        self._scroll_area: Optional[QScrollArea] = None
        self._preset_layout: Optional[QVBoxLayout] = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Preset icon
        self._preset_icon_layout = QHBoxLayout()
        self._preset_icon_layout.addStretch()
        self._preset_icon = QLabel()
        self._preset_icon.setPixmap(
            QPixmap(str(filepaths.get_app_dir() / 'resources' / 'images' / 'settings_icon.png'))
            .scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )
        self._preset_icon_layout.addWidget(self._preset_icon)
        self._preset_icon_layout.addStretch()

        self._preset_radio_layout = QVBoxLayout()
        self._preset_radio_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._preset_radio_buttons = []
        for preset in self.appstate.presets.get_presets():
            radio_button = QRadioButton(preset)
            radio_button.setObjectName(preset)
            radio_button.toggled.connect(self._check_preset_selected)
            self._preset_radio_buttons.append(radio_button)
            self._preset_radio_layout.addWidget(radio_button)

        self._preset_radio_widget = QWidget()
        self._preset_radio_widget.setLayout(self._preset_radio_layout)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setWidget(self._preset_radio_widget)
        self._scroll_area.setProperty('class', 'border')

        self._description = QLabel(self.tr('Select a preset'))
        self._description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._description.setProperty('class', 'description')

        # Preset Layout
        self._preset_layout = QVBoxLayout()
        self._preset_layout.addLayout(self._preset_icon_layout)
        self._preset_layout.addWidget(self._scroll_area)
        self._preset_layout.addWidget(self._description)

        self.setLayout(self._preset_layout)
        self.setFixedSize(240, 360)

    ##############################
    #         CONTROLLER         #
    ##############################

    def _check_preset_selected(self):
        for radio_button in self._preset_radio_buttons:
            if radio_button.isChecked():
                self.preset = radio_button.objectName()
                self.preset_changed_signal.emit()
                break

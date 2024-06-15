from typing import Optional
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QRadioButton, QLabel, QScrollArea
from ..models.app_state import AppState
from ..utils import filepaths


class CollectionSelectionWidget(QWidget):
    collection_changed_signal = pyqtSignal()

    def __init__(self, media_type: str):
        super().__init__()
        self.appstate = AppState.get_instance()
        self.media_type = media_type
        self.task = 'detect'
        self.collection = ''

        # PyQT6 Components
        self._collection_icon_layout: Optional[QHBoxLayout] = None
        self._collection_icon: Optional[QLabel] = None
        self._collection_radio_layout: Optional[QVBoxLayout] = None
        self._collection_radio_buttons: Optional[list[QRadioButton]] = None
        self._collection_radio_widget: Optional[QWidget] = None
        self._scroll_area: Optional[QScrollArea] = None
        self._collection_layout: Optional[QVBoxLayout] = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Task icon
        self._collection_icon_layout = QHBoxLayout()
        self._collection_icon_layout.addStretch()
        self._collection_icon = QLabel()
        self._collection_icon.setPixmap(
            QPixmap(str(filepaths.get_app_dir() / 'resources' / 'images' / 'input_icon.png'))
            .scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )
        self._collection_icon_layout.addWidget(self._collection_icon)
        self._collection_icon_layout.addStretch()

        collections = self.appstate.collections.get_collections(self.media_type)
        self._collection_radio_layout = QVBoxLayout()
        self._collection_radio_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._collection_radio_buttons = []
        for collection in collections:
            radio_button = QRadioButton(collection)
            radio_button.setObjectName(collection)
            radio_button.toggled.connect(self._check_collection_selected)
            self._collection_radio_buttons.append(radio_button)
            self._collection_radio_layout.addWidget(radio_button)

        self._collection_radio_widget = QWidget()
        self._collection_radio_widget.setLayout(self._collection_radio_layout)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setWidget(self._collection_radio_widget)
        self._scroll_area.setProperty('class', 'border')

        self._description = QLabel('Select a collection')
        self._description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._description.setProperty('class', 'description')

        # Task Layout
        self._collection_layout = QVBoxLayout()
        self._collection_layout.addLayout(self._collection_icon_layout)
        self._collection_layout.addWidget(self._scroll_area)
        self._collection_layout.addWidget(self._description)

        self.setLayout(self._collection_layout)
        self.setFixedSize(240, 360)

    ##############################
    #         CONTROLLER         #
    ##############################

    def _check_collection_selected(self):
        for radio_button in self._collection_radio_buttons:
            if radio_button.isChecked():
                self.collection = radio_button.objectName()
                self.collection_changed_signal.emit()
                break

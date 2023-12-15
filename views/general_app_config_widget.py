from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt
from models.app_config import AppConfig
import logging


class GeneralAppConfigWidget(QWidget):
    def __init__(self, config: AppConfig):
        super().__init__()

        # PyQT6 Components
        self._main_layout: Optional[QVBoxLayout] = None
        self._qss_label: Optional[QLabel] = None
        self._qss_combo: Optional[QComboBox] = None
        self._qss_layout: Optional[QVBoxLayout] = None
        self._local_label: Optional[QLabel] = None
        self._local_combo: Optional[QComboBox] = None
        self.local_layout: Optional[QVBoxLayout] = None

        self._config = config
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self._main_layout = QVBoxLayout()
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._main_layout.addLayout(self.qss_ui())
        self._main_layout.addLayout(self.local_ui())
        self.setLayout(self._main_layout)

    def qss_ui(self) -> QVBoxLayout:
        self._qss_label = QLabel('QSS (need restart):')
        self._qss_combo = QComboBox()
        self._qss_combo.addItem('App Default', 'app')
        self._qss_combo.addItem('System', 'sys')
        self._qss_combo.setCurrentText(self.get_qss())
        self._qss_combo.currentIndexChanged.connect(self.set_qss)
        self._qss_combo = self._qss_combo

        self._qss_layout = QVBoxLayout()
        self._qss_layout.addWidget(self._qss_label)
        self._qss_layout.addWidget(self._qss_combo)
        return self._qss_layout

    def local_ui(self):
        self._local_label = QLabel('Localization:')
        self._local_combo = QComboBox()
        self._local_combo.addItem('English', 'en')
        self._local_combo.addItem('French', 'fr')
        self._local_combo.setCurrentText(self.get_local())
        self._local_combo.currentIndexChanged.connect(self.set_local)
        self._local_combo = self._local_combo

        self.local_layout = QVBoxLayout()
        self.local_layout.addWidget(self._local_label)
        self.local_layout.addWidget(self._local_combo)
        return self.local_layout

    ##############################
    #         CONTROLLER         #
    ##############################

    def get_qss(self) -> str:
        qss = self._config.qss
        if qss == 'app':
            return 'App Default'
        else:
            return 'System'

    def set_qss(self):
        logging.debug(f'Setting QSS to {self._qss_combo.currentData()}')
        self._config.qss = self._qss_combo.currentData()

    def get_local(self) -> str:
        local = self._config.localization
        if local == 'fr':
            return 'French'
        else:
            return 'English'

    def set_local(self):
        logging.debug(f'Setting localization to {self._local_combo.currentData()}')
        self._config.localization = self._local_combo.currentData()

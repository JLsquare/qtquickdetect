import logging

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt
from models.app_config import AppConfig


class GeneralAppConfigWidget(QWidget):
    def __init__(self, config: AppConfig):
        super().__init__()
        self._qss_combo = None
        self._local_combo = None
        self._config = config
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(self.qss_ui())
        main_layout.addLayout(self.local_ui())
        self.setLayout(main_layout)

    def qss_ui(self) -> QVBoxLayout:
        qss_label = QLabel('QSS (need restart):')
        qss_combo = QComboBox()
        qss_combo.addItem('App Default', 'app')
        qss_combo.addItem('System', 'sys')
        qss_combo.setCurrentText(self.get_qss())
        qss_combo.currentIndexChanged.connect(self.set_qss)
        self._qss_combo = qss_combo

        qss_layout = QVBoxLayout()
        qss_layout.addWidget(qss_label)
        qss_layout.addWidget(qss_combo)

        return qss_layout

    def local_ui(self):
        local_label = QLabel('Localization:')
        local_combo = QComboBox()
        local_combo.addItem('English', 'en')
        local_combo.addItem('French', 'fr')
        local_combo.setCurrentText(self.get_local())
        local_combo.currentIndexChanged.connect(self.set_local)
        self._local_combo = local_combo

        local_layout = QVBoxLayout()
        local_layout.addWidget(local_label)
        local_layout.addWidget(local_combo)

        return local_layout

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

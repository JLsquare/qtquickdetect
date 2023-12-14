from PyQt6.QtWidgets import QWidget, QTabWidget, QGridLayout, QPushButton, QVBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt
from models.app_state import AppState
from views.general_app_config_widget import GeneralAppConfigWidget
import logging


class AppConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._appstate = AppState.get_instance()
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self.setWindowTitle(self.tr('QTQuickDetect Settings'))
        self.setGeometry(100, 100, 480, 480)
        self.setStyleSheet(self._appstate.qss)
        self.setProperty('class', 'dark-bg')

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        tab = QTabWidget(self)
        tab.addTab(GeneralAppConfigWidget(self._appstate.config), "General")

        main_layout.addWidget(tab, 0, 0, 2, 1)
        main_layout.addWidget(self.cancel_button_ui(), 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.save_button_ui(), 2, 0, alignment=Qt.AlignmentFlag.AlignRight)

    def cancel_button_ui(self) -> QPushButton:
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.cancel_settings)

        return cancel_button

    def save_button_ui(self) -> QPushButton:
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_settings)

        return save_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def save_settings(self):
        self._appstate.save()
        logging.debug('Saved settings')
        self.close()

    def cancel_settings(self):
        logging.debug('Canceled settings')
        self.close()

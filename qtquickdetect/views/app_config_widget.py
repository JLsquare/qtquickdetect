import logging

from typing import Optional
from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QLabel, QComboBox, QSpacerItem, \
    QSizePolicy, QMessageBox, QApplication
from PyQt6.QtCore import Qt
from ..models.app_config import AppConfig
from ..models.app_state import AppState


class AppConfigWidget(QWidget):
    """
    AppConfigWidget is a QWidget that provides a user interface for modifying the application configuration.
    """
    def __init__(self):
        """
        Initializes the AppConfigWidget.
        """
        super().__init__()
        self.app_state: AppState = AppState.get_instance()

        # PyQT6 Components
        self._spacer: Optional[QSpacerItem] = None
        self._main_layout: Optional[QGridLayout] = None
        self._cancel_button: Optional[QPushButton] = None
        self._save_button: Optional[QPushButton] = None
        self._open_config_button: Optional[QPushButton] = None
        self._reset_config_button: Optional[QPushButton] = None
        self._qss_label: Optional[QLabel] = None
        self._qss_combo: Optional[QComboBox] = None
        self._qss_layout: Optional[QVBoxLayout] = None
        self._local_label: Optional[QLabel] = None
        self._local_combo: Optional[QComboBox] = None
        self._local_layout: Optional[QVBoxLayout] = None
        self._config_label: Optional[QLabel] = None
        self._config_layout: Optional[QVBoxLayout] = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self) -> None:
        """
        Initializes the user interface components.
        """
        self.setWindowTitle(self.tr('QTQuickDetect Settings'))
        self.setGeometry(100, 100, 480, 480)
        self.setStyleSheet(self.app_state.qss)
        self.setProperty('class', 'dark-bg')

        self._main_layout = QGridLayout(self)
        self.setLayout(self._main_layout)

        self._main_layout.addLayout(self.qss_ui(), 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
        self._main_layout.addLayout(self.local_ui(), 1, 0, alignment=Qt.AlignmentFlag.AlignTop)
        self._main_layout.addLayout(self.config_buttons_ui(), 2, 0, alignment=Qt.AlignmentFlag.AlignTop)
        self._main_layout.addItem(self.spacer(), 3, 0, 1, 2)
        self._main_layout.addWidget(self.cancel_button_ui(), 4, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self._main_layout.addWidget(self.save_button_ui(), 4, 1, alignment=Qt.AlignmentFlag.AlignRight)

    def qss_ui(self) -> QVBoxLayout:
        """
        Creates and returns the QSS settings layout.

        :return: QVBoxLayout for QSS settings.
        """
        self._qss_label = QLabel(self.tr('QSS (need restart):'))
        self._qss_combo = QComboBox()
        self._qss_combo.addItem(self.tr('Dark (default)'), 'dark')
        self._qss_combo.addItem(self.tr('Light'), 'light')
        self._qss_combo.addItem(self.tr('System'), 'sys')
        self._qss_combo.setCurrentText(self.get_qss())
        self._qss_combo.currentIndexChanged.connect(self.set_qss)

        self._qss_layout = QVBoxLayout()
        self._qss_layout.addWidget(self._qss_label)
        self._qss_layout.addWidget(self._qss_combo)
        return self._qss_layout

    def local_ui(self) -> QVBoxLayout:
        """
        Creates and returns the localization settings layout.

        :return: QVBoxLayout for localization settings.
        """
        self._local_label = QLabel(self.tr('Language (need restart):'))
        self._local_combo = QComboBox()
        self._local_combo.addItem('English', 'en')
        self._local_combo.addItem('Français', 'fr')
        self._local_combo.setCurrentText(self.get_local())
        self._local_combo.currentIndexChanged.connect(self.set_local)

        self._local_layout = QVBoxLayout()
        self._local_layout.addWidget(self._local_label)
        self._local_layout.addWidget(self._local_combo)
        return self._local_layout

    def config_buttons_ui(self) -> QVBoxLayout:
        """
        Creates and returns the config buttons layout.

        :return: QVBoxLayout for config buttons.
        """
        self._config_label = QLabel(self.tr('Advanced Options:'))
        self._open_config_button = QPushButton(self.tr('Open App Config'))
        self._open_config_button.clicked.connect(self.open_app_config)
        self._reset_config_button = QPushButton(self.tr('Reset App Config'))
        self._reset_config_button.setProperty("class", "red")
        self._reset_config_button.clicked.connect(self.reset_app_config)

        self._config_layout = QVBoxLayout()
        self._config_layout.addWidget(self._config_label)
        self._config_layout.addWidget(self._open_config_button)
        self._config_layout.addWidget(self._reset_config_button)
        return self._config_layout

    def spacer(self) -> QSpacerItem:
        """
        Creates and returns a spacer item.

        :return: QSpacerItem for layout spacing.
        """
        self._spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        return self._spacer

    def cancel_button_ui(self) -> QPushButton:
        """
        Creates and returns the cancel button.

        :return: QPushButton for canceling settings changes.
        """
        self._cancel_button = QPushButton(self.tr('Cancel'))
        self._cancel_button.clicked.connect(self.cancel_settings)
        return self._cancel_button

    def save_button_ui(self) -> QPushButton:
        """
        Creates and returns the save button.

        :return: QPushButton for saving settings changes.
        """
        self._save_button = QPushButton(self.tr('Save'))
        self._save_button.clicked.connect(self.save_settings)
        return self._save_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def save_settings(self) -> None:
        """
        Saves the current settings and closes the widget.
        """
        self.app_state.save()
        logging.debug('Saved settings')

        # QMessageBox to ask for restart with choice to not restart for now
        reply = QMessageBox.question(self, 'Restart Required',
                                     'Settings have been saved. Would you like to restart the application now?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            QApplication.quit()
        else:
            logging.debug('User chose not to restart the application.')

    def cancel_settings(self) -> None:
        """
        Cancels the settings changes by reverting to the previous settings.
        """
        logging.debug('Canceled settings')
        self.app_state.app_config = AppConfig()
        self._qss_combo.setCurrentText(self.get_qss())
        self._local_combo.setCurrentText(self.get_local())

    def get_qss(self) -> str:
        """
        Retrieves the current QSS setting.

        :return: The current QSS setting as a string.
        """
        qss = self.app_state.app_config.qss
        if qss == 'dark':
            return self.tr('Dark (default)')
        elif qss == 'light':
            return self.tr('Light')
        else:
            return self.tr('System')

    def set_qss(self) -> None:
        """
        Sets the QSS setting based on the combo box selection.
        """
        logging.debug(f"{self.tr('Setting QSS to')} {self._qss_combo.currentData()}")
        self.app_state.app_config.qss = self._qss_combo.currentData()

    def get_local(self) -> str:
        """
        Retrieves the current localization setting.

        :return: The current localization setting as a string.
        """
        local = self.app_state.app_config.localization
        if local == 'fr':
            return 'Français'
        else:
            return 'English'

    def set_local(self) -> None:
        """
        Sets the localization setting based on the combo box selection.
        """
        logging.debug(f'Setting localization to {self._local_combo.currentData()}')
        self.app_state.app_config.localization = self._local_combo.currentData()

    def open_app_config(self) -> None:
        """
        Opens the app config JSON file.
        """
        try:
            self.app_state.app_config.open_config()
            QMessageBox.information(self, "Success", "App config JSON opened successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open app config: {str(e)}")

    def reset_app_config(self) -> None:
        """
        Resets the app config to default values.
        """
        reply = QMessageBox.question(self, 'Reset App Config',
                                     "Are you sure you want to reset the app config to default values?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.app_state.app_config.reset_config()
                self._qss_combo.setCurrentText(self.get_qss())
                self._local_combo.setCurrentText(self.get_local())
                QMessageBox.information(self, "Success", "App config reset successfully.")
                self.save_settings()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reset app config: {str(e)}")

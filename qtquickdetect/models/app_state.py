import logging
from typing import Optional

from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication
from .app_config import AppConfig
from .collections import Collections
from .presets import Presets
from ..utils import filepaths


class AppState:
    """
    AppState is a singleton class responsible for managing the application's state.
    It holds references to various components such as configuration, collections, presets,
    and manages application-level settings like QSS and localization.
    """
    _instance = None

    def __init__(self):
        """
        Initializes the AppState instance, setting up the application configuration,
        collections, presets, and QSS. Ensures that only one instance of the class can be created.
        """
        if AppState._instance is not None:
            raise Exception('Singleton class, use get_instance() instead')

        AppState._instance = self

        self.pipelines: list = []
        self.app_config: AppConfig = AppConfig()
        self.collections: Collections = Collections()
        self.presets: Presets = Presets()
        self.qss: Optional[str] = None
        self.app: Optional[QApplication] = None
        self._translator: Optional[QTranslator] = None

        self.update_qss()

    @staticmethod
    def get_instance() -> 'AppState':
        """
        Returns the singleton instance of the AppState class. Creates a new instance if none exists.
        :return: The singleton instance of AppState.
        """
        if AppState._instance is None:
            AppState()
        return AppState._instance

    def set_app(self, app: QApplication) -> None:
        """
        Sets the QApplication instance for the application state and updates localization settings.
        :param app: The QApplication instance to set.
        """
        self.app = app
        self.update_localization()

    def stop_pipelines(self) -> None:
        """
        Requests cancellation and waits for all pipelines to stop.
        """
        for pipeline in self.pipelines:
            pipeline.request_cancel()
            pipeline.wait()

    def update_qss(self) -> None:
        """
        Updates the QSS (stylesheet) based on the application configuration.
        """
        if self.app_config.qss == 'app':
            with open(filepaths.get_app_dir() / 'resources' / 'qss' / 'stylesheet.qss', 'r') as file:
                self.qss = file.read()
        else:
            self.qss = None

    def update_localization(self) -> None:
        """
        Updates the application's localization settings based on the application configuration.
        """
        if self.app_config.localization == 'fr':
            self._translator = QTranslator()
            if self._translator.load('fr.qm', str(filepaths.get_app_dir() / 'resources' / 'locales')):
                logging.info('Loaded translator')
                self.app.installTranslator(self._translator)
            else:
                logging.warning('Failed to load translator')
        else:
            if self._translator:
                self.app.removeTranslator(self._translator)
                logging.info('Removed translator')

    def save(self) -> None:
        """
        Saves the current application configuration and updates QSS and localization settings.
        """
        self.app_config.save()
        self.update_qss()
        self.update_localization()

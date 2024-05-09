from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication
from models.app_config import AppConfig
from models.collections import Collections
from models.presets import Presets
import logging


class AppState:
    _instance = None

    def __init__(self):
        self._translator = None
        if AppState._instance is not None:
            raise Exception('Singleton class, use get_instance() instead')
        
        AppState._instance = self

        self.pipelines = []
        self.app_config = AppConfig()
        self.collections = Collections()
        self.presets = Presets()
        self.qss = None
        self.app = None

        self.update_qss()

    @staticmethod
    def get_instance() -> 'AppState':
        if AppState._instance is None:
            AppState()
        return AppState._instance

    def set_app(self, app: QApplication):
        self.app = app
        self.update_localization()

    def stop_pipelines(self):
        for pipeline in self.pipelines:
            pipeline.request_cancel()
            pipeline.wait()

    def update_qss(self):
        if self.app_config.qss == 'app':
            with open('ressources/qss/stylesheet.qss', 'r') as file:
                self.qss = file.read()
        else:
            self.qss = None

    def update_localization(self):
        if self.app_config.localization == 'fr':
            self._translator = QTranslator()
            if self._translator.load('fr.qm', 'ressources/locale'):
                logging.info('Loaded translator')
                self.app.installTranslator(self._translator)
            else:
                logging.warning('Failed to load translator')
        else:
            self.app.removeTranslator(self._translator)
            logging.info('Removed translator')

    def save(self):
        self.app_config.save()
        self.update_qss()
        self.update_localization()

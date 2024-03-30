from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication
from models.app_config import AppConfig
from utils.ressource_path import get_ressource_path
import logging


class AppState:
    _instance = None

    def __init__(self):
        self._translator = None
        if AppState._instance is not None:
            raise Exception('Singleton class, use get_instance() instead')
        
        AppState._instance = self

        self.pipelines = []
        self.opened_projects = []
        self.config = AppConfig()
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
        if self.config.qss == 'app':
            stylesheet_path = get_ressource_path('qss/stylesheet.qss')
            with open(stylesheet_path, 'r') as file:
                self.qss = file.read()
        else:
            self.qss = None

    def update_localization(self):
        if self.config.localization == 'fr':
            self._translator = QTranslator()
            local_path = get_ressource_path('local')
            if self._translator.load('fr.qm', local_path):
                logging.info('Loaded translator')
                self.app.installTranslator(self._translator)
            else:
                logging.warning('Failed to load translator')
        else:
            self.app.removeTranslator(self._translator)
            logging.info('Removed translator')

    def save(self):
        self.config.save()
        self.update_qss()
        self.update_localization()

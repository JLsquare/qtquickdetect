from models.config_file import ConfigFile
import torch


class AppState:
    _instance = None

    def __init__(self):
        if AppState._instance is not None:
            raise Exception('Singleton class, use get_instance() instead')
        
        AppState._instance = self

        self.config = ConfigFile()
        self.device = torch.device(self.config.device)
        self.confidence_threshold = self.config.confidence_threshold
        self.pipelines = []

        with open('ressources/qss/stylesheet.qss', 'r') as file:
            self.qss = file.read()

    @staticmethod
    def get_instance() -> 'AppState':
        if AppState._instance is None:
            AppState()
        return AppState._instance

    def save(self):
        self.config.save()
        self.device = torch.device(self.config.device)
        self.confidence_threshold = self.config.confidence_threshold

    def stop_pipelines(self):
        for pipeline in self.pipelines:
            pipeline.request_cancel()
            pipeline.wait()

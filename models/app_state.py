from models.settings import ConfigFile

class AppState:
    _instance = None

    def __init__(self):
        if AppState._instance is not None:
            raise Exception('Singleton class, use get_instance() instead')
        
        _instance = self

        self.config = ConfigFile()

        self.device = torch.device(self.config.device)
        self.confidence_threshold = self.config.confidence_threshold

    @staticmethod
    def get_instance():
        if AppState._instance is None:
            AppState()
        return AppState._instance

    def save(self):
        self.config.save()
        self.device = torch.device(self.config.device)
        self.confidence_threshold = self.config.confidence_threshold

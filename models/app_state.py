class AppState:
    _instance = None

    def __init__(self):
        if AppState._instance is not None:
            raise Exception('Singleton class, use get_instance() instead')
        
        AppState._instance = self

        self.pipelines = []
        self.opened_projects = []

        with open('ressources/qss/stylesheet.qss', 'r') as file:
            self.qss = file.read()

    @staticmethod
    def get_instance() -> 'AppState':
        if AppState._instance is None:
            AppState()
        return AppState._instance

    def stop_pipelines(self):
        for pipeline in self.pipelines:
            pipeline.request_cancel()
            pipeline.wait()

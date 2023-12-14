from models.app_state import AppState
from models.project_config import ProjectConfig
import os
import torch


class Project:
    def __init__(self, project_name: str):
        self._appstate = AppState.get_instance()
        self.project_name = project_name
        if project_name in self._appstate.opened_projects:
            raise Exception(f'Project {project_name} already opened!')

        if not os.path.exists(f'projects/{project_name}'):
            os.mkdir(f'projects/{project_name}')
            os.mkdir(f'projects/{project_name}/input')
            os.mkdir(f'projects/{project_name}/input/images')
            os.mkdir(f'projects/{project_name}/input/videos')
            os.mkdir(f'projects/{project_name}/result')

        self.config = ProjectConfig(project_name)
        self.device = torch.device(self.config.device)
        self._appstate.opened_projects.append(self.project_name)

    def __del__(self):
        self._appstate.opened_projects.remove(self.project_name)

    def save(self):
        self.config.save()
        self.device = torch.device(self.config.device)
        
import logging
import json
import shutil
from pathlib import Path
from typing import Dict, Any

from ..utils import filepaths


class AppConfig:
    """
    AppConfig is responsible for managing application configuration.
    It handles reading from and writing to a JSON config file,
    ensuring the config values are valid, and providing default values if needed.
    """

    def __init__(self):
        """
        Initializes the AppConfig instance, setting default values and loading
        configuration from the config file if it exists. Creates a config file
        with default values if it doesn't exist.
        """
        self.localization: str = 'en'
        self.qss: str = 'dark'
        self.pipelines: Dict[str, Any] = {}
        self.models: Dict[str, Any] = {}

        filepaths.create_config_dir()
        self.path: Path = filepaths.get_base_config_dir() / 'app_config.json'

        if self.path.exists():
            if self.path.is_file():
                self._read_config()
            else:
                raise Exception('app_config.json is a directory!')
        else:
            shutil.copy(filepaths.get_app_dir() / 'resources' / 'default_app_config.json', self.path)
            self._read_config()

    def _read_config(self) -> None:
        """
        Attempts to read the config file and sets instance variables.
        Resets any invalid values to default if necessary.
        """
        save = False

        with open(self.path, 'r') as f:
            config = json.load(f)

            for key in self.__dict__:
                if key in config:
                    try:
                        tmp = config[key]
                        logging.debug(f'Read config key {key}: {tmp}')
                        self.__dict__[key] = tmp
                    except Exception as e:
                        save = True
                        logging.warning(f'Could not read config key {key}: {e}')

        if self._revert_invalid():
            save = True

        if save:
            self.save()

    def _revert_invalid(self) -> bool:
        """
        Reverts invalid values to default values.
        :return: True if any values were changed, False otherwise.
        """
        changed = False

        if self.localization not in ['en', 'fr']:
            logging.warning(f'Invalid localization in config: {self.localization}')
            self.localization = 'en'
            changed = True

        if self.qss not in ['dark', 'light', 'sys']:
            logging.warning(f'Invalid qss in config: {self.qss}')
            self.qss = 'dark'
            changed = True

        return changed

    def save(self) -> None:
        """
        Writes the current config values to the config file.
        """
        self._revert_invalid()

        with open(self.path, 'w') as f:
            data = self.__dict__.copy()
            del data['path']  # Remove path from data as it should not be saved in the config
            json.dump(data, f, indent=4)

import logging
import json

from ..utils import filepaths


class AppConfig:
    def __init__(self):
        self.localization = 'en'
        self.qss = 'app'
        self.pipelines = {}
        self.models = {}
        
        filepaths.create_config_dir()

        self.path = filepaths.get_base_config_dir() / 'app_config.json'

        if self.path.exists():
            if self.path.is_file():
                self._read_config()
            else:
                raise Exception('app_config.json is a directory!')
        else:
            self.save()

    def _read_config(self):
        """
        Attempts to read the config file
        Resets any invalid values to default
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
                    except:
                        save = True
                        logging.warning(f'Could not read config key {key}')

        if self._revert_invalid():
            save = True

        if save:
            self.save()

    def _revert_invalid(self) -> bool:
        """
        Reverts invalid values to default
        :return: True if the config file was changed, False otherwise
        """
        changed = False

        if self.localization not in ['en', 'fr']:
            logging.warning(f'Invalid localization in config: {self.localization}')
            self.localization = 'en'
            changed = True

        if self.qss not in ['app', 'sys']:
            logging.warning(f'Invalid qss in config: {self.qss}')
            self.qss = 'app'
            changed = True

        return changed

    def save(self):
        """
        Writes the config file
        """
        self._revert_invalid()

        with open(self.path, 'w') as f:
            data = self.__dict__.copy()
            del data['path']
            json.dump(data, f, indent=4)


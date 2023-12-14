import logging
import json
import os


class AppConfig:
    def __init__(self):
        self.localization = 'en'
        self.qss = 'app'

        self.path = 'app_config.json'

        if os.path.exists(self.path):
            if os.path.isfile(self.path):
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

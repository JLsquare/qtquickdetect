import logging
import json
import torch
import os
import re

DEVICE_VALIDATION_REGEX = re.compile(r'^(cpu|cuda)(:\d+)?$')

class ConfigFile:
    def __init__(self):
        self.device = 'cpu'
        self.confidence_threshold = 0.8

        if os.path.exists('config.json'):
            if os.path.isfile('config.json'):
                self._read_config()
            else:
                raise Exception('config.json is a directory!')
        else:
            self.save()

    def _read_config(self):
        """
        Attempts to read the config file
        Resets any invalid values to default
        """
        save = False

        with open('config.json', 'r') as f:
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

        if not DEVICE_VALIDATION_REGEX.match(self.device):
            logging.warning(f'Invalid device in config: {self.device}')
            self.device = 'cpu'
            changed = True

        if not (0 <= self.confidence_threshold <= 1):
            logging.warning(f'Invalid confidence threshold in config: {self.confidence_threshold}')
            self.confidence_threshold = 0.8
            changed = True

        return changed


    def save(self):
        """
        Writes the config file
        """
        self._revert_invalid()

        with open('config.json', 'w') as f:
            json.dump(self.__dict__, f, indent=4)

        
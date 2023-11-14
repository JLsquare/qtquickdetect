import logging
import json
import os
import re

DEVICE_VALIDATION_REGEX = re.compile(r'^(cpu|cuda)(:\d+)?$')

class ConfigFile:
    def __init__(self):
        self.device = 'cpu'
        self.confidence_threshold = 0.8

        self.image_format = 'png'
        self.image_box_color = (0, 255, 0, 255)
        self.image_text_color = (0, 0, 0, 255)
        self.image_box_thickness = 2
        self.image_text_size = 1.5

        self.video_format = 'mp4'
        self.video_box_color = (0, 255, 0, 255)
        self.video_text_color = (0, 0, 0, 255)
        self.video_box_thickness = 2
        self.video_text_size = 1.5

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

        if self.image_format not in ['png', 'jpg']:
            logging.warning(f'Invalid image format in config: {self.image_format}')
            self.image_format = 'png'
            changed = True

        if not self._check_color(self.image_box_color):
            logging.warning(f'Invalid image box color in config: {self.image_box_color}')
            self.image_box_color = (0, 255, 0, 255)
            changed = True

        if not self._check_color(self.image_text_color):
            logging.warning(f'Invalid image text color in config: {self.image_text_color}')
            self.image_text_color = (0, 0, 0, 255)
            changed = True

        if self.image_box_thickness < 0:
            logging.warning(f'Invalid video box thickness in config: {self.video_box_thickness}')
            self.video_box_thickness = 2
            changed = True

        if self.image_text_size < 0:
            logging.warning(f'Invalid video text size in config: {self.video_text_size}')
            self.video_text_size = 1.5
            changed = True

        if self.video_format not in ['mp4', 'avi']:
            logging.warning(f'Invalid video format in config: {self.video_format}')
            self.video_format = 'mp4'
            changed = True

        if not self._check_color(self.video_box_color):
            logging.warning(f'Invalid video box color in config: {self.video_box_color}')
            self.video_box_color = (0, 255, 0, 255)
            changed = True

        if not self._check_color(self.video_text_color):
            logging.warning(f'Invalid video text color in config: {self.video_text_color}')
            self.video_text_color = (0, 0, 0, 255)
            changed = True

        if self.video_box_thickness < 0:
            logging.warning(f'Invalid video box thickness in config: {self.video_box_thickness}')
            self.video_box_thickness = 2
            changed = True

        if self.video_text_size < 0:
            logging.warning(f'Invalid video text size in config: {self.video_text_size}')
            self.video_text_size = 1.5
            changed = True

        return changed

    def _check_color(self, color) -> bool:
        if len(color) != 4:
            return False

        for c in color:
            if not (0 <= c <= 255):
                return False

        return True

    def save(self):
        """
        Writes the config file
        """
        self._revert_invalid()

        with open('config.json', 'w') as f:
            json.dump(self.__dict__, f, indent=4)

import logging
import json
import os
import re
import utils.filepaths as filepaths

DEVICE_VALIDATION_REGEX = re.compile(r'^(cpu|cuda)(:\d+)?$')


class Preset:
    def __init__(self, preset_name: str):
        self.device = 'cpu'
        self.half_precision = False
        self.iou_threshold = 0.7

        self.image_format = 'png'
        self.video_format = 'mp4'

        self.box_color = (0, 255, 0, 255)
        self.box_color_per_class = False
        self.segment_color = (0, 255, 0, 255)
        self.segment_color_per_class = False
        self.text_color = (0, 0, 0, 255)
        self.box_thickness = 2
        self.text_size = 1.5

        self.path = os.path.join(filepaths.get_base_data_dir(), 'presets', preset_name)

        if os.path.exists(self.path):
            self._read_config()
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

        if not isinstance(self.half_precision, bool):
            logging.warning(f'Invalid half precision in config: {self.half_precision}')
            self.half_precision = False
            changed = True

        if not isinstance(self.iou_threshold, float) or not (0 <= self.iou_threshold <= 1):
            logging.warning(f'Invalid iou threshold in config: {self.iou_threshold}')
            self.iou_threshold = 0.7
            changed = True

        if not isinstance(self.device, str) or not DEVICE_VALIDATION_REGEX.match(self.device):
            logging.warning(f'Invalid device in config: {self.device}')
            self.device = 'cpu'
            changed = True

        if not isinstance(self.image_format, str) or self.image_format not in ['png', 'jpg']:
            logging.warning(f'Invalid image format in config: {self.image_format}')
            self.image_format = 'png'
            changed = True

        if not isinstance(self.video_format, str) or self.video_format not in ['mp4', 'avi']:
            logging.warning(f'Invalid video format in config: {self.video_format}')
            self.video_format = 'mp4'
            changed = True

        if not self._check_color(self.box_color):
            logging.warning(f'Invalid image box color in config: {self.box_color}')
            self.box_color = (0, 255, 0, 255)
            changed = True

        if not self._check_color(self.segment_color):
            logging.warning(f'Invalid image segment color in config: {self.segment_color}')
            self.segment_color = (0, 255, 0, 255)
            changed = True

        if not self._check_color(self.text_color):
            logging.warning(f'Invalid image text color in config: {self.text_color}')
            self.text_color = (0, 0, 0, 255)
            changed = True

        if not isinstance(self.box_thickness, int) and self.box_thickness < 0:
            logging.warning(f'Invalid video box thickness in config: {self.box_thickness}')
            self.box_thickness = 2
            changed = True

        if not isinstance(self.text_size, float) and self.text_size < 0:
            logging.warning(f'Invalid video text size in config: {self.text_size}')
            self.text_size = 1.5
            changed = True

        if not isinstance(self.box_color_per_class, bool):
            logging.warning(f'Invalid box color per class in config: {self.box_color_per_class}')
            self.color_per_class = False
            changed = True

        if not isinstance(self.segment_color_per_class, bool):
            logging.warning(f'Invalid segment color per class in config: {self.segment_color_per_class}')
            self.segment_color_per_class = False
            changed = True

        return changed

    @staticmethod
    def _check_color(color) -> bool:
        if not isinstance(color, list):
            return False

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

        with open(self.path, 'w') as f:
            data = self.__dict__.copy()
            del data['path']
            json.dump(data, f, indent=4)

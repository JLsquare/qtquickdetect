import logging
import json
import re
from pathlib import Path
from ..utils import filepaths

# Regular expression to validate device strings
DEVICE_VALIDATION_REGEX = re.compile(r'^(cpu|cuda)(:\d+)?$')


class Preset:
    """
    Preset is responsible for managing configuration presets for the application.
    It handles reading from and writing to a JSON config file, ensuring the config values
    are valid, and providing default values if needed.
    """

    def __init__(self, preset_name: str):
        """
        Initializes the Preset instance, setting default values and loading
        configuration from the config file if it exists. Creates a config file
        with default values if it doesn't exist.

        :param preset_name: The name of the preset.
        """
        self.device: str = 'cpu'
        self.half_precision: bool = False
        self.iou_threshold: float = 0.7

        self.image_format: str = 'png'
        self.video_format: str = 'mp4'

        self.box_color: tuple[int, int, int, int] = (0, 255, 0, 255)
        self.box_color_per_class: bool = True
        self.box_thickness: int = 2

        self.segment_color: tuple[int, int, int, int] = (0, 255, 0, 255)
        self.segment_color_per_class: bool = True
        self.segment_thickness: int = 2

        self.pose_head_color: tuple[int, int, int, int] = (0, 255, 0, 255)
        self.pose_chest_color: tuple[int, int, int, int] = (0, 255, 0, 255)
        self.pose_leg_color: tuple[int, int, int, int] = (0, 255, 0, 255)
        self.pose_arm_color: tuple[int, int, int, int] = (0, 255, 0, 255)
        self.pose_point_size: int = 3
        self.pose_line_thickness: int = 2

        self.text_color: tuple[int, int, int, int] = (0, 0, 0, 255)
        self.text_size: float = 1.5

        self.path: Path = filepaths.get_base_data_dir() / 'presets' / preset_name

        if self.path.exists():
            self._read_config()
        else:
            self.save()

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
                        self.__dict__[key] = config[key]
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
            logging.warning(f'Invalid box color in config: {self.box_color}')
            self.box_color = (0, 255, 0, 255)
            changed = True

        if not isinstance(self.box_color_per_class, bool):
            logging.warning(f'Invalid box color per class in config: {self.box_color_per_class}')
            self.box_color_per_class = True
            changed = True

        if not isinstance(self.box_thickness, int) or self.box_thickness < 0:
            logging.warning(f'Invalid box thickness in config: {self.box_thickness}')
            self.box_thickness = 2
            changed = True

        if not self._check_color(self.segment_color):
            logging.warning(f'Invalid segment color in config: {self.segment_color}')
            self.segment_color = (0, 255, 0, 255)
            changed = True

        if not isinstance(self.segment_color_per_class, bool):
            logging.warning(f'Invalid segment color per class in config: {self.segment_color_per_class}')
            self.segment_color_per_class = True
            changed = True

        if not isinstance(self.segment_thickness, int) or self.segment_thickness < 0:
            logging.warning(f'Invalid segment thickness in config: {self.segment_thickness}')
            self.segment_thickness = 2
            changed = True

        if not self._check_color(self.pose_head_color):
            logging.warning(f'Invalid pose head color in config: {self.pose_head_color}')
            self.pose_head_color = (0, 255, 0, 255)
            changed = True

        if not self._check_color(self.pose_chest_color):
            logging.warning(f'Invalid pose chest color in config: {self.pose_chest_color}')
            self.pose_chest_color = (0, 255, 0, 255)
            changed = True

        if not self._check_color(self.pose_leg_color):
            logging.warning(f'Invalid pose leg color in config: {self.pose_leg_color}')
            self.pose_leg_color = (0, 255, 0, 255)
            changed = True

        if not self._check_color(self.pose_arm_color):
            logging.warning(f'Invalid pose arm color in config: {self.pose_arm_color}')
            self.pose_arm_color = (0, 255, 0, 255)
            changed = True

        if not isinstance(self.pose_point_size, int) or self.pose_point_size < 0:
            logging.warning(f'Invalid pose point size in config: {self.pose_point_size}')
            self.pose_point_size = 3
            changed = True

        if not isinstance(self.pose_line_thickness, int) or self.pose_line_thickness < 0:
            logging.warning(f'Invalid pose line thickness in config: {self.pose_line_thickness}')
            self.pose_line_thickness = 2
            changed = True

        if not self._check_color(self.text_color):
            logging.warning(f'Invalid text color in config: {self.text_color}')
            self.text_color = (0, 0, 0, 255)
            changed = True

        if not isinstance(self.text_size, float) or self.text_size < 0:
            logging.warning(f'Invalid text size in config: {self.text_size}')
            self.text_size = 1.5
            changed = True

        return changed

    @staticmethod
    def _check_color(color: tuple) -> bool:
        """
        Validates a color tuple to ensure it has four integer elements between 0 and 255.

        :param color: The color tuple to check.
        :return: True if the color is valid, False otherwise.
        """
        if len(color) != 4:
            return False

        for c in color:
            if not (0 <= c <= 255):
                return False

        return True

    def save(self) -> None:
        """
        Writes the current preset configuration to the config file.
        """
        self._revert_invalid()

        with open(self.path, 'w') as f:
            data = self.__dict__.copy()
            del data['path']  # Remove path from data as it should not be saved in the config
            json.dump(data, f, indent=4)

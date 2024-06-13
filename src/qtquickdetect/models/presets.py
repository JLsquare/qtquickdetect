import os
import utils.filepaths as filepaths
from models.preset import Preset


class Presets:
    def __init__(self):
        if not os.path.exists(os.path.join(filepaths.get_base_data_dir(), 'presets')):
            os.mkdir(os.path.join(filepaths.get_base_data_dir(), 'presets'))
        if not os.path.exists(os.path.join(filepaths.get_base_data_dir(), 'presets', 'default.json')):
            Preset('default.json')

    @staticmethod
    def get_presets():
        """
        Get the names of the presets.
        """

        return os.listdir(os.path.join(filepaths.get_base_data_dir(), 'presets'))

    @staticmethod
    def get_preset(preset_name: str):
        """
        Get the path of the preset.

        :param preset_name: Name of the preset.
        """

        return Preset(preset_name)

    @staticmethod
    def create_preset(preset_name: str):
        """
        Create a new preset.

        :param preset_name: Name of the preset.
        """

        if os.path.exists(os.path.join(filepaths.get_base_data_dir(), 'presets', preset_name)):
            raise FileExistsError(f'Preset {preset_name} already exists!')
        Preset(preset_name)

    @staticmethod
    def change_preset_name(preset_name: str, preset_new_name: str):
        """
        Change the name of the preset.

        :param preset_name: Name of the preset.
        :param preset_new_name: New name of the preset.
        """

        old_preset = os.path.join(filepaths.get_base_data_dir(), 'presets', preset_name)
        new_preset = os.path.join(filepaths.get_base_data_dir(), 'presets', preset_new_name)
        os.rename(old_preset, new_preset)

    @staticmethod
    def delete_preset(preset_name: str):
        """
        Delete the preset.

        :param preset_name: Name of the preset.
        """

        os.remove(os.path.join(filepaths.get_base_data_dir(), 'presets', preset_name))
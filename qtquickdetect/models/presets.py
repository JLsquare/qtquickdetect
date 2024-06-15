from ..utils import filepaths
from .preset import Preset


class Presets:
    """
    Presets is responsible for managing configuration presets for the application.
    It provides methods to create, retrieve, rename, and delete presets.
    """

    def __init__(self):
        """
        Initializes the Presets instance by ensuring the necessary directory
        structure exists for storing presets and creating a default preset if it doesn't exist.
        """
        presets_dir = filepaths.get_base_data_dir() / 'presets'
        presets_dir.mkdir(exist_ok=True)
        default_preset = presets_dir / 'default.json'
        if not default_preset.exists():
            Preset('default.json')

    @staticmethod
    def get_presets() -> list[str]:
        """
        Get the names of the presets.

        :return: List of preset names.
        """
        presets_dir = filepaths.get_base_data_dir() / 'presets'
        return [preset.name for preset in presets_dir.iterdir()]

    @staticmethod
    def get_preset(preset_name: str) -> Preset:
        """
        Get the specified preset.

        :param preset_name: Name of the preset.
        :return: Preset instance.
        """
        return Preset(preset_name)

    @staticmethod
    def create_preset(preset_name: str) -> None:
        """
        Create a new preset.

        :param preset_name: Name of the preset.
        :raises FileExistsError: If the preset already exists.
        """
        preset_path = filepaths.get_base_data_dir() / 'presets' / preset_name
        if preset_path.exists():
            raise FileExistsError(f'Preset {preset_name} already exists!')
        Preset(preset_name)

    @staticmethod
    def change_preset_name(preset_name: str, preset_new_name: str) -> None:
        """
        Change the name of the preset.

        :param preset_name: Name of the preset.
        :param preset_new_name: New name of the preset.
        """
        old_preset = filepaths.get_base_data_dir() / 'presets' / preset_name
        new_preset = filepaths.get_base_data_dir() / 'presets' / preset_new_name
        old_preset.rename(new_preset)

    @staticmethod
    def delete_preset(preset_name: str) -> None:
        """
        Delete the preset.

        :param preset_name: Name of the preset.
        """
        (filepaths.get_base_data_dir() / 'presets' / preset_name).unlink()

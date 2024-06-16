import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from qtquickdetect.models.preset import Preset  # Adjust the import according to your actual module structure
from qtquickdetect.models.presets import Presets  # Adjust the import according to your actual module structure
from qtquickdetect.utils import filepaths  # Adjust the import according to your actual module structure


@pytest.fixture
def mock_filepaths(tmp_path):
    """
    Fixture to mock filepaths used in Presets.
    """
    mock_filepaths = MagicMock()
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    mock_filepaths.get_base_data_dir.return_value = data_dir
    yield mock_filepaths


@pytest.fixture
def setup_presets(mock_filepaths, monkeypatch):
    monkeypatch.setattr(filepaths, 'get_base_data_dir', mock_filepaths.get_base_data_dir)
    Presets()


def test_initialization_creates_default_preset(mock_filepaths, setup_presets):
    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / 'default.json'
    assert preset_path.exists()


def test_get_presets(mock_filepaths, setup_presets):
    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / 'default.json'
    preset_path.touch()

    presets = Presets.get_presets()

    assert 'default.json' in presets


def test_create_preset(mock_filepaths, setup_presets):
    preset_name = "new_preset.json"
    Presets.create_preset(preset_name)

    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / preset_name
    assert preset_path.exists()


def test_create_existing_preset_raises_error(mock_filepaths, setup_presets):
    preset_name = "existing_preset.json"
    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / preset_name
    preset_path.touch()

    with pytest.raises(FileExistsError):
        Presets.create_preset(preset_name)


def test_change_preset_name(mock_filepaths, setup_presets):
    preset_name = "old_preset.json"
    new_preset_name = "new_preset.json"
    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / preset_name
    preset_path.touch()

    Presets.change_preset_name(preset_name, new_preset_name)

    new_preset_path = mock_filepaths.get_base_data_dir() / 'presets' / new_preset_name
    assert new_preset_path.exists()
    assert not preset_path.exists()


def test_delete_preset(mock_filepaths, setup_presets):
    preset_name = "delete_preset.json"
    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / preset_name
    preset_path.touch()

    Presets.delete_preset(preset_name)

    assert not preset_path.exists()


def test_get_preset(mock_filepaths, setup_presets):
    preset_name = "default.json"
    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / preset_name
    preset_path.touch()

    preset = Presets.get_preset(preset_name)

    assert isinstance(preset, Preset)

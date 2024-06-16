import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from qtquickdetect.models.preset import Preset  # Adjust the import according to your actual module structure
from qtquickdetect.utils import filepaths  # Adjust the import according to your actual module structure

@pytest.fixture
def mock_filepaths(tmp_path):
    """
    Fixture to mock filepaths used in Preset.
    """
    mock_filepaths = MagicMock()
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    mock_filepaths.get_base_data_dir.return_value = data_dir
    yield mock_filepaths

@pytest.fixture
def preset_name():
    return "default_preset.json"

def test_initialization_creates_default_preset(mock_filepaths, preset_name, monkeypatch):
    monkeypatch.setattr(filepaths, 'get_base_data_dir', mock_filepaths.get_base_data_dir)

    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / preset_name
    assert not preset_path.exists()

    # Ensure directory structure exists
    preset_path.parent.mkdir(parents=True, exist_ok=True)

    preset = Preset(preset_name)

    assert preset_path.exists()
    assert preset.device == 'cpu'
    assert preset.half_precision is False
    assert preset.iou_threshold == 0.7

def test_reading_existing_preset(mock_filepaths, preset_name, monkeypatch):
    monkeypatch.setattr(filepaths, 'get_base_data_dir', mock_filepaths.get_base_data_dir)

    existing_preset = {
        "device": "cuda:0",
        "half_precision": True,
        "iou_threshold": 0.5
    }
    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / preset_name
    preset_path.parent.mkdir(parents=True, exist_ok=True)
    with open(preset_path, 'w') as f:
        json.dump(existing_preset, f)

    preset = Preset(preset_name)

    assert preset.device == 'cuda:0'
    assert preset.half_precision is True
    assert preset.iou_threshold == 0.5

def test_reverting_invalid_values(mock_filepaths, preset_name, monkeypatch):
    monkeypatch.setattr(filepaths, 'get_base_data_dir', mock_filepaths.get_base_data_dir)

    invalid_preset = {
        "device": "invalid_device",
        "half_precision": "not_a_bool",
        "iou_threshold": 2.0
    }
    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / preset_name
    preset_path.parent.mkdir(parents=True, exist_ok=True)
    with open(preset_path, 'w') as f:
        json.dump(invalid_preset, f)

    preset = Preset(preset_name)

    assert preset.device == 'cpu'  # Should revert to default
    assert preset.half_precision is False  # Should revert to default
    assert preset.iou_threshold == 0.7  # Should revert to default

def test_save_preset(mock_filepaths, preset_name, monkeypatch):
    monkeypatch.setattr(filepaths, 'get_base_data_dir', mock_filepaths.get_base_data_dir)

    # Ensure directory structure exists
    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / preset_name
    preset_path.parent.mkdir(parents=True, exist_ok=True)

    preset = Preset(preset_name)
    preset.device = "cuda:0"
    preset.half_precision = True
    preset.iou_threshold = 0.5
    preset.save()

    with open(preset_path, 'r') as f:
        saved_preset = json.load(f)

    assert saved_preset["device"] == "cuda:0"
    assert saved_preset["half_precision"] is True
    assert saved_preset["iou_threshold"] == 0.5

def test_invalid_color_reverts_to_default(mock_filepaths, preset_name, monkeypatch):
    monkeypatch.setattr(filepaths, 'get_base_data_dir', mock_filepaths.get_base_data_dir)

    invalid_preset = {
        "box_color": (300, -20, 1000, 0)
    }
    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / preset_name
    preset_path.parent.mkdir(parents=True, exist_ok=True)
    with open(preset_path, 'w') as f:
        json.dump(invalid_preset, f)

    preset = Preset(preset_name)

    assert preset.box_color == (0, 255, 0, 255)  # Should revert to default

def test_invalid_image_format_reverts_to_default(mock_filepaths, preset_name, monkeypatch):
    monkeypatch.setattr(filepaths, 'get_base_data_dir', mock_filepaths.get_base_data_dir)

    invalid_preset = {
        "image_format": "bmp"
    }
    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / preset_name
    preset_path.parent.mkdir(parents=True, exist_ok=True)
    with open(preset_path, 'w') as f:
        json.dump(invalid_preset, f)

    preset = Preset(preset_name)

    assert preset.image_format == "png"  # Should revert to default

def test_invalid_video_format_reverts_to_default(mock_filepaths, preset_name, monkeypatch):
    monkeypatch.setattr(filepaths, 'get_base_data_dir', mock_filepaths.get_base_data_dir)

    invalid_preset = {
        "video_format": "mov"
    }
    preset_path = mock_filepaths.get_base_data_dir() / 'presets' / preset_name
    preset_path.parent.mkdir(parents=True, exist_ok=True)
    with open(preset_path, 'w') as f:
        json.dump(invalid_preset, f)

    preset = Preset(preset_name)

    assert preset.video_format == "mp4"  # Should revert to default

import json
import shutil
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from qtquickdetect.models.app_config import AppConfig  # Adjust the import according to your actual module structure
from qtquickdetect.utils import filepaths  # Adjust the import according to your actual module structure


@pytest.fixture
def mock_filepaths(tmp_path):
    """
    Fixture to mock filepaths used in AppConfig.
    """
    mock_filepaths = MagicMock()
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    mock_filepaths.get_base_config_dir.return_value = config_dir
    mock_filepaths.get_app_dir.return_value = tmp_path
    yield mock_filepaths


def test_initialization_creates_default_config(mock_filepaths, monkeypatch):
    monkeypatch.setattr(filepaths, 'create_config_dir', mock_filepaths.create_config_dir)
    monkeypatch.setattr(filepaths, 'get_base_config_dir', mock_filepaths.get_base_config_dir)
    monkeypatch.setattr(filepaths, 'get_app_dir', mock_filepaths.get_app_dir)

    default_config_path = mock_filepaths.get_app_dir() / 'resources' / 'default_app_config.json'
    default_config_content = {
        "localization": "en",
        "qss": "dark",
        "pipelines": {},
        "models": {}
    }
    default_config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(default_config_path, 'w') as f:
        json.dump(default_config_content, f)

    app_config = AppConfig()

    assert app_config.localization == 'en'
    assert app_config.qss == 'dark'
    assert app_config.pipelines == {}
    assert app_config.models == {}

    config_path = mock_filepaths.get_base_config_dir() / 'app_config.json'
    assert config_path.exists()


def test_reading_existing_config(mock_filepaths, monkeypatch):
    monkeypatch.setattr(filepaths, 'create_config_dir', mock_filepaths.create_config_dir)
    monkeypatch.setattr(filepaths, 'get_base_config_dir', mock_filepaths.get_base_config_dir)

    existing_config = {
        "localization": "fr",
        "qss": "light",
        "pipelines": {"example_pipeline": "pipeline_data"},
        "models": {"example_model": "model_data"}
    }
    config_path = mock_filepaths.get_base_config_dir() / 'app_config.json'
    with open(config_path, 'w') as f:
        json.dump(existing_config, f)

    app_config = AppConfig()

    assert app_config.localization == 'fr'
    assert app_config.qss == 'light'
    assert app_config.pipelines == {"example_pipeline": "pipeline_data"}
    assert app_config.models == {"example_model": "model_data"}


def test_reverting_invalid_values(mock_filepaths, monkeypatch):
    monkeypatch.setattr(filepaths, 'create_config_dir', mock_filepaths.create_config_dir)
    monkeypatch.setattr(filepaths, 'get_base_config_dir', mock_filepaths.get_base_config_dir)

    invalid_config = {
        "localization": "invalid",
        "qss": "invalid",
        "pipelines": {},
        "models": {}
    }
    config_path = mock_filepaths.get_base_config_dir() / 'app_config.json'
    with open(config_path, 'w') as f:
        json.dump(invalid_config, f)

    app_config = AppConfig()

    assert app_config.localization == 'en'  # Should revert to default
    assert app_config.qss == 'dark'  # Should revert to default


def test_save_config(mock_filepaths, monkeypatch):
    monkeypatch.setattr(filepaths, 'create_config_dir', mock_filepaths.create_config_dir)
    monkeypatch.setattr(filepaths, 'get_base_config_dir', mock_filepaths.get_base_config_dir)

    app_config = AppConfig()
    app_config.localization = "fr"
    app_config.qss = "light"
    app_config.save()

    config_path = mock_filepaths.get_base_config_dir() / 'app_config.json'
    with open(config_path, 'r') as f:
        saved_config = json.load(f)

    assert saved_config["localization"] == "fr"
    assert saved_config["qss"] == "light"


def test_config_directory_is_not_file(mock_filepaths, monkeypatch):
    monkeypatch.setattr(filepaths, 'create_config_dir', mock_filepaths.create_config_dir)
    monkeypatch.setattr(filepaths, 'get_base_config_dir', mock_filepaths.get_base_config_dir)

    config_path = mock_filepaths.get_base_config_dir() / 'app_config.json'
    config_path.mkdir()

    with pytest.raises(Exception, match='app_config.json is a directory!'):
        AppConfig()

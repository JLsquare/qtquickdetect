import pytest

from unittest.mock import MagicMock, patch, mock_open
from PyQt6.QtWidgets import QApplication
from qtquickdetect.models.app_config import AppConfig
from qtquickdetect.models.collections import Collections
from qtquickdetect.models.presets import Presets
from qtquickdetect.models.app_state import AppState
from qtquickdetect.utils import filepaths

@pytest.fixture
def mock_filepaths(tmp_path):
    """
    Fixture to mock filepaths used in AppState.
    """
    mock_filepaths = MagicMock()
    app_dir = tmp_path / "app"
    resources_dir = app_dir / "resources"
    qss_dir = resources_dir / "qss"
    locales_dir = resources_dir / "locales"

    qss_dir.mkdir(parents=True, exist_ok=True)
    locales_dir.mkdir(parents=True, exist_ok=True)

    dark_qss = qss_dir / "dark.qss"
    light_qss = qss_dir / "light.qss"
    dark_qss.touch()
    light_qss.touch()

    mock_filepaths.get_app_dir.return_value = app_dir
    yield mock_filepaths

@pytest.fixture
def setup_app_state(monkeypatch, mock_filepaths):
    monkeypatch.setattr(filepaths, 'get_app_dir', mock_filepaths.get_app_dir)

    # Create a mock AppConfig with necessary attributes
    mock_app_config = MagicMock(spec=AppConfig)
    mock_app_config.qss = 'dark'
    mock_app_config.localization = 'en'
    mock_app_config.save = MagicMock()
    mock_app_config.models = {}  # Ensure models attribute exists

    # Patch AppConfig.__init__ to do nothing and then set attributes
    def mock_app_config_init(self):
        self.qss = mock_app_config.qss
        self.localization = mock_app_config.localization
        self.save = mock_app_config.save
        self.models = mock_app_config.models

    monkeypatch.setattr(AppConfig, '__init__', mock_app_config_init)

    monkeypatch.setattr(Collections, '__init__', lambda self: None)
    monkeypatch.setattr(Presets, '__init__', lambda self: None)
    AppState._instance = None  # Reset singleton instance before each test

    app_state = AppState.get_instance()
    app_state.app_config = mock_app_config  # Ensure the mock is used
    return app_state

def test_singleton_behavior(setup_app_state):
    app_state1 = AppState.get_instance()
    app_state2 = AppState.get_instance()
    assert app_state1 is app_state2

def test_update_qss_dark_mode(setup_app_state, mock_filepaths):
    app_state = setup_app_state
    app_state.app_config.qss = 'dark'

    with patch("builtins.open", mock_open(read_data="dark qss content")):
        app_state.update_qss()

    assert app_state.qss == "dark qss content"

def test_update_qss_light_mode(setup_app_state, mock_filepaths):
    app_state = setup_app_state
    app_state.app_config.qss = 'light'

    with patch("builtins.open", mock_open(read_data="light qss content")):
        app_state.update_qss()

    assert app_state.qss == "light qss content"

def test_update_qss_no_mode(setup_app_state):
    app_state = setup_app_state
    app_state.app_config.qss = 'none'
    app_state.update_qss()
    assert app_state.qss is None

def test_update_localization_fr(setup_app_state, mock_filepaths):
    app_state = setup_app_state
    app_state.app_config.localization = 'fr'
    app_state.app = MagicMock(spec=QApplication)

    translator = MagicMock()
    with patch('qtquickdetect.models.app_state.QTranslator', return_value=translator):
        app_state.update_localization()

    translator.load.assert_called_once_with('fr.qm', str(mock_filepaths.get_app_dir() / 'resources' / 'locales'))
    app_state.app.installTranslator.assert_called_once_with(translator)

def test_update_localization_en(setup_app_state):
    app_state = setup_app_state
    app_state.app_config.localization = 'en'
    app_state.app = MagicMock(spec=QApplication)
    app_state._translator = MagicMock()

    app_state.update_localization()
    app_state.app.removeTranslator.assert_called_once_with(app_state._translator)

def test_save(setup_app_state):
    app_state = setup_app_state
    app_state.app_config.save = MagicMock()
    app_state.update_qss = MagicMock()
    app_state.update_localization = MagicMock()

    app_state.save()

    app_state.app_config.save.assert_called_once()
    app_state.update_qss.assert_called_once()
    app_state.update_localization.assert_called_once()

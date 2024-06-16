import pytest
from unittest.mock import patch, MagicMock
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QApplication
from qtquickdetect.views.app_config_widget import AppConfigWidget
from qtquickdetect.models.app_state import AppState
from qtquickdetect.models.app_config import AppConfig


@pytest.fixture
def app_config_widget(qtbot):
    app_state = AppState.get_instance()
    widget = AppConfigWidget()
    qtbot.addWidget(widget)
    return widget


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_initial_state_of_app_config_widget(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.qss = 'dark'
    mock_app_state.app_config.qss = 'dark'
    mock_app_state.app_config.localization = 'en'
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = AppConfigWidget()
    qtbot.addWidget(widget)

    # Check the initial state of QSS combo box
    assert widget._qss_combo.currentText() == 'Dark (default)'
    assert widget._qss_combo.currentData() == 'dark'

    # Check the initial state of localization combo box
    assert widget._local_combo.currentText() == 'English'
    assert widget._local_combo.currentData() == 'en'


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_qss_setting_change(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.qss = 'dark'
    mock_app_state.app_config.qss = 'dark'
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = AppConfigWidget()
    qtbot.addWidget(widget)

    # Change QSS setting
    widget._qss_combo.setCurrentIndex(1)  # Change to 'Light'
    assert widget._qss_combo.currentData() == 'light'
    widget._qss_combo.setCurrentIndex(2)  # Change to 'System'
    assert widget._qss_combo.currentData() == 'sys'


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_local_setting_change(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.app_config.localization = 'en'
    mock_app_state.qss = 'dark'  # Ensure qss is set to a valid string
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = AppConfigWidget()
    qtbot.addWidget(widget)

    # Change localization setting
    widget._local_combo.setCurrentIndex(1)  # Change to 'Français'
    assert widget._local_combo.currentData() == 'fr'
    widget._local_combo.setCurrentIndex(0)  # Change to 'English'
    assert widget._local_combo.currentData() == 'en'


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_save_settings(mock_get_instance, qtbot, monkeypatch):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.qss = 'dark'  # Ensure qss is set to a valid string
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = AppConfigWidget()
    qtbot.addWidget(widget)

    # Mock the QApplication.quit method
    quit_called = False

    def mock_quit():
        nonlocal quit_called
        quit_called = True

    monkeypatch.setattr('PyQt6.QtWidgets.QApplication.quit', mock_quit)

    # Trigger save settings
    qtbot.mouseClick(widget._save_button, Qt.MouseButton.LeftButton)

    # Check that the save method of app_state was called
    mock_app_state.save.assert_called_once()

    # Simulate QMessageBox response for "No"
    QMessageBox.exec = lambda s: QMessageBox.StandardButton.No
    assert not quit_called

    # Simulate QMessageBox response for "Yes"
    QMessageBox.exec = lambda s: QMessageBox.StandardButton.Yes
    qtbot.mouseClick(widget._save_button, Qt.MouseButton.LeftButton)
    assert quit_called


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_cancel_settings(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    original_config = AppConfig()
    original_config.qss = 'dark'
    original_config.localization = 'en'
    mock_app_state.app_config = original_config
    mock_app_state.qss = 'dark'
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = AppConfigWidget()
    qtbot.addWidget(widget)

    # Change settings
    widget._qss_combo.setCurrentIndex(1)  # Change to 'Light'
    widget._local_combo.setCurrentIndex(1)  # Change to 'Français'

    # Trigger cancel settings
    qtbot.mouseClick(widget._cancel_button, Qt.MouseButton.LeftButton)

    # Check that settings are reverted
    assert widget._qss_combo.currentText() == 'Dark (default)'
    assert widget._local_combo.currentText() == 'English'
    assert mock_app_state.app_config.qss == 'dark'
    assert mock_app_state.app_config.localization == 'en'

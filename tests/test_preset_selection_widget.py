import pytest

from unittest.mock import patch, MagicMock
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QSignalSpy
from qtquickdetect.views.preset_selection_widget import PresetSelectionWidget
from qtquickdetect.models.app_state import AppState


@pytest.fixture
def preset_selection_widget(qtbot):
    app_state = AppState.get_instance()
    widget = PresetSelectionWidget()
    qtbot.addWidget(widget)
    return widget


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_initial_state_of_preset_selection_widget(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.presets.get_presets.return_value = ["Preset1", "Preset2"]
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = PresetSelectionWidget()
    qtbot.addWidget(widget)

    # Check that the icon is set
    assert widget._preset_icon.pixmap() is not None

    # Check that the radio buttons are created correctly
    assert len(widget._preset_radio_buttons) == 2
    assert widget._preset_radio_buttons[0].text() == "Preset1"
    assert widget._preset_radio_buttons[1].text() == "Preset2"

    # Check that the description is set correctly
    assert widget._preset_description.text() == "Select a preset"


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_preset_selection_changes_preset_property(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.presets.get_presets.return_value = ["Preset1", "Preset2"]
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = PresetSelectionWidget()
    qtbot.addWidget(widget)

    # Select a preset and check the preset property
    widget._preset_radio_buttons[0].setChecked(True)
    assert widget.preset == "Preset1"

    widget._preset_radio_buttons[1].setChecked(True)
    assert widget.preset == "Preset2"


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_preset_changed_signal_emitted(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.presets.get_presets.return_value = ["Preset1", "Preset2"]
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = PresetSelectionWidget()
    qtbot.addWidget(widget)

    # Connect a signal spy to the preset_changed_signal
    signal_spy = QSignalSpy(widget.preset_changed_signal)

    # Select a preset and check if the signal was emitted
    widget._preset_radio_buttons[0].setChecked(True)
    assert len(signal_spy) == 1

    widget._preset_radio_buttons[1].setChecked(True)
    assert widget._preset_radio_buttons[0].isChecked() is False
    assert len(signal_spy) == 3  # 1 for the selection, 1 for the deselection of the previous selection


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_widget_layout_and_properties(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.presets.get_presets.return_value = ["Preset1", "Preset2"]
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = PresetSelectionWidget()
    qtbot.addWidget(widget)

    # Check layout properties
    assert widget.layout() is widget._preset_layout
    assert widget._preset_layout.count() == 3

    # Check scroll area properties
    assert widget._scroll_area.widget() is widget._preset_radio_widget
    assert widget._scroll_area.widgetResizable()
    assert widget._scroll_area.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded
    assert widget._scroll_area.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff

    # Check description label properties
    assert widget._preset_description.text() == "Select a preset"
    assert widget._preset_description.alignment() == Qt.AlignmentFlag.AlignCenter

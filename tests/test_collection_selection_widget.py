import pytest
from unittest.mock import patch, MagicMock
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QSignalSpy
from qtquickdetect.views.collection_selection_widget import CollectionSelectionWidget
from qtquickdetect.models.app_state import AppState


@pytest.fixture
def collection_selection_widget(qtbot):
    app_state = AppState.get_instance()
    widget = CollectionSelectionWidget(media_type="image")
    qtbot.addWidget(widget)
    return widget


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_initial_state_of_collection_selection_widget(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.collections.get_collections.return_value = ["Collection1", "Collection2"]
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = CollectionSelectionWidget(media_type="image")
    qtbot.addWidget(widget)

    # Check that the icon is set
    assert widget._collection_icon.pixmap() is not None

    # Check that the radio buttons are created correctly
    assert len(widget._collection_radio_buttons) == 2
    assert widget._collection_radio_buttons[0].text() == "Collection1"
    assert widget._collection_radio_buttons[1].text() == "Collection2"

    # Check that the description is set correctly
    assert widget._collection_description.text() == "Select a collection"

@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_collection_selection_changes_collection_property(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.collections.get_collections.return_value = ["Collection1", "Collection2"]
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = CollectionSelectionWidget(media_type="image")
    qtbot.addWidget(widget)

    # Select a collection and check the collection property
    widget._collection_radio_buttons[0].setChecked(True)
    assert widget.collection == "Collection1"

    widget._collection_radio_buttons[1].setChecked(True)
    assert widget.collection == "Collection2"


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_collection_changed_signal_emitted(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.collections.get_collections.return_value = ["Collection1", "Collection2"]
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = CollectionSelectionWidget(media_type="image")
    qtbot.addWidget(widget)

    # Connect a signal spy to the collection_changed_signal
    signal_spy = QSignalSpy(widget.collection_changed_signal)

    # Select a collection and check if the signal was emitted
    widget._collection_radio_buttons[0].setChecked(True)
    assert len(signal_spy) == 1

    widget._collection_radio_buttons[1].setChecked(True)
    assert widget._collection_radio_buttons[0].isChecked() is False
    assert len(signal_spy) == 3  # 1 for the selection, 1 for the deselection of the previous selection

@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_widget_layout_and_properties(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.collections.get_collections.return_value = ["Collection1", "Collection2"]
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = CollectionSelectionWidget(media_type="image")
    qtbot.addWidget(widget)

    # Check layout properties
    assert widget.layout() is widget._collection_layout
    assert widget._collection_layout.count() == 3

    # Check scroll area properties
    assert widget._scroll_area.widget() is widget._collection_radio_widget
    assert widget._scroll_area.widgetResizable()
    assert widget._scroll_area.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded
    assert widget._scroll_area.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff

    # Check description label properties
    assert widget._collection_description.text() == "Select a collection"
    assert widget._collection_description.alignment() == Qt.AlignmentFlag.AlignCenter
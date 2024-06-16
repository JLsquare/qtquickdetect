import pytest
from unittest.mock import patch, MagicMock
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QSignalSpy
from qtquickdetect.views.task_selection_widget import TaskSelectionWidget
from qtquickdetect.models.app_state import AppState


@pytest.fixture
def task_selection_widget(qtbot):
    app_state = AppState.get_instance()
    widget = TaskSelectionWidget()
    qtbot.addWidget(widget)
    return widget


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_initial_state_of_task_selection_widget(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = TaskSelectionWidget()
    qtbot.addWidget(widget)

    # Check that the icon is set
    assert widget._task_icon.pixmap() is not None

    # Check that the radio buttons are created correctly
    assert widget._task_radio_detection.text() == "Detect"
    assert widget._task_radio_segmentation.text() == "Segment"
    assert widget._task_radio_classification.text() == "Classify"
    assert widget._task_radio_posing.text() == "Pose"

    # Check that the description is set correctly
    assert widget._task_description.text() == "Select a task"

    # Check initial task selection
    assert widget.task == "detect"
    assert widget._task_radio_detection.isChecked()


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_task_selection_changes_task_property(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = TaskSelectionWidget()
    qtbot.addWidget(widget)

    # Select different tasks and check the task property
    widget._task_radio_segmentation.setChecked(True)
    assert widget.task == "segment"

    widget._task_radio_classification.setChecked(True)
    assert widget.task == "classify"

    widget._task_radio_posing.setChecked(True)
    assert widget.task == "pose"


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_task_changed_signal_emitted(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = TaskSelectionWidget()
    qtbot.addWidget(widget)

    # Connect a signal spy to the task_changed_signal
    signal_spy = QSignalSpy(widget.task_changed_signal)

    # Select a task and check if the signal was emitted
    widget._task_radio_segmentation.setChecked(True)
    assert len(signal_spy) == 2  # 1 for the selection, 1 for the deselection of the previous selection

    widget._task_radio_classification.setChecked(True)
    assert len(signal_spy) == 4

    widget._task_radio_posing.setChecked(True)
    assert len(signal_spy) == 6


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_widget_layout_and_properties(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = TaskSelectionWidget()
    qtbot.addWidget(widget)

    # Check layout properties
    assert widget.layout() is widget._task_layout
    assert widget._task_layout.count() == 3

    # Check description label properties
    assert widget._task_description.text() == "Select a task"
    assert widget._task_description.alignment() == Qt.AlignmentFlag.AlignCenter

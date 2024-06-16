import pytest
from unittest.mock import patch, MagicMock
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QPushButton
from qtquickdetect.views.inference_widget import InferenceWidget
from qtquickdetect.views.collection_selection_widget import CollectionSelectionWidget
from qtquickdetect.views.models_selection_widget import ModelsSelectionWidget
from qtquickdetect.views.progress_bar_widget import ProgressBarWidget
from qtquickdetect.views.task_selection_widget import TaskSelectionWidget
from qtquickdetect.views.preset_selection_widget import PresetSelectionWidget


@pytest.fixture
def app():
    return QApplication([])


@pytest.fixture
def inference_widget(qtbot):
    widget = InferenceWidget(media_type="image", open_last_inference=lambda: None)
    qtbot.addWidget(widget)
    return widget


def test_initial_state_of_inference_widget(inference_widget):
    assert inference_widget.media_type == "image"
    assert inference_widget.pipeline_manager is None
    assert inference_widget.file_count == 0

    # Check UI components initialization
    assert isinstance(inference_widget._collection, CollectionSelectionWidget)
    assert isinstance(inference_widget._preset, PresetSelectionWidget)
    assert isinstance(inference_widget._task, TaskSelectionWidget)
    assert isinstance(inference_widget._models, ModelsSelectionWidget)
    assert isinstance(inference_widget._progress_bar, ProgressBarWidget)
    assert isinstance(inference_widget._btn_run, QPushButton)
    assert isinstance(inference_widget._btn_cancel, QPushButton)

    # Check initial states of buttons
    assert not inference_widget._btn_run.isEnabled()
    assert not inference_widget._btn_cancel.isEnabled()


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_check_run(mock_get_instance, inference_widget):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_get_instance.return_value = mock_app_state

    # Mock necessary attributes for running the pipeline
    inference_widget._collection.collection = "test_collection"
    inference_widget._task.task = "test_task"
    inference_widget._models.weights = {"test_model": ["weight1"]}

    # Trigger the check_run method
    inference_widget.check_run()

    # Verify the run button is enabled
    assert inference_widget._btn_run.isEnabled()


def test_update_models_task(inference_widget):
    # Mock the task attribute
    inference_widget._task.task = "test_task"

    # Call the update_models_task method
    inference_widget.update_models_task()

    # Verify the task is updated in the models selection widget
    assert inference_widget._models.task == "test_task"


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_run_without_inputs(mock_get_instance, qtbot, inference_widget):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_get_instance.return_value = mock_app_state
    mock_app_state.collections.get_collection_file_paths.return_value = []

    # Mock necessary attributes for running the pipeline
    inference_widget._collection.collection = "test_collection"
    inference_widget._task.task = "test_task"
    inference_widget._models.weights = {"test_model": ["weight1"]}

    # Trigger the run method
    qtbot.mouseClick(inference_widget._btn_run, Qt.MouseButton.LeftButton)

    # Verify the error message is shown and run button is re-enabled
    assert not inference_widget._btn_run.isEnabled()
    assert inference_widget._btn_cancel.isEnabled() is False


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_cancel_current_pipeline(mock_get_instance, qtbot, inference_widget):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_get_instance.return_value = mock_app_state

    # Mock necessary attributes for cancelling the pipeline
    inference_widget.pipeline_manager = MagicMock()

    # Call the cancel_current_pipeline method
    inference_widget.cancel_current_pipeline()

    # Verify the pipeline manager's cancel method is called
    inference_widget.pipeline_manager.request_cancel.assert_called_once()
    assert not inference_widget._btn_cancel.isEnabled()
    assert inference_widget._btn_run.isEnabled()

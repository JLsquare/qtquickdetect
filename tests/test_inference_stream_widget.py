import pytest
from unittest.mock import patch, MagicMock
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLineEdit, QPushButton
from qtquickdetect.views.inference_stream_widget import InferenceStreamWidget
from qtquickdetect.views.stream_widget import StreamWidget
from qtquickdetect.views.models_selection_widget import ModelsSelectionWidget
from qtquickdetect.views.task_selection_widget import TaskSelectionWidget
from qtquickdetect.views.preset_selection_widget import PresetSelectionWidget

@pytest.fixture
def app():
    return QApplication([])

@pytest.fixture
def inference_stream_widget(qtbot):
    widget = InferenceStreamWidget()
    qtbot.addWidget(widget)
    return widget

def test_initial_state_of_inference_stream_widget(inference_stream_widget):
    assert inference_stream_widget.pipeline_manager is None

    # Check UI components initialization
    assert isinstance(inference_stream_widget._url, QLineEdit)
    assert isinstance(inference_stream_widget._preset, PresetSelectionWidget)
    assert isinstance(inference_stream_widget._task, TaskSelectionWidget)
    assert isinstance(inference_stream_widget._models, ModelsSelectionWidget)
    assert isinstance(inference_stream_widget._btn_run, QPushButton)

    # Check initial states of buttons
    assert not inference_stream_widget._btn_run.isEnabled()

def test_check_run(inference_stream_widget):
    assert not inference_stream_widget._btn_run.isEnabled()

    # Mock necessary attributes for running the pipeline
    inference_stream_widget._url.setText("http://example.com/stream")
    inference_stream_widget._preset.preset = "test_preset"
    inference_stream_widget._task.task = "test_task"
    inference_stream_widget._models.weights = {"test_model": ["weight1"]}

    # Trigger the check_run method
    inference_stream_widget.check_run()

    # Verify the run button is enabled
    assert inference_stream_widget._btn_run.isEnabled()

def test_update_models_task(inference_stream_widget):
    # Mock the task attribute
    inference_stream_widget._task.task = "test_task"

    # Call the update_models_task method
    inference_stream_widget.update_models_task()

    # Verify the task is updated in the models selection widget
    assert inference_stream_widget._models.task == "test_task"

# TODO test with url to run

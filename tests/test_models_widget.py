import pytest

from qtquickdetect.views.models_widget import ModelsWidget
from qtquickdetect.models.app_state import AppState
from unittest.mock import patch, MagicMock
from pathlib import Path

@pytest.fixture
def models_widget(qtbot):
    app_state = AppState.get_instance()
    widget = ModelsWidget()
    qtbot.addWidget(widget)
    return widget

@patch('qtquickdetect.utils.filepaths.get_app_dir')
@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_initial_state_of_models_widget(mock_get_instance, mock_get_app_dir, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.app_config.models = {
        'Model1': {
            'pipeline': 'Pipeline1',
            'task': 'Task1',
            'model_builders': {
                'model_builder1': ['weight1.pt', 'weight2.pt']
            }
        },
        'Model2': {
            'pipeline': 'Pipeline2',
            'task': 'Task2',
            'model_builders': {
                'model_builder2': ['weight3.pt']
            }
        }
    }
    mock_get_instance.return_value = mock_app_state

    # Setup the mock for filepaths.get_app_dir
    mock_get_app_dir.return_value = Path('/mock/path')

    # Create the widget
    widget = ModelsWidget()
    qtbot.addWidget(widget)

    # Check that the tree widget is created
    assert widget._tree_widget is not None
    assert widget._tree_widget.columnCount() == 2
    assert widget._tree_widget.topLevelItemCount() == 2

    # Check the contents of the tree widget
    model1_item = widget._tree_widget.topLevelItem(0)
    assert model1_item.text(0) == 'Model1'
    assert model1_item.text(1) == 'Pipeline - Pipeline1, Task - Task1'
    assert model1_item.childCount() == 2

    model_builder1_item = model1_item.child(0)
    weight1_item = model_builder1_item.child(0)
    assert weight1_item.text(0) == 'weight1.pt'
    assert weight1_item.text(1) == 'Not downloaded'  # Mocking file existence not checked yet

    model_builder2_item = model1_item.child(1)
    weight2_item = model_builder2_item.child(0)
    assert weight2_item.text(0) == 'weight2.pt'
    assert weight2_item.text(1) == 'Not downloaded'

    model2_item = widget._tree_widget.topLevelItem(1)
    assert model2_item.text(0) == 'Model2'
    assert model2_item.text(1) == 'Pipeline - Pipeline2, Task - Task2'
    assert model2_item.childCount() == 1

    model_builder3_item = model2_item.child(0)
    weight3_item = model_builder3_item.child(0)
    assert weight3_item.text(0) == 'weight3.pt'
    assert weight3_item.text(1) == 'Not downloaded'

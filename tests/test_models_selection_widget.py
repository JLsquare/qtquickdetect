import pytest

from unittest.mock import patch, MagicMock
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QSignalSpy
from qtquickdetect.views.models_selection_widget import ModelsSelectionWidget
from qtquickdetect.models.app_state import AppState


@pytest.fixture
def models_selection_widget(qtbot):
    app_state = AppState.get_instance()
    widget = ModelsSelectionWidget()
    qtbot.addWidget(widget)
    return widget


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_initial_state_of_models_selection_widget(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.app_config.models = {
        "Model1": {"task": "detect", "model_builders": {"model_builder1": ["weight2"]}},
        "Model2": {"task": "detect", "model_builders": {"model_builder2": ["weight3", "weight4"]}}
    }
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = ModelsSelectionWidget()
    qtbot.addWidget(widget)

    # Check that the icon is set
    assert widget._model_icon.pixmap() is not None

    # Check that the model tree is populated correctly
    assert widget._model_tree.topLevelItemCount() == 2
    model1_item = widget._model_tree.topLevelItem(0)
    model2_item = widget._model_tree.topLevelItem(1)
    assert model1_item.text(0) == "Model1"
    assert model2_item.text(0) == "Model2"
    assert model1_item.childCount() == 1
    assert model2_item.childCount() == 2
    assert model1_item.child(0).text(0) == "model_builder1"
    assert model2_item.child(0).text(0) == "model_builder2"
    assert model2_item.child(1).text(0) == "model_builder2"

    # Check that the description is set correctly
    assert widget._model_description.text() == "Select the models weights"


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_model_selection_changes_weights_property(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.app_config.models = {
        "Model1": {"task": "detect", "model_builders": {"model_builder1": ["weight2"]}},
        "Model2": {"task": "detect", "model_builders": {"model_builder2": ["weight3", "weight4"]}}
    }
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = ModelsSelectionWidget()
    qtbot.addWidget(widget)

    # Select weights and check the weights property
    model1_item = widget._model_tree.topLevelItem(0)
    weight2_item = model1_item.child(0)
    weight2_item.setCheckState(0, Qt.CheckState.Checked)
    assert widget.weights == {"Model1": ["weight2"]}
    weight2_item.setCheckState(0, Qt.CheckState.Unchecked)
    assert widget.weights == {}

    model2_item = widget._model_tree.topLevelItem(1)
    weight3_item = model2_item.child(0)
    weight4_item = model2_item.child(1)
    weight3_item.setCheckState(0, Qt.CheckState.Checked)
    weight4_item.setCheckState(0, Qt.CheckState.Checked)
    assert widget.weights == {"Model2": ["weight3", "weight4"]}
    weight3_item.setCheckState(0, Qt.CheckState.Unchecked)
    assert widget.weights == {"Model2": ["weight4"]}
    weight4_item.setCheckState(0, Qt.CheckState.Unchecked)
    assert widget.weights == {}


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_models_changed_signal_emitted(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.app_config.models = {
        "Model1": {"task": "detect", "model_builders": {"model_builder1": ["weight2"]}},
        "Model2": {"task": "detect", "model_builders": {"model_builder2": ["weight3", "weight4"]}}
    }
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = ModelsSelectionWidget()
    qtbot.addWidget(widget)

    # Connect a signal spy to the models_changed_signal
    signal_spy = QSignalSpy(widget.models_changed_signal)

    # Select a weight and check if the signal was emitted
    model1_item = widget._model_tree.topLevelItem(0)
    weight1_item = model1_item.child(0)
    weight1_item.setCheckState(0, Qt.CheckState.Checked)
    assert len(signal_spy) == 1

    weight1_item.setCheckState(0, Qt.CheckState.Unchecked)
    assert len(signal_spy) == 2


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_widget_layout_and_properties(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.app_config.models = {
        "Model1": {"task": "detect", "model_builders": {"model_builder1": ["weight2"]}},
        "Model2": {"task": "detect", "model_builders": {"model_builder2": ["weight3", "weight4"]}}
    }
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = ModelsSelectionWidget()
    qtbot.addWidget(widget)

    # Check layout properties
    assert widget.layout() is widget._model_layout
    assert widget._model_layout.count() == 3

    # Check tree properties
    assert widget._model_tree.isHeaderHidden() is True
    assert widget._model_tree.columnCount() == 1

    # Check description label properties
    assert widget._model_description.text() == "Select the models weights"
    assert widget._model_description.alignment() == Qt.AlignmentFlag.AlignCenter


@patch('qtquickdetect.models.app_state.AppState.get_instance')
def test_set_task_updates_model_tree(mock_get_instance, qtbot):
    # Setup the mock for app_state
    mock_app_state = MagicMock()
    mock_app_state.get_theme_file_prefix.return_value = "default_"
    mock_app_state.app_config.models = {
        "Model1": {"task": "detect", "model_builders": {"model_builder1": ["weight2"]}},
        "Model2": {"task": "classify", "model_builders": {"model_builder2": ["weight3", "weight4"]}}
    }
    mock_get_instance.return_value = mock_app_state

    # Create the widget
    widget = ModelsSelectionWidget()
    qtbot.addWidget(widget)

    # Check initial state
    assert widget._model_tree.topLevelItemCount() == 1
    assert widget._model_tree.topLevelItem(0).text(0) == "Model1"

    # Change the task to 'classify'
    widget.set_task("classify")
    assert widget._model_tree.topLevelItemCount() == 1
    assert widget._model_tree.topLevelItem(0).text(0) == "Model2"

    # Change the task to 'detect'
    widget.set_task("detect")
    assert widget._model_tree.topLevelItemCount() == 1
    assert widget._model_tree.topLevelItem(0).text(0) == "Model1"

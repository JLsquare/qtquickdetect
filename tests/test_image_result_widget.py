import pytest
from unittest.mock import patch, MagicMock, call
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidgetItem
from qtquickdetect.views.image_result_widget import ImageResultWidget
from qtquickdetect.models.preset import Preset
from pathlib import Path

@pytest.fixture
def image_result_widget(qtbot):
    preset_name = 'dummy_preset'
    preset = Preset(preset_name)
    result_path = Path('/some/fake/path')
    widget = ImageResultWidget(preset, result_path)
    qtbot.addWidget(widget)
    return widget

def test_initial_state_of_image_result_widget(image_result_widget):
    widget = image_result_widget

    # Verify initial state of file select combo box
    assert widget._file_select_combo.count() == 0

    # Verify initial state of model select combo box
    assert widget._model_select_combo.count() == 0

    # Verify initial state of layer list
    assert widget._layer_list.count() == 0

    # Verify initial state of buttons
    assert widget._return_button.text() == 'Return'
    assert widget._open_result_folder_button.text() == 'Open Result Folder'
    assert widget._save_json_button.text() == 'Save JSON'
    assert widget._save_image_button.text() == 'Save Image'

@patch('qtquickdetect.views.image_result_widget.QFileDialog.getSaveFileName')
@patch('qtquickdetect.views.image_result_widget.QMessageBox.critical')
def test_save_image_no_selection(mock_critical, mock_get_save_file_name, image_result_widget, qtbot):
    widget = image_result_widget
    mock_get_save_file_name.return_value = ('/fake/path/image.png', '')

    qtbot.mouseClick(widget._save_image_button, Qt.MouseButton.LeftButton)

    # Verify that an error message is shown when no image is selected
    mock_critical.assert_called_once_with(widget, 'Error', 'No image selected.')

@patch('qtquickdetect.views.image_result_widget.QFileDialog.getSaveFileName')
@patch('qtquickdetect.views.image_result_widget.QMessageBox.critical')
def test_save_json_no_selection(mock_critical, mock_get_save_file_name, image_result_widget, qtbot):
    widget = image_result_widget
    mock_get_save_file_name.return_value = ('/fake/path/data.json', '')

    qtbot.mouseClick(widget._save_json_button, Qt.MouseButton.LeftButton)

    # Verify that an error message is shown when no model is selected
    mock_critical.assert_called_once_with(widget, 'Error', 'No model selected.')

# TODO test with images in input.
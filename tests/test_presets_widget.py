import pytest

from PyQt6.QtCore import Qt
from qtquickdetect.views.presets_widget import PresetsWidget
from qtquickdetect.models.app_state import AppState

@pytest.fixture
def presets_widget(qtbot):
    app_state = AppState.get_instance()
    widget = PresetsWidget(lambda: None)
    qtbot.addWidget(widget)
    return widget

def test_initial_state_of_presets_widget(presets_widget):
    assert presets_widget._preset_list.count() == len(AppState.get_instance().presets.get_presets())
    assert not presets_widget._scroll_area.isVisible()

def test_add_preset(presets_widget, qtbot):
    initial_preset_count = presets_widget._preset_list.count()
    qtbot.mouseClick(presets_widget._add_preset_button, Qt.MouseButton.LeftButton)
    assert presets_widget._preset_list.count() == initial_preset_count + 1
    new_preset_item = presets_widget._preset_list.item(initial_preset_count)
    assert new_preset_item.text().startswith("New Preset")

def test_set_half_precision(presets_widget, qtbot):
    qtbot.mouseClick(presets_widget._add_preset_button, Qt.MouseButton.LeftButton)
    new_preset_item = presets_widget._preset_list.item(0)
    presets_widget._preset_list.setCurrentItem(new_preset_item)
    initial_state = presets_widget._half_precision_checkbox.isChecked()
    presets_widget._half_precision_checkbox.setChecked(not initial_state)
    assert presets_widget.current_preset.half_precision != initial_state


def test_set_iou_threshold(presets_widget, qtbot):
    qtbot.mouseClick(presets_widget._add_preset_button, Qt.MouseButton.LeftButton)
    new_preset_item = presets_widget._preset_list.item(0)
    presets_widget._preset_list.setCurrentItem(new_preset_item)

    initial_iou = presets_widget._iou_slider.value()
    print(f"Initial IOU: {initial_iou}")

    new_iou = (initial_iou + 10) % 100
    presets_widget._iou_slider.setValue(new_iou)
    updated_iou = presets_widget._iou_slider.value()
    print(f"Updated IOU: {updated_iou}")

    assert presets_widget.current_preset.iou_threshold == new_iou / 100.0

def test_set_image_format(presets_widget, qtbot):
    qtbot.mouseClick(presets_widget._add_preset_button, Qt.MouseButton.LeftButton)
    new_preset_item = presets_widget._preset_list.item(0)
    presets_widget._preset_list.setCurrentItem(new_preset_item)
    initial_format = presets_widget._image_format_combo.currentText()
    new_format = "jpg" if initial_format == "png" else "png"
    presets_widget._image_format_combo.setCurrentText(new_format)
    assert presets_widget.current_preset.image_format == new_format

def test_set_video_format(presets_widget, qtbot):
    qtbot.mouseClick(presets_widget._add_preset_button, Qt.MouseButton.LeftButton)
    new_preset_item = presets_widget._preset_list.item(0)
    presets_widget._preset_list.setCurrentItem(new_preset_item)
    initial_format = presets_widget._video_format_combo.currentText()
    new_format = "avi" if initial_format == "mp4" else "mp4"
    presets_widget._video_format_combo.setCurrentText(new_format)
    assert presets_widget.current_preset.video_format == new_format
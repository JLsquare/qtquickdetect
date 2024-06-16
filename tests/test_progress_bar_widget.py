import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from qtquickdetect.views.progress_bar_widget import ProgressBarWidget  # Adjust the import path as necessary


@pytest.fixture
def app():
    return QApplication([])


@pytest.fixture
def progress_bar_widget(qtbot):
    widget = ProgressBarWidget()
    qtbot.addWidget(widget)
    return widget


def test_initial_state_of_progress_bar_widget(progress_bar_widget):
    assert progress_bar_widget.value() == 0
    assert progress_bar_widget.maximum() == 100
    assert progress_bar_widget.minimum() == 0
    assert progress_bar_widget.isTextVisible() is True
    assert progress_bar_widget.format() == '%p%'
    assert progress_bar_widget.alignment() == Qt.AlignmentFlag.AlignCenter


def test_update_progress_bar(progress_bar_widget):
    progress = 50
    total = 100
    extra = 10
    file_name = "test_file.txt"

    progress_bar_widget.update_progress_bar(progress, total, extra, file_name)

    expected_value = int(((progress + extra) / total) * 100)
    assert progress_bar_widget.value() == expected_value
    assert progress_bar_widget.format() == f'{file_name} - %p%'

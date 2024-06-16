import pytest
from PyQt6 import QtCore
from qtquickdetect.views.collections_widget import CollectionsWidget
from qtquickdetect.models.app_state import AppState


@pytest.fixture
def collections_widget(qtbot):
    app_state = AppState.get_instance()
    widget = CollectionsWidget(media_type="image")
    qtbot.addWidget(widget)
    return widget


def test_initial_state_of_collections_widget(collections_widget):
    assert collections_widget._collection_list.count() == len(
        AppState.get_instance().collections.get_collections("image"))
    assert collections_widget._collection_file_list.count() == 0


def test_add_collection(collections_widget, qtbot):
    initial_collection_count = collections_widget._collection_list.count()
    qtbot.mouseClick(collections_widget._add_collection_button, QtCore.Qt.MouseButton.LeftButton)
    assert collections_widget._collection_list.count() == initial_collection_count + 1
    new_collection_item = collections_widget._collection_list.item(initial_collection_count)
    assert new_collection_item.text().startswith("New Collection")


def test_delete_collection(collections_widget, qtbot):
    qtbot.mouseClick(collections_widget._add_collection_button, QtCore.Qt.MouseButton.LeftButton)
    initial_collection_count = collections_widget._collection_list.count()
    collections_widget._collection_list.setCurrentRow(0)
    qtbot.mouseClick(collections_widget._delete_collection_button, QtCore.Qt.MouseButton.LeftButton)
    assert collections_widget._collection_list.count() == initial_collection_count - 1


def test_add_files_to_collection(collections_widget, qtbot, tmp_path):
    # Add a new collection
    qtbot.mouseClick(collections_widget._add_collection_button, QtCore.Qt.MouseButton.LeftButton)
    new_collection_item = collections_widget._collection_list.item(0)
    collections_widget._collection_list.setCurrentItem(new_collection_item)

    # Create temporary files to add
    file_paths = []
    for i in range(3):
        file_path = tmp_path / f"image_{i}.png"
        file_path.touch()
        file_paths.append(file_path)

    collections_widget.process_files(file_paths)
    assert collections_widget._collection_file_list.count() == len(file_paths)


def test_delete_files_from_collection(collections_widget, qtbot, tmp_path):
    # Add a new collection
    qtbot.mouseClick(collections_widget._add_collection_button, QtCore.Qt.MouseButton.LeftButton)
    new_collection_item = collections_widget._collection_list.item(0)
    collections_widget._collection_list.setCurrentItem(new_collection_item)

    # Create temporary files to add
    file_paths = []
    for i in range(3):
        file_path = tmp_path / f"image_{i}.png"
        file_path.touch()
        file_paths.append(file_path)

    collections_widget.process_files(file_paths)
    collections_widget._collection_file_list.setCurrentRow(0)

    initial_file_count = collections_widget._collection_file_list.count()
    qtbot.mouseClick(collections_widget._delete_file_button, QtCore.Qt.MouseButton.LeftButton)
    assert collections_widget._collection_file_list.count() == initial_file_count - 1

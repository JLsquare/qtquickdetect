import shutil
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from qtquickdetect.models.collections import Collections  # Adjust the import according to your actual module structure
from qtquickdetect.utils import filepaths  # Adjust the import according to your actual module structure


@pytest.fixture
def mock_filepaths(tmp_path):
    """
    Fixture to mock filepaths used in Collections.
    """
    mock_filepaths = MagicMock()
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    mock_filepaths.get_base_data_dir.return_value = data_dir
    yield mock_filepaths


@pytest.fixture
def setup_collections(mock_filepaths, monkeypatch):
    monkeypatch.setattr(filepaths, 'get_base_data_dir', mock_filepaths.get_base_data_dir)
    Collections()


def test_create_collection(mock_filepaths, setup_collections):
    collection_name = "new_collection"
    media_type = "image"

    Collections.create_collection(collection_name, media_type)
    collection_path = mock_filepaths.get_base_data_dir() / 'collections' / media_type / collection_name

    assert collection_path.exists()


def test_get_collections(mock_filepaths, setup_collections):
    collection_name = "new_collection"
    media_type = "image"
    collection_path = mock_filepaths.get_base_data_dir() / 'collections' / media_type / collection_name
    collection_path.mkdir()

    collections = Collections.get_collections(media_type)

    assert collection_name in collections


def test_create_existing_collection_raises_error(mock_filepaths, setup_collections):
    collection_name = "new_collection"
    media_type = "image"
    collection_path = mock_filepaths.get_base_data_dir() / 'collections' / media_type / collection_name
    collection_path.mkdir()

    with pytest.raises(FileExistsError):
        Collections.create_collection(collection_name, media_type)


def test_create_collection_invalid_type_raises_error(mock_filepaths, setup_collections):
    with pytest.raises(ValueError):
        Collections.create_collection("new_collection", "invalid_type")


def test_get_collection_file_paths(mock_filepaths, setup_collections):
    collection_name = "new_collection"
    media_type = "image"
    collection_path = mock_filepaths.get_base_data_dir() / 'collections' / media_type / collection_name
    collection_path.mkdir()

    file_path = collection_path / "file.txt"
    file_path.touch()

    files = Collections.get_collection_file_paths(collection_name, media_type)

    assert file_path in files


def test_get_collection_path(mock_filepaths, setup_collections):
    collection_name = "new_collection"
    media_type = "image"
    collection_path = Collections.get_collection_path(collection_name, media_type)

    expected_path = mock_filepaths.get_base_data_dir() / 'collections' / media_type / collection_name

    assert collection_path == expected_path


def test_change_collection_name(mock_filepaths, setup_collections):
    collection_name = "old_collection"
    new_collection_name = "new_collection"
    media_type = "image"
    collection_path = mock_filepaths.get_base_data_dir() / 'collections' / media_type / collection_name
    collection_path.mkdir()

    Collections.change_collection_name(collection_name, new_collection_name, media_type)

    new_collection_path = mock_filepaths.get_base_data_dir() / 'collections' / media_type / new_collection_name

    assert new_collection_path.exists()
    assert not collection_path.exists()


def test_delete_collection(mock_filepaths, setup_collections):
    collection_name = "new_collection"
    media_type = "image"
    collection_path = mock_filepaths.get_base_data_dir() / 'collections' / media_type / collection_name
    collection_path.mkdir()

    Collections.delete_collection(collection_name, media_type)

    assert not collection_path.exists()

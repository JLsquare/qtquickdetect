import shutil

from pathlib import Path
from ..utils import filepaths


class Collections:
    def __init__(self):
        (filepaths.get_base_data_dir() / 'collections').mkdir(exist_ok=True)
        (filepaths.get_base_data_dir() / 'collections' / 'image').mkdir(exist_ok=True)
        (filepaths.get_base_data_dir() / 'collections' / 'video').mkdir(exist_ok=True)

    @staticmethod
    def get_collections(media_type: str) -> list[str]:
        """
        Get the collections of the specified media type.

        :param media_type: Type of the media (video or image).
        :return: List of collection names.
        """
        return [x.name for x in (filepaths.get_base_data_dir() / 'collections' / media_type).iterdir()]

    @staticmethod
    def create_collection(collection_name: str, media_type: str) -> None:
        """
        Create a new collection.

        :param collection_name: Name of the collection.
        :param media_type: Type of the collection (video or image).
        """

        if media_type not in ['video', 'image']:
            raise ValueError('Collection type must be either video or image!')
        if (filepaths.get_base_data_dir() / 'collections' / media_type / collection_name).exists():
            raise FileExistsError(f'Collection {collection_name} already exists!')
        (filepaths.get_base_data_dir() / 'collections' / media_type / collection_name).mkdir(exist_ok=True)


    @staticmethod
    def get_collection_file_paths(collection_name: str, media_type: str) -> list[Path]:
        """
        Get the paths of the files in the collection.

        :param collection_name: Name of the collection.
        :param media_type: Type of the collection (video or image).
        :return: List of file paths.
        """
        return list((filepaths.get_base_data_dir() / 'collections' / media_type / collection_name).iterdir())

    @staticmethod
    def get_collection_path(collection_name: str, media_type: str) -> Path:
        """
        Get the path of the collection.

        :param collection_name: Name of the collection.
        :param media_type: Type of the collection (video or image).
        :return: Path of the collection.
        """
        return filepaths.get_base_data_dir() / 'collections' / media_type / collection_name

    @staticmethod
    def change_collection_name(collection_name: str, collection_new_name: str, media_type: str) -> None:
        """
        Change the name of the collection.

        :param collection_name: Name of the collection.
        :param collection_new_name: New name of the collection.
        :param media_type: Type of the collection (video or image).
        """
        old_collection = filepaths.get_base_data_dir() / 'collections' / media_type / collection_name
        new_collection = filepaths.get_base_data_dir() / 'collections' / media_type / collection_new_name
        old_collection.rename(new_collection)

    @staticmethod
    def delete_collection(collection_name: str, media_type: str) -> None:
        """
        Delete the collection.

        :param collection_name: Name of the collection.
        :param media_type: Type of the collection (video or image).
        """
        shutil.rmtree(filepaths.get_base_data_dir() / 'collections' / media_type / collection_name)

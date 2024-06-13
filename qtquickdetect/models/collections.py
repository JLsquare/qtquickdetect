import os
import shutil

from ..utils import filepaths


def _get_collections_dir() -> str:
    return os.path.join(filepaths.get_base_data_dir(), 'collections')


class Collections:
    def __init__(self):
        if not os.path.exists(_get_collections_dir()):
            os.mkdir(_get_collections_dir())
        if not os.path.exists(os.path.join(_get_collections_dir(), 'image')):
            os.mkdir(os.path.join(_get_collections_dir(), 'image'))
        if not os.path.exists(os.path.join(_get_collections_dir(), 'video')):
            os.mkdir(os.path.join(_get_collections_dir(), 'video'))

    @staticmethod
    def get_collections(media_type: str):
        """
        Get the collections of the specified media type.

        :param media_type: Type of the media (video or image).
        """
        return os.listdir(os.path.join(_get_collections_dir(), media_type))

    @staticmethod
    def create_collection(collection_name: str, media_type: str):
        """
        Create a new collection.

        :param collection_name: Name of the collection.
        :param media_type: Type of the collection (video or image).
        """

        if media_type not in ['video', 'image']:
            raise ValueError('Collection type must be either video or image!')
        if os.path.exists(os.path.join(_get_collections_dir(), media_type, collection_name)):
            raise FileExistsError(f'Collection {collection_name} already exists!')
        os.mkdir(os.path.join(_get_collections_dir(), media_type, collection_name))


    @staticmethod
    def get_collection_file_paths(collection_name: str, media_type: str):
        """
        Get the paths of the files in the collection.

        :param collection_name: Name of the collection.
        :param media_type: Type of the collection (video or image).
        """

        files = os.listdir(os.path.join(_get_collections_dir(), media_type, collection_name))
        return [os.path.join(_get_collections_dir(), media_type, collection_name, file) for file in files]

    @staticmethod
    def get_collection_path(collection_name: str, media_type: str):
        """
        Get the path of the collection.

        :param collection_name: Name of the collection.
        :param media_type: Type of the collection (video or image).
        """

        return os.path.join(_get_collections_dir(), media_type, collection_name)

    @staticmethod
    def change_collection_name(collection_name: str, collection_new_name: str, media_type: str):
        """
        Change the name of the collection.

        :param collection_name: Name of the collection.
        :param collection_new_name: New name of the collection.
        :param media_type: Type of the collection (video or image).
        """

        original_path = os.path.join(_get_collections_dir(), media_type, collection_name)
        new_path = os.path.join(_get_collections_dir(), media_type, collection_new_name)
        os.rename(original_path, new_path)

    @staticmethod
    def delete_collection(collection_name: str, media_type: str):
        """
        Delete the collection.

        :param collection_name: Name of the collection.
        :param media_type: Type of the collection (video or image).
        """

        shutil.rmtree(os.path.join(_get_collections_dir(), media_type, collection_name))

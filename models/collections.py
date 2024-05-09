import os
import shutil


class Collections:
    def __init__(self):
        if not os.path.exists('collections'):
            os.mkdir('collections')
        if not os.path.exists('collections/image'):
            os.mkdir('collections/image')
        if not os.path.exists('collections/video'):
            os.mkdir('collections/video')

    @staticmethod
    def get_collections(media_type: str):
        """
        Get the collections of the specified media type.

        :param media_type: Type of the media (video or image).
        """
        return os.listdir(f'collections/{media_type}')

    @staticmethod
    def create_collection(collection_name: str, media_type: str):
        """
        Create a new collection.

        :param collection_name: Name of the collection.
        :param media_type: Type of the collection (video or image).
        """
        if media_type not in ['video', 'image']:
            raise ValueError('Collection type must be either video or image!')
        if os.path.exists(f'collections/{media_type}/{collection_name}'):
            raise FileExistsError(f'Collection {collection_name} already exists!')
        os.mkdir(f'collections/{media_type}/{collection_name}')

    @staticmethod
    def get_collection_file_paths(collection_name: str, media_type: str):
        """
        Get the paths of the files in the collection.

        :param collection_name: Name of the collection.
        :param media_type: Type of the collection (video or image).
        """
        return [f'collections/{media_type}/{collection_name}/{file}' for file in os.listdir(f'collections/{media_type}/{collection_name}')]

    @staticmethod
    def get_collection_path(collection_name: str, media_type: str):
        """
        Get the path of the collection.

        :param collection_name: Name of the collection.
        :param media_type: Type of the collection (video or image).
        """
        return os.path.abspath(f'collections/{media_type}/{collection_name}')

    @staticmethod
    def change_collection_name(collection_name: str, collection_new_name: str, media_type: str):
        """
        Change the name of the collection.

        :param collection_name: Name of the collection.
        :param collection_new_name: New name of the collection.
        :param media_type: Type of the collection (video or image).
        """
        os.rename(f'collections/{media_type}/{collection_name}', f'collections/{media_type}/{collection_new_name}')

    @staticmethod
    def delete_collection(collection_name: str, media_type: str):
        """
        Delete the collection.

        :param collection_name: Name of the collection.
        :param media_type: Type of the collection (video or image).
        """
        shutil.rmtree(f'collections/{media_type}/{collection_name}')

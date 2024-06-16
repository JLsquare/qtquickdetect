import os
import sys

from pathlib import Path

TMP_DIR = None

if "pytest" in sys.modules:
    import tempfile

    TMP_DIR = tempfile.TemporaryDirectory()


def get_base_config_dir() -> Path:
    """
    Returns the folder where the config files should reside
    :return: The folder path
    """
    if TMP_DIR:
        return Path(TMP_DIR.name) / 'config'

    if sys.platform == 'win32':
        return Path(os.getenv('APPDATA')) / 'QtQuickDetect'
    elif sys.platform == 'darwin':
        raise Exception('macOS is not supported yet')
    else:
        homedir = os.getenv('HOME')

        if homedir is None:
            raise Exception('Could not find home directory')  # Linux is weird sometimes

        return Path(homedir) / '.config' / 'qtquickdetect'


def create_config_dir() -> None:
    """
    Creates the config directory if it does not exist
    """
    get_base_config_dir().mkdir(exist_ok=True)


# for application state files, such as model weights and user images
def get_base_data_dir() -> Path:
    """
    Returns the folder where the data files should reside
    :return: The folder path
    """
    if TMP_DIR:
        return Path(TMP_DIR.name) / 'data'

    if sys.platform == 'win32':
        return Path(os.getenv('APPDATA')) / 'QtQuickDetect' / 'data'
    elif sys.platform == 'darwin':
        raise Exception('macOS is not supported yet')
    else:
        homedir = os.getenv('HOME')

        if homedir is None:
            raise Exception('Could not find home directory')

        return Path(homedir) / '.local' / 'share' / 'qtquickdetect'


def create_data_dir() -> None:
    """
    Creates the filesystem tree for the application data if it does not exist
    """
    get_base_data_dir().mkdir(exist_ok=True)

    for subdir in ['weights', 'presets', 'collections']:
        path = get_base_data_dir() / subdir
        path.mkdir(exist_ok=True)


# for temporary files, such as logs and cache
def get_base_cache_dir() -> Path:
    """
    Returns the folder where the cache files should reside
    :return: The folder path
    """
    if TMP_DIR:
        return Path(TMP_DIR.name) / 'cache'

    if sys.platform == 'win32':
        return Path(os.getenv('APPDATA')) / 'QtQuickDetect' / 'cache'
    elif sys.platform == 'darwin':
        raise Exception('macOS is not supported yet')
    else:
        homedir = os.getenv('HOME')

        if homedir is None:
            raise Exception('Could not find home directory')

        return Path(homedir) / '.cache' / 'qtquickdetect'


def create_cache_dir() -> None:
    """
    Creates the cache directory if it does not exist
    """
    get_base_cache_dir().mkdir(exist_ok=True)


# get the path to where the app's code is stored
def get_app_dir() -> Path:
    """
    Returns the folder where the application code is stored
    :return: The folder path
    """
    return Path(__file__).parent.parent


if "pytest" in sys.modules:
    import tempfile

    # run the folder creation functions, as most tests don't go through the main function
    create_config_dir()
    create_data_dir()
    create_cache_dir()

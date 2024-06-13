import os
import sys

def get_base_config_dir() -> str:
    """
    Returns the folder where the config files should reside
    @return: The folder path
    """
    if sys.platform == 'win32':
        return os.path.join(os.getenv('APPDATA'), 'QtQuickDetect')
    elif sys.platform == 'darwin':
        raise Exception('macOS is not supported yet')
    else:
        homedir = os.getenv('HOME')

        if homedir is None:
            raise Exception('Could not find home directory') # Linux is weird sometimes
        
        return os.path.join(homedir, '.config', 'qtquickdetect')
    
def create_config_dir() -> None:
    """
    Creates the config directory if it does not exist
    """
    base_dir = get_base_config_dir()
    
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

# for application state files, such as model weights and user images
def get_base_data_dir() -> str:
    """
    Returns the folder where the data files should reside
    @return: The folder path
    """
    if sys.platform == 'win32':
        return os.path.join(os.getenv('APPDATA'), 'QtQuickDetect', 'data')
    elif sys.platform == 'darwin':
        raise Exception('macOS is not supported yet')
    else:
        homedir = os.getenv('HOME')

        if homedir is None:
            raise Exception('Could not find home directory') 
        
        return os.path.join(homedir, '.local', 'share', 'qtquickdetect')
    
def create_data_dir() -> None:
    """
    Creates the filesystem tree for the application data if it does not exist
    """
    base_dir = get_base_data_dir()

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    for subdir in ['weights', 'presets', 'collections']:
        path = os.path.join(base_dir, subdir)
        if not os.path.exists(path):
            os.mkdir(path)

# for temporary files, such as logs and cache
def get_base_cache_dir() -> str:
    """
    Returns the folder where the cache files should reside
    @return: The folder path
    """
    if sys.platform == 'win32':
        return os.path.join(os.getenv('APPDATA'), 'QtQuickDetect', 'cache')
    elif sys.platform == 'darwin':
        raise Exception('macOS is not supported yet')
    else:
        homedir = os.getenv('HOME')

        if homedir is None:
            raise Exception('Could not find home directory') 
        
        return os.path.join(homedir, '.cache', 'qtquickdetect')
    
def create_cache_dir() -> None:
    """
    Creates the cache directory if it does not exist
    """
    base_dir = get_base_cache_dir()
    
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

# get the path to where the app's code is stored
def get_app_dir() -> str:
    """
    Returns the folder where the application code is stored
    @return: The folder path
    """
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return path
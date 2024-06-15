import logging
import os
import sys
import pathlib

from PyQt6.QtWidgets import QApplication
from .models.app_state import AppState
from .views.main_window import MainWindow
from .utils import filepaths


def main():
    # get path to python package
    package_path = pathlib.Path(__file__).absolute().parent.parent
    os.chdir(package_path)

    # Configure logging
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    # Ensure 'projects' directory exists
    try:
        os.makedirs(os.path.join(filepaths.get_base_data_dir(), 'projects'), exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to create 'projects' directory: {e}")
        sys.exit(1)

    filepaths.create_cache_dir()
    filepaths.create_config_dir()
    filepaths.create_data_dir()

    print("Starting QtQuickDetect")

    # Set up the QApplication
    app = QApplication([])

    # Connect the application's aboutToQuit signal to the AppState's stop_pipelines method
    appstate = AppState.get_instance()
    app.aboutToQuit.connect(appstate.stop_pipelines)
    appstate.set_app(app)

    # Show the main window
    window = MainWindow()
    window.show()

    # Run the application
    return app.exec()

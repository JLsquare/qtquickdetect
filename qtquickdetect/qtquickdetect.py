from PyQt6.QtWidgets import QApplication
from models.app_state import AppState
from views.main_window import MainWindow
import utils.filepaths as filepaths
import logging
import os
import sys


def main():
    # Configure logging
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    # Ensure 'projects' directory exists
    try:
        os.makedirs('projects', exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to create 'projects' directory: {e}")
        sys.exit(1)

    filepaths.create_cache_dir()
    filepaths.create_config_dir()
    filepaths.create_data_dir()

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


if __name__ == "__main__":
    sys.exit(main())

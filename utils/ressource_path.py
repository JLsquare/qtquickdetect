import os
import sys


def get_ressource_path(relative_path: str) -> str:
    """Get the absolute path to a ressource file for pyinstaller compatibility."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, "ressources", relative_path)

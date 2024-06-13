import os
import subprocess
import sys

from pathlib import Path


def open_file_explorer(path: Path) -> None:
    if not path.exists():
        raise Exception(f"Path '{path}' does not exist")

    path = path.resolve()

    if sys.platform.startswith('linux'):
        subprocess.run(['xdg-open', str(path)])
    elif sys.platform == 'darwin':
        subprocess.run(['open', str(path)])
    elif sys.platform == 'win32':
        os.startfile(str(path))
    else:
        raise Exception(f"Platform '{sys.platform}' not supported")
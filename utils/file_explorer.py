import os
import subprocess
import sys


def open_file_explorer(path):
    if not os.path.exists(path):
        raise Exception(f"Path '{path}' does not exist")

    path = os.path.normpath(path)

    if sys.platform.startswith('linux'):
        subprocess.run(['xdg-open', path])
    elif sys.platform == 'darwin':
        subprocess.run(['open', path])
    elif sys.platform == 'win32':
        os.startfile(path)
    else:
        raise Exception(f"Platform '{sys.platform}' not supported")

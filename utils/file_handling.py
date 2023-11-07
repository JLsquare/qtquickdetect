import os
import random


def get_tmp_filepath(ext: str):
    """
    Returns a random filepath in the temporary directory
    :param ext: File extension (with the dot)
    """
    basename = random.randbytes(12).hex()
    return os.path.join('tmp', basename + ext)
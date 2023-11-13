import os


def get_tmp_filepath(ext: str):
    """
    TO BE PHASED OUT (remove when all references are gone)
    """
    raise NotImplementedError 

def new_project(name: str) -> None:
    """
    Creates a new project folder
    :param name: Name of the project
    """

    # TODO: Handle collisions
    os.mkdir(name)



import os
import shutil

"""
SystemManager class to manage system operations.
"""


class SystemManager:
    """
    Deletes directories if they exist.
    """

    @staticmethod
    def clean_directories(dirs):
        for dir_path in dirs:
            if os.path.exists(dir_path):
                print(f"Deleting the directory {dir_path}")
                shutil.rmtree(dir_path)

    """
    Checks if a directory exists.
    """

    @staticmethod
    def directory_exists(dir_path):
        return os.path.exists(dir_path)

import os
import shutil


class SystemManager:
    @staticmethod
    def clean_directories(dirs):
        """
        Supprime les répertoires s'ils existent.
        """
        for dir_path in dirs:
            if os.path.exists(dir_path):
                print(f"Suppression du répertoire {dir_path}")
                shutil.rmtree(dir_path)
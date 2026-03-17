"""Module to copy files from package"""

import os
import yaml
from datetime import date
import json
from typing import Self
from zipfile import ZipFile


import NemAll_Python_AllplanSettings as AllplanSettings

from .yaml_models import AppConfig


class CopyFiles(AppConfig):
    """Class to move plugin files to repected directories."""

    def _get_lib_path(self) -> str:
        """Get path of library folder.

        Returns:
            str: Full path to library folder.
        """

        return f"{self.installation.get_path_function()}Library\\AllepPlugins\\{self.plugin.developer}\\{self.plugin.name}"

    def _make_directory(self, path: str) -> str:
        """Make directory and return its full path

        Args:
            path: path of the directory.

        Returns:
            str: Full path of the newily created folder.
        """

        directory_name = f"{self.plugin.developer}\\{self.plugin.name}"
        full_path      = os.path.join(path, directory_name)
        
        os.makedirs(full_path, exist_ok = True)
        return full_path

    def move_files(self, path_to_allep: str):
        """Move files to respective folders.

        Args:
            path_to_allep: Path to folder.
        """

        folders = {
            "library": "Library",
            "pythonpart_scripts": "PythonPartsScripts",
            "actionbar": "PythonPartsActionbar",
        }

        with ZipFile(path_to_allep, "r") as package:
            path = self.installation.get_path_function()
            for x, info in package.NameToInfo.items():
                if (x.count("/") < 2 and x[-1] == "/") or x.endswith(".yml"):
                    continue

                attr = x.split("/")[0]

                for key, value in folders.items():
                    directory_name = None
                    if attr == getattr(self.installation, key, None):
                        directory_name = value
                        break

                if not directory_name:
                    continue

                folder       = "AllepPlugins"
                library      = f"{path}{directory_name}\\{folder}"


                directory_path = self._make_directory(library)
                info.filename  = "/".join(info.filename.split("/")[1:])
                package.extract(member = info, path = directory_path)

            if self.installation.py_packages:
                lib_path = self._get_lib_path()
                package.extract(self.installation.py_packages, path = lib_path)

    @classmethod
    def create(cls, path_to_allp: str) -> Self:
        """Helper function to create class Instance.

        Args:
            path_to_allp: Path to allep folder.
        Returns:
            CopyFiles: Instance of Copy File.
        """

        with ZipFile(path_to_allp) as package:
            with package.open("install-config.yml", "r") as file:
                config_data = yaml.safe_load(file)
                return cls.model_validate(config_data)

    def create_manifest_file(self) -> None:
        """ Create manifest file for Plugins"""

        path        = self.installation.get_path_function()
        folder_name = f"{path}AllepPlugins"
        file_path   = f"{folder_name}\\manifests.json"
        plugin_data = {
            "pluginName": self.plugin.name,
            "developerName": self.plugin.developer,
            "createdOn": str(date.today())
        }

        if not os.path.exists(file_path):
            os.makedirs(f"{folder_name}")

            with open(file_path, "w", encoding = "UTF-8") as file:
                json.dump({"plugins": [plugin_data]}, file)
        else:
            new_plugin = True

            with open(file_path, encoding = "UTF-8") as file:
                data = json.load(file)

                for plugin in data["plugins"]:

                    if ( plugin["pluginName"] == self.plugin.name and plugin["developerName"] == self.plugin.developer ):
                        new_plugin = False

            if new_plugin:
                data["plugins"].append(plugin_data)

                with open(file_path, "w", encoding="UTF-8") as file:
                    json.dump(data, file)

        print("Manifest file creation complete.")

if __name__ == "__main__":
    pass

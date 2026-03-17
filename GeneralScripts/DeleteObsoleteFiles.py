"""
Delete the obsolete files
"""

# pylint: disable=bare-except

import glob
import os
import shutil
import traceback

import NemAll_Python_AllplanSettings as AllplanSettings

from FileNameService import FileNameService

def delete_obsolete_files():
    """ Delete the obsolete files """

    try:
        file_name = AllplanSettings.AllplanPaths.GetEtcPath() + "PythonPartsFramework\\FilesToDelete.dat"

        if file_name.find("\\DeliveryData\\") != -1:
            return

        if not os.path.exists(file_name):
            return

        with open(file_name, 'r', encoding = "utf-8") as file:
            for line in file:
                line = line.strip("\n")

                if not line:
                    continue

                parts = line.split(",")

                if len(parts) < 2 or not parts[1].startswith("etc\\"):
                    continue

                del_file_pattern = FileNameService.get_global_standard_path(parts[1])

                if parts[0] == "d":
                    if os.path.exists(del_file_pattern):
                        shutil.rmtree(del_file_pattern)
                else:
                    for del_file_name in glob.glob(del_file_pattern):
                        if os.path.exists(del_file_name):
                            os.remove(del_file_name)

        if os.access(file_name, os.W_OK):
            os.remove(file_name)

    except:
        traceback.print_exc()

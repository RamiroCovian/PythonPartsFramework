""" Script for creation of html documentation files
"""
import sys
import shutil
import os
import pathlib
import pydoc

# pylint: disable=unused-import
# pylint: disable=wrong-import-position

cwd = os.getcwd()
drive = pathlib.Path(cwd).drive

if len(sys.argv) > 1:
    sys.path.append(drive + sys.argv[1])

print(sys.path)


#------------------ get the path names and create the doc folder

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TARGET_DIR = SCRIPT_DIR + '\\InterfaceDoc\\'

HELP_DIR = os.path.dirname(TARGET_DIR)

if not os.path.exists(HELP_DIR):
    os.makedirs(HELP_DIR)


#------------------ create the documentation

for filename in ('NemAll_Python_Geometry',
                 'NemAll_Python_Reinforcement',
                 'NemAll_Python_IFW_ElementAdapter',
                 'NemAll_Python_Palette',
                 'NemAll_Python_Utility',
                 'NemAll_Python_BaseElements',
                 'NemAll_Python_BasisElements',
                 'NemAll_Python_ArchElements',
                 'NemAll_Python_Precast',
                 'NemAll_Python_AllplanSettings',
                 'NemAll_Python_IFW_Input',
                 'builtins'):
    pydoc.writedoc(filename, True)

    path_and_name_old = SCRIPT_DIR +'\\' + filename + '.html'
    path_and_name_new = TARGET_DIR + filename + '.html'

    # if there is already the target file delete it first

    if os.path.isfile(path_and_name_new):
        os.remove(path_and_name_new)

    shutil.move(path_and_name_old, path_and_name_new)

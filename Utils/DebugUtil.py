""" implementation of the debug utilities """

# pylint: disable=too-many-try-statements
# pylint: disable=import-outside-toplevel

import sys

class DebugUtil():
    """ implementation of the debug utilities """

    @staticmethod
    def start_debugger(info_by_msg_box: bool) -> bool:
        """ start the debugger

        Args:
            info_by_msg_box: True = info by message box / False = info by print

        Returns:
            started debugger state
        """

        exe = sys.executable

        try:
            import debugpy

            python_path = ""

            for path in sys.path:
                if path.lower().endswith("\\prg\\python"):
                    python_path = path
                    break

            sys.executable = fr"{python_path}\Python.exe"

            if debugpy.is_client_connected():
                sys.executable = exe
                return False

            if not DebugUtil.__show_info_box(info_by_msg_box):
                sys.executable = exe
                return False

            debugpy.listen(("localhost", 5678))

            debugpy.wait_for_client()

            sys.executable = exe

            return True

        except ImportError:
            import NemAll_Python_Utility as AllplanUtil

            info = "No Python extension for debugging available:\n\n" \
                   "Please install 'debugpy' to the folder ...\\prg\\Python"

            if info_by_msg_box:
                AllplanUtil.ShowMessageBox(info, AllplanUtil.MB_OK)
            else:
                print(info)

            return False


    @staticmethod
    def __show_info_box(info_by_msg_box: bool) -> int:
        """ start the debugger

        Args:
            info_by_msg_box: True = info by message box / False = info by print

        Returns:
            result from the message box
        """

        import NemAll_Python_Utility as AllplanUtil

        info = "Close the info dialog and \n\n" \
               "Visual Studio Code:\n" \
               "    - Select 'Attach to Allplan'\n" \
               "    - Click 'RUN AND DEBUG'\n" \
               "\n" \
               "Visual Studio:\n" \
               "    - Attach to Process\n" \
               "    - Connection type: Python remote (ptvsd)\n" \
               "    - Connection target: localhost:5678\n" \
               "    - Enter\n" \
               "    - Select the Python process"

        if info_by_msg_box:
            return AllplanUtil.ShowMessageBox(info, AllplanUtil.MB_OKCANCEL) == AllplanUtil.IDOK

        print(info)

        return True

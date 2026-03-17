""" implementation of the Allplan path mock.
"""

# pylint: disable=invalid-name

import os
import tempfile
import sys

class AllplanPathsMock():
    """ implementation of the Allplan path moc
    """

    ETC_PATH = "DeliveryData\\etc\\"

    def __init__(self,
                 etc_path: str = "DeliveryData\\etc\\"):
        """ initialize

        Args:
            etc_path: Allplan etc path+
        """

        AllplanPathsMock.ETC_PATH = etc_path


    @staticmethod
    def GetPathOfApplication() -> str:
        """ get the path of the application

        Returns:
            path of the application
        """

        if (path := next((path for path in sys.path if path.find("_CM") != -1), None)) is not None:
            return path

        if (path := next((path for path in sys.path if path.lower().find("prg") != -1 and \
                          "python" not in path.lower()), None)) is not None:                    # pylint: disable=magic-value-comparison
            return path


        #----------------- for test robots

        if (path := next((path for path in sys.path if path.find("BuildOutput") != -1), None)) is None:
            return ""

        if path.endswith("Dll"):
            return path

        ip = path.find("\\Dll\\")

        return path[0: ip + 5]


    @staticmethod
    def GetPythonPartsEtcPath() -> str:
        """ get the etc path

        Returns:
            PythonPart etc path
        """

        return AllplanPathsMock.ETC_PATH


    @staticmethod
    def GetUsrPath() -> str:
        """ get the usr path

        Returns:
            usr path
        """
        return ""


    @staticmethod
    def GetStdPath() -> str:
        """ get the std path

        Returns:
            std path
        """

        return os.getcwd()[:3] + "TestAutomation\\TestSuites\\Allplan\\DATA\\Startdaten\\UnitTests\\std\\"


    @staticmethod
    def GetCurPrjPath() -> str:
        """ get the project path

        Returns:
            current project path
        """

        return tempfile.gettempdir() + "\\"


    @staticmethod
    def GetPrgPath() -> str:
        """ get the program path

        Returns:
            prg path
        """

        return ""


    @staticmethod
    def GetEtcPath() -> str:
        """ get the etc path

        Returns:
            etc path
        """

        return AllplanPathsMock.ETC_PATH

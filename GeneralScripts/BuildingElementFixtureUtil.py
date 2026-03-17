"""
Script for BuildingElementFixtureUtil
"""

import NemAll_Python_Palette as AllplanPalette

class BuildingElementFixtureUtil():
    """
    Definition of class BuildingElementFixtureUtil

    Create the fixture properties from a value string
    """


    @staticmethod
    def get_fixtureprpoperties_from_libraryelement(library_ele):
        """ Get the fixture properties from the library element """

        if library_ele == None:
            return AllplanPalette.FixtureProperties("", "", "")

        props = library_ele.GetProperties()

        return AllplanPalette.FixtureProperties(props.GetPath(), props.GetGroup(), props.GetElement())

    @staticmethod
    def get_fixturesinglepath_from_libraryelement(library_ele):
        """ Get the fixture properties from the library element """

        if library_ele == None:
            return ""

        props = library_ele.GetProperties()

        return props.GetSingleFilePath()

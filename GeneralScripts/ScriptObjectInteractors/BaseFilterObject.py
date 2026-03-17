""" implementation of the base filter object
"""

import abc

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter


class BaseFilterObject():
    """ implementation of the base filter object
    """

    @abc.abstractmethod
    def __call__(self,
                 _element: AllplanEleAdapter.BaseElementAdapter) -> bool:
        """ execute the filtering

        Args:
            _element: element to filter

        Returns:
            element fulfills the filter: True/False
        """

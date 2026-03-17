""" implementation of the PythonPart decorators for the pylint extension
"""

import os

from typing import Callable, Any, cast

class PythonPartPylintDecorator():
    """ implementation of the PythonPart decorators for the pylint extension
    """

    @staticmethod
    def deprecated(replace: str = "") -> Callable:
        """ create the deprecated function decorator

        Args:
            replace: replace information

        Returns:
            function decorator
        """

        def function_decorator(func: Callable) -> Callable:
            """ decorator of the final function

            Args:
                func: function to execute

            Returns:
                decorated function
            """

            show_message = True

            def wrapper(*fct_args   : Any,
                        **fct_kwargs: Any) -> Any:
                """ wrapper function

                Args:
                    *fct_args:    arguments
                    **fct_kwargs: keyword arguments

                Returns:
                    function result
                """

                nonlocal show_message

                if show_message:
                    os.system("color")

                    print()
                    print()
                    print("\033[91mDeprecated: " + func.__qualname__ + " -> " + replace + " \033[00m")
                    print()
                    print()

                    show_message = False

                return cast(Callable, func)(*fct_args, **fct_kwargs)

            return wrapper

        return function_decorator

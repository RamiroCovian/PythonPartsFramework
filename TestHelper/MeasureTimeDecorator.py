""" implementation of the timeit decorator
"""

from typing import Callable, Any, cast

import time

class MeasureTimeDecorator():
    """ implementation of the timeit decorator
    """

    @staticmethod
    def print_time(message: str,
                   repeat : int) -> Callable:
        """ measure time decorator

        Args:
            message: message to print for the time
            repeat:  repeat the test

        Returns:
            decorator function
        """

        def function_decorator(func: Callable) -> Callable:
            """ decorator of the final function

            Args:
                func: function to execute

            Returns:
                decorated function
            """

            def wrapper(*fct_args   : Any,
                        **fct_kwargs: Any) -> Any:
                """ wrapper function

                Args:
                    *fct_args:    arguments
                    **fct_kwargs: keyword arguments

                Returns:
                    function result
                """

                result = None

                for _ in range(repeat):
                    start_time = time.time()

                    result = cast(Callable, func)(*fct_args, **fct_kwargs)

                    end_time = time.time()

                    print()
                    print(message + ":", f'{end_time-start_time:7.3f}s')

                return result

            return wrapper

        return function_decorator

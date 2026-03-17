""" implementation of the profile utilities for the Austin profiler
"""

# pylint: disable=import-error

import os
import codecs

from typing import Any, Dict, Callable, List

import multiprocessing

from austin.simple import SimpleAustin
from austin.stats import AustinStats, InvalidSample, AustinStatsType


class MySimpleAustin(SimpleAustin):
    """ implementation of the simple Austin class
    """

    def __init__(self,
                 austin_running_event: multiprocessing.Event,   # type: ignore
                 test_running_event  : multiprocessing.Event,   # type: ignore
                 terminate_event     : multiprocessing.Event,   # type: ignore
                 process_id          : str,
                 result_file_name    : str):
        """ initialize

        Args:
            austin_running_event: signals the running austin
            test_running_event:   signals the running test
            terminate_event:      signals the profile termination
            process_id:           process ID of the profess to profile
            result_file_name:     name of the result file
        """

        super().__init__()

        self._stats               = AustinStats(AustinStatsType.WALL)
        self._sample_count        = 0
        self._sample_data         = []
        self._error_count         = 0
        self.austin_running_event = austin_running_event
        self.test_running_event   = test_running_event
        self.terminate_event      = terminate_event
        self.process_id           = "P" + process_id
        self.result_file_name     = result_file_name


    def on_ready(self,
                    _process      : Any,
                    _child_process: Any,
                    _command_line : str,
                    _data         : Any = None) -> Any:
        """ function description

        Args:
            _process:       process
            _child_process: child process
            _command_line:  command line
            _data:          data
        """

        self.austin_running_event.set()


    def on_sample_received(self,
                            text: str):
        """ receive the sample result

        Args:
            text: sample result
        """
        try:
            if not self.test_running_event.is_set():
                return

            if not text.startswith(self.process_id):
                return

            self._sample_data.append(text + "\n")

            self._sample_count += 1

            if self.terminate_event.is_set():
                self._running = False           # pylint: disable=attribute-defined-outside-init

        except InvalidSample:
            self._error_count += 1


    def on_terminate(self,
                        _stats: Dict[str, str]):
        """ terminate the profiling

        Args:
            _stats: stats
        """

        cwd = os.getcwd()

        old_path = "\\DeliveryData\\"
        new_path = cwd[:2] + "\\DeliveryData\\"

        with codecs.open(cwd + "\\" + self.result_file_name + ".aprof", "w", encoding = "UTF-8") as file:
            for line in self._sample_data:
                file.write(line.replace(old_path, new_path))

        self.proc.returncode = 0


#----------------- create the Austin process

def austin_process(austin_running_event: multiprocessing.Event,   # type: ignore
                   test_running_event  : multiprocessing.Event,   # type: ignore
                   terminate_event     : multiprocessing.Event,   # type: ignore
                   finish_event        : multiprocessing.Event,   # type: ignore
                   process_id          : str,
                   result_file_name    : str):
    """ start the Austin process

    Args:
        austin_running_event: signals the running austin
        test_running_event:   signals the running test
        terminate_event:      signals the profile termination
        finish_event:         signals the profile thread finish
        process_id:           process id to profile
        result_file_name:     name of the result file
    """

    MySimpleAustin(austin_running_event, test_running_event, terminate_event, process_id, result_file_name).start(["-Cp", process_id])

    finish_event.set()


def profile_by_austin(result_file_name: str,
                      function        : Callable,
                      *param          : List[Any]):
    """ profile by Austin profiler

    Args:
        result_file_name: name of the result file
        function:         function to execute
        *param:           function parameter
    """

    austin_running_event = multiprocessing.Event()
    test_running_event   = multiprocessing.Event()
    terminate_event      = multiprocessing.Event()
    finish_event         = multiprocessing.Event()

    austin_proc = multiprocessing.Process(target = austin_process,
                                            args = (austin_running_event, test_running_event,
                                                    terminate_event, finish_event, str(os.getpid()), result_file_name,))

    austin_proc.start()

    austin_running_event.wait()

    test_running_event.set()

    if param:
        ret_value = function(*param)
    else:
        ret_value = function()

    terminate_event.set()

    finish_event.wait()

    return ret_value

""" implementation of the base custom checker
"""

from astroid import nodes

from pylint.checkers import BaseChecker

COMMA = ","

class BaseCustomChecker(BaseChecker):
    """ implementation of the base custom checker
    """

    __lines: list[str] = []

    def visit_module(self,
                     node: nodes.Module):
        """ visit the module

        Args:
            node: node of the module
        """

        self.__lines = [str(line, "UTF-8") for line in node.stream().readlines()]


    def _get_current_line(self,
                          node: nodes.ALL_NODE_CLASSES) -> str:
        """ get the current line

        Returns:
            current line
        """

        full_line = ""

        for line in self.__lines[node.fromlineno - 1: node.tolineno]:
            line = line.strip("\r\n\\ ")

            full_line += line

            if not line.endswith("\\"):
                return full_line

    @staticmethod
    def split_by_comma(text: str) -> list[str]:
        """ split the text by a comma, check for comma in quotes or brackets

        Args:
            text: text

        Returns:
            pars of the splitted text
        """

        if COMMA not in text:
            return [text]

        in_quotes   = False
        in_brackets = 0
        i_start     = 0
        parts       = []

        for index, char in enumerate(text):
            match char:
                case ",":
                    if not in_quotes and not in_brackets:
                        parts.append(text[i_start: index])
                        i_start = index + 1

                case "\"":
                    in_quotes = not in_quotes

                case "(" | "[":
                    in_brackets += 1

                case ")" | "]":
                    in_brackets -= 1

        parts.append(text[i_start:])

        return parts

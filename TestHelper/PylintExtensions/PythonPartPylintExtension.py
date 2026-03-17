""" implementation of the PythonPart pylint extension
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from astroid import InferenceError, Uninferable, nodes
from astroid.nodes import Call, ClassDef, FunctionDef, Name, Attribute, Decorators, Const, Unknown, Module, AssignAttr
from astroid.bases import BoundMethod
from pylint.checkers import BaseChecker
from pylint.checkers.utils import infer_all

if TYPE_CHECKING:
    from pylint.lint import PyLinter

# pylint: disable=line-too-long

DEPRECATED_FUNCTIONS = {"BuildingElement.change_property": "use HandlePropertiesService.update_property_value",
                        "LibraryBitmapPreview.create_libary_bitmap_preview": "use create_library_bitmap_preview(...)",
                        "DrawingFileService.ExportIFC": "use NemAll_Python_BaseElements.ExportImportService.ExportIFC",
                        "DrawingFileService.ImportIFC": "use NemAll_Python_BaseElements.ExportImportService.ImportIFC",
                        "DrawingFileService.ExportDWGByTheme": "use NemAll_Python_BaseElements.ExportImportService.ExportDWGByTheme",
                        "DrawingFileService.ExportDWG": "use NemAll_Python_BaseElements.ExportImportService.ExportDWG",
                        "DrawingFileService.ImportDWG": "use NemAll_Python_BaseElements.ExportImportService.ImportDWG",
                        "CoordinateInput.SelectWallFace": "use NemAll_Python_BaseElements.FaceSelectService.SelectWallFace",
                        "CoordinateInput.SelectWallFaceInUVS": "use NemAll_Python_BaseElements.FaceSelectService.SelectWallFaceInUVS",
                        "CoordinateInput.SelectPolyhedron": "use NemAll_Python_BaseElements.FaceSelectService.SelectPolyhedron"}

# pylint: enable=line-too-long

DEPRECATED = "deprecated"
DECORATOR  = "PythonPartPylintDecorator"
NEM_ALL    = "NemAll_"


class PythonPartPylintExtension(BaseChecker):
    """ implementation of the PythonPart pylint extension
    """
    name = DEPRECATED

    priority = -1
    msgs = {"W0001": ("%s.%s is deprecated: %s;  %s.",
                      DEPRECATED,
                      "Functions that have been marked via annotations as deprecated should not be used.")
           }

    function_parameters: dict[str, str] = {}
    class_members      : dict[str, str] = {}

    def decorator_call(self,
                       node     : Decorators,
                       decorator: Call):
        """analyze a decorator of type Call

        Args:
            node:      node
            decorator: decorator
        """

        if (func := decorator.func) is None:
            return

        if not isinstance(func, Attribute):
            return

        if func.attrname != DEPRECATED or \
            not func.expr or not isinstance(func.expr, Name) or func.expr.name != DECORATOR:
            return

        if not isinstance((function := node.parent), FunctionDef):
            return

        if not isinstance((function_class := function.parent), (ClassDef, Module)):
            return

        replace = ""

        replace_key = "replace"

        if decorator.keywords is not None:
            for key_word in decorator.keywords:
                if key_word.arg == replace_key and isinstance(key_word.value, Const):
                    replace = f'{key_word.value.value}'

        self.add_message(DEPRECATED,
                            node = function,
                            args =(function_class.name, function.name, replace, ""))

        return


    def decorator_attribute(self,
                            node     : Decorators,
                            decorator: Attribute):
        """ analyze a decorator of type Attribute

        Args:
            node:      node
            decorator: decorator
        """

        if decorator.attrname != DEPRECATED or \
            not isinstance(decorator.expr, Name) or decorator.expr.name != DECORATOR:
            return

        if not isinstance((function := node.parent), FunctionDef):
            return

        if not isinstance((function_class := function.parent), ClassDef):
            return

        self.add_message(DEPRECATED,
                            node = function,
                            args =(function_class.name, function.name, "", ""))

        return


    def visit_decorators(self, node: Decorators):
        """ decorator visitor

        Args:
            node: node to analyze
        """

        if node.nodes is None:
            return

        for decorator in node.get_children():

            #------------- decorator with additional information

            if isinstance(decorator, Call):
                self.decorator_call(node, decorator)


            #------------- check for deprecation decorator without parameter

            elif isinstance(decorator, Attribute):
                self.decorator_attribute(node, decorator)


    def visit_classdef(self,
                       _node: nodes.ClassDef):
        """ visit the class definition

        Args:
            _node: class node
        """

        self.class_members = {}


    def visit_functiondef(self, node: nodes.FunctionDef) -> None:
        """ visit the function definition

        Args:
            node: function node
        """

        self.function_parameters = {}

        for arg, annotation in zip(node.args.arguments, node.args.annotations):
            if arg is not None and annotation is not None and arg.name is not None:
                self.function_parameters[arg.name] = \
                    annotation.name if isinstance(annotation, Name) and annotation.name is not None else \
                    annotation.attrname if isinstance(annotation, Attribute) and annotation.attrname is not None else ""


    def visit_assign(self, node: nodes.Assign):
        """ visit the value assign

        Args:
            node: assign node
        """

        if not isinstance(node.value, Name) or node.value.name is None:
            return

        if (annotation := self.function_parameters.get(node.value.name)) is None:
            return

        self_const = "self"

        for target in node.targets:
            if not isinstance(target, AssignAttr) or not isinstance(target.expr, Name) or \
               not target.expr.name == self_const or target.attrname is None:
                continue

            self.class_members[target.attrname] = annotation


    def visit_attribute(self,
                        node: Call):
        """ check for deprecated functions calls

        Args:
            node: node
        """

        if not isinstance(node, Attribute) or node.expr is None:
            return


        #----------------- check for owner is a function argument

        if isinstance(node.expr, Name) and node.expr.name is not None and node.attrname is not None:
            if (annotation := self.function_parameters.get(node.expr.name)) is None:
                annotation = node.expr.name

            if (replace := DEPRECATED_FUNCTIONS.get(annotation + "." + node.attrname)) is not None:
                self.add_message(DEPRECATED,
                                node = node,
                                args =(annotation, node.attrname, replace, ""))

                return


        #----------------- check for owner is a class member

        if isinstance(node.expr, Attribute) and node.expr.attrname is not None and node.attrname is not None:
            if (annotation := self.class_members.get(node.expr.attrname)) is None:
                annotation = node.expr.attrname

            if (replace := DEPRECATED_FUNCTIONS.get(annotation + "." + node.attrname)) is not None:
                self.add_message(DEPRECATED,
                                node = node,
                                args =(annotation, node.attrname, replace, ""))

                return


        #----------------- get the owner and check for deprecated

        if not node.attrname:
            return

        try:
            inferred = list(node.expr.infer())

        except InferenceError:
            return

        instance_of_nemall = "Instance of NemAll_"

        for owner in inferred:
            name = str(owner)

            if owner is Uninferable or isinstance(owner, Unknown) or instance_of_nemall not in name:
                continue

            name = name.split(".", 1)[-1] + "." + node.attrname

            if (replace := DEPRECATED_FUNCTIONS.get(name)) is None:
                continue

            names = name.split(".")

            self.add_message(DEPRECATED,
                             node = node,
                             args =(names[-2], names[-1], replace, ""))



    def visit_call(self,
                   node: Call):
        """ check for deprecated functions calls

        Args:
            node: node
        """

        if isinstance(node.func, Name) and node.func.name == "HandleProperties":
            args = node.func.parent.args

            if len(args) >= 4 and len(args[3].elts) > 0 and str(type(args[3].elts[0])).endswith(".Tuple'>"):
                self.add_message(DEPRECATED,
                                 node = node,
                                 args =("HandleProperties", " Use of tuple as parameter", "use HandleParameterData", ""))

                return


        #----------------- check for deprecated functions


        for inferred in infer_all(node.func):
            if isinstance(inferred, BoundMethod):
                func = inferred.qname() # type: ignore

                if isinstance(func, str):
                    names = func.split(".")

                    if (replace := DEPRECATED_FUNCTIONS.get(func)) is not None:
                        self.add_message(DEPRECATED,
                                         node = node,
                                         args =(names[-2], names[-1], replace, ""))

                        return




def register(linter: PyLinter):
    """ register the extension

    Args:
        linter: linter
    """

    linter.register_checker(PythonPartPylintExtension(linter))

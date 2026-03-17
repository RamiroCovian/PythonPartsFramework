""" definition of the parameter property value types impl
"""

from .ValueTypeUtils.ValueType import ValueType

from .ParameterPropertyValueType import ParameterPropertyValueType
from .ParameterPropertyValueTypes import ParameterPropertyValueTypes

class ParameterPropertyValueTypesImpl():
    """ definition of the parameter property value types impl
    """

    __value_types_impl = {}

    @staticmethod
    def get_value_type_impl(value_type: str) -> ParameterPropertyValueType:
        """ get the value type

        Args:
            value_type: value type name

        Returns:
            value type implementation
        """

        value_type = value_type.lower()

        if not ParameterPropertyValueTypesImpl.__value_types_impl:
            ParameterPropertyValueTypesImpl.__init_value_types()

        if (value_type_impl := ParameterPropertyValueTypesImpl.__value_types_impl.get(value_type)) is not None:
            return value_type_impl

        if value_type.startswith("tuple"):
            return ValueType("TupleImpl", value_type, True, True).create_parameter_property_value_type()

        if value_type.startswith("namedtuple"):
            return ValueType("NamedTupleImpl", value_type, True, True).create_parameter_property_value_type()

        if value_type.startswith("dynamiclist"):
            return ValueType("DynamicListImpl", value_type, True, True).create_parameter_property_value_type()

        if (value_type_impl := ParameterPropertyValueTypesImpl.__value_types_impl.get(f"${value_type}")) is not None:
            return value_type_impl

        return ParameterPropertyValueType(ValueType("", value_type, False, False))


    @staticmethod
    def has_value_type_impl(value_type: str) -> bool:
        """ check the value type implementation

        Args:
            value_type: value type name

        Returns:
            has value type implementation state
        """

        value_type = value_type.lower()

        if not ParameterPropertyValueTypesImpl.__value_types_impl:
            ParameterPropertyValueTypesImpl.__init_value_types()

        return value_type in ParameterPropertyValueTypesImpl.__value_types_impl or \
               value_type.startswith("tuple") or value_type.startswith("namedtuple") or \
               value_type.startswith("dynamiclist")


    @staticmethod
    def __init_value_types():
        """ create the list with the implemented value types
        """

        for key in ParameterPropertyValueTypes.__dict__:
            impl = getattr(ParameterPropertyValueTypes, key)

            if isinstance(impl, ValueType) and impl.has_impl:
                ParameterPropertyValueTypesImpl.__value_types_impl[str(impl)] = impl.create_parameter_property_value_type()

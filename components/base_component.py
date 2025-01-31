from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar
from materials.material import Material
from units_config import ureg, Quantity
from typing import Any, Optional


class BaseComponent(ABC):
    """Abstract base class for all fastener assembly components.

    This class defines the core interface that all components must implement,
    including material properties, geometry, and unit handling.

    Attributes:
        material (Material): The material assigned to this component
        component_id (str): Unique identifier for this component

    Example:
        >>> bolt = Bolt(steel_material, length=10*ureg.mm)
        >>> bolt.material.get_property('density')
        <Quantity(7.85, 'gram / centimeter ** 3')>
        >>> bolt.convert_length(bolt.length, 'inch')
        <Quantity(0.3937, 'inch')>
    """

    def __init__(self, material: Material):
        """Initialize the base component.

        Args:
            material: Material instance defining the component's material properties

        Raises:
            ValueError: If material is None or invalid
        """
        if not material or not isinstance(material, Material):
            raise ValueError('A valid Material instance must be provided')
        self._material = material
        self._component_id = str(id(self))

    @property
    def material(self) ->Material:
        """Get the component's material.

        Returns:
            The Material instance assigned to this component

        Example:
            >>> component.material.get_property('density')
            <Quantity(7.85, 'gram / centimeter ** 3')>
        """
        return self._material

    @property
    def component_id(self) ->str:
        """Get the component's unique identifier.

        Returns:
            String identifier unique to this component instance

        Example:
            >>> component.component_id
            '140712834927872'
        """
        return self._component_id

    @abstractmethod
    def validate_geometry(self) ->bool:
        """Validate the component's geometric properties.

        All components must implement geometry validation appropriate to their
        specific dimensional constraints.

        Returns:
            True if geometry is valid

        Raises:
            ValueError: If geometry is invalid, with specific reason
            NotImplementedError: If not implemented by subclass

        Example:
            >>> bolt.validate_geometry()  # checks length > 0
            True
        """
        raise NotImplementedError("validate_geometry must be implemented by subclass")

    def convert_length(self, value: Quantity, target_unit: str) ->Quantity:
        """Convert a length value to the specified unit.

        Args:
            value: The length value to convert (must be a length quantity)
            target_unit: The target unit string (e.g., 'mm', 'inch')

        Returns:
            The converted quantity in the target unit

        Raises:
            ValueError: If value is not a length quantity
            ValueError: If target_unit is not a valid length unit

        Example:
            >>> component.convert_length(10 * ureg.mm, 'inch')
            <Quantity(0.3937, 'inch')>
        """
        if not isinstance(value, Quantity):
            raise ValueError('Value must be a Quantity')
        try:
            return value.to(target_unit)
        except Exception as e:
            raise ValueError(f'Invalid conversion: {str(e)}')

    def validate_length(self, value: Quantity, min_val: Optional[Quantity]=
        None, max_val: Optional[Quantity]=None) ->bool:
        """Validate a length value against optional minimum and maximum bounds.

        Args:
            value: The length value to validate (must be a length quantity)
            min_val: Optional minimum allowed value (in length units)
            max_val: Optional maximum allowed value (in length units)

        Returns:
            True if value is valid, False otherwise

        Raises:
            ValueError: If value is not a length quantity
            ValueError: If min/max values are not length quantities

        Example:
            >>> component.validate_length(10 * ureg.mm, min_val=0 * ureg.mm)
            True
        """
        if not isinstance(value, Quantity):
            raise ValueError('Value must be a Quantity')
        if min_val is not None:
            if not isinstance(min_val, Quantity):
                raise ValueError('min_val must be a Quantity')
            if value < min_val:
                return False
        if max_val is not None:
            if not isinstance(max_val, Quantity):
                raise ValueError('max_val must be a Quantity')
            if value > max_val:
                return False
        return True

    @material.setter
    def material(self, value: Material) ->None:
        """Set the component's material.

    Args:
        value: New Material instance to assign to this component

    Raises:
        ValueError: If material is None or invalid

    Example:
        >>> component.material = new_material
    """
        if not value or not isinstance(value, Material):
            raise ValueError('A valid Material instance must be provided')
        self._material = value

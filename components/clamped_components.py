"""
Clamped components module for fastener assemblies.

This module provides the abstract base class for clamped components and concrete implementations
for washers and plates.
"""
from abc import ABC, abstractmethod
from typing import Optional
from pint import Quantity
from components.base_component import BaseComponent
from materials.material import Material
from units_config import ureg


class ClampedComponent(BaseComponent, ABC):
    """Abstract base class for components that can be clamped in a fastener assembly.

    Defines the interface for all clamped components including washers and plates.
    """

    @property
    @abstractmethod
    def thickness(self) ->Quantity:
        """Get the thickness of the clamped component."""
        pass

    @thickness.setter
    @abstractmethod
    def thickness(self, value: Quantity) ->None:
        """Set the thickness of the clamped component."""
        pass

    @abstractmethod
    def validate_geometry(self) -> bool:
        """Validate the component's geometric properties.
        
        Returns:
            True if geometry is valid
            
        Raises:
            ValueError: If geometry is invalid, with specific reason
        """
        raise NotImplementedError("validate_geometry must be implemented by subclass")


from typing import Optional
from pint import Quantity
from components.base_component import BaseComponent
from materials.material import Material
from units_config import ureg


class Washer(ClampedComponent):
    """A washer component in a fastener assembly.

    Represents a washer with inner diameter, outer diameter, thickness, and material properties.
    Supports both metric and imperial units through pint unit handling.

    Attributes:
        inner_diameter (Quantity): The inner diameter of the washer
        outer_diameter (Quantity): The outer diameter of the washer
        thickness (Quantity): The thickness of the washer
        material (Material): Reference to the washer material

    Example:
        >>> washer = Washer(
        ...     inner_diameter=10 * ureg.mm,
        ...     outer_diameter=20 * ureg.mm,
        ...     thickness=2 * ureg.mm,
        ...     material=some_material
        ... )
    """

    def __init__(self, inner_diameter: Quantity, outer_diameter: Quantity,
        thickness: Quantity, material: Material) ->None:
        """Initialize a new Washer instance.

    Args:
        inner_diameter: The inner diameter of the washer (length units)
        outer_diameter: The outer diameter of the washer (length units)
        thickness: The thickness of the washer (length units)
        material: Reference to the washer material

    Raises:
        ValueError: If dimensions are invalid or material reference is missing
    """
        super().__init__(material=material)
        self._inner_diameter = inner_diameter
        self._outer_diameter = outer_diameter
        self._thickness = thickness
        self.validate_geometry()

    @property
    def inner_diameter(self) ->Quantity:
        """Get the inner diameter of the washer."""
        return self._inner_diameter

    @inner_diameter.setter
    def inner_diameter(self, value: Quantity) ->None:
        """Set the inner diameter of the washer.

        Args:
            value: New inner diameter value (length units)

        Raises:
            ValueError: If the new value is invalid
        """
        self._inner_diameter = value
        self.validate_geometry()

    @property
    def outer_diameter(self) ->Quantity:
        """Get the outer diameter of the washer."""
        return self._outer_diameter

    @outer_diameter.setter
    def outer_diameter(self, value: Quantity) ->None:
        """Set the outer diameter of the washer.

        Args:
            value: New outer diameter value (length units)

        Raises:
            ValueError: If the new value is invalid
        """
        self._outer_diameter = value
        self.validate_geometry()

    @property
    def thickness(self) ->Quantity:
        """Get the thickness of the washer."""
        return self._thickness

    @thickness.setter
    def thickness(self, value: Quantity) ->None:
        """Set the thickness of the washer.

        Args:
            value: New thickness value (length units)

        Raises:
            ValueError: If the new value is invalid
        """
        self._thickness = value
        self.validate_geometry()

    def validate_geometry(self) ->None:
        """Validate the washer configuration.

        Checks:
        - All dimensions are positive
        - Outer diameter is greater than inner diameter

        Raises:
            ValueError: If any validation check fails
        """
        if not all(isinstance(dim, Quantity) for dim in [self.
            _inner_diameter, self._outer_diameter, self._thickness]):
            raise ValueError('All dimensions must be quantities with units')
        inner_mm = self._inner_diameter.to('mm').magnitude
        outer_mm = self._outer_diameter.to('mm').magnitude
        thickness_mm = self._thickness.to('mm').magnitude
        if inner_mm <= 0 or outer_mm <= 0 or thickness_mm <= 0:
            raise ValueError('All dimensions must be positive')
        if inner_mm >= outer_mm:
            raise ValueError(
                'Outer diameter must be greater than inner diameter')


class PlateComponent(ClampedComponent):
    """A plate component in a fastener assembly.

    Represents a plate with thickness and material properties.
    Supports both metric and imperial units through pint unit handling.

    Attributes:
        thickness (Quantity): The thickness of the plate
        material (Material): Reference to the plate material

    Example:
        >>> plate = PlateComponent(
        ...     thickness=5 * ureg.mm,
        ...     material=some_material
        ... )
    """

    def __init__(self, thickness: Quantity, material: Material, **kwargs) ->None:
        """Initialize a new PlateComponent instance.

        Args:
            thickness: The thickness of the plate (length units)
            material: Reference to the plate material
            **kwargs: Additional arguments passed to parent class

        Raises:
            ValueError: If thickness is invalid or material reference is missing
        """
        self._thickness = thickness  # Set thickness before parent init might need it
        super().__init__(material=material, **kwargs)
        self.validate_geometry()

    @property
    def thickness(self) ->Quantity:
        """Get the thickness of the plate."""
        return self._thickness

    @thickness.setter
    def thickness(self, value: Quantity) ->None:
        """Set the thickness of the plate.

        Args:
            value: New thickness value (length units)

        Raises:
            ValueError: If the new value is invalid
        """
        self._thickness = value
        self.validate_geometry()

    def validate_geometry(self) -> bool:
        """Validate the plate configuration.

        Checks:
        - Thickness is positive
        - Thickness has valid units

        Returns:
            True if geometry is valid

        Raises:
            ValueError: If any validation check fails
        """
        if not isinstance(self._thickness, Quantity):
            raise ValueError('Thickness must be a quantity with units')
            
        try:
            thickness_mm = self._thickness.to('mm').magnitude
        except:
            raise ValueError('Thickness must have valid length units')
            
        if thickness_mm <= 0:
            raise ValueError('Thickness must be positive')
            
        return True


__all__ = ['ClampedComponent', 'Washer', 'PlateComponent']

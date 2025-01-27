from typing import Optional, Union
from pint import Quantity
from units_config import ureg
from materials.material import Material
from components.clamped_components import PlateComponent
from components.threaded_components import ThreadedComponent
from utils.thread_utils import is_valid_thread_spec, calculate_pitch_diameter
from components.base_component import BaseComponent


class ThreadedPlate(ThreadedComponent, PlateComponent):
    """A plate component with both clamped and threaded characteristics.

    Combines properties of a plate component with threaded features, supporting
    both metric and imperial units through pint unit handling.

    Attributes:
        thickness (Quantity): The thickness of the plate
        material (Material): Reference to the plate material
        thread_spec (str): Thread specification (e.g., "1/4-20 UNC")
        pitch_diameter (Quantity): Thread pitch diameter with length units
        threaded_length (Quantity): Length of threaded section with length units
        clearance_hole_diameter (Quantity): Diameter of clearance hole with length units
        thread_location_x (Quantity): X coordinate of thread location
        thread_location_y (Quantity): Y coordinate of thread location
    """

    def __init__(self, thickness: Union[Quantity, float], material: Material, 
                 thread_spec: str, threaded_length: Union[Quantity, float],
                 clearance_hole_diameter: Union[Quantity, float], 
                 thread_location_x: Union[Quantity, float]=None, 
                 thread_location_y: Union[Quantity, float]=None) -> None:
        """Initialize a ThreadedPlate instance.

        Args:
            thickness: The thickness of the plate (with units if Quantity)
            material: Reference to the plate material
            thread_spec: Thread specification string (e.g., "1/4-20 UNC")
            threaded_length: Length of threaded section (with units if Quantity)
            clearance_hole_diameter: Diameter of clearance hole (with units if Quantity)
            thread_location_x: X coordinate of thread location (with units if Quantity)
            thread_location_y: Y coordinate of thread location (with units if Quantity)

        Raises:
            ValueError: If dimensions are invalid
            ValueError: If thread specification is invalid
            ValueError: If threaded length exceeds plate thickness
            ValueError: If clearance hole diameter is less than pitch diameter
            TypeError: If material is invalid type
        """
        # Initialize base class
        BaseComponent.__init__(self, material=material)  # Only initialize material once
        
        # Set up threaded component attributes
        if not is_valid_thread_spec(thread_spec):
            raise ValueError(f'Invalid thread specification: {thread_spec}')
        self._thread_spec = thread_spec
        
        # Convert numeric values to Quantities
        if isinstance(thickness, (int, float)):
            thickness = ureg.Quantity(thickness, 'mm')
        if isinstance(threaded_length, (int, float)):
            threaded_length = ureg.Quantity(threaded_length, 'mm')
        if isinstance(clearance_hole_diameter, (int, float)):
            clearance_hole_diameter = ureg.Quantity(clearance_hole_diameter, 'mm')
            
        # Validate and set dimensions
        if not isinstance(thickness, Quantity) or thickness.magnitude <= 0:
            raise ValueError('Thickness must be a positive quantity with units')
        self._thickness = thickness
        
        if not isinstance(threaded_length, Quantity) or threaded_length.magnitude <= 0:
            raise ValueError('Threaded length must be a positive quantity with units')
        self._threaded_length = threaded_length
        
        if not isinstance(clearance_hole_diameter, Quantity) or clearance_hole_diameter.magnitude <= 0:
            raise ValueError('Clearance hole diameter must be a positive quantity with units')
        self._clearance_hole_diameter = clearance_hole_diameter
        
        # Calculate pitch diameter after thread spec is validated
        self._pitch_diameter = calculate_pitch_diameter(thread_spec)
        
        # Handle optional thread locations
        if thread_location_x is None:
            thread_location_x = 0
        if thread_location_y is None:
            thread_location_y = 0
            
        if isinstance(thread_location_x, (int, float)):
            self._thread_location_x = ureg.Quantity(thread_location_x, 'mm')
        else:
            self._thread_location_x = thread_location_x
            
        if isinstance(thread_location_y, (int, float)):
            self._thread_location_y = ureg.Quantity(thread_location_y, 'mm')
        else:
            self._thread_location_y = thread_location_y
            
        # Validate all attributes after they're set up
        self.validate_geometry()

    @property
    def thickness(self) -> Quantity:
        """Get the thickness of the plate."""
        return self._thickness

    @thickness.setter
    def thickness(self, value: Quantity) -> None:
        """Set the thickness of the plate.
        
        Args:
            value: New thickness value (with units if Quantity)
            
        Raises:
            ValueError: If value is not positive
        """
        if isinstance(value, (int, float)):
            value = ureg.Quantity(value, 'mm')
        if not isinstance(value, Quantity) or value.magnitude <= 0:
            raise ValueError('Thickness must be a positive quantity with units')
        self._thickness = value
        self.validate_geometry()

    @property
    def threaded_length(self) -> Quantity:
        """Get the length of the threaded section."""
        return self._threaded_length

    @threaded_length.setter
    def threaded_length(self, value: Quantity) -> None:
        """Set the length of the threaded section.
        
        Args:
            value: New threaded length value (with units if Quantity)
            
        Raises:
            ValueError: If value is not positive or exceeds plate thickness
        """
        if isinstance(value, (int, float)):
            value = ureg.Quantity(value, 'mm')
        if not isinstance(value, Quantity) or value.magnitude <= 0:
            raise ValueError('Threaded length must be a positive quantity with units')
        self._threaded_length = value
        self.validate_geometry()

    @property
    def clearance_hole_diameter(self) -> Quantity:
        """Get the clearance hole diameter."""
        return self._clearance_hole_diameter

    @clearance_hole_diameter.setter
    def clearance_hole_diameter(self, value: Quantity) -> None:
        """Set the clearance hole diameter.
        
        Args:
            value: New clearance hole diameter value (with units if Quantity)
            
        Raises:
            ValueError: If value is not positive or less than pitch diameter
        """
        if isinstance(value, (int, float)):
            value = ureg.Quantity(value, 'mm')
        if not isinstance(value, Quantity) or value.magnitude <= 0:
            raise ValueError('Clearance hole diameter must be a positive quantity with units')
        self._clearance_hole_diameter = value
        self.validate_geometry()

    @property
    def thread_location_x(self) -> Quantity:
        """Get the X coordinate of the thread location."""
        return self._thread_location_x

    @thread_location_x.setter
    def thread_location_x(self, value: Quantity) -> None:
        """Set the X coordinate of the thread location."""
        if isinstance(value, (int, float)):
            value = ureg.Quantity(value, 'mm')
        if not isinstance(value, Quantity):
            raise ValueError('Thread location X must be a quantity with units')
        self._thread_location_x = value
        self.validate_geometry()

    @property
    def thread_location_y(self) -> Quantity:
        """Get the Y coordinate of the thread location."""
        return self._thread_location_y

    @thread_location_y.setter
    def thread_location_y(self, value: Quantity) -> None:
        """Set the Y coordinate of the thread location."""
        if isinstance(value, (int, float)):
            value = ureg.Quantity(value, 'mm')
        if not isinstance(value, Quantity):
            raise ValueError('Thread location Y must be a quantity with units')
        self._thread_location_y = value
        self.validate_geometry()

    def validate_geometry(self) -> None:
        """Validate the threaded plate configuration.

        Checks:
        - All dimensions are positive (from PlateComponent)
        - Material reference is valid (from BaseComponent)
        - Thread specification is valid (from ThreadedComponent)
        - Threaded length does not exceed plate thickness
        - Clearance hole diameter is greater than pitch diameter
        - Thread location is valid

        Raises:
            ValueError: If any validation check fails
        """
        # Cross-property validations
        if self.threaded_length > self.thickness:
            raise ValueError('Threaded length cannot exceed plate thickness')
        if self.clearance_hole_diameter <= self.pitch_diameter:
            raise ValueError('Clearance hole diameter must be greater than pitch diameter')

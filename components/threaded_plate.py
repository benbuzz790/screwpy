from typing import Optional, Union
from pint import Quantity
from units_config import ureg
from materials.material import Material
from components.clamped_components import PlateComponent
from components.threaded_components import ThreadedComponent
from utils.thread_utils import is_valid_thread_spec, calculate_pitch_diameter


class ThreadedPlate(ThreadedComponent, PlateComponent):
    """A plate component with both clamped and threaded characteristics.

    Combines properties of a plate component with threaded features, supporting
    both metric and imperial units through pint unit handling.

    Attributes:
        thickness (Quantity): The thickness of the plate
        material (Material): Reference to the plate material
        thread_spec (str): Thread specification (e.g., "1/4-20")
        pitch_diameter (Quantity): Thread pitch diameter with length units
        threaded_length (Quantity): Length of threaded section with length units
        clearance_hole_diameter (Quantity): Diameter of clearance hole with length units
        thread_location_x (Quantity): X coordinate of thread location
        thread_location_y (Quantity): Y coordinate of thread location

    Example:
        >>> from units_config import ureg
        >>> from materials.material import Material
        >>> material = Material("Steel")
        >>> plate = ThreadedPlate(
        ...     thickness=10 * ureg.mm,
        ...     material=material,
        ...     thread_spec="M6-1",
        ...     threaded_length=8 * ureg.mm,
        ...     clearance_hole_diameter=6.5 * ureg.mm,
        ...     thread_location_x=20 * ureg.mm,
        ...     thread_location_y=20 * ureg.mm
        ... )
    """

    def __init__(self, thickness: Union[Quantity, float], material:
        Material, thread_spec: str, threaded_length: Union[Quantity, float],
        clearance_hole_diameter: Union[Quantity, float], thread_location_x:
        Union[Quantity, float]=None, thread_location_y: Union[Quantity,
        float]=None) ->None:
        """Initialize a ThreadedPlate instance.

    Args:
        thickness: The thickness of the plate (with units if Quantity)
        material: Reference to the plate material
        thread_spec: Thread specification string (e.g., "M6-1")
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
        ThreadedComponent.__init__(self, thread_spec=thread_spec,
            threaded_length=threaded_length, material=material)
        PlateComponent.__init__(self, thickness=thickness, material=material)
        if isinstance(clearance_hole_diameter, (int, float)):
            self._clearance_hole_diameter = ureg.Quantity(
                clearance_hole_diameter, 'mm')
        else:
            self._clearance_hole_diameter = clearance_hole_diameter
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
        self.validate_geometry()

    def validate_geometry(self) ->None:
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
        PlateComponent.validate_geometry(self)
        if self.threaded_length > self.thickness:
            raise ValueError('Threaded length cannot exceed plate thickness')
        if not isinstance(self._clearance_hole_diameter, Quantity):
            raise ValueError(
                'Clearance hole diameter must be a quantity with units')
        if self._clearance_hole_diameter.magnitude <= 0:
            raise ValueError('Clearance hole diameter must be positive')
        if self._clearance_hole_diameter <= self.pitch_diameter:
            raise ValueError(
                'Clearance hole diameter must be greater than pitch diameter')
        if not isinstance(self._thread_location_x, Quantity):
            raise ValueError('Thread location X must be a quantity with units')
        if not isinstance(self._thread_location_y, Quantity):
            raise ValueError('Thread location Y must be a quantity with units')

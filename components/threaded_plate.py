from typing import Optional, Union
from units_config import ureg
from materials.material import Material
from .base_component import BaseComponent
from .clamped_components import PlateComponent
from .threaded_components import ThreadedComponent
from utils.thread_utils import parse_thread_specification, calculate_pitch_diameter

Quantity = ureg.Quantity

class ThreadedPlate(ThreadedComponent, PlateComponent):
    def __init__(self, material: Material, thickness: Union[Quantity, float], thread_spec: str,
                 threaded_length: Union[Quantity, float], clearance_hole_diameter: Union[Quantity, float],
                 thread_location_x: Optional[Union[Quantity, float]] = None,
                 thread_location_y: Optional[Union[Quantity, float]] = None):
        # Convert numeric values to quantities
        if isinstance(thickness, (int, float)):
            thickness = thickness * ureg.mm
        if isinstance(threaded_length, (int, float)):
            threaded_length = threaded_length * ureg.mm
        if isinstance(clearance_hole_diameter, (int, float)):
            clearance_hole_diameter = clearance_hole_diameter * ureg.mm
        if isinstance(thread_location_x, (int, float)):
            thread_location_x = thread_location_x * ureg.mm
        if isinstance(thread_location_y, (int, float)):
            thread_location_y = thread_location_y * ureg.mm

        # Set default locations if None
        if thread_location_x is None:
            thread_location_x = 0 * ureg.mm
        if thread_location_y is None:
            thread_location_y = 0 * ureg.mm

        # Initialize BaseComponent just once
        BaseComponent.__init__(self, material=material)

        # Initialize ThreadedComponent attributes
        self._thread_spec = thread_spec
        thread_info = parse_thread_specification(thread_spec)
        self._nominal_diameter = thread_info.nominal_diameter
        self._pitch_diameter = calculate_pitch_diameter(thread_spec)
        self._is_metric = thread_info.is_metric

        # Initialize all attributes
        self._thickness = thickness
        self._threaded_length = threaded_length
        self._clearance_hole_diameter = clearance_hole_diameter
        self._thread_location_x = thread_location_x
        self._thread_location_y = thread_location_y

        # Validate the complete geometry - will raise ValueError if invalid
        self.validate_geometry()

    def validate_geometry(self) -> None:
        # Validate basic dimensions
        if not isinstance(self._thickness, Quantity) or self._thickness <= 0 * ureg.mm:
            raise ValueError("Thickness must be positive")
        if not isinstance(self._threaded_length, Quantity) or self._threaded_length <= 0 * ureg.mm:
            raise ValueError("Threaded length must be positive")
        if not isinstance(self._clearance_hole_diameter, Quantity) or self._clearance_hole_diameter <= 0 * ureg.mm:
            raise ValueError("Clearance hole diameter must be positive")

        # Validate thread spec
        thread_info = parse_thread_specification(self._thread_spec)
        if thread_info is None:
            raise ValueError("Invalid thread specification")

        # Validate threaded length against thickness
        if self._threaded_length > self._thickness:
            raise ValueError(f"Threaded length {self._threaded_length} exceeds thickness {self._thickness}")

        # Validate clearance hole size against thread diameter
        if self._clearance_hole_diameter <= self._nominal_diameter:
            raise ValueError(f"Clearance hole diameter ({self._clearance_hole_diameter}) must be larger than thread diameter ({self._nominal_diameter})")
        # For standard hex head bolts, head diameter is typically 1.5x nominal diameter
        typical_head_diameter = (1.5 * self._nominal_diameter).to(ureg.mm)
        if self._clearance_hole_diameter >= typical_head_diameter:
            raise ValueError(f"Clearance hole diameter ({self._clearance_hole_diameter}) must be smaller than head diameter ({typical_head_diameter})")

        # Validate thread locations if specified
        if self._thread_location_x is not None:
            if not isinstance(self._thread_location_x, Quantity):
                raise ValueError("Thread location X must be a quantity with units")
        if self._thread_location_y is not None:
            if not isinstance(self._thread_location_y, Quantity):
                raise ValueError("Thread location Y must be a quantity with units")

    @property
    def thread_location_x(self) -> Optional[Quantity]:
        return self._thread_location_x

    @thread_location_x.setter
    def thread_location_x(self, value: Union[Quantity, float, None]) -> None:
        if value is not None:
            if isinstance(value, (int, float)):
                value = value * ureg.mm
            if not isinstance(value, Quantity):
                raise ValueError("Thread location X must be a quantity with units")
        old_value = self._thread_location_x
        self._thread_location_x = value
        try:
            self.validate_geometry()
        except ValueError as e:
            self._thread_location_x = old_value  # Reset to original state
            raise ValueError(f"Invalid thread location X: {str(e)}")

    @property
    def thread_location_y(self) -> Optional[Quantity]:
        return self._thread_location_y

    @thread_location_y.setter
    def thread_location_y(self, value: Union[Quantity, float, None]) -> None:
        if value is not None:
            if isinstance(value, (int, float)):
                value = value * ureg.mm
            if not isinstance(value, Quantity):
                raise ValueError("Thread location Y must be a quantity with units")
        old_value = self._thread_location_y
        self._thread_location_y = value
        try:
            self.validate_geometry()
        except ValueError as e:
            self._thread_location_y = old_value  # Reset to original state
            raise ValueError(f"Invalid thread location Y: {str(e)}")

    @property
    def threaded_length(self) -> Quantity:
        return self._threaded_length

    @threaded_length.setter
    def threaded_length(self, value: Union[Quantity, float]) -> None:
        if isinstance(value, (int, float)):
            value = value * ureg.mm
        if not isinstance(value, Quantity):
            raise ValueError("Threaded length must be a quantity with units")
        old_value = self._threaded_length
        self._threaded_length = value
        try:
            self.validate_geometry()
        except ValueError as e:
            self._threaded_length = old_value  # Reset to original state
            raise ValueError(f"Invalid threaded length: {str(e)}")

    @property
    def clearance_hole_diameter(self) -> Quantity:
        return self._clearance_hole_diameter

    @clearance_hole_diameter.setter
    def clearance_hole_diameter(self, value: Union[Quantity, float]) -> None:
        if isinstance(value, (int, float)):
            value = value * ureg.mm
        if not isinstance(value, Quantity):
            raise ValueError("Clearance hole diameter must be a quantity with units")
        old_value = self._clearance_hole_diameter
        self._clearance_hole_diameter = value
        try:
            self.validate_geometry()
        except ValueError as e:
            self._clearance_hole_diameter = old_value  # Reset to original state
            raise ValueError(f"Invalid clearance hole diameter: {str(e)}")

    def __str__(self):
        return f"Threaded Plate ({self.thickness} thick, {self.thread_spec})"

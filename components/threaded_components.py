from typing import Optional
from units_config import ureg, Quantity
from .base_component import BaseComponent
from materials.material import Material
from utils.thread_utils import parse_thread_specification, calculate_pitch_diameter

class ThreadedComponent(BaseComponent):
    """Base class for all threaded components."""

    def __init__(self, material: Material, thread_spec: str, threaded_length: Quantity, **kwargs):
        # Only pass material to BaseComponent
        super().__init__(material=material)
        # Handle ThreadedComponent's own parameters
        self._thread_spec = thread_spec
        self._threaded_length = threaded_length
        # Calculate and store thread info
        thread_info = parse_thread_specification(thread_spec)
        self._nominal_diameter = thread_info.nominal_diameter
        self._pitch_diameter = calculate_pitch_diameter(thread_spec)
        self._is_metric = thread_info.is_metric
        self._thread_spec = thread_spec
        self._threaded_length = threaded_length
        # Calculate and store thread info
        thread_info = parse_thread_specification(thread_spec)
        self._nominal_diameter = thread_info.nominal_diameter
        self._pitch_diameter = calculate_pitch_diameter(thread_spec)
        self._is_metric = thread_info.is_metric

    @property
    def thread_spec(self) -> str:
        return self._thread_spec

    @property
    def nominal_diameter(self) -> Quantity:
        return self._nominal_diameter

    @property
    def pitch_diameter(self) -> Quantity:
        return self._pitch_diameter

    @property
    def is_metric(self) -> bool:
        return self._is_metric

    @property
    def threaded_length(self) -> Quantity:
        return self._threaded_length

    def validate_geometry(self) -> bool:
        if not self._thread_spec:
            raise ValueError("Thread specification cannot be empty")
        if not self.validate_length(self._threaded_length, min_val=0*ureg.mm):
            raise ValueError(f"Invalid threaded length: {self._threaded_length}")
        return True

class Fastener(ThreadedComponent):
    """Fastener (bolt) component."""

    def __init__(self, thread_spec: str, length: Quantity, threaded_length: Quantity,
                 head_diameter: Quantity, head_height: Quantity, is_flat: bool, 
                 tool_size: str, material: Material):
        super().__init__(material=material, thread_spec=thread_spec, threaded_length=threaded_length)
        self._length = length
        self._head_diameter = head_diameter
        self._head_height = head_height
        self._is_flat = is_flat
        self._tool_size = tool_size
        self.validate_geometry()

    @property
    def length(self) -> Quantity:
        return self._length

    @length.setter
    def length(self, value: Quantity) -> None:
        if not self.validate_length(value, min_val=0*ureg.mm):
            raise ValueError(f"Invalid length: {value}")
        if value < self.threaded_length:
            raise ValueError(f"Length {value} must be greater than threaded length {self.threaded_length}")
        self._length = value

    @property
    def head_diameter(self) -> Quantity:
        return self._head_diameter

    @head_diameter.setter
    def head_diameter(self, value: Quantity) -> None:
        if not self.validate_length(value, min_val=0*ureg.mm):
            raise ValueError(f"Invalid head diameter: {value}")
        if value <= self.pitch_diameter:
            raise ValueError(f"Head diameter {value} must be greater than pitch diameter {self.pitch_diameter}")
        self._head_diameter = value

    @property
    def head_height(self) -> Quantity:
        return self._head_height

    @head_height.setter
    def head_height(self, value: Quantity) -> None:
        if not self.validate_length(value, min_val=0*ureg.mm):
            raise ValueError(f"Invalid head height: {value}")
        self._head_height = value

    @property
    def is_flat(self) -> bool:
        return self._is_flat

    @is_flat.setter
    def is_flat(self, value: bool) -> None:
        self._is_flat = bool(value)

    @property
    def tool_size(self) -> str:
        return self._tool_size

    @tool_size.setter
    def tool_size(self, value: str) -> None:
        if not value:
            raise ValueError("Tool size cannot be empty")
        self._tool_size = str(value)

    def validate_geometry(self) -> bool:
        super().validate_geometry()

        if not self.validate_length(self._length, min_val=0*ureg.mm):
            raise ValueError(f"Invalid length: {self._length}")
        if not self.validate_length(self._head_diameter, min_val=0*ureg.mm):
            raise ValueError(f"Invalid head diameter: {self._head_diameter}")
        if not self.validate_length(self._head_height, min_val=0*ureg.mm):
            raise ValueError(f"Invalid head height: {self._head_height}")

        if self._head_diameter <= self.pitch_diameter:
            raise ValueError(f"Head diameter {self._head_diameter} must be greater than pitch diameter {self.pitch_diameter}")

        if self.threaded_length > self._length:
            raise ValueError(f"Threaded length {self.threaded_length} exceeds total length {self._length}")

        return True

    def __str__(self):
        return f"{self.thread_spec} Bolt ({self.length})"

class Nut(ThreadedComponent):
    """Nut component."""

    def __init__(self, thread_spec: str, width_across_flats: Quantity, height: Quantity, material: Material):
        super().__init__(material=material, thread_spec=thread_spec, threaded_length=height)
        self._width_across_flats = width_across_flats
        self.validate_geometry()

    @property
    def width_across_flats(self) -> Quantity:
        return self._width_across_flats

    @width_across_flats.setter
    def width_across_flats(self, value: Quantity) -> None:
        if not self.validate_length(value, min_val=0*ureg.mm):
            raise ValueError(f"Invalid width across flats: {value}")
        if value <= self.pitch_diameter:
            raise ValueError(f"Width across flats {value} must be greater than pitch diameter {self.pitch_diameter}")
        self._width_across_flats = value

    @property
    def height(self) -> Quantity:
        return self.threaded_length

    @height.setter
    def height(self, value: Quantity) -> None:
        if not self.validate_length(value, min_val=0*ureg.mm):
            raise ValueError(f"Invalid height: {value}")
        self._threaded_length = value

    def validate_geometry(self) -> bool:
        super().validate_geometry()

        if self._width_across_flats <= self.pitch_diameter:
            raise ValueError(f"Width across flats {self._width_across_flats} must be greater than pitch diameter {self.pitch_diameter}")

        return True

    def __str__(self):
        return f"{self.thread_spec} Nut"

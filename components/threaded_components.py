"""Threaded components module for fastener assemblies."""

from abc import ABC, abstractmethod
from typing import Optional
from components.base_component import BaseComponent
from materials.material import Material
from utils.thread_utils import is_valid_thread_spec, calculate_pitch_diameter
from units_config import ureg, Quantity


class ThreadedComponent(BaseComponent, ABC):
    """Abstract base class for components with threads."""

    def __init__(self, thread_spec: str, threaded_length: Quantity, material: Material) -> None:
        """Initialize ThreadedComponent.

        Args:
            thread_spec: Thread specification (e.g., "1/4-20")
            threaded_length: Length of threaded section
            material: Component material
        """
        BaseComponent.__init__(self, material=material)

        # Validate thread specification
        if not is_valid_thread_spec(thread_spec):
            raise ValueError(f'Invalid thread specification: {thread_spec}')

        self._thread_spec = thread_spec
        self._threaded_length = threaded_length
        self._pitch_diameter = calculate_pitch_diameter(thread_spec)

    @property
    def thread_spec(self) -> str:
        """Get the thread specification."""
        return self._thread_spec

    @property
    def threaded_length(self) -> Quantity:
        """Get the length of the threaded section."""
        return self._threaded_length

    @threaded_length.setter
    def threaded_length(self, value: Quantity) -> None:
        """Set the length of the threaded section."""
        self._threaded_length = value

    @property
    def pitch_diameter(self) -> Quantity:
        """Get the pitch diameter."""
        return self._pitch_diameter


class Fastener(ThreadedComponent):
    """A fastener component in an assembly."""

    def __init__(self, thread_spec: str, length: Quantity, threaded_length: Quantity,
                 head_diameter: Quantity, head_height: Quantity, is_flat: bool,
                 tool_size: str, material: Material) -> None:
        """Initialize a new Fastener.

        Args:
            thread_spec: Thread specification (e.g., "1/4-20")
            length: Total fastener length
            threaded_length: Length of threaded section
            head_diameter: Diameter of fastener head
            head_height: Height of fastener head
            is_flat: Whether the head is flat
            tool_size: Size of tool needed for fastener
            material: Fastener material
        """
        super().__init__(thread_spec=thread_spec, threaded_length=threaded_length, material=material)
        self._length = length
        self._head_diameter = head_diameter
        self._head_height = head_height
        self._is_flat = is_flat
        self._tool_size = tool_size
        self.validate_geometry()

    def validate_geometry(self) -> bool:
        """Validate fastener geometry.

        Returns:
            True if geometry is valid

        Raises:
            ValueError: If geometry is invalid
        """
        if (self._length.magnitude <= 0 or self._head_diameter.magnitude <= 0 or
            self._head_height.magnitude <= 0):
            raise ValueError('All dimensions must be positive')
        if self._length <= self.threaded_length:
            raise ValueError('Total length must be greater than threaded length')
        if self._head_diameter <= self.pitch_diameter:
            raise ValueError('Head diameter must be greater than pitch diameter')
        return True

    @property
    def length(self) -> Quantity:
        """Get the total fastener length."""
        return self._length

    @length.setter
    def length(self, value: Quantity) -> None:
        """Set the total fastener length."""
        self._length = value
        self.validate_geometry()

    @property
    def head_diameter(self) -> Quantity:
        """Get the head diameter."""
        return self._head_diameter
    
    @head_diameter.setter
    def head_diameter(self, value:Quantity) -> None:
        self._head_diameter = value
        self.validate_geometry()


    @property
    def head_height(self) -> Quantity:
        """Get the head height."""
        return self._head_height
    
    @head_height.setter
    def head_height(self, value: Quantity) -> None:
        self._head_height = value
        self.validate_geometry()


    @property
    def is_flat(self) -> bool:
        """Get whether the head is flat."""
        return self._is_flat

    @is_flat.setter
    def is_flat(self, value: bool) -> None:
        """Set whether the head is flat."""
        self._is_flat = value

    @property
    def tool_size(self) -> str:
        """Get the tool size needed."""
        return self._tool_size


class Nut(ThreadedComponent):
    """A nut component in an assembly."""

    def __init__(self, thread_spec: str, width_across_flats: Quantity,
                 height: Quantity, material: Material) -> None:
        """Initialize a new Nut.

        Args:
            thread_spec: Thread specification (e.g., "1/4-20")
            width_across_flats: Width across the flats
            height: Total height of nut
            material: Nut material
        """
        super().__init__(thread_spec=thread_spec, threaded_length=height, material=material)
        self._width_across_flats = width_across_flats
        self._height = height
        self.validate_geometry()

    def validate_geometry(self) -> bool:
        """Validate nut geometry.

        Returns:
            True if geometry is valid

        Raises:
            ValueError: If geometry is invalid
        """
        if (self._width_across_flats.magnitude <= 0 or self._height.magnitude <= 0):
            raise ValueError('All dimensions must be positive')
        if self._width_across_flats <= self.pitch_diameter:
            raise ValueError('Width across flats must be greater than pitch diameter')
        return True

    @property
    def width_across_flats(self) -> Quantity:
        """Get the width across flats."""
        return self._width_across_flats

    @width_across_flats.setter
    def width_across_flats(self, value:Quantity) -> None:
        self._width_across_flats = value
        self.validate_geometry()

    @property
    def height(self) -> Quantity:
        """Get the total height."""
        return self._height

    @height.setter
    def height(self, value: Quantity) -> None:
        """Set the total height."""
        self._height = value
        self._threaded_length = value  # Keep threaded_length synchronized with height for nuts
        self.validate_geometry()

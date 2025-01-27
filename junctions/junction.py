"""Junction module for fastener assemblies."""
from typing import List, Union, Optional
from components.threaded_components import Fastener, Nut
from components.threaded_plate import ThreadedPlate
from components.clamped_components import ClampedComponent
from utils.thread_utils import are_threads_compatible as check_thread_compatibility
from units_config import ureg, Quantity


class Junction:
    """A complete fastener assembly junction.
    
    Represents a complete fastener assembly including:
    - One fastener
    - One or more clamped components
    - One threaded member (nut or threaded plate)
    
    Validates assembly compatibility and manages component relationships.
    """

    def __init__(self, fastener: Fastener, clamped_components: List[
        ClampedComponent], threaded_member: Union[Nut, ThreadedPlate]) ->None:
        """Initialize a new Junction.
        
        Args:
            fastener: The fastener component
            clamped_components: List of components being clamped
            threaded_member: The threaded member (nut or threaded plate)
            
        Raises:
            ValueError: If assembly is invalid
        """
        self.fastener = fastener
        self.clamped_components = clamped_components
        self.threaded_member = threaded_member
        self.validate_assembly()

    def validate_assembly(self) ->None:
        """Validate the complete assembly.

    Checks:
    - Thread compatibility
    - Sufficient fastener length
    - Valid component stack-up
    - No duplicate components

    Raises:
        ValueError: If assembly is invalid
    """
        if not check_thread_compatibility(self.fastener.thread_spec, self.
            threaded_member.thread_spec):
            raise ValueError('Thread specifications are not compatible')
        # Check for duplicate components by identity
        seen = set()
        for comp in self.clamped_components:
            if id(comp) in seen:
                raise ValueError('Duplicate components not allowed in assembly')
            seen.add(id(comp))
        stack_up = self.calculate_stack_up()
        if self.fastener.length <= stack_up:
            raise ValueError('Fastener length insufficient for assembly')
        if not self.clamped_components:
            raise ValueError(
                'Assembly must have at least one clamped component')

    def calculate_stack_up(self) ->Quantity:
        """Calculate total thickness of clamped components plus threaded member.

    Returns:
        Total stack-up thickness with units
    """
        # Start with zero in mm for consistent unit handling
        total = 0 * ureg.mm
        # Convert all thicknesses to mm for consistent addition
        for component in self.clamped_components:
            total += component.thickness.to('mm')
        if isinstance(self.threaded_member, Nut):
            total += self.threaded_member.height.to('mm')
        elif isinstance(self.threaded_member, ThreadedPlate):
            total += self.threaded_member.thickness.to('mm')
        # Return in the same units as the first component for consistency
        if self.clamped_components:
            return total.to(self.clamped_components[0].thickness.units)
        return total

    @property
    def grip_length(self) ->Quantity:
        """Calculate the grip length of the assembly.

    The grip length is the total thickness of all clamped components,
    not including the threaded member (nut or threaded plate).

    Returns:
        Grip length with units
    """
        total = 0 * ureg.mm
        # Convert all thicknesses to mm for consistent addition
        for component in self.clamped_components:
            total += component.thickness.to('mm')
        # Return in the same units as the first component for consistency
        if self.clamped_components:
            return total.to(self.clamped_components[0].thickness.units)
        return total

    def add_clamped_component(self, component: ClampedComponent) ->None:
        """Add a clamped component to the assembly.

    Args:
        component: The component to add

    Raises:
        ValueError: If component is invalid or duplicate
    """
        if component in self.clamped_components:
            raise ValueError('Component already exists in assembly')
        self.clamped_components.append(component)
        self.validate_assembly()

    def remove_clamped_component(self, index: int) ->ClampedComponent:
        """Remove a clamped component from the assembly.

    Args:
        index: Index of component to remove

    Returns:
        The removed component

    Raises:
        IndexError: If index is invalid
    """
        removed = self.clamped_components.pop(index)
        self.validate_assembly()
        return removed

    def set_fastener(self, fastener: Fastener) ->None:
        """Update the fastener component.

    Args:
        fastener: New fastener component

    Raises:
        ValueError: If new fastener is incompatible
    """
        self.fastener = fastener
        self.validate_assembly()

    def set_threaded_member(self, member: Union[Nut, ThreadedPlate]) ->None:
        """Update the threaded member.

    Args:
        member: New threaded member

    Raises:
        ValueError: If new member is incompatible
    """
        self.threaded_member = member
        self.validate_assembly()

    @property
    def stack_up_thickness(self) ->Quantity:
        """Get the total stack-up thickness of the assembly.

    Returns:
        Total thickness of all components in the assembly with units
    """
        return self.calculate_stack_up()


__all__ = ['Junction']

from typing import List, Union, Optional
from units_config import ureg
from components.threaded_components import Fastener, Nut
from components.threaded_plate import ThreadedPlate
from components.clamped_components import ClampedComponent
from enum import Enum
from math import log, pi
from typing import List, Union, Optional, Tuple
Quantity = ureg.Quantity
ThreadedMember = Union[Nut, ThreadedPlate]



class Junction:
    """A class representing a mechanical fastener junction.

    Manages the assembly of a fastener, clamped components, and a threaded member (nut or threaded plate).
    Provides validation and calculations for the assembly.

    Attributes:
        fastener: The fastener (bolt) used in the junction
        clamped_components: List of components being clamped
        threaded_member: The threaded member (nut or threaded plate) that mates with the fastener
    """

    class JointConfiguration(Enum):
        """Enum representing different joint configurations per NASA-TM-106943.
        THROUGH_BOLT: Standard through-bolt configuration
        FLAT_HEAD_THROUGH: Flat head fastener in through-hole configuration
        THREADED_END: Threaded end (blind hole) configuration
        FLAT_HEAD_THREADED: Flat head fastener in threaded hole configuration
        """
        THROUGH_BOLT = 1
        FLAT_HEAD_THROUGH = 2
        THREADED_END = 3
        FLAT_HEAD_THREADED = 4

    def __init__(self, fastener: Fastener, clamped_components: List[
        ClampedComponent], threaded_member: ThreadedMember):
        """Initialize a new Junction.

        Args:
            fastener: The fastener to use
            clamped_components: List of components to be clamped
            threaded_member: Threaded member (nut or threaded plate) to mate with fastener

        Raises:
            ValueError: If the assembly is invalid
        """
        if not clamped_components:
            raise ValueError('Must have at least one clamped component')
        self._fastener = None
        self._threaded_member = None
        self._clamped_components = []
        self.fastener = fastener
        self.threaded_member = threaded_member
        for component in clamped_components:
            self.add_clamped_component(component)
        self._validate_assembly()

    @property
    def fastener(self) ->Fastener:
        """The fastener used in the junction."""
        return self._fastener

    @fastener.setter
    def fastener(self, value: Fastener):
        if not isinstance(value, Fastener):
            raise ValueError('Fastener must be a Fastener instance')
        self._fastener = value

    @property
    def threaded_member(self) ->ThreadedMember:
        """The threaded member (nut or threaded plate) in the junction."""
        return self._threaded_member

    @threaded_member.setter
    def threaded_member(self, value: ThreadedMember):
        if not isinstance(value, (Nut, ThreadedPlate)):
            raise ValueError(
                'Threaded member must be a Nut or ThreadedPlate instance')
        self._threaded_member = value

    @property
    def clamped_components(self) ->List[ClampedComponent]:
        """List of components being clamped in the junction."""
        return self._clamped_components.copy()

    @property
    def grip_length(self) ->Quantity:
        """Calculate the total grip length of the assembly."""
        if not self._clamped_components:
            return 0 * ureg.inch
        base_unit = self._clamped_components[0].thickness.units
        return sum((comp.thickness.to(base_unit) for comp in self.
            _clamped_components), 0 * base_unit)

    @property
    def stack_up_thickness(self) ->Quantity:
        """Calculate the total stack-up thickness of the assembly.

        For nut assemblies: sum of all clamped components
        For threaded plate assemblies: sum of non-threaded components only

        Returns:
            Total stack-up thickness as a Quantity
        """
        if isinstance(self.threaded_member, ThreadedPlate):
            thickness = sum((comp.thickness for comp in self.
                _clamped_components if comp != self.threaded_member), 0 *
                ureg.mm)
        else:
            thickness = self.grip_length
        return thickness

    def add_clamped_component(self, component: ClampedComponent) ->None:
        """Add a clamped component to the junction.

        Args:
            component: The component to add

        Raises:
            ValueError: If the component is invalid
        """
        if not isinstance(component, ClampedComponent):
            raise ValueError('Component must be a ClampedComponent instance')
        self._clamped_components.append(component)
        self._validate_assembly()

    def remove_clamped_component(self, index: int) ->ClampedComponent:
        """Remove a clamped component from the junction.

        Args:
            index: Index of the component to remove

        Returns:
            The removed component

        Raises:
            ValueError: If removing the component would make the assembly invalid
            IndexError: If the index is out of range
        """
        if len(self._clamped_components) <= 1:
            raise ValueError('Cannot remove last clamped component')
        component = self._clamped_components.pop(index)
        try:
            self._validate_assembly()
        except ValueError as e:
            self._clamped_components.insert(index, component)
            raise ValueError(
                f'Removing component would make assembly invalid: {str(e)}')
        return component

    def set_fastener(self, fastener: Fastener) ->None:
        """Update the fastener in the junction.

        Args:
            fastener: The new fastener

        Raises:
            ValueError: If the new fastener would make the assembly invalid
        """
        old_fastener = self._fastener
        self.fastener = fastener
        try:
            self._validate_assembly()
        except ValueError as e:
            self._fastener = old_fastener
            raise ValueError(
                f'New fastener would make assembly invalid: {str(e)}')

    def set_threaded_member(self, member: ThreadedMember) ->None:
        """Update the threaded member in the junction.

        Args:
            member: The new threaded member

        Raises:
            ValueError: If the new member would make the assembly invalid
        """
        old_member = self._threaded_member
        self.threaded_member = member
        try:
            self._validate_assembly()
        except ValueError as e:
            self._threaded_member = old_member
            raise ValueError(
                f'New threaded member would make assembly invalid: {str(e)}')

    def _validate_assembly(self) ->None:
        """Validate the complete assembly.

        Raises:
            ValueError: If the assembly is invalid
        """
        if (not self._fastener or not self._threaded_member or not self.
            _clamped_components):
            raise ValueError(
                'Assembly must have fastener, threaded member, and at least one clamped component'
                )
        if self._fastener.thread_spec != self._threaded_member.thread_spec:
            raise ValueError(
                'Thread specifications must match between fastener and threaded member'
                )
        fastener_material = self._fastener.material
        threaded_material = self._threaded_member.material
        if not hasattr(fastener_material, 'yield_strength') or not hasattr(
            threaded_material, 'yield_strength'):
            raise ValueError(
                'Both fastener and threaded member materials must have yield strengths defined'
                )
        thread_engagement = self._calculate_thread_engagement()
        if '-' in self._fastener.thread_spec:
            fraction_str = self._fastener.thread_spec.split('-')[0]
            if '/' in fraction_str:
                num, denom = map(float, fraction_str.split('/'))
                nominal_diameter = num / denom * ureg.inch
            else:
                nominal_diameter = float(fraction_str) * ureg.inch
        else:
            nominal_diameter = float(self._fastener.thread_spec.strip('M').
                split('x')[0]) * ureg.mm
        min_engagement = 0.5 * nominal_diameter
        if thread_engagement < min_engagement:
            raise ValueError(
                f'Insufficient thread engagement. Minimum required: {min_engagement}, actual: {thread_engagement}'
                )
        required_length = self.stack_up_thickness
        if isinstance(self._threaded_member, Nut):
            required_length += self._threaded_member.height
        if self._fastener.length <= required_length:
            raise ValueError('Fastener length insufficient for assembly')

    def _calculate_thread_engagement(self) ->Quantity:
        """Calculate the thread engagement length between fastener and threaded member.

        Returns:
            The length of thread engagement as a Quantity
        """
        return min(self._threaded_member.threaded_length, self._fastener.
            threaded_length)

    def calculate_bolt_stiffness(self) ->Quantity:
        """Calculate bolt stiffness per NASA-STD-5020.

        Returns:
            Bolt stiffness (k_b) as a Quantity
        """
        area = 0.25 * 3.14159 * self.fastener._nominal_diameter ** 2
        length = self.grip_length
        modulus = self.fastener.material.elastic_modulus
        return area * modulus / length

    def calculate_joint_stiffness(self) ->Quantity:
        """Calculate joint stiffness per NASA-STD-5020.

        Returns:
            Joint stiffness (k_c) as a Quantity
        """
        return 3.0 * self.calculate_bolt_stiffness()

    @property
    def configuration_type(self) ->'Junction.JointConfiguration':
        """Determine the joint configuration type based on component properties.

    Returns:
        JointConfiguration: The type of joint configuration per NASA-TM-106943
    """
        is_flat_head = hasattr(self.fastener, 'is_flat_head'
            ) and self.fastener.is_flat_head
        is_threaded_end = isinstance(self.threaded_member, ThreadedPlate)
        if is_flat_head and is_threaded_end:
            return self.JointConfiguration.FLAT_HEAD_THREADED
        elif is_flat_head:
            return self.JointConfiguration.FLAT_HEAD_THROUGH
        elif is_threaded_end:
            return self.JointConfiguration.THREADED_END
        else:
            return self.JointConfiguration.THROUGH_BOLT

    def _get_configuration_parameters(self) ->Tuple[Quantity, Quantity,
        Quantity]:
        """Calculate configuration-specific parameters needed for stiffness calculations.

    Returns:
        Tuple containing:
        - L: Effective length for stiffness calculation
        - D: Nominal diameter
        - E_j: Joint material modulus (effective)
    """
        config = self.configuration_type
        D = self.fastener._nominal_diameter
        thicknesses = [comp.thickness for comp in self._clamped_components]
        moduli = [comp.material.elastic_modulus for comp in self.
            _clamped_components]
        if config == self.JointConfiguration.THROUGH_BOLT:
            L = sum(thicknesses)
            sum_l_E = sum(l / E for l, E in zip(thicknesses, moduli))
            E_j = L / (2 * pi) / sum_l_E
        elif config == self.JointConfiguration.FLAT_HEAD_THROUGH:
            h = self.fastener.head_height if hasattr(self.fastener,
                'head_height') else 0 * ureg.mm
            L = sum(thicknesses) - h / 2
            sum_l_E = sum(l / E for l, E in zip(thicknesses, moduli))
            E_j = L / sum_l_E ** 0.5
        elif config == self.JointConfiguration.THREADED_END:
            thread_length = self.threaded_member.threaded_length
            L = sum(thicknesses[:-1]) + (thicknesses[-1] - thread_length / 2)
            sum_l_E = sum(l / E for l, E in zip(thicknesses[:-1], moduli[:-1]))
            sum_l_E += (thicknesses[-1] - thread_length / 2) / moduli[-1]
            E_j = L / sum_l_E
        else:
            h = self.fastener.head_height if hasattr(self.fastener,
                'head_height') else 0 * ureg.mm
            thread_length = self.threaded_member.threaded_length
            L = thicknesses[0] - h / 2 + sum(thicknesses[1:-1]) + (thicknesses
                [-1] - thread_length / 2)
            sum_l_E = (thicknesses[0] - h / 2) / moduli[0]
            sum_l_E += sum(l / E for l, E in zip(thicknesses[1:-1], moduli[
                1:-1]))
            sum_l_E += (thicknesses[-1] - thread_length / 2) / moduli[-1]
            E_j = L / sum_l_E
        return L, D, E_j

    def calculate_bolt_stiffness(self) ->Quantity:
        """Calculate bolt stiffness per NASA-TM-106943.

    Returns:
        Bolt stiffness (K_b) as a Quantity
    """
        L, D, _ = self._get_configuration_parameters()
        A = 0.25 * pi * D ** 2
        E_b = self.fastener.material.elastic_modulus
        K_b = A * E_b / L
        return K_b

    def calculate_joint_stiffness(self) ->Quantity:
        """Calculate joint stiffness per NASA-TM-106943.

    Returns:
        Joint stiffness (K_j) as a Quantity
    """
        L, D, E_j = self._get_configuration_parameters()
        config = self.configuration_type
        if config == self.JointConfiguration.THROUGH_BOLT:
            K_j = pi * E_j * D / (2 * log((L + 0.5 * D) / (L + 2.5 * D)))
        elif config == self.JointConfiguration.FLAT_HEAD_THROUGH:
            d_h = self.fastener.head_diameter if hasattr(self.fastener,
                'head_diameter') else 1.5 * D
            d_w = (d_h + D) / 2
            numerator = (L + d_w - D) * (d_w + D) * (L + 0.5 * D)
            denominator = (L + d_w + D) * (d_w - D) * (L + 2.5 * D)
            K_j = pi * E_j * D / log(numerator / denominator)
        elif config == self.JointConfiguration.THREADED_END:
            K_j = pi * E_j * D / log((2.0 * L + 0.5 * D) / (2.0 * L + 2.5 * D))
        else:
            d_h = self.fastener.head_diameter if hasattr(self.fastener,
                'head_diameter') else 1.5 * D
            d_w = (d_h + D) / 2
            numerator = (L + d_w - D) * (d_w + D)
            denominator = (L + d_w + D) * (d_w - D)
            K_j = pi * E_j * D / log(numerator / denominator)
        return K_j

    def calculate_stiffness_factor(self) ->float:
        """Calculate the stiffness factor (Φ) per NASA-TM-106943 equation 29.

    Returns:
        Stiffness factor (Φ) as a dimensionless float
    """
        K_b = self.calculate_bolt_stiffness()
        K_j = self.calculate_joint_stiffness()
        return float(K_b / (K_b + K_j))

    def calculate_loading_plane_factor(self) ->float:
        """Calculate the loading plane factor (n) per NASA-TM-106943.

    Returns:
        Loading plane factor (n) as a dimensionless float
    """
        config = self.configuration_type
        thicknesses = [comp.thickness for comp in self._clamped_components]
        total_thickness = sum(thicknesses)
        if config == self.JointConfiguration.THROUGH_BOLT:
            numerator = sum(thicknesses[:-1]) + thicknesses[-1] / 2
            n = float(numerator / total_thickness)
        elif config == self.JointConfiguration.FLAT_HEAD_THROUGH:
            h = self.fastener.head_height if hasattr(self.fastener,
                'head_height') else 0 * ureg.mm
            numerator = thicknesses[0] - h / 2 + sum(thicknesses[1:-1]
                ) + thicknesses[-1] / 2
            n = float(numerator / total_thickness)
        elif config == self.JointConfiguration.THREADED_END:
            thread_length = self.threaded_member.threaded_length
            numerator = sum(thicknesses[:-1]) + (thicknesses[-1] - 
                thread_length / 2)
            n = float(numerator / total_thickness)
        else:
            h = self.fastener.head_height if hasattr(self.fastener,
                'head_height') else 0 * ureg.mm
            thread_length = self.threaded_member.threaded_length
            numerator = thicknesses[0] - h / 2 + sum(thicknesses[1:-1]) + (
                thicknesses[-1] - thread_length / 2)
            n = float(numerator / total_thickness)
        return n

from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from units_config import ureg, Quantity
from typing import List, ClassVar, Tuple
from utils.unit_utils import ureg, Quantity


@dataclass
class Environment:
    """Environmental and loading conditions for fastener analysis.

    All attributes are Pint Quantities with appropriate units:
    - Forces in N or lbf
    - Moments in N⋅m or lbf⋅ft  
    - Temperatures in K or °R
    - Torques in N⋅m or lbf⋅ft

    Attributes:
        tension: Axial load along fastener
        shear: Shear load perpendicular to fastener
        bending: Bending moment on fastener
        min_temp: Minimum environmental temperature
        nom_temp: Nominal assembly temperature  
        max_temp: Maximum environmental temperature
        preload_torque: Installation torque
    """
    ABSOLUTE_ZERO: ClassVar[Quantity] = ureg.Quantity(0, 'kelvin')
    FORCE_UNITS: ClassVar[Tuple[str, ...]] = ('newton', 'lbf')
    MOMENT_UNITS: ClassVar[Tuple[str, ...]] = ('newton * meter', 'foot * lbf')
    TEMP_UNITS: ClassVar[Tuple[str, ...]] = ('kelvin', 'rankine')
    VALID_AXES: ClassVar[Tuple[str, ...]] = ('x', 'y', 'z')
    tension: Quantity
    shear: Quantity
    bending: Quantity
    min_temp: Quantity
    nom_temp: Quantity
    max_temp: Quantity
    preload_torque: Quantity

    def __post_init__(self) ->None:
        """Validate all inputs upon initialization."""
        self.validate()

    def validate(self) ->None:
        """Validate all environment parameters.

        Checks:
        - All temperatures are above absolute zero
        - Preload torque is positive
        - All quantities have correct units

        Raises:
            ValueError: If any validation check fails
        """
        for temp in (self.min_temp, self.nom_temp, self.max_temp):
            if not isinstance(temp, Quantity):
                raise ValueError(f'Temperature {temp} must be a Pint Quantity')
            if temp.to_base_units().units not in (ureg.kelvin, ureg.rankine):
                raise ValueError(f'Temperature {temp} must be in K or °R')
            if temp <= self.ABSOLUTE_ZERO:
                raise ValueError(
                    f'Temperature {temp} must be above absolute zero')
        for force in (self.tension, self.shear):
            if not isinstance(force, Quantity):
                raise ValueError(f'Force {force} must be a Pint Quantity')
            if force.dimensionality != ureg.newton.dimensionality:
                raise ValueError(f'Force {force} must have force units (N or lbf)')
        for moment in (self.bending, self.preload_torque):
            if not isinstance(moment, Quantity):
                raise ValueError(f'Moment {moment} must be a Pint Quantity')
            if moment.dimensionality != (ureg.newton * ureg.meter).dimensionality:
                raise ValueError(f'Moment {moment} must have moment units (N⋅m or lbf⋅ft)')
        if self.preload_torque <= 0:
            raise ValueError('Preload torque must be positive')

    @classmethod
    def set_force_from_6dof(cls, forces: List[Quantity], moments: List[
        Quantity], fastener_axis: str) ->'Environment':
        """Create Environment from 6DOF forces and moments.

        Args:
            forces: List of [Fx, Fy, Fz] forces as Quantities
            moments: List of [Mx, My, Mz] moments as Quantities
            fastener_axis: Axis of fastener ('x', 'y', or 'z')

        Returns:
            New Environment instance with converted loads

        Raises:
            ValueError: If inputs are invalid or axis is not 'x', 'y', or 'z'
        """
        if len(forces) != 3 or len(moments) != 3:
            raise ValueError('Forces and moments must be lists of length 3')
        if fastener_axis not in cls.VALID_AXES:
            raise ValueError(f'Fastener axis must be one of {cls.VALID_AXES}')
        f_array = np.array([f.to_base_units().magnitude for f in forces])
        m_array = np.array([m.to_base_units().magnitude for m in moments])
        axis_idx = {'x': 0, 'y': 1, 'z': 2}[fastener_axis]
        axis_vector = np.zeros(3)
        axis_vector[axis_idx] = 1
        tension = f_array[axis_idx] * forces[0].units
        f_perp = f_array - f_array[axis_idx] * axis_vector
        shear = np.sqrt(np.sum(f_perp ** 2)) * forces[0].units
        m_perp = m_array - m_array[axis_idx] * axis_vector
        bending = np.sqrt(np.sum(m_perp ** 2)) * moments[0].units
        return cls(tension=tension, shear=shear, bending=bending, min_temp=
            300 * ureg.kelvin, nom_temp=300 * ureg.kelvin, max_temp=300 *
            ureg.kelvin, preload_torque=1 * ureg.newton * ureg.meter)

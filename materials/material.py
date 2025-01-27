from abc import ABC, abstractmethod
from typing import Optional
import pint
from units_config import ureg
from typing import Dict, Any
from units_config import ureg, Quantity




class Material(ABC):
    """Abstract base class for all materials in the system.

    This class provides the foundation for all material definitions, ensuring proper
    unit handling and validation of material properties. All properties use pint units
    and support both imperial and metric systems.
    """

    def __init__(self):
        """Initialize a new Material instance with None values."""
        self._yield_strength: Optional[Quantity] = None
        self._ultimate_strength: Optional[Quantity] = None
        self._density: Optional[Quantity] = None
        self._poisson_ratio: Optional[float] = None
        self._elastic_modulus: Optional[Quantity] = None
        self._thermal_expansion: Optional[Quantity] = None

    def _validate_stress_units(self, value: Quantity, name: str) ->Quantity:
        """Validate that a value has stress units and convert to Pa.

        Args:
            value: Value to validate
            name: Name of the property for error messages

        Returns:
            Quantity: Value converted to Pa

        Raises:
            TypeError: If value is not a Quantity or has wrong units
        """
        if not isinstance(value, Quantity):
            raise TypeError(f'{name} must be a Quantity with stress units')
        try:
            return value.to('Pa')
        except:
            raise TypeError(f'{name} must have stress units')

    def _validate_positive(self, value: Quantity, name: str) ->None:
        """Validate that a value is positive.

        Args:
            value: Value to validate
            name: Name of the property for error messages

        Raises:
            ValueError: If value is not positive
        """
        if value.magnitude <= 0:
            raise ValueError(f'{name} must be positive')

    @property
    def yield_strength(self) ->Quantity:
        """Get the material yield strength."""
        if self._yield_strength is None:
            raise ValueError('Yield strength has not been set')
        return self._yield_strength

    @yield_strength.setter
    def yield_strength(self, value: Quantity):
        """Set the material yield strength."""
        value_pa = self._validate_stress_units(value, 'Yield strength')
        self._validate_positive(value_pa, 'Yield strength')
        if (self._ultimate_strength is not None and value_pa.magnitude >=
            self._ultimate_strength.to('Pa').magnitude):
            raise ValueError(
                'Yield strength must be less than ultimate strength')
        self._yield_strength = value_pa

    @property
    def ultimate_strength(self) ->Quantity:
        """Get the material ultimate strength."""
        if self._ultimate_strength is None:
            raise ValueError('Ultimate strength has not been set')
        return self._ultimate_strength

    @ultimate_strength.setter
    def ultimate_strength(self, value: Quantity):
        """Set the material ultimate strength."""
        value_pa = self._validate_stress_units(value, 'Ultimate strength')
        self._validate_positive(value_pa, 'Ultimate strength')
        if (self._yield_strength is not None and value_pa.magnitude <= self
            ._yield_strength.to('Pa').magnitude):
            raise ValueError(
                'Ultimate strength must be greater than yield strength')
        self._ultimate_strength = value_pa

    @property
    def density(self) ->Quantity:
        """Get the material density."""
        if self._density is None:
            raise ValueError('Density has not been set')
        return self._density

    @density.setter
    def density(self, value: Quantity):
        """Set the material density."""
        if not isinstance(value, Quantity):
            raise TypeError('Density must be a Quantity with density units')
        try:
            value_kgm3 = value.to('kg/m^3')
        except:
            raise TypeError('Density must have mass/volume units')
        self._validate_positive(value_kgm3, 'Density')
        self._density = value_kgm3

    @property
    def poisson_ratio(self) ->float:
        """Get the material Poisson's ratio."""
        if self._poisson_ratio is None:
            raise ValueError("Poisson's ratio has not been set")
        return self._poisson_ratio

    @poisson_ratio.setter
    def poisson_ratio(self, value: float):
        """Set the material Poisson's ratio."""
        if not isinstance(value, (int, float)):
            raise TypeError("Poisson's ratio must be a number")
        if value <= 0 or value >= 0.5:
            raise ValueError("Poisson's ratio must be between 0 and 0.5")
        self._poisson_ratio = float(value)

    @property
    def elastic_modulus(self) ->Quantity:
        """Get the material elastic modulus."""
        if self._elastic_modulus is None:
            raise ValueError('Elastic modulus has not been set')
        return self._elastic_modulus

    @elastic_modulus.setter
    def elastic_modulus(self, value: Quantity):
        """Set the material elastic modulus."""
        if not isinstance(value, Quantity):
            raise TypeError(
                'Elastic modulus must be a Quantity with stress units')
        try:
            value_pa = value.to('Pa')
        except:
            raise TypeError('Elastic modulus must have stress units')
        if value_pa.magnitude <= 0:
            raise ValueError('Elastic modulus must be positive')
        self._elastic_modulus = value_pa

    @property
    def thermal_expansion(self) ->Quantity:
        """Get the material coefficient of thermal expansion."""
        if self._thermal_expansion is None:
            raise ValueError('Thermal expansion coefficient has not been set')
        return self._thermal_expansion

    @thermal_expansion.setter
    def thermal_expansion(self, value: Quantity):
        """Set the material coefficient of thermal expansion."""
        if not isinstance(value, Quantity):
            raise TypeError(
                'Thermal expansion coefficient must be a Quantity with 1/temperature units'
                )
        try:
            value_k = value.to('1/K')
        except:
            raise TypeError(
                'Thermal expansion coefficient must have 1/temperature units')
        if value_k.magnitude <= 0:
            raise ValueError('Thermal expansion coefficient must be positive')
        self._thermal_expansion = value_k

    @abstractmethod
    def identify(self) ->str:
        """Return a string identifying the specific material."""
        pass

from typing import Optional
import pint
from units_config import ureg
from materials.material import Material


class GenericSteel(Material):
    """Generic structural steel material with standard properties.

    This class represents a generic structural steel with typical material properties
    based on common structural steel grades. Values are based on general purpose
    structural steel properties.

    Standard values:
    - Yield strength: 250 MPa (36 ksi)
    - Ultimate strength: 400 MPa (58 ksi)
    - Density: 7850 kg/m³ (0.284 lb/in³)
    - Poisson's ratio: 0.29
    - Modulus of elasticity: 200 GPa (29000 ksi)
    - Coefficient of thermal expansion: 11.7e-6 /K

    All properties can be modified after instantiation while maintaining
    material-specific constraints.

    Example:
        >>> steel = GenericSteel()
        >>> print(steel.yield_strength.to('ksi'))
        36.259 ksi
        >>> steel.yield_strength = 300 * ureg.megapascal
        >>> print(steel.yield_strength.to('ksi'))
        43.511 ksi

    Sources:
    - ASTM A36 Steel properties
    - Standard structural steel handbooks
    """

    def __init__(self):
        """Initialize GenericSteel with standard property values."""
        super().__init__()
        self.yield_strength = 250 * ureg.megapascal
        self.ultimate_strength = 400 * ureg.megapascal
        self.density = 7850 * ureg('kg/m^3')
        self.poisson_ratio = 0.29
        self.elastic_modulus = 200 * ureg.gigapascal
        self.thermal_expansion = 1.17e-05 * ureg('1/K')

    def identify(self) ->str:
        """Return material identification string.

        Returns:
            str: Material identification string
        """
        return 'Generic Structural Steel'


class GenericAluminum(Material):
    """Generic aluminum material with standard properties.

    This class represents a generic aluminum with typical material properties
    based on common aluminum alloy grades. Values are based on general purpose
    aluminum alloy properties (similar to 6061-T6).

    Standard values:
    - Yield strength: 276 MPa (40 ksi)
    - Ultimate strength: 310 MPa (45 ksi)
    - Density: 2700 kg/m³ (0.098 lb/in³)
    - Poisson's ratio: 0.33
    - Modulus of elasticity: 69 GPa (10000 ksi)
    - Coefficient of thermal expansion: 23.1e-6 /K

    All properties can be modified after instantiation while maintaining
    material-specific constraints.

    Example:
        >>> aluminum = GenericAluminum()
        >>> print(aluminum.density.to('lb/in^3'))
        0.098 pound / inch ** 3
        >>> aluminum.yield_strength = 290 * ureg.megapascal
        >>> print(aluminum.yield_strength.to('ksi'))
        42.069 ksi

    Sources:
    - Standard aluminum alloy handbooks
    - Common 6061-T6 aluminum properties
    """

    def __init__(self):
        """Initialize GenericAluminum with standard property values."""
        super().__init__()
        self.yield_strength = 276 * ureg.megapascal
        self.ultimate_strength = 310 * ureg.megapascal
        self.density = 2700 * ureg('kg/m^3')
        self.poisson_ratio = 0.33
        self.elastic_modulus = 69 * ureg.gigapascal
        self.thermal_expansion = 2.31e-05 * ureg('1/K')

    def identify(self) ->str:
        """Return material identification string.

        Returns:
            str: Material identification string
        """
        return 'Generic Aluminum'

"""Standard material definitions.

This module provides pre-configured Material instances for common materials
used in structural analysis.
"""

from units_config import ureg
from materials.material import Material

# Generic structural steel based on ASTM A36 properties
GenericSteel = Material("Generic Structural Steel")
GenericSteel.yield_strength = 250 * ureg.megapascal
GenericSteel.ultimate_strength = 400 * ureg.megapascal
GenericSteel.density = 7850 * ureg('kg/m^3')
GenericSteel.poisson_ratio = 0.29
GenericSteel.elastic_modulus = 200 * ureg.gigapascal
GenericSteel.thermal_expansion = 1.17e-05 * ureg('1/K')

# Generic aluminum based on 6061-T6 properties
GenericAluminum = Material("Generic Aluminum (6061-T6)")
GenericAluminum.yield_strength = 276 * ureg.megapascal
GenericAluminum.ultimate_strength = 310 * ureg.megapascal
GenericAluminum.density = 2700 * ureg('kg/m^3')
GenericAluminum.poisson_ratio = 0.33
GenericAluminum.elastic_modulus = 69 * ureg.gigapascal
GenericAluminum.thermal_expansion = 2.31e-05 * ureg('1/K')

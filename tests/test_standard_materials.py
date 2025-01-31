import unittest
from units_config import ureg
from materials.material import Material
from materials.standard_materials import GenericSteel, GenericAluminum


class TestStandardMaterials(unittest.TestCase):
    """Test cases for standard materials classes."""

    def setUp(self):
        """Set up test cases."""
        # Create fresh copies of the standard materials for testing
        self.steel = Material("Generic Structural Steel")
        self.steel.yield_strength = 250 * ureg.megapascal
        self.steel.ultimate_strength = 400 * ureg.megapascal
        self.steel.density = 7850 * ureg('kg/m^3')
        self.steel.poisson_ratio = 0.29
        self.steel.elastic_modulus = 200 * ureg.gigapascal
        self.steel.thermal_expansion = 1.17e-05 * ureg('1/K')

        self.aluminum = Material("Generic Aluminum (6061-T6)")
        self.aluminum.yield_strength = 276 * ureg.megapascal
        self.aluminum.ultimate_strength = 310 * ureg.megapascal
        self.aluminum.density = 2700 * ureg('kg/m^3')
        self.aluminum.poisson_ratio = 0.33
        self.aluminum.elastic_modulus = 69 * ureg.gigapascal
        self.aluminum.thermal_expansion = 2.31e-05 * ureg('1/K')

    def test_steel_default_values(self):
        """Test GenericSteel default property values."""
        self.assertAlmostEqual(self.steel.yield_strength.to('MPa').
            magnitude, 250)
        self.assertAlmostEqual(self.steel.ultimate_strength.to('MPa').
            magnitude, 400)
        self.assertAlmostEqual(self.steel.density.to('kg/m^3').magnitude, 7850)
        self.assertAlmostEqual(self.steel.poisson_ratio, 0.29)
        self.assertAlmostEqual(self.steel.elastic_modulus.to('GPa').
            magnitude, 200)
        self.assertAlmostEqual(self.steel.thermal_expansion.to('1/K').
            magnitude, 1.17e-05)
        self.assertEqual(self.steel.name, 'Generic Structural Steel')

    def test_aluminum_default_values(self):
        """Test GenericAluminum default property values."""
        self.assertAlmostEqual(self.aluminum.yield_strength.to('MPa').
            magnitude, 276)
        self.assertAlmostEqual(self.aluminum.ultimate_strength.to('MPa').
            magnitude, 310)
        self.assertAlmostEqual(self.aluminum.density.to('kg/m^3').magnitude,
            2700)
        self.assertAlmostEqual(self.aluminum.poisson_ratio, 0.33)
        self.assertAlmostEqual(self.aluminum.elastic_modulus.to('GPa').
            magnitude, 69)
        self.assertAlmostEqual(self.aluminum.thermal_expansion.to('1/K').
            magnitude, 2.31e-05)
        self.assertEqual(self.aluminum.name, 'Generic Aluminum (6061-T6)')

    def test_steel_unit_conversions(self):
        """Test GenericSteel property unit conversions."""
        self.assertAlmostEqual(self.steel.yield_strength.to('ksi').
            magnitude, 36.259, places=3)
        self.assertAlmostEqual(self.steel.ultimate_strength.to('ksi').
            magnitude, 58.015, places=3)
        self.assertAlmostEqual(self.steel.density.to('lb/in^3').magnitude, 
            0.284, places=3)
        self.assertAlmostEqual(self.steel.elastic_modulus.to('ksi').
            magnitude, 29007.547, places=0)

    def test_aluminum_unit_conversions(self):
        """Test GenericAluminum property unit conversions."""
        self.assertAlmostEqual(self.aluminum.yield_strength.to('ksi').
            magnitude, 40.03, places=3)
        self.assertAlmostEqual(self.aluminum.ultimate_strength.to('ksi').
            magnitude, 44.962, places=3)
        self.assertAlmostEqual(self.aluminum.density.to('lb/in^3').
            magnitude, 0.098, places=3)
        self.assertAlmostEqual(self.aluminum.elastic_modulus.to('ksi').
            magnitude, 10007.605, places=0)

    def test_property_modification(self):
        """Test property modification with validation."""
        new_yield = 300 * ureg.megapascal
        self.steel.yield_strength = new_yield
        self.assertEqual(self.steel.yield_strength, new_yield)
        new_density = 2720 * ureg('kg/m^3')
        self.aluminum.density = new_density
        self.assertEqual(self.aluminum.density, new_density)

    def test_steel_validation(self):
        """Test steel property validation."""
        with self.assertRaises(ValueError):
            self.steel.yield_strength = 500 * ureg.megapascal
        with self.assertRaises(ValueError):
            self.steel.poisson_ratio = 0.6
        with self.assertRaises(TypeError):
            self.steel.yield_strength = 250 * ureg.kelvin

    def test_aluminum_validation(self):
        """Test aluminum property validation."""
        with self.assertRaises(ValueError):
            self.aluminum.yield_strength = 400 * ureg.megapascal
        with self.assertRaises(ValueError):
            self.aluminum.poisson_ratio = 0.6
        with self.assertRaises(TypeError):
            self.aluminum.density = 2700 * ureg.pascal

    def test_unit_compatibility(self):
        """Test unit compatibility and conversions."""
        steel_yield = self.steel.yield_strength
        self.assertTrue(steel_yield.check('[force]/[length]^2'))
        steel_density = self.steel.density
        self.assertTrue(steel_density.check('[mass]/[length]^3'))
        al_modulus = self.aluminum.elastic_modulus
        self.assertTrue(al_modulus.check('[force]/[length]^2'))
        al_thermal = self.aluminum.thermal_expansion
        self.assertTrue(al_thermal.check('1/[temperature]'))

"""Test cases for the Material base class."""

import unittest
from materials.material import Material
from units_config import ureg
import pint


class ConcreteMaterial(Material):
    """Concrete implementation of Material for testing."""
    
    def identify(self) -> str:
        """Return material identification."""
        return "Test Material"


class TestMaterial(unittest.TestCase):
    """Test cases for the Material base class."""

    def setUp(self):
        """Set up test fixtures."""
        self.material = ConcreteMaterial()

    def test_yield_strength(self):
        """Test yield strength property."""
        self.material.yield_strength = 250000000.0 * ureg.Pa
        self.assertEqual(self.material.yield_strength, 250000000.0 * ureg.Pa)
        self.material.yield_strength = 36000 * ureg.psi
        converted_pa = self.material.yield_strength.to('Pa').magnitude
        expected_pa = 248211280
        percent_diff = abs(converted_pa - expected_pa) / expected_pa * 100
        self.assertLess(percent_diff, 0.01,
            f'PSI to Pa conversion error too large: {percent_diff}%')
        with self.assertRaises(ValueError):
            self.material.yield_strength = -100 * ureg.Pa
        with self.assertRaises(TypeError):
            self.material.yield_strength = 100
        with self.assertRaises(TypeError):
            self.material.yield_strength = 100 * ureg.meter

    def test_ultimate_strength(self):
        """Test ultimate strength property."""
        self.material.ultimate_strength = 400000000.0 * ureg.Pa
        self.assertEqual(self.material.ultimate_strength, 400000000.0 * ureg.Pa)
        self.material.yield_strength = 300000000.0 * ureg.Pa
        with self.assertRaises(ValueError):
            self.material.ultimate_strength = 200000000.0 * ureg.Pa

    def test_density(self):
        """Test density property."""
        self.material.density = 7800 * ureg('kg/m^3')
        self.assertEqual(self.material.density, 7800 * ureg('kg/m^3'))
        self.material.density = 0.28 * ureg('lb/in^3')
        converted_density = self.material.density.to('kg/m^3').magnitude
        expected_density = 7750
        percent_diff = abs(converted_density - expected_density) / expected_density * 100
        self.assertLess(percent_diff, 0.01,
            f'Density conversion error too large: {percent_diff}%')
        with self.assertRaises(ValueError):
            self.material.density = -100 * ureg('kg/m^3')

    def test_poisson_ratio(self):
        """Test Poisson's ratio property."""
        self.material.poisson_ratio = 0.3
        self.assertEqual(self.material.poisson_ratio, 0.3)
        with self.assertRaises(ValueError):
            self.material.poisson_ratio = 0
        with self.assertRaises(ValueError):
            self.material.poisson_ratio = 0.51

    def test_elastic_modulus(self):
        """Test elastic modulus property."""
        self.material.elastic_modulus = 200000000000.0 * ureg.Pa
        self.assertEqual(self.material.elastic_modulus, 200000000000.0 * ureg.Pa)
        self.material.elastic_modulus = 29007548.8 * ureg.psi
        self.assertAlmostEqual(
            self.material.elastic_modulus.to('Pa').magnitude,
            200000000000.0,
            delta=1000000.0,  # Allow 1 MPa difference
            msg='PSI to Pa conversion error too large')
        with self.assertRaises(ValueError):
            self.material.elastic_modulus = -100 * ureg.Pa

    def test_thermal_expansion(self):
        """Test thermal expansion coefficient property."""
        self.material.thermal_expansion = 12e-6 / ureg.K
        self.assertEqual(self.material.thermal_expansion, 12e-6 / ureg.K)
        # Test with a different value in 1/K
        self.material.thermal_expansion = 13e-6 / ureg.K
        self.assertAlmostEqual(
            self.material.thermal_expansion.magnitude,
            13e-6,
            delta=1e-8,
            msg='Thermal expansion coefficient storage error')
        with self.assertRaises(ValueError):
            self.material.thermal_expansion = -1e-6 / ureg.K

    def test_property_access_before_setting(self):
        """Test accessing properties before they are set."""
        material = ConcreteMaterial()
        with self.assertRaises(ValueError):
            _ = material.yield_strength
        with self.assertRaises(ValueError):
            _ = material.ultimate_strength
        with self.assertRaises(ValueError):
            _ = material.density
        with self.assertRaises(ValueError):
            _ = material.elastic_modulus
        with self.assertRaises(ValueError):
            _ = material.thermal_expansion

    def test_identify(self):
        """Test material identification."""
        self.assertEqual(self.material.identify(), "Test Material")


if __name__ == '__main__':
    unittest.main()

import unittest
from pint import Quantity
from units_config import ureg
from utils.unit_utils import (
    to_imperial, to_metric, standardize_units, 
    is_valid_unit_type, are_units_compatible, validate_unit_dimension, 
    safe_add, safe_multiply, safe_divide, compare_with_tolerance, 
    format_quantity, format_with_units, format_unit_string
)


class TestUnitUtils(unittest.TestCase):
    """Test cases for unit_utils module."""

    def test_to_imperial(self):
        """Test conversion to imperial units."""
        # Test numeric conversions
        self.assertEqual(to_imperial(25.4 * ureg.millimeter), 1 * ureg.inch)
        self.assertTrue(compare_with_tolerance(to_imperial(4.44822 * ureg.newton), 1 * ureg.lbf, 1e-6))
        self.assertTrue(compare_with_tolerance(to_imperial(6894.76 * ureg.pascal), 1 * ureg.psi, 1e-6))
    
        # Test unit string formatting
        temp = to_imperial(300 * ureg.kelvin)
        self.assertEqual(format_unit_string(str(temp.units)), '°F')
    
        # Test other unit handling
        density = 1000 * ureg('kg/m^3')
        self.assertEqual(to_imperial(density).units, ureg('lb/inch^3').units)
        self.assertEqual(to_imperial(0.5 * ureg.dimensionless), 0.5 * ureg.dimensionless)
        with self.assertRaises(ValueError):
            to_imperial(1 * ureg.candela)

    def test_to_metric(self):
        """Test conversion to metric units."""
        # Test numeric conversions
        self.assertEqual(to_metric(1 * ureg.inch), 25.4 * ureg.millimeter)
        self.assertTrue(compare_with_tolerance(to_metric(1 * ureg.lbf), 4.44822 * ureg.newton, 1e-6))
    
        # Test unit string formatting
        psi = 1 * ureg.psi
        self.assertEqual(format_unit_string(str(to_metric(psi).units)), 'MPa')
        self.assertEqual(format_unit_string(str(to_metric(70 * ureg.kelvin).units)), '°C')
    
        # Test other unit handling
        density = 0.1 * ureg('lb/inch^3')
        self.assertEqual(to_metric(density).units, ureg('kg/m^3').units)
        self.assertEqual(to_metric(0.5 * ureg.dimensionless), 0.5 * ureg.dimensionless)
        with self.assertRaises(ValueError):
            to_metric(1 * ureg.candela)

    def test_standardize_units(self):
        """Test standardization to preferred unit system."""
        length = 25.4 * ureg.millimeter
        self.assertEqual(standardize_units(length, 'imperial'), 1 * ureg.inch)
        self.assertEqual(standardize_units(length, 'metric'), 25.4 * ureg.
            millimeter)
        with self.assertRaises(ValueError):
            standardize_units(length, 'invalid')

    def test_is_valid_unit_type(self):
        """Test unit type validation using dimensionality strings."""
        self.assertTrue(is_valid_unit_type(1 * ureg.meter, '[L]'))
        self.assertFalse(is_valid_unit_type(1 * ureg.newton, '[L]'))
        self.assertTrue(is_valid_unit_type(1 * ureg.newton, '[M][L]/[T]^2'))
        self.assertFalse(is_valid_unit_type(1 * ureg.meter, '[M][L]/[T]^2'))
        self.assertTrue(is_valid_unit_type(1 * ureg.pascal, '[M][L]/[T]^2/[L]^2'))
        self.assertTrue(is_valid_unit_type(1 * ureg.kelvin, '[T]'))
        self.assertTrue(is_valid_unit_type(1 * ureg('kg/m^3'), '[M]/[L]^3'))
        self.assertTrue(is_valid_unit_type(1 * ureg('1/K'), '1/[T]'))
        self.assertTrue(is_valid_unit_type(1 * ureg.dimensionless, ''))
        with self.assertRaises(ValueError):
            is_valid_unit_type(1 * ureg.meter, 'invalid')

    def test_are_units_compatible(self):
        """Test unit compatibility checking."""
        self.assertTrue(are_units_compatible(1 * ureg.meter, 1 * ureg.inch))
        self.assertTrue(are_units_compatible(1 * ureg.newton, 1 * ureg.lbf))
        self.assertFalse(are_units_compatible(1 * ureg.meter, 1 * ureg.newton))
        self.assertFalse(are_units_compatible(1 * ureg.second, 1 * ureg.kelvin)
            )

    def test_validate_unit_dimension(self):
        """Test dimension validation."""
        self.assertTrue(is_valid_unit_type(1 * ureg.meter, 'length'))
        self.assertTrue(validate_unit_dimension(1 * ureg('kg/m^3'),
            '[mass]/[length]^3'))
        self.assertFalse(validate_unit_dimension(1 * ureg.meter, '[mass]'))
        self.assertFalse(validate_unit_dimension(1 * ureg.meter, 'invalid'))

    def test_safe_add(self):
        """Test safe addition of quantities."""
        result = safe_add(1 * ureg.meter, 100 * ureg.centimeter)
        self.assertEqual(result, 2 * ureg.meter)
        with self.assertRaises(ValueError):
            safe_add(1 * ureg.meter, 1 * ureg.second)

    def test_safe_multiply(self):
        """Test safe multiplication of quantities."""
        force = 10 * ureg.newton
        distance = 2 * ureg.meter
        work = safe_multiply(force, distance)
        self.assertEqual(work, 20 * ureg.newton * ureg.meter)

    def test_safe_divide(self):
        """Test safe division of quantities."""
        distance = 10 * ureg.meter
        time = 2 * ureg.second
        speed = safe_divide(distance, time)
        self.assertEqual(speed, 5 * ureg.meter / ureg.second)
        with self.assertRaises(ValueError):
            safe_divide(distance, 0 * ureg.second)

    def test_compare_with_tolerance(self):
        """Test comparison with tolerance."""
        q1 = 1.0 * ureg.meter
        q2 = 1.001 * ureg.meter
        self.assertTrue(compare_with_tolerance(q1, q2, 0.01))
        q3 = 1.02 * ureg.meter
        self.assertFalse(compare_with_tolerance(q1, q3, 0.01))
        with self.assertRaises(ValueError):
            compare_with_tolerance(1 * ureg.meter, 1 * ureg.second, 0.01)

    def test_format_quantity(self):
        """Test quantity formatting."""
        quantity = 1.23456 * ureg.meter
        self.assertEqual(format_quantity(quantity, 2), '1.23 m')
        self.assertEqual(format_quantity(quantity, 4), '1.2346 m')

    def test_format_with_units(self):
        """Test unit formatting."""
        quantity = 1.23456 * ureg.meter
        self.assertEqual(format_with_units(quantity), '1.23456 m')
        speed = 20 * ureg.meter / ureg.second
        self.assertTrue('m' in format_with_units(speed))
        self.assertTrue('s' in format_with_units(speed))

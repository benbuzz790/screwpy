import unittest
from utils.thread_utils import ThreadInfo, parse_thread_specification, validate_thread_format, extract_thread_dimensions, calculate_pitch_diameter, calculate_minor_diameter, calculate_thread_pitch, is_valid_thread_spec, validate_thread_series, are_threads_compatible
from units_config import ureg
from utils.thread_utils import parse_thread_specification, calculate_pitch_diameter, is_valid_thread_spec


class TestThreadUtils(unittest.TestCase):
    """Test cases for thread utilities."""

    def setUp(self):
        """Set up test cases."""
        self.valid_unc_specs = ['1/4-20 UNC', '3/8-16 UNC', '1/2-13 UNC',
            '3/4-10 UNC']
        self.valid_unf_specs = ['1/4-28 UNF', '3/8-24 UNF', '1/2-20 UNF',
            '3/4-16 UNF']
        self.invalid_specs = ['1/4-28 UNC', '3/8-20 UNF', '1-13 UNC',
            '1/4-20', '1/4 UNC', 'abc-def UNC']

    def test_parse_thread_specification(self):
        """Test thread specification parsing."""
        thread_info = parse_thread_specification('1/4-20 UNC')
        self.assertEqual(thread_info.nominal_diameter.to('inch').magnitude, 0.25)
        self.assertEqual(thread_info.threads_per_inch, 20)
        self.assertEqual(thread_info.series, 'UNC')
        self.assertTrue(thread_info.is_fractional)
        thread_info = parse_thread_specification('3/8-24 UNF')
        self.assertEqual(thread_info.nominal_diameter.to('inch').magnitude, 0.375)
        self.assertEqual(thread_info.threads_per_inch, 24)
        self.assertEqual(thread_info.series, 'UNF')
        self.assertTrue(thread_info.is_fractional)
        for invalid_spec in self.invalid_specs:
            with self.assertRaises(ValueError):
                parse_thread_specification(invalid_spec)

    def test_validate_thread_format(self):
        """Test thread format validation."""
        for spec in (self.valid_unc_specs + self.valid_unf_specs):
            self.assertTrue(validate_thread_format(spec))
        for spec in self.invalid_specs:
            self.assertFalse(validate_thread_format(spec))

    def test_extract_thread_dimensions(self):
        """Test thread dimension extraction."""
        dims = extract_thread_dimensions('1/4-20 UNC')
        self.assertEqual(dims['major_diameter'], 0.25 * ureg.inch)
        self.assertEqual(dims['thread_pitch'], 0.05 * ureg.inch)
        self.assertIsInstance(dims['pitch_diameter'], ureg.Quantity)
        self.assertIsInstance(dims['minor_diameter'], ureg.Quantity)
        with self.assertRaises(ValueError):
            extract_thread_dimensions('invalid-spec')

    def test_calculate_diameters(self):
        """Test diameter calculations."""
        spec = '1/4-20 UNC'
        pitch_dia = calculate_pitch_diameter(spec)
        minor_dia = calculate_minor_diameter(spec)
        thread_pitch = calculate_thread_pitch(spec)
        self.assertIsInstance(pitch_dia, ureg.Quantity)
        self.assertIsInstance(minor_dia, ureg.Quantity)
        self.assertIsInstance(thread_pitch, ureg.Quantity)
        self.assertLess(pitch_dia, 0.25 * ureg.inch)
        self.assertLess(minor_dia, pitch_dia)
        self.assertEqual(thread_pitch, 0.05 * ureg.inch)

    def test_thread_validation(self):
        """Test thread validation functions."""
        # Test valid UNC specs
        for spec in self.valid_unc_specs:
            self.assertTrue(is_valid_thread_spec(spec), f"Failed for valid UNC spec: {spec}")
            self.assertTrue(validate_thread_series(spec), f"Failed series validation for UNC spec: {spec}")
        
        # Test valid UNF specs
        for spec in self.valid_unf_specs:
            self.assertTrue(is_valid_thread_spec(spec), f"Failed for valid UNF spec: {spec}")
            self.assertTrue(validate_thread_series(spec), f"Failed series validation for UNF spec: {spec}")
        
        # Test invalid specs
        for spec in self.invalid_specs:
            self.assertFalse(is_valid_thread_spec(spec), f"Should fail for invalid spec: {spec}")
            self.assertFalse(validate_thread_series(spec), f"Should fail series validation for invalid spec: {spec}")

    def test_thread_compatibility(self):
        """Test thread compatibility checking."""
        self.assertTrue(are_threads_compatible('1/4-20 UNC', '1/4-20 UNC'))
        self.assertTrue(are_threads_compatible('3/8-24 UNF', '3/8-24 UNF'))
        self.assertFalse(are_threads_compatible('1/4-20 UNC', '1/4-28 UNF'))
        self.assertFalse(are_threads_compatible('3/8-16 UNC', '1/4-20 UNC'))
        self.assertFalse(are_threads_compatible('1/4-20 UNC', 'invalid-spec'))

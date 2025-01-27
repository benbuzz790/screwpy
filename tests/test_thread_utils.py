import unittest
from utils.thread_utils import (ThreadInfo, parse_thread_specification, validate_thread_format,
                              extract_thread_dimensions, calculate_pitch_diameter, calculate_minor_diameter,
                              calculate_thread_pitch, is_valid_thread_spec, validate_thread_series,
                              are_threads_compatible)
from units_config import ureg

class TestThreadUtils(unittest.TestCase):
    """Test cases for thread utilities."""

    def setUp(self):
        """Set up test cases."""
        # Standard thread specifications for testing
        self.valid_unc_specs = ['1/4-20 UNC', '3/8-16 UNC', '1/2-13 UNC', '3/4-10 UNC']
        self.valid_unf_specs = ['1/4-28 UNF', '3/8-24 UNF', '1/2-20 UNF', '3/4-16 UNF']
        self.valid_metric_specs = ['M6x1.0', 'M8x1.25', 'M10x1.5', 'M12x1.75', 'M16x2.0', 'M20x2.5']
        
        # Invalid format specs (not checking standard sizes, only format validity)
        self.invalid_specs = [
            '1/4-20',      # missing series
            '1/4 UNC',     # missing thread count
            'abc-def UNC', # invalid numbers
            '1/4/2-20 UNC',# invalid fraction format
            '1/-20 UNC',   # negative numbers
            '1/0-20 UNC',  # division by zero
            '',            # empty string
            '1/4-abc UNC', # non-numeric thread count
            '1/4-20 UNCC', # invalid series format
            'M6',          # missing pitch
            'M6x',         # missing pitch value
            'Mx1.0',       # missing diameter
            'M-6x1.0',     # negative diameter
            'M6x-1.0',     # negative pitch
            'M6X1.0'       # wrong x format
        ]

    def test_parse_thread_specification_imperial(self):
        """Test imperial thread specification parsing."""
        # Test UNC thread
        thread_info = parse_thread_specification('1/4-20 UNC')
        self.assertEqual(thread_info.nominal_diameter.to('inch').magnitude, 0.25)
        self.assertEqual(thread_info.threads_per_inch, 20)
        self.assertEqual(thread_info.series, 'UNC')
        self.assertTrue(thread_info.is_fractional)
        self.assertFalse(thread_info.is_metric)
        self.assertIsNone(thread_info.thread_pitch)

        # Test UNF thread
        thread_info = parse_thread_specification('3/8-24 UNF')
        self.assertEqual(thread_info.nominal_diameter.to('inch').magnitude, 0.375)
        self.assertEqual(thread_info.threads_per_inch, 24)
        self.assertEqual(thread_info.series, 'UNF')
        self.assertTrue(thread_info.is_fractional)
        self.assertFalse(thread_info.is_metric)

    def test_parse_thread_specification_metric(self):
        """Test metric thread specification parsing."""
        # Test standard M10 thread
        thread_info = parse_thread_specification('M10x1.5')
        self.assertEqual(thread_info.nominal_diameter.to('mm').magnitude, 10)
        self.assertEqual(thread_info.thread_pitch.to('mm').magnitude, 1.5)
        self.assertEqual(thread_info.series, 'M')
        self.assertTrue(thread_info.is_metric)
        self.assertIsNone(thread_info.threads_per_inch)
        self.assertFalse(thread_info.is_fractional)

        # Test all standard metric sizes
        for spec in self.valid_metric_specs:
            thread_info = parse_thread_specification(spec)
            self.assertTrue(thread_info.is_metric)
            self.assertEqual(thread_info.series, 'M')

    def test_invalid_specifications(self):
        """Test invalid thread specifications."""
        for invalid_spec in self.invalid_specs:
            with self.assertRaises(ValueError):
                parse_thread_specification(invalid_spec)

        # Test non-standard metric sizes
        invalid_metric = ['M7x1.0', 'M10x1.0', 'M15x2.0']
        for spec in invalid_metric:
            with self.assertRaises(ValueError):
                parse_thread_specification(spec)

    def test_validate_thread_format(self):
        """Test thread format validation."""
        # Test valid formats
        for spec in (self.valid_unc_specs + self.valid_unf_specs + self.valid_metric_specs):
            self.assertTrue(validate_thread_format(spec))

        # Test invalid formats
        for spec in self.invalid_specs:
            self.assertFalse(validate_thread_format(spec))

    def test_thread_calculations_imperial(self):
        """Test thread calculations for imperial threads."""
        spec = '1/4-20 UNC'
        dims = extract_thread_dimensions(spec)
        
        # Check all dimensions are present and have correct units
        self.assertEqual(dims['major_diameter'], 0.25 * ureg.inch)
        self.assertEqual(dims['thread_pitch'], 0.05 * ureg.inch)
        self.assertIsInstance(dims['pitch_diameter'], ureg.Quantity)
        self.assertIsInstance(dims['minor_diameter'], ureg.Quantity)

        # Check relative sizes
        self.assertLess(dims['minor_diameter'], dims['pitch_diameter'])
        self.assertLess(dims['pitch_diameter'], dims['major_diameter'])

    def test_thread_calculations_metric(self):
        """Test thread calculations for metric threads."""
        spec = 'M10x1.5'
        dims = extract_thread_dimensions(spec)
        
        # Check all dimensions are present and have correct units
        self.assertEqual(dims['major_diameter'], 10 * ureg.mm)
        self.assertEqual(dims['thread_pitch'], 1.5 * ureg.mm)
        self.assertIsInstance(dims['pitch_diameter'], ureg.Quantity)
        self.assertIsInstance(dims['minor_diameter'], ureg.Quantity)

        # Check relative sizes
        self.assertLess(dims['minor_diameter'], dims['pitch_diameter'])
        self.assertLess(dims['pitch_diameter'], dims['major_diameter'])

    def test_thread_compatibility(self):
        """Test thread compatibility checking."""
        # Test imperial compatibility
        self.assertTrue(are_threads_compatible('1/4-20 UNC', '1/4-20 UNC'))
        self.assertTrue(are_threads_compatible('3/8-24 UNF', '3/8-24 UNF'))
        self.assertFalse(are_threads_compatible('1/4-20 UNC', '1/4-28 UNF'))
        self.assertFalse(are_threads_compatible('3/8-16 UNC', '1/4-20 UNC'))

        # Test metric compatibility
        self.assertTrue(are_threads_compatible('M10x1.5', 'M10x1.5'))
        self.assertTrue(are_threads_compatible('M20x2.5', 'M20x2.5'))
        self.assertFalse(are_threads_compatible('M10x1.5', 'M10x1.0'))
        self.assertFalse(are_threads_compatible('M8x1.25', 'M10x1.5'))

        # Test metric-imperial incompatibility
        self.assertFalse(are_threads_compatible('M10x1.5', '3/8-16 UNC'))
        self.assertFalse(are_threads_compatible('1/4-20 UNC', 'M6x1.0'))

    def test_thread_series_validation(self):
        """Test thread series validation."""
        # Test valid series
        self.assertTrue(validate_thread_series('1/4-20 UNC'))
        self.assertTrue(validate_thread_series('3/8-24 UNF'))
        self.assertTrue(validate_thread_series('M10x1.5'))

        # Test invalid series
        self.assertFalse(validate_thread_series('1/4-20 ABC'))
        self.assertFalse(validate_thread_series('M10x1.0'))  # Non-standard pitch
        self.assertFalse(validate_thread_series('M7x1.0'))   # Non-standard size

if __name__ == '__main__':
    unittest.main()

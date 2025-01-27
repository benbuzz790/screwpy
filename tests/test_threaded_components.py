import unittest
from pint import Quantity
from units_config import ureg
from tests.test_base_component import TestMaterial
from components.threaded_components import ThreadedComponent, Fastener, Nut


class TestFastener(unittest.TestCase):
    """Test cases for Fastener class."""

    def setUp(self):
        """Set up test fixtures."""
        self.material = TestMaterial('Steel', {'yield_strength': 250 * ureg.MPa})
        self.fastener = Fastener(thread_spec='1/4-20 UNC', length=2 * ureg.inch,
            threaded_length=1.5 * ureg.inch, head_diameter=0.5 * ureg.inch,
            head_height=0.25 * ureg.inch, is_flat=False, tool_size='3/8',
            material=self.material)

    def test_fastener_creation(self):
        """Test fastener creation with valid parameters."""
        self.assertEqual(self.fastener.thread_spec, '1/4-20 UNC')
        self.assertEqual(self.fastener.length, 2 * ureg.inch)
        self.assertEqual(self.fastener.threaded_length, 1.5 * ureg.inch)
        self.assertEqual(self.fastener.head_diameter, 0.5 * ureg.inch)
        self.assertEqual(self.fastener.head_height, 0.25 * ureg.inch)
        self.assertFalse(self.fastener.is_flat)
        self.assertEqual(self.fastener.tool_size, '3/8')
        self.assertEqual(self.fastener.material, self.material)

    def test_invalid_dimensions(self):
        """Test fastener creation with invalid dimensions."""
        with self.assertRaises(ValueError):
            Fastener(thread_spec='1/4-20', length=-1 * ureg.inch,
                threaded_length=1.5 * ureg.inch, head_diameter=0.5 * ureg.
                inch, head_height=0.25 * ureg.inch, is_flat=False,
                tool_size='3/8', material=self.material)
        with self.assertRaises(ValueError):
            Fastener(thread_spec='1/4-20', length=1 * ureg.inch,
                threaded_length=1.5 * ureg.inch, head_diameter=0.5 * ureg.
                inch, head_height=0.25 * ureg.inch, is_flat=False,
                tool_size='3/8', material=self.material)

    def test_unit_conversion(self):
        """Test unit conversion between imperial and metric."""
        metric_fastener = Fastener(thread_spec='M6x1', length=50 * ureg.mm,  # Will handle metric in separate PR
            threaded_length=40 * ureg.mm, head_diameter=12 * ureg.mm,
            head_height=6 * ureg.mm, is_flat=True, tool_size='10mm',
            material=self.material)
        length_inch = metric_fastener.length.to(ureg.inch)
        self.assertAlmostEqual(length_inch.magnitude, 1.9685, places=4)

    def test_property_setters(self):
        """Test property setters with validation."""
        self.fastener.length = 2.5 * ureg.inch
        self.assertEqual(self.fastener.length, 2.5 * ureg.inch)
        self.fastener.is_flat = True
        self.assertTrue(self.fastener.is_flat)
        with self.assertRaises(ValueError):
            self.fastener.head_diameter = 0.1 * ureg.inch
        with self.assertRaises(ValueError):
            self.fastener.length = 1 * ureg.inch


class TestNut(unittest.TestCase):
    """Test cases for Nut class."""

    def setUp(self):
        """Set up test fixtures."""
        self.material = TestMaterial('Steel', {'yield_strength': 250 * ureg.MPa})
        self.nut = Nut(thread_spec='1/4-20 UNC', width_across_flats=7 / 16 *
            ureg.inch, height=7 / 32 * ureg.inch, material=self.material)

    def test_nut_creation(self):
        """Test nut creation with valid parameters."""
        self.assertEqual(self.nut.thread_spec, '1/4-20 UNC')
        self.assertEqual(self.nut.width_across_flats, 7 / 16 * ureg.inch)
        self.assertEqual(self.nut.height, 7 / 32 * ureg.inch)
        self.assertEqual(self.nut.material, self.material)
        self.assertEqual(self.nut.threaded_length, self.nut.height)

    def test_invalid_dimensions(self):
        """Test nut creation with invalid dimensions."""
        with self.assertRaises(ValueError):
            Nut(thread_spec='1/4-20', width_across_flats=-7 / 16 * ureg.
                inch, height=7 / 32 * ureg.inch, material=self.material)
        with self.assertRaises(ValueError):
            Nut(thread_spec='1/4-20', width_across_flats=0.1 * ureg.inch,
                height=7 / 32 * ureg.inch, material=self.material)

    def test_unit_conversion(self):
        """Test unit conversion between imperial and metric."""
        metric_nut = Nut(thread_spec='M6x1', width_across_flats=10 * ureg.mm,  # Will handle metric in separate PR
            height=5 * ureg.mm, material=self.material)
        width_inch = metric_nut.width_across_flats.to(ureg.inch)
        self.assertAlmostEqual(width_inch.magnitude, 0.3937, places=4)

    def test_property_setters(self):
        """Test property setters with validation."""
        self.nut.height = 0.25 * ureg.inch
        self.assertEqual(self.nut.height, 0.25 * ureg.inch)
        self.assertEqual(self.nut.threaded_length, 0.25 * ureg.inch)
        with self.assertRaises(ValueError):
            self.nut.width_across_flats = 0.1 * ureg.inch
        with self.assertRaises(ValueError):
            self.nut.height = -0.25 * ureg.inch

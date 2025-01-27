import unittest
from components.clamped_components import Washer, PlateComponent
from tests.test_base_component import TestMaterial
from units_config import ureg


class TestWasher(unittest.TestCase):
    """Test cases for the Washer component."""

    def setUp(self):
        """Set up test fixtures."""
        self.material = TestMaterial('Steel', {'yield_strength': 250 * ureg.MPa})
        self.washer = Washer(inner_diameter=10 * ureg.mm, outer_diameter=20 *
            ureg.mm, thickness=2 * ureg.mm, material=self.material)

    def test_valid_creation(self):
        """Test creating a washer with valid parameters."""
        washer = Washer(inner_diameter=0.5 * ureg.inch, outer_diameter=1.0 *
            ureg.inch, thickness=0.125 * ureg.inch, material=self.material)
        self.assertIsInstance(washer, Washer)

    def test_invalid_dimensions(self):
        """Test validation of invalid dimensions."""
        with self.assertRaises(ValueError):
            Washer(inner_diameter=-10 * ureg.mm, outer_diameter=20 * ureg.
                mm, thickness=2 * ureg.mm, material=self.material)
        with self.assertRaises(ValueError):
            Washer(inner_diameter=20 * ureg.mm, outer_diameter=10 * ureg.mm,
                thickness=2 * ureg.mm, material=self.material)
        with self.assertRaises(ValueError):
            Washer(inner_diameter=10 * ureg.mm, outer_diameter=20 * ureg.mm,
                thickness=0 * ureg.mm, material=self.material)

    def test_property_access(self):
        """Test getting and setting properties."""
        self.assertEqual(self.washer.inner_diameter, 10 * ureg.mm)
        self.assertEqual(self.washer.outer_diameter, 20 * ureg.mm)
        self.assertEqual(self.washer.thickness, 2 * ureg.mm)
        self.assertEqual(self.washer.material, self.material)
        self.washer.inner_diameter = 12 * ureg.mm
        self.assertEqual(self.washer.inner_diameter, 12 * ureg.mm)
        self.washer.outer_diameter = 25 * ureg.mm
        self.assertEqual(self.washer.outer_diameter, 25 * ureg.mm)
        self.washer.thickness = 3 * ureg.mm
        self.assertEqual(self.washer.thickness, 3 * ureg.mm)

    def test_unit_conversion(self):
        """Test unit conversion capabilities."""
        washer = Washer(inner_diameter=0.5 * ureg.inch, outer_diameter=1.0 *
            ureg.inch, thickness=0.125 * ureg.inch, material=self.material)
        self.assertAlmostEqual(washer.inner_diameter.to('mm').magnitude, 
            12.7, places=1)
        self.assertAlmostEqual(washer.outer_diameter.to('mm').magnitude, 
            25.4, places=1)
        self.assertAlmostEqual(washer.thickness.to('mm').magnitude, 3.175,
            places=3)

    def test_invalid_material(self):
        """Test validation of invalid material reference."""
        with self.assertRaises(ValueError):
            Washer(inner_diameter=10 * ureg.mm, outer_diameter=20 * ureg.mm,
                thickness=2 * ureg.mm, material=None)


class TestPlateComponent(unittest.TestCase):
    """Test cases for the PlateComponent."""

    def setUp(self):
        """Set up test fixtures."""
        self.material = TestMaterial('Steel', {'yield_strength': 250 * ureg.MPa})
        self.plate = PlateComponent(thickness=5 * ureg.mm, material=self.
            material)

    def test_valid_creation(self):
        """Test creating a plate with valid parameters."""
        plate = PlateComponent(thickness=0.25 * ureg.inch, material=self.
            material)
        self.assertIsInstance(plate, PlateComponent)

    def test_invalid_dimensions(self):
        """Test validation of invalid dimensions."""
        with self.assertRaises(ValueError):
            PlateComponent(thickness=-5 * ureg.mm, material=self.material)
        with self.assertRaises(ValueError):
            PlateComponent(thickness=0 * ureg.mm, material=self.material)

    def test_property_access(self):
        """Test getting and setting properties."""
        self.assertEqual(self.plate.thickness, 5 * ureg.mm)
        self.assertEqual(self.plate.material, self.material)
        self.plate.thickness = 6 * ureg.mm
        self.assertEqual(self.plate.thickness, 6 * ureg.mm)
        new_material = TestMaterial('Aluminum', {'yield_strength': 200 * ureg.MPa})
        self.plate.material = new_material
        self.assertEqual(self.plate.material, new_material)

    def test_unit_conversion(self):
        """Test unit conversion capabilities."""
        plate = PlateComponent(thickness=0.25 * ureg.inch, material=self.
            material)
        self.assertAlmostEqual(plate.thickness.to('mm').magnitude, 6.35,
            places=2)

    def test_invalid_material(self):
        """Test validation of invalid material reference."""
        with self.assertRaises(ValueError):
            PlateComponent(thickness=5 * ureg.mm, material=None)

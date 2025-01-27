import unittest
from pint import Quantity
from units_config import ureg
from materials.material import Material
from components.threaded_plate import ThreadedPlate

class TestThreadedPlate(unittest.TestCase):
    """Test cases for the ThreadedPlate class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.material = TestMaterial("Steel", {'yield_strength': 250 * ureg.MPa})
        self.thickness = 10 * ureg.mm
        self.thread_spec = "M6-1"
        self.threaded_length = 8 * ureg.mm
        self.clearance_hole_diameter = 6.5 * ureg.mm
        self.thread_location_x = 20 * ureg.mm
        self.thread_location_y = 20 * ureg.mm

        # Create a default threaded plate for testing
        self.plate = ThreadedPlate(
            thickness=self.thickness,
            material=self.material,
            thread_spec=self.thread_spec,
            threaded_length=self.threaded_length,
            clearance_hole_diameter=self.clearance_hole_diameter,
            thread_location_x=self.thread_location_x,
            thread_location_y=self.thread_location_y
        )

    def test_initialization(self):
        """Test successful initialization with valid parameters."""
        self.assertIsInstance(self.plate, ThreadedPlate)
        self.assertEqual(self.plate.thickness, self.thickness)
        self.assertEqual(self.plate.material, self.material)
        self.assertEqual(self.plate.thread_spec, self.thread_spec)
        self.assertEqual(self.plate.threaded_length, self.threaded_length)
        self.assertEqual(self.plate.clearance_hole_diameter, self.clearance_hole_diameter)
        self.assertEqual(self.plate.thread_location_x, self.thread_location_x)
        self.assertEqual(self.plate.thread_location_y, self.thread_location_y)

    def test_initialization_with_defaults(self):
        """Test initialization with default thread locations."""
        plate = ThreadedPlate(
            thickness=self.thickness,
            material=self.material,
            thread_spec=self.thread_spec,
            threaded_length=self.threaded_length,
            clearance_hole_diameter=self.clearance_hole_diameter
        )
        self.assertEqual(plate.thread_location_x, 0 * ureg.mm)
        self.assertEqual(plate.thread_location_y, 0 * ureg.mm)

    def test_initialization_with_numeric_values(self):
        """Test initialization with numeric values instead of Quantities."""
        plate = ThreadedPlate(
            thickness=10,
            material=self.material,
            thread_spec=self.thread_spec,
            threaded_length=8,
            clearance_hole_diameter=6.5,
            thread_location_x=20,
            thread_location_y=20
        )
        self.assertEqual(plate.thickness, 10 * ureg.mm)
        self.assertEqual(plate.threaded_length, 8 * ureg.mm)
        self.assertEqual(plate.clearance_hole_diameter, 6.5 * ureg.mm)
        self.assertEqual(plate.thread_location_x, 20 * ureg.mm)
        self.assertEqual(plate.thread_location_y, 20 * ureg.mm)

    def test_imperial_units(self):
        """Test initialization and operation with imperial units."""
        plate = ThreadedPlate(
            thickness=0.5 * ureg.inch,
            material=self.material,
            thread_spec="1/4-20",
            threaded_length=0.375 * ureg.inch,
            clearance_hole_diameter=0.3125 * ureg.inch,
            thread_location_x=1 * ureg.inch,
            thread_location_y=1 * ureg.inch
        )
        self.assertIsInstance(plate, ThreadedPlate)
        self.assertEqual(plate.thickness, 0.5 * ureg.inch)
        self.assertEqual(plate.thread_spec, "1/4-20")

    def test_invalid_thread_spec(self):
        """Test initialization with invalid thread specification."""
        with self.assertRaises(ValueError):
            ThreadedPlate(
                thickness=self.thickness,
                material=self.material,
                thread_spec="invalid-thread",
                threaded_length=self.threaded_length,
                clearance_hole_diameter=self.clearance_hole_diameter
            )

    def test_invalid_threaded_length(self):
        """Test initialization with threaded length exceeding thickness."""
        with self.assertRaises(ValueError):
            ThreadedPlate(
                thickness=self.thickness,
                material=self.material,
                thread_spec=self.thread_spec,
                threaded_length=12 * ureg.mm,  # Greater than thickness
                clearance_hole_diameter=self.clearance_hole_diameter
            )

    def test_invalid_clearance_hole(self):
        """Test initialization with invalid clearance hole diameter."""
        with self.assertRaises(ValueError):
            ThreadedPlate(
                thickness=self.thickness,
                material=self.material,
                thread_spec=self.thread_spec,
                threaded_length=self.threaded_length,
                clearance_hole_diameter=4 * ureg.mm  # Too small
            )

    def test_property_setters(self):
        """Test property setters with valid values."""
        new_thickness = 15 * ureg.mm
        new_threaded_length = 12 * ureg.mm
        new_clearance_hole = 7 * ureg.mm
        new_location_x = 30 * ureg.mm
        new_location_y = 30 * ureg.mm

        self.plate.thickness = new_thickness
        self.plate.threaded_length = new_threaded_length
        self.plate.clearance_hole_diameter = new_clearance_hole
        self.plate.thread_location_x = new_location_x
        self.plate.thread_location_y = new_location_y

        self.assertEqual(self.plate.thickness, new_thickness)
        self.assertEqual(self.plate.threaded_length, new_threaded_length)
        self.assertEqual(self.plate.clearance_hole_diameter, new_clearance_hole)
        self.assertEqual(self.plate.thread_location_x, new_location_x)
        self.assertEqual(self.plate.thread_location_y, new_location_y)

    def test_invalid_property_values(self):
        """Test property setters with invalid values."""
        with self.assertRaises(ValueError):
            self.plate.thickness = -10 * ureg.mm

        with self.assertRaises(ValueError):
            self.plate.threaded_length = -8 * ureg.mm

        with self.assertRaises(ValueError):
            self.plate.clearance_hole_diameter = -6.5 * ureg.mm

    def test_unit_conversion(self):
        """Test unit conversion between metric and imperial."""
        # Create plate with metric units
        metric_plate = ThreadedPlate(
            thickness=10 * ureg.mm,
            material=self.material,
            thread_spec="M6-1",
            threaded_length=8 * ureg.mm,
            clearance_hole_diameter=6.5 * ureg.mm
        )

        # Convert to imperial and check values
        thickness_inch = metric_plate.thickness.to("inch")
        threaded_length_inch = metric_plate.threaded_length.to("inch")
        clearance_hole_inch = metric_plate.clearance_hole_diameter.to("inch")

        self.assertAlmostEqual(thickness_inch.magnitude, 0.3937, places=4)
        self.assertAlmostEqual(threaded_length_inch.magnitude, 0.3150, places=4)
        self.assertAlmostEqual(clearance_hole_inch.magnitude, 0.2559, places=4)


if __name__ == "__main__":
    unittest.main()

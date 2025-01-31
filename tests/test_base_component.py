"""Tests for the BaseComponent class."""

import unittest
from components.base_component import BaseComponent
from materials.material import Material
from tests.test_material import create_test_material
from units_config import ureg, Quantity


class ConcreteComponent(BaseComponent):
    """Concrete implementation of BaseComponent for testing."""
    
    def __init__(self, material: Material, length: Quantity):
        super().__init__(material)
        self._length = length
        
    @property
    def length(self) -> Quantity:
        return self._length
        
    def validate_geometry(self) -> bool:
        return self.validate_length(self.length, ureg.Quantity(0, "mm"))


class TestBaseComponent(unittest.TestCase):
    """Test cases for BaseComponent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.material = create_test_material("Test Material")
        self.length = 10 * ureg.mm
        self.component = ConcreteComponent(self.material, self.length)

    def test_init(self):
        """Test component initialization."""
        self.assertIsInstance(self.component, BaseComponent)
        self.assertEqual(self.component.material, self.material)

    def test_init_invalid_material(self):
        """Test initialization with invalid material."""
        with self.assertRaises(ValueError):
            ConcreteComponent(None, self.length)
        with self.assertRaises(ValueError):
            ConcreteComponent("not a material", self.length)

    def test_material_property(self):
        """Test material property access."""
        self.assertEqual(self.component.material, self.material)

    def test_convert_length(self):
        """Test length conversion functionality."""
        # Test metric to metric conversion
        length_mm = 25.4 * ureg.mm
        length_cm = self.component.convert_length(length_mm, "cm")
        self.assertEqual(length_cm.magnitude, 2.54)
        
        # Test metric to imperial conversion
        length_inch = self.component.convert_length(length_mm, "inch")
        self.assertEqual(length_inch.magnitude, 1.0)
        
        # Test imperial to metric conversion
        length_ft = 1 * ureg.ft
        length_m = self.component.convert_length(length_ft, "m")
        self.assertAlmostEqual(length_m.magnitude, 0.3048)

    def test_convert_length_errors(self):
        """Test length conversion error cases."""
        # Test invalid quantity
        with self.assertRaises(ValueError):
            self.component.convert_length(10, "mm")
            
        # Test invalid unit
        with self.assertRaises(ValueError):
            self.component.convert_length(10 * ureg.mm, "invalid_unit")

    def test_validate_length(self):
        """Test length validation functionality."""
        length = 10 * ureg.mm
        
        # Test basic validation
        self.assertTrue(self.component.validate_length(length))
        
        # Test with min value
        self.assertTrue(self.component.validate_length(length, min_val=5 * ureg.mm))
        self.assertFalse(self.component.validate_length(length, min_val=15 * ureg.mm))
        
        # Test with max value
        self.assertTrue(self.component.validate_length(length, max_val=15 * ureg.mm))
        self.assertFalse(self.component.validate_length(length, max_val=5 * ureg.mm))
        
        # Test with both min and max
        self.assertTrue(self.component.validate_length(length, 
                                                     min_val=5 * ureg.mm,
                                                     max_val=15 * ureg.mm))
        self.assertFalse(self.component.validate_length(length,
                                                      min_val=15 * ureg.mm,
                                                      max_val=20 * ureg.mm))

    def test_validate_length_errors(self):
        """Test length validation error cases."""
        # Test invalid quantity
        with self.assertRaises(ValueError):
            self.component.validate_length(10)
            
        # Test invalid min value
        with self.assertRaises(ValueError):
            self.component.validate_length(10 * ureg.mm, min_val=5)
            
        # Test invalid max value
        with self.assertRaises(ValueError):
            self.component.validate_length(10 * ureg.mm, max_val=15)

    def test_validate_geometry(self):
        """Test geometry validation."""
        # Test valid geometry
        self.assertTrue(self.component.validate_geometry())
        
        # Test invalid geometry
        invalid_component = ConcreteComponent(self.material, -1 * ureg.mm)
        self.assertFalse(invalid_component.validate_geometry())


if __name__ == '__main__':
    unittest.main()

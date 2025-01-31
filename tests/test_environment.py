import unittest
import numpy as np
from environment import Environment
from units_config import ureg


class TestEnvironment(unittest.TestCase):
    """Test suite for Environment class."""

    def setUp(self):
        """Set up test fixtures with valid metric and imperial environments."""
        self.env_metric = Environment(tension=1000 * ureg.newton, shear=500 *
            ureg.newton, bending=100 * ureg.newton * ureg.meter, min_temp=
            250 * ureg.kelvin, nom_temp=300 * ureg.kelvin, max_temp=350 *
            ureg.kelvin, preload_torque=50 * ureg.newton * ureg.meter)
        self.env_imperial = Environment(tension=100 * ureg.lbf, shear=50 *
            ureg.lbf, bending=20 * ureg.foot * ureg.lbf, min_temp=450 *
            ureg.rankine, nom_temp=540 * ureg.rankine, max_temp=630 * ureg.
            rankine, preload_torque=10 * ureg.foot * ureg.lbf)

    def test_valid_initialization(self):
        """Test initialization with valid inputs."""
        self.assertIsInstance(self.env_metric, Environment)
        self.assertIsInstance(self.env_imperial, Environment)

    def test_temperature_validation(self):
        """Test temperature validation."""
        with self.assertRaises(ValueError):
            Environment(tension=1000 * ureg.newton, shear=500 * ureg.newton,
                bending=100 * ureg.newton * ureg.meter, min_temp=0 * ureg.
                kelvin, nom_temp=300 * ureg.kelvin, max_temp=350 * ureg.
                kelvin, preload_torque=50 * ureg.newton * ureg.meter)
        with self.assertRaises(ValueError):
            Environment(tension=1000 * ureg.newton, shear=500 * ureg.newton,
                bending=100 * ureg.newton * ureg.meter, min_temp=-10 * ureg
                .kelvin, nom_temp=300 * ureg.kelvin, max_temp=350 * ureg.
                kelvin, preload_torque=50 * ureg.newton * ureg.meter)

    def test_force_unit_validation(self):
        """Test force unit validation."""
        with self.assertRaises(ValueError):
            Environment(tension=1000 * ureg.kilogram, shear=500 * ureg.
                newton, bending=100 * ureg.newton * ureg.meter, min_temp=
                250 * ureg.kelvin, nom_temp=300 * ureg.kelvin, max_temp=350 *
                ureg.kelvin, preload_torque=50 * ureg.newton * ureg.meter)

    def test_moment_unit_validation(self):
        """Test moment unit validation."""
        with self.assertRaises(ValueError):
            Environment(tension=1000 * ureg.newton, shear=500 * ureg.newton,
                bending=100 * ureg.newton, min_temp=250 * ureg.kelvin,
                nom_temp=300 * ureg.kelvin, max_temp=350 * ureg.kelvin,
                preload_torque=50 * ureg.newton * ureg.meter)

    def test_preload_torque_validation(self):
        """Test preload torque validation."""
        with self.assertRaises(ValueError):
            Environment(tension=1000 * ureg.newton, shear=500 * ureg.newton,
                bending=100 * ureg.newton * ureg.meter, min_temp=250 * ureg
                .kelvin, nom_temp=300 * ureg.kelvin, max_temp=350 * ureg.
                kelvin, preload_torque=-50 * ureg.newton * ureg.meter)

    def test_6dof_conversion_x_axis(self):
        """Test 6DOF load conversion for x-axis."""
        forces = [1000 * ureg.newton, 500 * ureg.newton, 250 * ureg.newton]
        moments = [20 * ureg.newton * ureg.meter, 30 * ureg.newton * ureg.
            meter, 40 * ureg.newton * ureg.meter]
        env = Environment.set_force_from_6dof(forces, moments, 'x')
        self.assertEqual(env.tension, forces[0])
        self.assertAlmostEqual(env.shear.magnitude, np.sqrt(500 ** 2 + 250 **
            2))
        self.assertAlmostEqual(env.bending.magnitude, np.sqrt(30 ** 2 + 40 **
            2))

    def test_6dof_conversion_y_axis(self):
        """Test 6DOF load conversion for y-axis."""
        forces = [1000 * ureg.newton, 500 * ureg.newton, 250 * ureg.newton]
        moments = [20 * ureg.newton * ureg.meter, 30 * ureg.newton * ureg.
            meter, 40 * ureg.newton * ureg.meter]
        env = Environment.set_force_from_6dof(forces, moments, 'y')
        self.assertEqual(env.tension, forces[1])
        self.assertAlmostEqual(env.shear.magnitude, np.sqrt(1000 ** 2 + 250 **
            2))
        self.assertAlmostEqual(env.bending.magnitude, np.sqrt(20 ** 2 + 40 **
            2))

    def test_6dof_conversion_z_axis(self):
        """Test 6DOF load conversion for z-axis."""
        forces = [1000 * ureg.newton, 500 * ureg.newton, 250 * ureg.newton]
        moments = [20 * ureg.newton * ureg.meter, 30 * ureg.newton * ureg.
            meter, 40 * ureg.newton * ureg.meter]
        env = Environment.set_force_from_6dof(forces, moments, 'z')
        self.assertEqual(env.tension, forces[2])
        self.assertAlmostEqual(env.shear.magnitude, np.sqrt(1000 ** 2 + 500 **
            2))
        self.assertAlmostEqual(env.bending.magnitude, np.sqrt(20 ** 2 + 30 **
            2))

    def test_invalid_axis_specification(self):
        """Test invalid axis specification."""
        forces = [1000 * ureg.newton] * 3
        moments = [20 * ureg.newton * ureg.meter] * 3
        with self.assertRaises(ValueError):
            Environment.set_force_from_6dof(forces, moments, 'w')

    def test_invalid_6dof_inputs(self):
        """Test invalid 6DOF input lists."""
        forces = [1000 * ureg.newton] * 2
        moments = [20 * ureg.newton * ureg.meter] * 3
        with self.assertRaises(ValueError):
            Environment.set_force_from_6dof(forces, moments, 'x')

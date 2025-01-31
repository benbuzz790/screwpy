import unittest
from utils.unit_utils import ureg, Quantity
from analysis.nasa5020 import NASA5020Analysis, _calculate_ultimate_margins, _calculate_yield_margins, _calculate_slip_margin, _calculate_separation_margin
from junctions.junction import Junction
from environment.environment import Environment
from components.threaded_components import Fastener, Nut
from components.clamped_components import PlateComponent, Washer
from tests.test_material import create_test_material


class TestNASA5020Analysis(unittest.TestCase):
    """
    Test suite for NASA5020Analysis class.
    Tests all calculations and scenarios required by NASA-STD-5020
    using real objects and integration tests.
    """

    def setUp(self):
        """Set up test fixtures."""
        # Create material for components
        # Create steel for bolt (higher strength, lower thermal expansion)
        # Create steel material with specific properties needed for NASA-5020 calculations
        self.steel = create_test_material('High Strength Steel')
        self.steel.ultimate_strength = 1000 * ureg.MPa  # Higher ultimate for fastener
        self.steel.yield_strength = 800 * ureg.MPa  # Higher yield for fastener
        self.steel.elastic_modulus = 210 * ureg.GPa  # Standard steel modulus
        self.steel.thermal_expansion = 13.0e-6 * ureg('1/K')  # Standard steel CTE
        self.steel.poisson_ratio = 0.29  # Standard steel Poisson's ratio
        self.steel.density = 7850 * ureg('kg/m^3')  # Standard steel density
        
        # Create aluminum for joint (lower strength, higher thermal expansion)
        # Create aluminum material with specific properties needed for NASA-5020 calculations
        self.aluminum = create_test_material('6061-T6 Aluminum')
        self.aluminum.ultimate_strength = 310 * ureg.MPa  # 6061-T6 ultimate
        self.aluminum.yield_strength = 276 * ureg.MPa  # 6061-T6 yield
        self.aluminum.elastic_modulus = 69 * ureg.GPa  # Standard aluminum modulus
        self.aluminum.thermal_expansion = 23.1e-6 * ureg('1/K')  # Standard aluminum CTE
        self.aluminum.poisson_ratio = 0.33  # Standard aluminum Poisson's ratio
        self.aluminum.density = 2700 * ureg('kg/m^3')  # Standard aluminum density
        
        # Create fastener
        self.fastener = Fastener(
            thread_spec="M12x1.75",
            length=50.0 * ureg.mm,
            threaded_length=20.0 * ureg.mm,
            head_diameter=18.0 * ureg.mm,
            head_height=8.0 * ureg.mm,
            material=self.steel,
            is_flat=False,  # Standard hex head bolt
            tool_size="10"  # 10mm hex key size
        )
        
        # Create washer
        self.washer = Washer(
            inner_diameter=13.0 * ureg.mm,
            outer_diameter=24.0 * ureg.mm,
            thickness=2.0 * ureg.mm,
            material=self.aluminum
        )
        
        # Create plates
        self.plate1 = PlateComponent(
            thickness=15.0 * ureg.mm,
            material=self.aluminum  # washer material
        )
        self.plate2 = PlateComponent(
            thickness=15.0 * ureg.mm,
            material=self.aluminum  # plate1 material
        )
        
        # Create nut
        self.nut = Nut(
            thread_spec="M12x1.75",
            width_across_flats=19.0 * ureg.mm,
            height=10.0 * ureg.mm,
            material=self.aluminum  # plate2 material
        )
        
        # Create junction with components
        self.junction = Junction(
            fastener=self.fastener,
            clamped_components=[self.washer, self.plate1, self.plate2],
            threaded_member=self.nut
        )
        self.environment = Environment(
            tension=1000 * ureg.newton,  # Example tensile load
            shear=500 * ureg.newton,     # Example shear load
            bending=100 * ureg.newton * ureg.meter,  # Example bending moment
            min_temp=250 * ureg.kelvin,  # Cold condition
            nom_temp=293.15 * ureg.kelvin,  # Room temperature
            max_temp=350 * ureg.kelvin,  # Hot condition
            preload_torque=50 * ureg.newton * ureg.meter  # Installation torque
        )
        self.config = {'unit_system': 'metric', 'friction_coefficient': 0.2,
            'safety_factors': {'ultimate': 1.4, 'yield': 1.2, 'separation':
            1.2}, 'fitting_factor': 1.2}
        self.analyzer = NASA5020Analysis(self.junction, self.environment, **self.config)

    def test_initialization(self):
        """Test proper initialization and input validation."""
        analyzer = NASA5020Analysis(self.junction, self.environment)
        self.assertIsInstance(analyzer, NASA5020Analysis)
        with self.assertRaises(TypeError):
            NASA5020Analysis('not a junction', self.environment)
        with self.assertRaises(TypeError):
            NASA5020Analysis(self.junction, 'not an environment')
        with self.assertRaises(ValueError):
            NASA5020Analysis(self.junction, self.environment, unit_system=
                'invalid')
        with self.assertRaises(ValueError):
            NASA5020Analysis(self.junction, self.environment,
                friction_coefficient=-0.1)
        with self.assertRaises(ValueError):
            NASA5020Analysis(self.junction, self.environment,
                safety_factors={'ultimate': 0.5})

    def test_preload_calculations(self):
        """Test preload calculations with temperature effects."""
        preloads = self.analyzer.calculate_preloads()
        self.assertIsInstance(preloads, dict)
        self.assertIn('min_preload', preloads)
        self.assertIn('max_preload', preloads)
        self.assertIn('nominal_preload', preloads)
        for value in preloads.values():
            self.assertIsInstance(value, Quantity)
        self.assertGreater(preloads['max_preload'], preloads['min_preload'])
        self.assertLessEqual(preloads['nominal_preload'], preloads[
            'max_preload'])
        self.assertGreaterEqual(preloads['nominal_preload'], preloads[
            'min_preload'])

    def test_ultimate_margins(self):
        """Test ultimate strength margin calculations."""
        margins = self.analyzer.calculate_ultimate_margins()
        self.assertIn('tension', margins)
        self.assertIn('shear', margins)
        self.assertIn('combined', margins)
        for margin in margins.values():
            self.assertIsInstance(margin, float)
        for margin in margins.values():
            self.assertGreater(margin, -1.0)

    def test_yield_margins(self):
        """Test yield strength margin calculations."""
        margins = self.analyzer.calculate_yield_margins()
        self.assertIn('tension', margins)
        self.assertIn('shear', margins)
        self.assertIn('combined', margins)
        for margin in margins.values():
            self.assertIsInstance(margin, float)
        for margin in margins.values():
            self.assertGreater(margin, -1.0)

    def test_slip_margin(self):
        """Test joint slip margin calculation."""
        margin = self.analyzer.calculate_slip_margin()
        self.assertIsInstance(margin, float)
        self.assertGreater(margin, -1.0)

    def test_separation_margin(self):
        """Test joint separation margin calculation."""
        margin = self.analyzer.calculate_separation_margin()
        self.assertIsInstance(margin, float)
        self.assertGreater(margin, -1.0)

    def test_temperature_effects(self):
        """Test temperature compensation in calculations."""
        cold_env = Environment(
            tension=1000 * ureg.newton,
            shear=500 * ureg.newton,
            bending=100 * ureg.newton * ureg.meter,
            min_temp=200 * ureg.kelvin,  # Colder condition
            nom_temp=273.15 * ureg.kelvin,  # Cold nominal
            max_temp=300 * ureg.kelvin,
            preload_torque=50 * ureg.newton * ureg.meter
        )
        hot_env = Environment(
            tension=1000 * ureg.newton,
            shear=500 * ureg.newton,
            bending=100 * ureg.newton * ureg.meter,
            min_temp=300 * ureg.kelvin,
            nom_temp=373.15 * ureg.kelvin,  # Hot nominal
            max_temp=400 * ureg.kelvin,  # Hotter condition
            preload_torque=50 * ureg.newton * ureg.meter
        )
        
        cold_analyzer = NASA5020Analysis(self.junction, cold_env, **self.config)
        hot_analyzer = NASA5020Analysis(self.junction, hot_env, **self.config)
        
        cold_preloads = cold_analyzer.calculate_preloads()
        hot_preloads = hot_analyzer.calculate_preloads()
        
        # Verify that temperature affects preload
        self.assertNotEqual(cold_preloads['min_preload'], cold_preloads['max_preload'])
        self.assertNotEqual(hot_preloads['min_preload'], hot_preloads['max_preload'])
        self.assertNotEqual(cold_preloads['min_preload'], hot_preloads['max_preload'])

    def test_unit_conversion(self):
        """Test handling of different unit systems."""
        imperial_config = self.config.copy()
        imperial_config['unit_system'] = 'imperial'
        imperial_analyzer = NASA5020Analysis(self.junction, self.
            environment, **imperial_config)
        metric_preloads = self.analyzer.calculate_preloads()
        imperial_preloads = imperial_analyzer.calculate_preloads()
        # Compare magnitudes since the quantities represent the same physical value
        self.assertNotEqual(
            metric_preloads['nominal_preload'].magnitude,
            imperial_preloads['nominal_preload'].magnitude,
            "Metric and imperial preloads should have different numerical values")
from typing import Dict, Tuple, Any, Optional
from utils.unit_utils import ureg, Quantity
from junctions.junction import Junction
from environment.environment import Environment

## Helper equations from NASA5020
def _calculate_ultimate_margins(tension_load: Quantity, shear_load: Quantity,
    ultimate_tensile_strength: Quantity, ultimate_shear_strength: Quantity,
    safety_factor: float, fitting_factor: float, stress_area: Quantity=None
    ) ->Dict[str, float]:
    """
    Calculate ultimate strength margins per NASA-STD-5020 section 6.2.

    Implements equations from sections 6.2.1-6.2.3 for tension, shear,
    and combined loading conditions.

    Args:
        tension_load: Applied tensile load
        shear_load: Applied shear load
        ultimate_tensile_strength: Material ultimate tensile strength
        ultimate_shear_strength: Material ultimate shear strength
        safety_factor: Ultimate safety factor
        fitting_factor: Joint fitting factor

    Returns:
        Dict containing margins for:
            - tension: Ultimate tensile margin
            - shear: Ultimate shear margin
            - combined: Combined loading margin

    Note:
        All margins must be ≥ 0 per NASA-STD-5020
        Uses equation 6-1 format: MS = P'/(FF·FS·P_L) - 1
    """
    if stress_area is not None:
        tension_stress = tension_load / stress_area
        shear_stress = shear_load / stress_area
    else:
        tension_stress = tension_load
        shear_stress = shear_load
    tension_margin = ultimate_tensile_strength / (tension_stress *
        safety_factor * fitting_factor) - 1.0
    shear_margin = ultimate_shear_strength / (shear_stress * safety_factor *
        fitting_factor) - 1.0
    combined_ratio = ((tension_stress * safety_factor * fitting_factor /
        ultimate_tensile_strength) ** 2 + (shear_stress * safety_factor *
        fitting_factor / ultimate_shear_strength) ** 2) ** 0.5
    combined_margin = 1.0 / combined_ratio - 1.0
    return {'tension': float(tension_margin), 'shear': float(shear_margin),
        'combined': float(combined_margin)}


def _calculate_yield_margins(tension_load: Quantity, shear_load: Quantity,
    yield_strength: Quantity, safety_factor: float, fitting_factor: float,
    stress_area: Quantity=None) ->Dict[str, float]:
    """
    Calculate yield strength margins per NASA-STD-5020 section 6.3.

    Implements yield margin calculations for tension, shear, and combined loading
    using von Mises criterion for combined loading.

    Args:
        tension_load: Applied tensile load
        shear_load: Applied shear load
        yield_strength: Material yield strength
        safety_factor: Yield safety factor
        fitting_factor: Joint fitting factor

    Returns:
        Dict containing margins for:
            - tension: Yield tensile margin
            - shear: Yield shear margin (using 0.577 * yield_strength)
            - combined: Combined loading margin using von Mises

    Note:
        All margins must be ≥ 0 per NASA-STD-5020
        Shear yield strength is calculated as 0.577 * yield_strength per von Mises
    """
    if stress_area is not None:
        tension_stress = tension_load / stress_area
        shear_stress = shear_load / stress_area
    else:
        tension_stress = tension_load
        shear_stress = shear_load
    yield_shear = yield_strength * 0.577
    tension_margin = yield_strength / (tension_stress * safety_factor *
        fitting_factor) - 1.0
    shear_margin = yield_shear / (shear_stress * safety_factor * fitting_factor
        ) - 1.0
    combined_ratio = ((tension_stress * safety_factor * fitting_factor /
        yield_strength) ** 2 + 3 * (shear_stress * safety_factor *
        fitting_factor / yield_strength) ** 2) ** 0.5
    combined_margin = 1.0 / combined_ratio - 1.0
    return {'tension': float(tension_margin), 'shear': float(shear_margin),
        'combined': float(combined_margin)}


def _calculate_slip_margin(preload: Quantity, shear_load: Quantity,
    friction_coefficient: float) ->float:
    """
    Calculate joint slip safety margin per NASA-STD-5020 section 6.4.

    Calculates the margin against slip based on friction between surfaces.
    Per NASA-STD-5020, friction coefficients should not exceed:
    - 0.2 for uncoated, non-lubricated metal surfaces (cleaned and visibly clean)
    - 0.1 for all other surfaces (coated, lubricated, non-metallic)

    Args:
        preload: Joint preload force
        shear_load: Applied shear load
        friction_coefficient: Surface friction coefficient (≤ 0.2)

    Returns:
        float: Slip margin of safety

    Note:
        All margins must be ≥ 0 per NASA-STD-5020
        If margin is negative, friction cannot be used as shear load path
    """
    slip_resistance = friction_coefficient * preload
    margin = slip_resistance / shear_load - 1.0
    return float(margin)

def _calculate_separation_margin(preload: Quantity, external_load: Quantity,
    bolt_stiffness: Quantity, joint_stiffness: Quantity, safety_factor:
    float, fitting_factor: float, loading_plane_factor: float,
    stiffness_factor: float) ->float:
    """
    Calculate joint separation margin per NASA-STD-5020 section 6.5 and NASA-TM-106943.

    Implements equation 6-23 to determine margin against joint separation.
    Uses loading plane factor (n) and stiffness factor (Φ) from NASA-TM-106943
    to determine load at interface.

    Args:
        preload: Minimum preload in joint
        external_load: Applied tensile load
        bolt_stiffness: Bolt stiffness (k_b)
        joint_stiffness: Joint stiffness (k_c)
        safety_factor: Separation safety factor
        fitting_factor: Joint fitting factor
        loading_plane_factor: n factor from NASA-TM-106943
        stiffness_factor: Φ factor from NASA-TM-106943

    Returns:
        float: Separation margin of safety

    Note:
        All margins must be ≥ 0 per NASA-STD-5020
        Uses equation 6-23: MS_sep = P_i/(FF·FS_sep·P_L) - 1
        Modified to use NASA-TM-106943 load distribution factors
    """
    bolt_load_change = loading_plane_factor * stiffness_factor * external_load
    interface_load = preload - bolt_load_change
    margin = interface_load / (external_load * safety_factor * fitting_factor
        ) - 1.0
    return float(margin)



## Analysis Class

class NASA5020Analysis:
    """
    Implements NASA-STD-5020 bolted joint analysis calculations.

    This class uses the Junction and Environment objects to perform all required
    margin calculations according to NASA-STD-5020.

    Args:
        junction (Junction): Junction object containing bolt/joint geometry
        environment (Environment): Environment conditions including temperature
        **kwargs: Configuration parameters including:
            unit_system (str): 'metric' or 'imperial'
            friction_coefficient (float): Default 0.2 uncoated, 0.1 coated
            safety_factors (dict): Ultimate, yield, and separation factors
            fitting_factor (float): Joint fitting factor
    """

    def __init__(self, junction: Junction, environment: Environment, **kwargs):
        self.junction = junction
        self.environment = environment
        self.unit_system = kwargs.get('unit_system', 'metric')
        self.friction_coefficient = kwargs.get('friction_coefficient', 0.2)
        self.safety_factors = kwargs.get('safety_factors', {'ultimate': 1.4,
            'yield': 1.2, 'separation': 1.2})
        self.fitting_factor = kwargs.get('fitting_factor', 1.0)
        self.nut_factor = kwargs.get('nut_factor', 0.2)
        self.preload_uncertainty_factor = kwargs.get('preload_uncertainty_factor', 0.25)
        self._validate_inputs()

    def _validate_inputs(self) ->None:
        """
        Validates all input parameters and configuration.

        Raises:
            ValueError: If any inputs are invalid or out of range
            TypeError: If inputs have incorrect types
        """
        if not isinstance(self.junction, Junction):
            raise TypeError('junction must be a Junction object')
        if not isinstance(self.environment, Environment):
            raise TypeError('environment must be an Environment object')
        if self.unit_system not in ['metric', 'imperial']:
            raise ValueError("unit_system must be 'metric' or 'imperial'")
        if not isinstance(self.friction_coefficient, (int, float)):
            raise TypeError('friction_coefficient must be a number')
        if not 0 < self.friction_coefficient <= 1.0:
            raise ValueError('friction_coefficient must be between 0 and 1')
        if not isinstance(self.safety_factors, dict):
            raise TypeError('safety_factors must be a dictionary')
        required_factors = {'ultimate', 'yield', 'separation'}
        if not all(k in self.safety_factors for k in required_factors):
            raise ValueError(f'safety_factors must include {required_factors}')
        if not all(isinstance(v, (int, float)) and v > 1.0 for v in self.
            safety_factors.values()):
            raise ValueError(
                'all safety factors must be numbers greater than 1.0')
        if not isinstance(self.fitting_factor, (int, float)):
            raise TypeError('fitting_factor must be a number')
        if self.fitting_factor < 1.0:
            raise ValueError(
                'fitting_factor must be greater than or equal to 1.0')

    def _get_stress_area(self) ->Quantity:
        """Calculate stress area from fastener nominal diameter.

        Returns:
            Quantity: Stress area in mm² (metric) or in² (imperial)
        """
        diameter = self.junction.fastener._nominal_diameter
        if self.unit_system == 'metric':
            return (0.25 * 3.14159 * diameter ** 2).to('mm^2')
        else:
            return (0.25 * 3.14159 * diameter ** 2).to('in^2')

    def calculate_preloads(self) ->Dict[str, Quantity]:
        """Calculate minimum, maximum, and nominal preload values with temperature effects.

        Implements NASA-STD-5020 equations 6-2 through 6-5 for preload calculation:
        - Eq 6-2: P_i = P_i0 + ΔP_t
        - Eq 6-3: ΔP_t = (α_b - α_c)·ΔT·E_b·A_b
        - Eq 6-4: P_i_max = T/(K·D) for torque-controlled tightening
        - Eq 6-5: P_i_min = 0.75·P_i_max for reuse cases

        Where:
        - P_i: Installation preload
        - P_i0: Initial preload at room temperature
        - ΔP_t: Preload change due to temperature
        - α_b, α_c: Thermal expansion coefficients of bolt and joint
        - ΔT: Temperature change from room temperature
        - E_b: Bolt elastic modulus
        - A_b: Bolt stress area

        Returns:
            Dict containing:
                min_preload: Minimum preload value (Eq 6-5)
                max_preload: Maximum preload value (Eq 6-4)
                nominal_preload: Average of min and max preloads

        Note:
            Temperature compensation uses differential thermal expansion
            between bolt and joint materials per Eq 6-2 and 6-3.
            Valid for temperature ranges where material properties remain linear.
        """
        diameter = self.junction.fastener._nominal_diameter
        nut_factor = self.nut_factor
        base_preload = (self.environment.preload_torque / (nut_factor *diameter)).to_base_units()
        base_max_preload = (1 + self.preload_uncertainty_factor) * base_preload
        base_min_preload = (1 - self.preload_uncertainty_factor) * base_max_preload
        delta_T_cold = (self.environment.nom_temp - self.environment.min_temp).to('kelvin')
        delta_T_hot = (self.environment.max_temp - self.environment.nom_temp).to('kelvin')
        alpha_bolt = self.junction.fastener.material.thermal_expansion.to('1/kelvin')
        E_bolt = self.junction.fastener.material.elastic_modulus
        stress_area = self._get_stress_area()
        alphas = [comp.material.thermal_expansion.to('1/kelvin') for comp in self.junction.clamped_components]
        alpha_joint = sum(alphas) / len(alphas)
        delta_alpha = alpha_bolt - alpha_joint
        thermal_strain_hot = delta_alpha * delta_T_hot
        thermal_strain_cold = delta_alpha * delta_T_cold
        delta_P_t_hot = (thermal_strain_hot * E_bolt * stress_area).to_base_units()
        delta_P_t_cold = (thermal_strain_cold * E_bolt * stress_area).to_base_units()
        delta_P_t_max = max(abs(delta_P_t_hot), abs(delta_P_t_cold))
        delta_P_t_min = min(abs(delta_P_t_hot), abs(delta_P_t_cold))
        min_preload = base_min_preload - delta_P_t_min
        max_preload = base_max_preload + delta_P_t_max
        nominal_preload = base_preload
        target_unit = 'lbf' if self.unit_system == 'imperial' else 'newton'
        return {'min_preload': min_preload.to(target_unit), 'max_preload':
            max_preload.to(target_unit), 'nominal_preload': nominal_preload
            .to(target_unit)}

    def calculate_ultimate_margins(self) ->Dict[str, float]:
        """Calculate ultimate strength margins per NASA-STD-5020 section 6.2."""
        return _calculate_ultimate_margins(tension_load=self.environment.
            tension, shear_load=self.environment.shear,
            ultimate_tensile_strength=self.junction.fastener.material.
            ultimate_strength, ultimate_shear_strength=self.junction.
            fastener.material.ultimate_shear_strength, safety_factor=self.
            safety_factors['ultimate'], fitting_factor=self.fitting_factor,
            stress_area=self._get_stress_area())

    def calculate_yield_margins(self) ->Dict[str, float]:
        """Calculate yield strength margins per NASA-STD-5020 section 6.3."""
        return _calculate_yield_margins(tension_load=self.environment.
            tension, shear_load=self.environment.shear, yield_strength=self
            .junction.fastener.material.yield_strength, safety_factor=self.
            safety_factors['yield'], fitting_factor=self.fitting_factor,
            stress_area=self._get_stress_area())

    def calculate_slip_margin(self) ->float:
        """Calculate joint slip safety margin per NASA-STD-5020 section 6.4."""
        return _calculate_slip_margin(preload=self.calculate_preloads()[
            'nominal_preload'], shear_load=self.environment.shear,
            friction_coefficient=self.friction_coefficient)

    def calculate_separation_margin(self) ->float:
        """Calculate joint separation margin per NASA-STD-5020 section 6.5 and NASA-TM-106943."""
        k_b = self.junction.calculate_bolt_stiffness()
        k_c = self.junction.calculate_joint_stiffness()
        n = self.junction.calculate_loading_plane_factor()
        phi = self.junction.calculate_stiffness_factor()
        return _calculate_separation_margin(preload=self.calculate_preloads(
            )['min_preload'], external_load=self.environment.tension,
            bolt_stiffness=k_b, joint_stiffness=k_c, safety_factor=self.
            safety_factors['separation'], fitting_factor=self.
            fitting_factor, loading_plane_factor=n, stiffness_factor=phi)
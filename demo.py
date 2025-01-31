from units_config import ureg
from materials.material import Material
from materials.standard_materials import GenericSteel, GenericAluminum
from components.threaded_components import Fastener, Nut
from components.clamped_components import PlateComponent
from components.threaded_plate import ThreadedPlate
from junctions.junction import Junction
from environment.environment import Environment
from analysis.nasa5020 import NASA5020Analysis


def create_sample_joint():
    """Create a sample bolted joint assembly for demonstration.

    Creates a joint with:
    - 1/2-13 UNC bolt
    - Two aluminum plates being clamped
    - Standard steel hex nut

    Returns:
        Junction: The assembled joint
    """

    # Option 1: Use a pre-configured material for the bolt and nut
    steel = GenericSteel

    # Option 2: Create a custom aluminum for the plates
    aluminum = Material("Custom 6061-T6")
    aluminum.yield_strength = 276 * ureg.megapascal
    aluminum.ultimate_strength = 310 * ureg.megapascal
    aluminum.density = 2700 * ureg('kg/m^3')
    aluminum.poisson_ratio = 0.33
    aluminum.elastic_modulus = 69 * ureg.gigapascal
    aluminum.thermal_expansion = 2.31e-05 * ureg('1/K')

    bolt = Fastener(thread_spec='1/2-13 UNC',
                    length=2.5 * ureg.inch,
                    threaded_length=1.5 * ureg.inch,
                    head_diameter=0.75 * ureg.inch,
                    head_height=0.375 * ureg.inch,
                    is_flat=False,
                    tool_size='3/4',
                    material=steel
                    )

    plate1 = PlateComponent(thickness=0.5 * ureg.inch, material=aluminum)
    plate2 = PlateComponent(thickness=0.5 * ureg.inch, material=aluminum)

    nut = Nut(thread_spec='1/2-13 UNC',
              width_across_flats=0.75 * ureg.inch,
              height=0.375 * ureg.inch,
              material=steel
              )

    joint = Junction(fastener=bolt,
                     clamped_components=[plate1, plate2],
                     threaded_member=nut
                     )
    return joint


def create_sample_environment():
    """Create a sample loading environment for demonstration.

    Creates an environment with:
    - 1000 lbf tensile load
    - 500 lbf shear load
    - Room temperature nominal, 0F to 200F extremes
    - 30 ft-lbf installation torque

    Returns:
        Environment: The loading environment
    """
    env = Environment(tension=1000 * ureg.lbf,
                      shear=500 * ureg.lbf,
                      bending=0 * ureg('ft*lbf'),
                      min_temp=255 * ureg.degK,
                      nom_temp=295 * ureg.degK,
                      max_temp=310 * ureg.degK,
                      preload_torque=50 * ureg('ft*lbf')
                    )
    return env


def run_analysis():
    """Run a complete NASA-5020 analysis on a sample joint."""
    joint = create_sample_joint()
    env = create_sample_environment()

    analyzer = NASA5020Analysis(junction=joint,
                                environment=env,
                                unit_system='imperial',
                                friction_coefficient=0.15,
                                safety_factors={'ultimate': 1.4,
                                                'yield': 1.2,
                                                'separation': 1.2},
                                fitting_factor=1.15
                                )
    preloads = analyzer.calculate_preloads()
    print('\nPreload Analysis:')
    print(f"Minimum preload: {preloads['min_preload']:.0f}")
    print(f"Maximum preload: {preloads['max_preload']:.0f}")
    print(f"Nominal preload: {preloads['nominal_preload']:.0f}")
    ultimate_margins = analyzer.calculate_ultimate_margins()
    print('\nUltimate Strength Margins:')
    print(f"Tension: {ultimate_margins['tension']:.3f}")
    print(f"Shear: {ultimate_margins['shear']:.3f}")
    print(f"Combined: {ultimate_margins['combined']:.3f}")
    yield_margins = analyzer.calculate_yield_margins()
    print('\nYield Strength Margins:')
    print(f"Tension: {yield_margins['tension']:.3f}")
    print(f"Shear: {yield_margins['shear']:.3f}")
    print(f"Combined: {yield_margins['combined']:.3f}")
    slip_margin = analyzer.calculate_slip_margin()
    print(f'\nSlip Margin: {slip_margin:.3f}')
    separation_margin = analyzer.calculate_separation_margin()
    print(f'\nSeparation Margin: {separation_margin:.3f}')


if __name__ == '__main__':
    run_analysis()

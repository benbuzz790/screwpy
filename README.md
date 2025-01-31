# ScrewPy

ScrewPy is a Python library for analyzing bolted joints and fastener assemblies according to NASA-STD-5020. It provides tools for calculating grip lengths, stack-up thicknesses, validating fastener assemblies, and performing comprehensive joint analysis.

## Key Features

- Support for both metric and imperial fasteners
- Material property management
- Component validation
- Assembly validation
- Unit conversion handling using Pint

## Current Limitations
- Limited to UNC, UNF, and metric thread types
- Basic thermal analysis (linear properties only)
- Single-fastener joints only

## Installation

```bash
pip install git+https://github.com/benbuzz790/screwpy.git
```

## Quick Start

```python
from units_config import ureg
from materials.material import Material
from materials.standard_materials import GenericSteel
from components.threaded_components import Fastener, Nut
from components.clamped_components import PlateComponent
from junctions.junction import Junction
from environment.environment import Environment
from analysis.nasa5020 import NASA5020Analysis

# Option 1: Use a pre-configured material
steel = GenericSteel  # Already configured with standard properties

# Option 2: Create a custom material
steel = Material("4340 Steel")
steel.yield_strength = 120000 * ureg.psi
steel.ultimate_strength = 140000 * ureg.psi
steel.elastic_modulus = 29e6 * ureg.psi
steel.thermal_expansion = 6.7e-6 * ureg('1/K')
steel.poisson_ratio = 0.29

# Create fastener
fastener = Fastener(
    thread_spec="1/2-13 UNC",
    length=2.5 * ureg.inch,
    threaded_length=1.5 * ureg.inch,
    head_diameter=0.75 * ureg.inch,
    head_height=0.375 * ureg.inch,
    is_flat=False,
    tool_size="3/4",
    material=steel
)

# Create two plates
plate1 = PlateComponent(
    thickness=0.5 * ureg.inch,
    material=steel
)
plate2 = PlateComponent(
    thickness=0.5 * ureg.inch,
    material=steel
)

# Create nut
nut = Nut(
    thread_spec="1/2-13 UNC",
    width_across_flats=0.75 * ureg.inch,
    height=0.375 * ureg.inch,
    material=steel
)

# Create assembly
junction = Junction(
    fastener=fastener,
    clamped_components=[plate1, plate2],
    threaded_member=nut
)

# Define environment
env = Environment(
    tension=1000 * ureg.lbf,
    shear=500 * ureg.lbf,
    bending=0 * ureg('ft*lbf'),
    min_temp=0 * ureg.degF,
    nom_temp=70 * ureg.degF,
    max_temp=200 * ureg.degF,
    preload_torque=30 * ureg('ft*lbf')
)

# Run NASA-5020 analysis
analyzer = NASA5020Analysis(
    junction=junction,
    environment=env,
    unit_system='imperial',
    friction_coefficient=0.15,
    safety_factors={
        'ultimate': 1.4,
        'yield': 1.2,
        'separation': 1.2
    },
    fitting_factor=1.15
)

# Get results
preloads = analyzer.calculate_preloads()
ultimate_margins = analyzer.calculate_ultimate_margins()
yield_margins = analyzer.calculate_yield_margins()
slip_margin = analyzer.calculate_slip_margin()
separation_margin = analyzer.calculate_separation_margin()
```

## NASA-STD-5020 Analysis

The library implements calculations from NASA-STD-5020 including:

- Preload calculations with temperature effects (NASA-STD-5020 sections 6.2-6.5)
- Ultimate strength margins (section 6.2)
- Yield strength margins (section 6.3)
- Joint slip resistance (section 6.4)
- Joint separation analysis (section 6.5)

## Documentation

- `doc/fastener_data_structure_spec.md`: Core data structure specifications
- `doc/nasa5020_analysis_spec.md`: Analysis method specifications
- `doc/nasa5020.md`: NASA-STD-5020 section 6, excerpted and converted to .md for llms

Each Python module also contains detailed docstrings with examples.

## Requirements

Each Python file has an accompanying requirements file (*_req.txt). The main project requirements are in project_req.txt.

## Testing

```bash
pytest
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](LICENSE)

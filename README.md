# ScrewPy

ScrewPy is a Python library for analyzing bolted joints and fastener assemblies. It provides tools for calculating grip lengths, stack-up thicknesses, and validating fastener assemblies.

## Features

- Support for both metric and imperial fasteners
- Material property management
- Component validation
- Assembly validation
- Unit conversion handling using Pint

## Installation

```bash
pip install screwpy
```

## Quick Start

```python
from screwpy.components import Fastener, Nut, PlateComponent
from screwpy.materials import StandardMaterials
from screwpy.junctions import Junction

# Create components
fastener = Fastener(
    thread_spec="1/2-13 UNC",
    length=2.0 * ureg.inch,
    material=StandardMaterials.steel()
)

plate = PlateComponent(
    thickness=0.25 * ureg.inch,
    material=StandardMaterials.aluminum()
)

nut = Nut(
    thread_spec="1/2-13 UNC",
    material=StandardMaterials.steel()
)

# Create and validate assembly
junction = Junction(
    fastener=fastener,
    clamped_components=[plate],
    threaded_member=nut
)
```

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

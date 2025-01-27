"""
Centralized unit registry configuration for the entire system.

This module provides a system-wide pint UnitRegistry configured for consistent
unit handling across the application. It exports a single ureg instance and
the Quantity type that should be used by all other modules.

Default Units:
    - Length: inch (also supports mm, m)
    - Force: lbf (also supports N)
    - Stress: psi (also supports MPa)
    - Mass: lb (also supports kg)
    - Density: lb/in³ (also supports kg/m³)
    - Temperature: °F (also supports °C, K)
    - Thermal expansion: 1/°F (also supports 1/K)

Usage:
    >>> from units_config import ureg, Quantity
    >>> length = 10 * ureg.inch
    >>> length.to('mm')
    >>> def my_func(value: Quantity) -> Quantity:
    ...     return value * 2

Best Practices:
    1. Always import ureg and Quantity from this module
    2. Use consistent units within calculations
    3. Convert to standard units early
    4. Validate unit types before operations
    5. Use Quantity type hints for clarity
"""

import pint
from pint import Quantity

# Create and configure the unit registry
ureg = pint.UnitRegistry()
ureg.default_system = 'imperial'
ureg.default_format = '~P'  # Compact pretty format

# Define custom units for threads
ureg.define('tpi = count / inch = threads_per_inch')  # threads per inch
ureg.define('thread_pitch = inch/count = inch/threads')  # pitch in inches
ureg.define('mm_pitch = millimeter = mm_per_thread')  # pitch in mm

# Make ureg and Quantity available for import
__all__ = ['ureg', 'Quantity']

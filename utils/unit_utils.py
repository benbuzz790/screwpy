from typing import Union, Optional
import math
from pint import Quantity, UnitRegistry
from units_config import ureg


def to_imperial(quantity: Quantity) ->Quantity:
    """Convert a quantity to standard imperial units.

    Args:
        quantity: The quantity to convert

    Returns:
        The quantity in standard imperial units

    Raises:
        ValueError: If conversion is not possible
    """
    dim = quantity.dimensionality
    if dim == ureg.meter.dimensionality:
        return quantity.to('inch')
    elif dim == ureg.newton.dimensionality:
        return quantity.to('lbf')
    elif dim == ureg.pascal.dimensionality:
        return quantity.to('psi')
    elif dim == ureg.kelvin.dimensionality:
        return quantity.to('degF')
    elif dim == (ureg.kilogram / ureg.meter ** 3).dimensionality:
        return quantity.to('lb/inch**3')
    elif dim == (1 / ureg.kelvin).dimensionality:
        return quantity.to('1/degF')
    elif dim == ureg.dimensionless:
        return quantity
    else:
        raise ValueError(f'No imperial conversion defined for dimension {dim}')


def to_metric(quantity: Quantity) ->Quantity:
    """Convert a quantity to standard metric units.

    Args:
        quantity: The quantity to convert

    Returns:
        The quantity in standard metric units

    Raises:
        ValueError: If conversion is not possible
    """
    dim = quantity.dimensionality
    if dim == ureg.meter.dimensionality:
        return quantity.to('millimeter')
    elif dim == ureg.newton.dimensionality:
        return quantity.to('newton')
    elif dim == ureg.pascal.dimensionality:
        return quantity.to('megapascal')
    elif dim == ureg.kelvin.dimensionality:
        return quantity.to('degC')
    elif dim == (ureg.kilogram / ureg.meter ** 3).dimensionality:
        return quantity.to('kg/m**3')
    elif dim == (1 / ureg.kelvin).dimensionality:
        return quantity.to('1/K')
    elif dim == ureg.dimensionless:
        return quantity
    else:
        raise ValueError(f'No metric conversion defined for dimension {dim}')


def standardize_units(quantity: Quantity, preferred: str) ->Quantity:
    """Convert a quantity to the preferred unit system.

    Args:
        quantity: The quantity to convert
        preferred: Either 'imperial' or 'metric'

    Returns:
        The quantity in the preferred unit system

    Raises:
        ValueError: If preferred system is invalid or conversion fails
    """
    if preferred.lower() not in ['imperial', 'metric']:
        raise ValueError("preferred must be 'imperial' or 'metric'")
    if preferred.lower() == 'imperial':
        return to_imperial(quantity)
    else:
        return to_metric(quantity)


def is_valid_unit_type(quantity: Quantity, expected_type: str) ->bool:
    """Check if a quantity has the expected unit type.

    Args:
        quantity: The quantity to check
        expected_type: String representing expected dimension (e.g. 'length', 'force')

    Returns:
        True if quantity matches expected type, False otherwise
    """
    dim_map = {'length': ureg.meter.dimensionality, 'force': ureg.newton.
        dimensionality, 'pressure': ureg.pascal.dimensionality,
        'temperature': ureg.kelvin.dimensionality, 'density': (ureg.
        kilogram / ureg.meter ** 3).dimensionality, 'thermal_expansion': (1 /
        ureg.kelvin).dimensionality, 'dimensionless': ureg.dimensionless}
    if expected_type not in dim_map:
        raise ValueError(f'Unknown unit type: {expected_type}')
    return quantity.dimensionality == dim_map[expected_type]


def are_units_compatible(q1: Quantity, q2: Quantity) ->bool:
    """Check if two quantities have compatible units.

    Args:
        q1: First quantity
        q2: Second quantity

    Returns:
        True if units are compatible, False otherwise
    """
    try:
        _ = q1 + q2
        return True
    except:
        return False


def validate_unit_dimension(quantity: Quantity, dimension: str) ->bool:
    """Validate that a quantity has the expected dimension.

    Args:
        quantity: The quantity to validate
        dimension: Expected dimension string (e.g. '[length]', '[mass]/[length]^3')

    Returns:
        True if dimensions match, False otherwise
    """
    try:
        expected = ureg.parse_units(dimension).dimensionality
        return quantity.dimensionality == expected
    except:
        return False


def safe_add(q1: Quantity, q2: Quantity) ->Quantity:
    """Safely add two quantities with unit validation.

    Args:
        q1: First quantity
        q2: Second quantity

    Returns:
        Sum of quantities

    Raises:
        ValueError: If units are incompatible
    """
    if not are_units_compatible(q1, q2):
        raise ValueError(f'Incompatible units: {q1.units} and {q2.units}')
    return q1 + q2


def safe_multiply(q1: Quantity, q2: Quantity) ->Quantity:
    """Safely multiply two quantities.

    Args:
        q1: First quantity
        q2: Second quantity

    Returns:
        Product of quantities
    """
    return q1 * q2


def safe_divide(q1: Quantity, q2: Quantity) ->Quantity:
    """Safely divide two quantities.

    Args:
        q1: First quantity (numerator)
        q2: Second quantity (denominator)

    Returns:
        Quotient of quantities

    Raises:
        ValueError: If denominator is zero
    """
    if q2.magnitude == 0:
        raise ValueError('Division by zero')
    return q1 / q2


def compare_with_tolerance(q1: Quantity, q2: Quantity, tolerance: float
    ) ->bool:
    """Compare two quantities within a relative tolerance.

    Args:
        q1: First quantity
        q2: Second quantity
        tolerance: Relative tolerance (e.g. 0.01 for 1%)

    Returns:
        True if quantities are equal within tolerance

    Raises:
        ValueError: If units are incompatible
    """
    if not are_units_compatible(q1, q2):
        raise ValueError(f'Incompatible units: {q1.units} and {q2.units}')
    q2_conv = q2.to(q1.units)
    rel_diff = abs((q1.magnitude - q2_conv.magnitude) / q1.magnitude)
    return rel_diff <= tolerance


def format_quantity(quantity: Quantity, precision: int) ->str:
    """Format a quantity with specified precision.

    Args:
        quantity: The quantity to format
        precision: Number of decimal places

    Returns:
        Formatted string with value and units
    """
    format_str = f'{{:.{precision}f}} {{}}'
    return format_str.format(quantity.magnitude, quantity.units)


def format_with_units(quantity: Quantity) ->str:
    """Format a quantity with its units.

    Args:
        quantity: The quantity to format

    Returns:
        String representation with units
    """
    return f'{quantity:~P}'


"""Unit conversion and validation utilities.

This module provides utility functions for common unit operations and conversions
across the system. It supports both imperial and metric units through pint,
with a preference for imperial units.

The module provides functions for:
- Unit conversions between imperial and metric systems
- Unit validation and compatibility checking
- Safe arithmetic operations with units
- Unit formatting and display

Examples:
    >>> length = 25.4 * ureg.millimeter
    >>> to_imperial(length)
    <Quantity(1.0, 'inch')>

    >>> force1 = 10 * ureg.lbf
    >>> force2 = 50 * ureg.newton
    >>> are_units_compatible(force1, force2)
    True
"""

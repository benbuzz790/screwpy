"""Unit handling utilities for NASA-STD-5020 fastener analysis.

This module provides a comprehensive set of utilities for handling units in fastener analysis,
following NASA-STD-5020 standards. SI/metric units are used as the default system, with
imperial units supported as alternates.

Common Usage:
    Converting units:
        >>> force = 100 * ureg.lbf
        >>> force_metric = to_metric(force)  # converts to newtons
        >>> pressure = 100 * ureg.pascal
        >>> pressure_imperial = to_imperial(pressure)  # converts to psi

    Validating units:
        >>> is_valid_unit_type(force, '[M][L]/[T]^2')  # checks force dimensions
        >>> are_units_compatible(force1, force2)  # checks if units can be combined

    Safe operations:
        >>> total_force = safe_add(force1, force2)  # validates before adding
        >>> moment = safe_multiply(force, distance)  # handles mixed units
        >>> stress = safe_divide(force, area)  # includes zero checks

    Formatting output:
        >>> print(format_quantity(force, 2))  # "100.00 N"
        >>> print(format_with_units(pressure))  # "100 MPa"

Unit Compatibility Rules:
    - Length: millimeter (mm) <-> inch
    - Force: newton (N) <-> pound-force (lbf)
    - Pressure: megapascal (MPa) <-> pounds per square inch (psi)
    - Temperature: celsius (°C) <-> fahrenheit (°F)
    - Density: kilogram/meter³ <-> pound/inch³

Best Practices:
    1. Always validate unit types before operations
    2. Use safe_* functions for mathematical operations
    3. Standardize units early in calculations
    4. Handle temperature conversions separately (non-linear)
    5. Use format_* functions for consistent output

Error Handling:
    ValueError is raised for:
        - Invalid unit types or dimensions
        - Incompatible unit combinations
        - Division by zero
        - Invalid conversion requests
    Error messages include context about expected vs received values.

See Also:
    NASA-STD-5020: Requirements for Threaded Fastening Systems in Spaceflight Hardware
"""

from typing import Union
from units_config import ureg, Quantity

def to_metric(quantity: Quantity) -> Quantity:
    """Convert a quantity to standard SI/metric units following NASA-STD-5020.

    Converts the input quantity to the appropriate metric unit based on its dimension:
        - Length: millimeters (mm)
        - Force: newtons (N)
        - Pressure: megapascals (MPa)
        - Temperature: celsius (°C)
        - Density: kilogram/meter³
        - Moment: newton-meters (N⋅m)

    Args:
        quantity: The quantity to convert. Must have valid dimensions.

    Returns:
        Quantity: The converted value in standard metric units.

    Raises:
        ValueError: If the quantity has unsupported dimensions.

    Examples:
        >>> length = 1 * ureg.inch
        >>> to_metric(length)
        <Quantity(25.4, 'millimeter')>

        >>> force = 100 * ureg.lbf
        >>> to_metric(force)
        <Quantity(444.822, 'newton')>

        >>> temp = 32 * ureg.degF
        >>> to_metric(temp)
        <Quantity(0, 'degree_Celsius')>
    """
    if quantity.dimensionless:
        return quantity

    if quantity.check('[temperature]'):
        return quantity.to('degree_Celsius')
    elif quantity.check('[mass] * [length] / [time] ** 2'):
        return quantity.to('newton')
    elif quantity.check('[mass] / [length] / [time] ** 2'):
        return quantity.to('megapascal')
    elif quantity.check('[length]'):
        return quantity.to('millimeter')
    elif quantity.check('[mass] * [length] ** 2 / [time] ** 2'):
        return quantity.to('newton_meter')
    elif quantity.check('[mass] / [length] ** 3'):
        return quantity.to('kilogram/meter**3')
    else:
        raise ValueError(f"Unsupported dimensions: {quantity.dimensionality}")
def to_imperial(quantity: Quantity) -> Quantity:
    """Convert a quantity to standard imperial units as alternate to NASA-STD-5020 SI units.

    Converts the input quantity to the appropriate imperial unit based on its dimension:
        - Length: inches (in)
        - Force: pound-force (lbf)
        - Pressure: pounds per square inch (psi)
        - Temperature: fahrenheit (°F)
        - Density: pound/inch³
        - Moment: foot-pounds (ft⋅lb)

    Args:
        quantity: The quantity to convert. Must have valid dimensions.

    Returns:
        Quantity: The converted value in standard imperial units.

    Raises:
        ValueError: If the quantity has unsupported dimensions.

    Examples:
        >>> length = 25.4 * ureg.millimeter
        >>> to_imperial(length)
        <Quantity(1.0, 'inch')>

        >>> force = 445 * ureg.newton
        >>> to_imperial(force)
        <Quantity(100.04, 'lbf')>

        >>> temp = 100 * ureg.degC
        >>> to_imperial(temp)
        <Quantity(212.0, 'degree_Fahrenheit')>
    """
    if quantity.dimensionless:
        return quantity

    if quantity.check('[temperature]'):
        return quantity.to('degree_Fahrenheit')
    elif quantity.check('[mass] * [length] / [time] ** 2'):
        return quantity.to('lbf')
    elif quantity.check('[mass] / [length] / [time] ** 2'):
        return quantity.to('psi')
    elif quantity.check('[length]'):
        return quantity.to('inch')
    elif quantity.check('[mass] * [length] ** 2 / [time] ** 2'):
        return quantity.to('foot_pound')
    elif quantity.check('[mass] / [length] ** 3'):
        return quantity.to('pound/inch**3')
    else:
        raise ValueError(f"Unsupported dimensions: {quantity.dimensionality}")

def standardize_units(quantity: Quantity, preferred: str = 'metric') -> Quantity:
    """Convert a quantity to standard units in the preferred system.

    Following NASA-STD-5020, metric/SI is the default standard system, with
    imperial units available as alternates. This function provides a unified
    interface to both to_metric() and to_imperial().

    Args:
        quantity: The quantity to convert. Must have valid dimensions.
        preferred: The preferred unit system, either 'metric' (default) or 'imperial'.
            Metric is the NASA standard, imperial provided as alternate.

    Returns:
        Quantity: The converted value in the preferred system's standard units.

    Raises:
        ValueError: If preferred is not 'metric' or 'imperial', or if the quantity
            has unsupported dimensions.

    Examples:
        >>> # Default behavior (metric)
        >>> force = 100 * ureg.lbf
        >>> standardize_units(force)
        <Quantity(444.822, 'newton')>

        >>> # Explicit system choice
        >>> length = 25.4 * ureg.millimeter
        >>> standardize_units(length, preferred='imperial')
        <Quantity(1.0, 'inch')>

        >>> # Dimensionless quantities are unchanged
        >>> ratio = 0.5 * ureg.dimensionless
        >>> standardize_units(ratio)
        <Quantity(0.5, 'dimensionless')>
    """
    if preferred not in ['metric', 'imperial']:
        raise ValueError("preferred must be 'metric' or 'imperial'")
    if preferred == 'imperial':
        return to_imperial(quantity)
    return to_metric(quantity)
def convert_to_pint_dimensions(shorthand: str) -> str:
    """Convert shorthand dimension format to pint's format.

    Converts various dimension notations to pint's native format:
        - Shorthand: '[L]', '[M][L]/[T]^2', '[M]/[L]^3'
        - Special case: '[T]' -> '[temperature]' or '[time]' based on context
        - Inverse units: '1/[T]' -> '1/[temperature]'

    Args:
        shorthand: Dimension string in shorthand format.

    Returns:
        str: Equivalent dimension string in pint's native format.

    Examples:
        >>> convert_to_pint_dimensions('[L]')
        '[length]'
        >>> convert_to_pint_dimensions('[M][L]/[T]^2')
        '[mass] * [length] / [time] ** 2'
        >>> convert_to_pint_dimensions('1/[T]')
        '1/[temperature]'
    """
    if not shorthand:  # Handle dimensionless case
        return ''

    # Handle inverse units
    if shorthand.startswith('1/'):
        inner = shorthand[2:]  # Remove '1/'
        return '1/' + convert_to_pint_dimensions(inner)

    # Special case for temperature and time (both use T)
    if '[T]' in shorthand:
        # If it's in a compound dimension with M or L, it's time
        if '[M]' in shorthand or '[L]' in shorthand:
            result = shorthand.replace('[T]', '[time]')
        else:
            # Otherwise it's temperature
            result = shorthand.replace('[T]', '[temperature]')
    else:
        result = shorthand

    # Special case for pressure
    if result == '[M][L]/[time]^2/[L]^2':
        return '[mass] / [length] / [time] ** 2'

    # Map shorthand to pint names
    result = result.replace('[L]', '[length]')
    result = result.replace('[M]', '[mass]')
    result = result.replace('^2', ' ** 2')
    result = result.replace('^3', ' ** 3')

    # Handle multiplication
    if '][' in result:
        result = result.replace('][', '] * [')

    return result

def is_valid_unit_type(quantity: Quantity, expected_dimension: str) -> bool:
    """Check if a quantity has the expected dimensionality.

    Validates that a quantity's dimensions match the expected type. Supports both
    shorthand notation and pint's native dimension format. Shorthand uses [L] for
    length, [M] for mass, [T] for time/temperature based on context.

    Args:
        quantity: The quantity to check.
        expected_dimension: The expected dimension in one of these formats:
            - Shorthand: '[L]', '[M][L]/[T]^2', '[M]/[L]^3'
            - Pint native: '[length]', '[mass] * [length] / [time] ** 2'
            - Plain names: 'length', 'mass', 'time', 'temperature'
            - Empty string for dimensionless quantities

    Returns:
        bool: True if the quantity's dimensions match the expected type.

    Raises:
        ValueError: If expected_dimension format is invalid.

    Examples:
        >>> # Using shorthand notation
        >>> force = 100 * ureg.newton
        >>> is_valid_unit_type(force, '[M][L]/[T]^2')
        True

        >>> # Using pint native format
        >>> is_valid_unit_type(force, '[mass] * [length] / [time] ** 2')
        True

        >>> # Using plain dimension names
        >>> length = 1 * ureg.meter
        >>> is_valid_unit_type(length, 'length')
        True

        >>> # Checking dimensionless quantities
        >>> ratio = 0.5 * ureg.dimensionless
        >>> is_valid_unit_type(ratio, '')
        True

        >>> # Temperature special case
        >>> temp = 100 * ureg.kelvin
        >>> is_valid_unit_type(temp, '[T]')  # [T] means temperature here
        True
    """
    if not expected_dimension:  # Handle dimensionless case
        return quantity.dimensionless

    # Convert plain dimension names to bracketed format
    if expected_dimension in {'length', 'mass', 'time', 'temperature'}:
        expected_dimension = f'[{expected_dimension}]'

    # Convert shorthand to pint format if needed
    if any(x in expected_dimension for x in 'LMT[]'):
        pint_dims = convert_to_pint_dimensions(expected_dimension)
    else:
        # If no special chars, treat as direct pint dimension name
        pint_dims = expected_dimension

    try:
        return quantity.check(pint_dims)
    except (AttributeError, KeyError):
        raise ValueError(f"Invalid dimension format: {expected_dimension}")

def are_units_compatible(q1: Quantity, q2: Quantity) -> bool:
    """Check if two quantities have compatible units for mathematical operations.

    Determines if two quantities can be used together in mathematical operations
    by checking their fundamental dimensions. Units are compatible if they share
    the same base dimensions (e.g., meters and inches are both [length]).

    Args:
        q1: First quantity to compare
        q2: Second quantity to compare

    Returns:
        bool: True if the quantities share the same base dimensions.

    Examples:
        >>> # Length units are compatible
        >>> are_units_compatible(1 * ureg.meter, 1 * ureg.inch)
        True

        >>> # Force units are compatible
        >>> are_units_compatible(1 * ureg.newton, 1 * ureg.lbf)
        True

        >>> # Length and force are not compatible
        >>> are_units_compatible(1 * ureg.meter, 1 * ureg.newton)
        False

        >>> # Temperature units are compatible
        >>> are_units_compatible(0 * ureg.degC, 32 * ureg.degF)
        True

        >>> # Dimensionless quantities are compatible
        >>> are_units_compatible(0.5 * ureg.dimensionless, 1.0 * ureg.dimensionless)
        True
    """
    return q1.dimensionality == q2.dimensionality

def validate_unit_dimension(quantity: Quantity, expected_dimension: str) -> bool:
    """Validate that a quantity has the expected dimensionality.

    Similar to is_valid_unit_type() but intended for validation workflows where
    returning False is preferred over raising exceptions. Useful in data validation
    and input checking scenarios.

    Args:
        quantity: The quantity to validate
        expected_dimension: The expected dimension in any supported format:
            - Shorthand: '[L]', '[M][L]/[T]^2'
            - Pint native: '[length]', '[mass] * [length] / [time] ** 2'
            - Plain names: 'length', 'mass', 'time', 'temperature'

    Returns:
        bool: True if dimensions match, False otherwise (including invalid formats)

    Examples:
        >>> # Basic validation
        >>> validate_unit_dimension(1 * ureg.meter, 'length')
        True

        >>> # Invalid dimension returns False
        >>> validate_unit_dimension(1 * ureg.meter, 'mass')
        False

        >>> # Invalid format returns False
        >>> validate_unit_dimension(1 * ureg.meter, 'invalid')
        False

        >>> # Complex dimensions
        >>> pressure = 1 * ureg.pascal
        >>> validate_unit_dimension(pressure, '[M][L]/[T]^2/[L]^2')
        True
    """
    try:
        return is_valid_unit_type(quantity, expected_dimension)
    except ValueError:
        return False
def safe_add(q1: Quantity, q2: Quantity) -> Quantity:
    """Safely add two quantities with unit validation.

    Validates unit compatibility before performing addition. Units must have the
    same base dimensions (e.g., both lengths or both forces) to be added.

    Args:
        q1: First quantity to add
        q2: Second quantity to add

    Returns:
        Quantity: Sum of the two quantities in the units of q1

    Raises:
        ValueError: If the quantities have incompatible units

    Examples:
        >>> # Adding same units
        >>> safe_add(1 * ureg.meter, 100 * ureg.centimeter)
        <Quantity(2.0, 'meter')>

        >>> # Adding different but compatible units
        >>> safe_add(1 * ureg.newton, 0.22481 * ureg.lbf)
        <Quantity(2.0, 'newton')>

        >>> # Incompatible units raise error
        >>> safe_add(1 * ureg.meter, 1 * ureg.second)
        Traceback (most recent call last):
            ...
        ValueError: Cannot add quantities with units meter and second
    """
    if not are_units_compatible(q1, q2):
        raise ValueError(f"Cannot add quantities with units {q1.units} and {q2.units}")
    return q1 + q2

def safe_multiply(q1: Quantity, q2: Union[Quantity, float]) -> Quantity:
    """Safely multiply quantities or quantity and scalar.

    Handles both quantity-quantity multiplication (resulting in compound units)
    and quantity-scalar multiplication (preserving original units).

    Args:
        q1: First quantity to multiply
        q2: Second quantity or scalar value

    Returns:
        Quantity: Product with appropriate compound units

    Examples:
        >>> # Quantity * scalar
        >>> safe_multiply(2 * ureg.meter, 3.0)
        <Quantity(6.0, 'meter')>

        >>> # Quantity * Quantity
        >>> safe_multiply(2 * ureg.newton, 3 * ureg.meter)
        <Quantity(6.0, 'newton * meter')>

        >>> # Creating compound units
        >>> force = 10 * ureg.newton
        >>> distance = 2 * ureg.meter
        >>> safe_multiply(force, distance)  # Creates torque
        <Quantity(20.0, 'newton * meter')>
    """
    return q1 * q2

def safe_divide(q1: Quantity, q2: Union[Quantity, float]) -> Quantity:
    """Safely divide quantities or quantity by scalar, preventing division by zero.

    Handles both quantity-quantity division (resulting in derived units)
    and quantity-scalar division (preserving original units). Includes
    validation to prevent division by zero.

    Args:
        q1: Numerator quantity
        q2: Denominator quantity or scalar

    Returns:
        Quantity: Quotient with appropriate derived units

    Raises:
        ValueError: If attempting to divide by zero

    Examples:
        >>> # Quantity / scalar
        >>> safe_divide(6 * ureg.meter, 2.0)
        <Quantity(3.0, 'meter')>

        >>> # Quantity / Quantity
        >>> safe_divide(6 * ureg.meter, 2 * ureg.second)
        <Quantity(3.0, 'meter / second')>

        >>> # Division by zero raises error
        >>> safe_divide(6 * ureg.meter, 0)
        Traceback (most recent call last):
            ...
        ValueError: Division by zero
    """
    if isinstance(q2, Quantity):
        if q2.magnitude == 0:
            raise ValueError("Division by zero")
    elif q2 == 0:
        raise ValueError("Division by zero")
    return q1 / q2

def compare_with_tolerance(q1: Quantity, q2: Quantity, tolerance: float = 1e-6) -> bool:
    """Compare two quantities within a relative tolerance.

    Compares quantities with compatible units, allowing for small numerical
    differences that may arise from unit conversions or floating point math.
    Uses relative tolerance for comparison.

    Args:
        q1: First quantity to compare
        q2: Second quantity to compare
        tolerance: Maximum allowed relative difference (default: 1e-6)

    Returns:
        bool: True if quantities are equal within tolerance

    Raises:
        ValueError: If quantities have incompatible units

    Examples:
        >>> # Basic comparison
        >>> q1 = 1.0 * ureg.meter
        >>> q2 = 1.001 * ureg.meter
        >>> compare_with_tolerance(q1, q2, 0.01)  # 1% tolerance
        True

        >>> # Unit conversion comparison
        >>> q1 = 1 * ureg.inch
        >>> q2 = 25.4 * ureg.millimeter
        >>> compare_with_tolerance(q1, q2)
        True

        >>> # Incompatible units raise error
        >>> compare_with_tolerance(1 * ureg.meter, 1 * ureg.second)
        Traceback (most recent call last):
            ...
        ValueError: Cannot compare quantities with units meter and second
    """
    if not are_units_compatible(q1, q2):
        raise ValueError(f"Cannot compare quantities with units {q1.units} and {q2.units}")
    return abs((q1 - q2)/q1) < tolerance
def format_unit_string(unit_str: str) -> str:
    """Format unit string with proper symbols and abbreviations.

    Converts pint's internal unit names to standard scientific notation:
        - Temperature: 'degree_Celsius' -> '°C', 'degree_Fahrenheit' -> '°F'
        - Pressure: 'megapascal' -> 'MPa'
        - Basic units: 'meter' -> 'm', 'newton' -> 'N'
        - Compound units: 'newton_meter' -> 'N⋅m'
        - Powers: 'meter**3' -> 'm³'

    Args:
        unit_str: The unit string to format

    Returns:
        str: Properly formatted unit string

    Examples:
        >>> format_unit_string('degree_Celsius')
        '°C'
        >>> format_unit_string('newton_meter')
        'N⋅m'
        >>> format_unit_string('kilogram/meter**3')
        'kg/m³'
    """
    if 'degree_Fahrenheit' in unit_str:
        return '°F'
    elif 'degree_Celsius' in unit_str:
        return '°C'
    elif 'megapascal' in unit_str:
        return 'MPa'
    elif unit_str == 'meter':
        return 'm'
    elif unit_str == 'millimeter':
        return 'mm'
    elif unit_str == 'newton':
        return 'N'
    elif unit_str == 'newton_meter':
        return 'N⋅m'
    elif unit_str == 'kilogram/meter**3':
        return 'kg/m³'
    elif unit_str == 'pound/inch**3':
        return 'lb/in³'
    elif unit_str == 'foot_pound':
        return 'ft⋅lb'
    return unit_str

def format_quantity(quantity: Quantity, precision: int = 3) -> str:
    """Format a quantity with specified precision in decimal places.

    Formats both the numerical value and units according to scientific
    conventions. Uses format_unit_string() for consistent unit display.

    Args:
        quantity: The quantity to format
        precision: Number of decimal places to show (default: 3)

    Returns:
        str: Formatted string with value and units

    Examples:
        >>> force = 1.23456 * ureg.newton
        >>> format_quantity(force, 2)
        '1.23 N'

        >>> temp = 21.5 * ureg.degC
        >>> format_quantity(temp, 1)
        '21.5 °C'

        >>> pressure = 2.5 * ureg.megapascal
        >>> format_quantity(pressure)
        '2.500 MPa'
    """
    unit_str = format_unit_string(str(quantity.units))
    return f"{quantity.magnitude:.{precision}f} {unit_str}"

def format_with_units(quantity: Quantity, precision: int = None) -> str:
    """Format a quantity with units and specified precision.

    Similar to format_quantity() but allows for optional precision specification.
    When precision is None, shows full precision of the value.

    Args:
        quantity: The quantity to format
        precision: Number of decimal places (None for full precision)

    Returns:
        str: Formatted string with value and units

    Examples:
        >>> # Full precision
        >>> length = 1.23456 * ureg.meter
        >>> format_with_units(length)
        '1.23456 m'

        >>> # Specified precision
        >>> format_with_units(length, 2)
        '1.23 m'

        >>> # Complex units
        >>> density = 1000 * ureg('kg/m^3')
        >>> format_with_units(density)
        '1000 kg/m³'
    """
    unit_str = format_unit_string(str(quantity.units))
    if precision is None:
        return f"{quantity.magnitude} {unit_str}"
    return f"{quantity.magnitude:.{precision}f} {unit_str}"

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import re
from units_config import ureg, Quantity

"""Thread specification parsing and calculation utilities."""

# Thread specification patterns
IMPERIAL_PATTERN = r'^(\d+/\d+|\d+\.?\d*)[-](\d+)\s+(UNC|UNF)$'
METRIC_PATTERN = r'^M(\d+(?:\.\d+)?)x(\d+\.?\d*)$'

# Standard thread specifications
THREAD_SPECS = {
    'UNC': {
        '1/4': 20,
        '3/8': 16,
        '1/2': 13,
        '3/4': 10
    },
    'UNF': {
        '1/4': 28,
        '3/8': 24,
        '1/2': 20,
        '3/4': 16
    },
    'M': {  # Metric threads: diameter(mm): pitch(mm)
        '6': 1.0,
        '8': 1.25,
        '10': 1.5,
        '12': 1.75,
        '16': 2.0,
        '20': 2.5
    }
}

@dataclass
class ThreadInfo:
    """Thread specification information."""
    nominal_diameter: Quantity
    series: str
    is_metric: bool = False
    # Imperial specific
    threads_per_inch: Optional[int] = None
    is_fractional: bool = False
    # Metric specific
    thread_pitch: Optional[Quantity] = None

def parse_thread_specification(spec: str) -> ThreadInfo:
    """Parse a thread specification string.

    Args:
        spec: Thread specification (e.g., "1/4-20 UNC" or "M10x1.5")

    Returns:
        ThreadInfo object with parsed values

    Raises:
        ValueError: If specification format is invalid or non-standard
    """
    # Try metric pattern first
    match = re.match(METRIC_PATTERN, spec.strip())
    if match:
        diameter_str, pitch_str = match.groups()
        diameter = float(diameter_str)
        pitch = float(pitch_str)
        
        # Validate against standard metric sizes
        if diameter_str not in THREAD_SPECS['M']:
            raise ValueError(f'Non-standard metric thread diameter: M{diameter_str}')
        if abs(pitch - THREAD_SPECS['M'][diameter_str]) > 0.001:  # Allow small float differences
            raise ValueError(f'Invalid thread pitch for M{diameter_str}: {pitch_str}')
            
        return ThreadInfo(
            nominal_diameter=diameter * ureg.mm,
            series='M',
            is_metric=True,
            thread_pitch=pitch * ureg.mm)
    
    # Try imperial pattern if not metric
    match = re.match(IMPERIAL_PATTERN, spec.strip())
    if not match:
        raise ValueError(f'Invalid thread specification format: {spec}')

    diameter_str, tpi_str, series = match.groups()

    # Validate against standard thread sizes
    if diameter_str not in THREAD_SPECS[series]:
        raise ValueError(f'Non-standard thread diameter for {series}: {diameter_str}')
    if int(tpi_str) != THREAD_SPECS[series][diameter_str]:
        raise ValueError(f'Invalid thread pitch for {series} {diameter_str}: {tpi_str}')

    # Convert fraction to decimal if needed
    if '/' in diameter_str:
        num, denom = map(int, diameter_str.split('/'))
        diameter = num / denom
    else:
        diameter = float(diameter_str)

    return ThreadInfo(
        nominal_diameter=diameter * ureg.inch,
        series=series,
        is_metric=False,
        threads_per_inch=int(tpi_str),
        is_fractional=('/' in diameter_str))

def is_valid_thread_spec(spec: str) -> bool:
    """Check if a thread specification is valid.

    Must be a standard size with correct format and thread pitch.
    """
    try:
        parse_thread_specification(spec)
        return True
    except ValueError:
        return False

def validate_thread_format(spec: str) -> bool:
    """Validate thread format only, not checking standard sizes.

    Args:
        spec: Thread specification (e.g., "1/4-20 UNC" or "M10x1.5")

    Returns:
        True if format matches pattern, regardless of values
    """
    # Try metric pattern first
    match = re.match(METRIC_PATTERN, spec.strip())
    if match:
        diameter_str, pitch_str = match.groups()
        try:
            float(diameter_str)
            float(pitch_str)
            return True
        except ValueError:
            return False

    # Try imperial pattern
    match = re.match(IMPERIAL_PATTERN, spec.strip())
    if not match:
        return False

    # Basic format validation - numbers and fractions only
    diameter_str, tpi_str, series = match.groups()
    try:
        if '/' in diameter_str:
            num, denom = map(int, diameter_str.split('/'))
            if denom == 0:
                return False
        else:
            float(diameter_str)
        int(tpi_str)
        return True
    except (ValueError, ZeroDivisionError):
        return False

def validate_thread_series(spec: str) -> bool:
    """Validate thread series is supported and correct for the size."""
    try:
        info = parse_thread_specification(spec)
        return info.series in ['UNC', 'UNF', 'M']
    except ValueError:
        return False

def calculate_pitch_diameter(spec: str) -> Quantity:
    """Calculate pitch diameter for a thread specification.

    Args:
        spec: Thread specification (e.g., "1/4-20 UNC" or "M10x1.5")

    Returns:
        Pitch diameter with units

    Raises:
        ValueError: If specification is invalid
    """
    info = parse_thread_specification(spec)
    if info.is_metric:
        # Metric formula: d2 = d - 0.6495 * P
        pitch = info.thread_pitch.to('mm').magnitude
        pitch_dia = info.nominal_diameter.to('mm').magnitude - 0.6495 * pitch
        return pitch_dia * ureg.mm
    else:
        # Imperial formula
        pitch_dia = info.nominal_diameter.to('inch').magnitude - 0.6495 / info.threads_per_inch
        return pitch_dia * ureg.inch

def calculate_minor_diameter(spec: str) -> Quantity:
    """Calculate minor diameter for a thread specification.

    Args:
        spec: Thread specification (e.g., "1/4-20 UNC" or "M10x1.5")

    Returns:
        Minor diameter with units

    Raises:
        ValueError: If specification is invalid
    """
    info = parse_thread_specification(spec)
    if info.is_metric:
        # Metric formula: d1 = d - 1.226869 * P
        pitch = info.thread_pitch.to('mm').magnitude
        minor_dia = info.nominal_diameter.to('mm').magnitude - 1.226869 * pitch
        return minor_dia * ureg.mm
    else:
        # Imperial formula
        minor_dia = info.nominal_diameter.to('inch').magnitude - 1.299 / info.threads_per_inch
        return minor_dia * ureg.inch

def calculate_thread_pitch(spec: str) -> Quantity:
    """Calculate thread pitch for a specification.

    Args:
        spec: Thread specification (e.g., "1/4-20 UNC" or "M10x1.5")

    Returns:
        Thread pitch with units

    Raises:
        ValueError: If specification is invalid
    """
    info = parse_thread_specification(spec)
    if info.is_metric:
        return info.thread_pitch
    else:
        return 1.0 / info.threads_per_inch * ureg.inch

def extract_thread_dimensions(spec: str) -> Dict[str, Quantity]:
    """Extract all thread dimensions from a specification.

    Args:
        spec: Thread specification (e.g., "1/4-20 UNC" or "M10x1.5")

    Returns:
        Dictionary containing major_diameter, thread_pitch, pitch_diameter, and minor_diameter

    Raises:
        ValueError: If specification is invalid
    """
    info = parse_thread_specification(spec)
    return {
        'major_diameter': info.nominal_diameter,
        'thread_pitch': calculate_thread_pitch(spec),
        'pitch_diameter': calculate_pitch_diameter(spec),
        'minor_diameter': calculate_minor_diameter(spec)
    }

def are_threads_compatible(spec1: str, spec2: str) -> bool:
    """Check if two thread specifications are compatible.

    Args:
        spec1: First thread specification
        spec2: Second thread specification

    Returns:
        True if threads are compatible
    """
    try:
        info1 = parse_thread_specification(spec1)
        info2 = parse_thread_specification(spec2)
        
        # Threads must be same type (metric or imperial)
        if info1.is_metric != info2.is_metric:
            return False
            
        if info1.is_metric:
            # For metric threads, compare diameter and pitch
            return (abs(info1.nominal_diameter.to('mm').magnitude -
                       info2.nominal_diameter.to('mm').magnitude) < 0.001 and
                    abs(info1.thread_pitch.to('mm').magnitude -
                        info2.thread_pitch.to('mm').magnitude) < 0.001)
        else:
            # For imperial threads
            return (abs(info1.nominal_diameter.to('inch').magnitude -
                       info2.nominal_diameter.to('inch').magnitude) < 0.0001 and
                    info1.threads_per_inch == info2.threads_per_inch and
                    info1.series == info2.series)
    except ValueError:
        return False

"""Utilities for thread specification parsing, validation, and calculations."""

import re
from typing import Dict, NamedTuple, Optional
from fractions import Fraction
from units_config import ureg, Quantity

class ThreadInfo(NamedTuple):
    """Container for parsed thread information."""
    nominal_diameter: Quantity
    threads_per_inch: Optional[int]
    thread_pitch: Optional[Quantity]
    series: str
    is_metric: bool
    is_fractional: bool

# Thread series data
UNC_SPECS = {
    "1/4": {"tpi": 20, "pitch_factor": 0.8750},
    "5/16": {"tpi": 18, "pitch_factor": 0.8750},
    "3/8": {"tpi": 16, "pitch_factor": 0.8750},
    "7/16": {"tpi": 14, "pitch_factor": 0.8750},
    "1/2": {"tpi": 13, "pitch_factor": 0.8750},
    "9/16": {"tpi": 12, "pitch_factor": 0.8750},
    "5/8": {"tpi": 11, "pitch_factor": 0.8750},
    "3/4": {"tpi": 10, "pitch_factor": 0.8750},
}

UNF_SPECS = {
    "1/4": {"tpi": 28, "pitch_factor": 0.9188},
    "5/16": {"tpi": 24, "pitch_factor": 0.9188},
    "3/8": {"tpi": 24, "pitch_factor": 0.9188},
    "7/16": {"tpi": 20, "pitch_factor": 0.9188},
    "1/2": {"tpi": 20, "pitch_factor": 0.9188},
    "9/16": {"tpi": 18, "pitch_factor": 0.9188},
    "5/8": {"tpi": 18, "pitch_factor": 0.9188},
    "3/4": {"tpi": 16, "pitch_factor": 0.9188},
}

METRIC_SPECS = {
    "M6": 1.0,
    "M8": 1.25,
    "M10": 1.5,
    "M12": 1.75,
    "M16": 2.0,
    "M20": 2.5,
}

def parse_thread_specification(spec: str) -> ThreadInfo:
    """Parse a thread specification string."""
    if not spec or not isinstance(spec, str):
        raise ValueError("Thread specification must be a non-empty string")

    # Check for metric specification
    metric_match = re.match(r"^M(\d+)x([\d.]+)$", spec)
    if metric_match:
        try:
            diameter = int(metric_match.group(1))
            pitch = float(metric_match.group(2))
            if diameter <= 0 or pitch <= 0:
                raise ValueError("Diameter and pitch must be positive")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid metric thread specification: {spec}")
            
        # Validate against standard metric sizes
        if f"M{diameter}" not in METRIC_SPECS or METRIC_SPECS[f"M{diameter}"] != pitch:
            raise ValueError(f"Non-standard metric thread specification: {spec}")
            
        return ThreadInfo(
            nominal_diameter=diameter * ureg.mm,
            threads_per_inch=None,
            thread_pitch=pitch * ureg.mm,
            series="M",
            is_metric=True,
            is_fractional=False
        )

    # Parse imperial specification - must match exactly including whitespace
    imperial_match = re.match(r"^(\d+(?:/\d+)?)-(\d+)\s+(UNC|UNF)$", spec)
    if not imperial_match:
        raise ValueError(f"Invalid thread specification format: {spec}")

    size, tpi, series = imperial_match.groups()
    
    try:
        if "/" in size:
            num, denom = size.split("/")
            if not num.isdigit() or not denom.isdigit():
                raise ValueError("Invalid fraction format")
            num, denom = int(num), int(denom)
            if denom == 0:
                raise ZeroDivisionError("Denominator cannot be zero")
            if num <= 0 or denom <= 0:
                raise ValueError("Numerator and denominator must be positive")
            size_val = num / denom
            is_fractional = True
        else:
            size_val = float(size)
            if size_val <= 0:
                raise ValueError("Size must be positive")
            is_fractional = False
            
        tpi_val = int(tpi)
        if tpi_val <= 0:
            raise ValueError("Threads per inch must be positive")
    except (ValueError, ZeroDivisionError) as e:
        raise ValueError(f"Invalid size or thread count in specification: {spec} - {str(e)}")
    
    # Validate against standard series
    specs = UNC_SPECS if series == "UNC" else UNF_SPECS
    if size not in specs or specs[size]["tpi"] != tpi_val:
        raise ValueError(f"Non-standard {series} thread specification: {spec}")
    
    return ThreadInfo(
        nominal_diameter=size_val * ureg.inch,
        threads_per_inch=tpi_val,
        thread_pitch=None,
        series=series,
        is_metric=False,
        is_fractional=is_fractional
    )

def validate_thread_format(spec: str) -> bool:
    """Validate a thread specification string format."""
    try:
        parse_thread_specification(spec)
        return True
    except ValueError:
        return False

def extract_thread_dimensions(spec: str) -> Dict[str, Quantity]:
    """Extract all relevant dimensions from a thread specification."""
    thread_info = parse_thread_specification(spec)
    
    if thread_info.is_metric:
        pitch = thread_info.thread_pitch
        major_diameter = thread_info.nominal_diameter
        pitch_diameter = major_diameter - (0.6495 * pitch)
        minor_diameter = major_diameter - (1.2269 * pitch)
    else:
        tpi = thread_info.threads_per_inch
        pitch = (1.0 / tpi) * ureg.inch
        major_diameter = thread_info.nominal_diameter
        pitch_diameter = major_diameter - (0.6495 / tpi * ureg.inch)
        minor_diameter = major_diameter - (1.2269 / tpi * ureg.inch)
    
    return {
        "major_diameter": major_diameter,
        "pitch_diameter": pitch_diameter,
        "minor_diameter": minor_diameter,
        "thread_pitch": pitch
    }

def calculate_pitch_diameter(spec: str) -> Quantity:
    """Calculate the pitch diameter for a thread specification."""
    return extract_thread_dimensions(spec)["pitch_diameter"]

def calculate_minor_diameter(spec: str) -> Quantity:
    """Calculate the minor diameter for a thread specification."""
    return extract_thread_dimensions(spec)["minor_diameter"]

def calculate_thread_pitch(spec: str) -> Quantity:
    """Calculate the thread pitch for a specification."""
    return extract_thread_dimensions(spec)["thread_pitch"]

def is_valid_thread_spec(spec: str) -> bool:
    """Check if a thread specification is valid and standard."""
    return validate_thread_format(spec)

def validate_thread_series(spec: str) -> bool:
    """Validate that a thread specification matches a standard series."""
    try:
        parse_thread_specification(spec)
        return True
    except ValueError:
        return False

def are_threads_compatible(spec1: str, spec2: str) -> bool:
    """Check if two thread specifications are compatible."""
    try:
        info1 = parse_thread_specification(spec1)
        info2 = parse_thread_specification(spec2)
        
        # Must be same unit system
        if info1.is_metric != info2.is_metric:
            return False
            
        # Must match in size and pitch
        if info1.is_metric:
            return (info1.nominal_diameter == info2.nominal_diameter and 
                   info1.thread_pitch == info2.thread_pitch)
        else:
            return (info1.nominal_diameter == info2.nominal_diameter and 
                   info1.threads_per_inch == info2.threads_per_inch)
    except ValueError:
        return False

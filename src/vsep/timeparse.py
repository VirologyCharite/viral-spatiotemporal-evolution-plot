"""Time string parsing utilities for viral spatiotemporal evolution plots."""

import math
import re
from pytimeparse.timeparse import timeparse


def parse_time_to_log10_seconds(time_str: str) -> float | None:
    """
    Parse a human-readable time string and convert to log10(seconds).

    Examples:
        "1 ms" -> -3.0
        "1 minute" -> ~1.78
        "1 year" -> ~7.5
        "4 billion years" -> ~17.1

    Args:
        time_str: Human-readable time string

    Returns:
        log10(seconds) if parsing succeeds, None otherwise

    Supported formats:
        - Sub-second: "1 nanosecond", "5 microseconds", "10 milliseconds", "500 ms"
        - Standard: "1 second", "5 minutes", "2 hours", "7 days", "3 weeks"
        - Long-term: "2 years", "1 decade", "5 centuries", "3 millennia"
        - Geological: "10 Myr", "4.5 Gyr", "100 million years", "2 billion years"
    """
    time_str_lower = time_str.lower().strip()

    # Extract number from the string
    number_match = re.search(r'(\d+(?:\.\d+)?)', time_str_lower)
    if not number_match:
        return None

    number = float(number_match.group(1))

    # Handle geological time units
    if any(term in time_str_lower for term in ['gyr', 'billion year', 'billion yr']):
        seconds = number * 365.25 * 24 * 3600 * 1e9  # billion years to seconds
        return math.log10(seconds)

    if any(term in time_str_lower for term in ['myr', 'million year', 'million yr']):
        seconds = number * 365.25 * 24 * 3600 * 1e6  # million years to seconds
        return math.log10(seconds)

    # Handle years (pytimeparse doesn't support years)
    if any(term in time_str_lower for term in ['year', 'yr', ' y']):
        # Check it's not "Myr" or "Gyr" which we handled above
        if not any(term in time_str_lower for term in ['myr', 'gyr']):
            seconds = number * 365.25 * 24 * 3600  # years to seconds
            return math.log10(seconds)

    # Handle centuries, decades, millennia
    if any(term in time_str_lower for term in ['centur', 'century']):
        seconds = number * 365.25 * 24 * 3600 * 100  # centuries to seconds
        return math.log10(seconds)

    if any(term in time_str_lower for term in ['decade']):
        seconds = number * 365.25 * 24 * 3600 * 10  # decades to seconds
        return math.log10(seconds)

    if any(term in time_str_lower for term in ['millennium', 'millennia']):
        seconds = number * 365.25 * 24 * 3600 * 1000  # millennia to seconds
        return math.log10(seconds)

    # Handle milliseconds (pytimeparse doesn't support ms)
    if any(term in time_str_lower for term in ['millisecond', 'msec', 'ms']):
        seconds = number / 1000.0  # milliseconds to seconds
        return math.log10(seconds)

    # Handle microseconds
    if any(term in time_str_lower for term in ['microsecond', 'usec', 'μs', 'us']):
        seconds = number / 1_000_000.0  # microseconds to seconds
        return math.log10(seconds)

    # Handle nanoseconds
    if any(term in time_str_lower for term in ['nanosecond', 'nsec', 'ns']):
        seconds = number / 1_000_000_000.0  # nanoseconds to seconds
        return math.log10(seconds)

    # Use pytimeparse for standard time units (seconds, minutes, hours, days, weeks)
    seconds = timeparse(time_str)
    if seconds is not None:
        return math.log10(seconds)

    return None


def convert_x_value(x_value) -> float | None:
    """
    Convert x value to log10(seconds). Handles both numeric values and time strings.

    Args:
        x_value: Either a numeric value (log10 seconds) or a time string

    Returns:
        log10(seconds) if conversion succeeds, None if string cannot be parsed
    """
    if isinstance(x_value, str):
        return parse_time_to_log10_seconds(x_value)
    else:
        # Assume it's already a numeric value (log10 seconds)
        return float(x_value)
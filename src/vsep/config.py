"""Configuration loading and processing for viral spatiotemporal evolution plots."""

import tomllib
from pathlib import Path
from typing import Any

from .timeparse import convert_x_value


def load_config(path: Path) -> dict[str, Any]:
    """Load configuration from TOML file."""
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def process_points(config: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """
    Process points from config, converting x values from time strings if needed.

    Args:
        config: Raw configuration dictionary from TOML

    Returns:
        Dictionary mapping category names to lists of processed points

    Side effects:
        Prints warnings for unparseable time strings
    """
    by_cat: dict[str, list[dict[str, Any]]] = {}

    for pt in config.get("points", []):
        # Convert x value if it's a time string
        x_val = convert_x_value(pt["x"])
        if x_val is None:
            print(f"Warning: Could not parse x value '{pt['x']}' for point '{pt.get('label', 'unknown')}', skipping point")
            continue

        # Create a new point dict with converted x value
        converted_pt = pt.copy()
        converted_pt["x"] = x_val
        by_cat.setdefault(pt.get("category", "unknown"), []).append(converted_pt)

    return by_cat
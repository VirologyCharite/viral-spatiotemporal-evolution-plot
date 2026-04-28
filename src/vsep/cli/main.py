#!/usr/bin/env python3
"""
Viral evolution timescale scatter plot CLI.

Reads a TOML configuration file and produces an interactive Plotly
scatter plot with hover descriptions for each data point.

Usage
-----
    make-plot                                   # reads data.toml, opens browser
    make-plot my_config.toml                    # custom config
    make-plot -o plot.html                      # save interactive HTML
    make-plot -o plot.png                       # save static image (requires kaleido)

Coordinate system (defined in the TOML)
-----------------------------------------
  x  =  log10(seconds) or human-readable time strings like "1 year", "5 ms"
  y  =  log10(metres)    e.g.  -8 = 10 nm   |   0  = 1 m      |   7.7 = planetary
"""

import argparse
import sys
from pathlib import Path

from vsep import build_figure, load_config


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Viral evolution timescale scatter plot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "config",
        nargs="?",
        default="data.toml",
        help="Path to TOML config file (default: data.toml)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="FILE",
        help=(
            "Output file. Use .html for interactive, "
            ".png / .pdf / .svg for static (requires kaleido: "
            "run 'uv add kaleido')."
        ),
    )
    args = parser.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        sys.exit(f"Config file not found: {cfg_path}")

    fig = build_figure(load_config(cfg_path))

    if args.output:
        out = Path(args.output)
        if out.suffix.lower() == ".html":
            fig.write_html(str(out), include_plotlyjs="cdn")
            print(f"Saved interactive HTML → {out}")
        else:
            fig.write_image(str(out))
            print(f"Saved image → {out}")
    else:
        fig.show()


if __name__ == "__main__":
    main()
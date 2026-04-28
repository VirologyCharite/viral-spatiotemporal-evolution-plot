#!/usr/bin/env python3
"""
Viral evolution timescale scatter plot.

Reads a TOML configuration file and produces an interactive Plotly
scatter plot with hover descriptions for each data point.

Usage
-----
    python virus_timescale.py                          # reads virus_timescale.toml, opens browser
    python virus_timescale.py my_config.toml           # custom config
    python virus_timescale.py -o plot.html             # save interactive HTML
    python virus_timescale.py -o plot.png              # save static image (requires kaleido)

Coordinate system (defined in the TOML)
-----------------------------------------
  x  =  log10(seconds)   e.g.  -3 = 1 ms   |  7.5 = 1 year   |  17.1 = 4 Gyr
  y  =  log10(metres)    e.g.  -8 = 10 nm   |   0  = 1 m      |   7.7 = planetary
"""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path
import tomllib
import plotly.graph_objects as go


# ── helpers ───────────────────────────────────────────────────────────────────


def wrap_html(text: str, width: int = 55) -> str:
    """Word-wrap plain text and join lines with HTML <br> tags."""
    return "<br>".join(textwrap.wrap(text, width=width))


def load_config(path: Path) -> dict:
    with open(path, "rb") as fh:
        return tomllib.load(fh)


# ── figure ────────────────────────────────────────────────────────────────────


def build_figure(cfg: dict) -> go.Figure:
    plot_cfg = cfg.get("plot", {})
    axes_cfg = cfg.get("axes", {})
    fonts_cfg = cfg.get("fonts", {})

    # Build a dict keyed by category id, preserving TOML order
    categories = {c["id"]: c for c in cfg.get("categories", [])}

    font_family = fonts_cfg.get("family", "Georgia, serif")
    title_size = fonts_cfg.get("title_size", 18)
    axis_label_size = fonts_cfg.get("axis_label_size", 14)
    tick_size = fonts_cfg.get("tick_size", 11)
    legend_size = fonts_cfg.get("legend_size", 12)
    hover_size = fonts_cfg.get("hover_size", 12)
    hover_width = fonts_cfg.get("hover_wrap_width", 55)

    marker_size = plot_cfg.get("marker_size", 12)
    marker_opacity = plot_cfg.get("marker_opacity", 0.85)

    # Group points by category
    by_cat: dict[str, list] = {}
    for pt in cfg.get("points", []):
        by_cat.setdefault(pt.get("category", "unknown"), []).append(pt)

    fig = go.Figure()

    for cat_id, cat_info in categories.items():
        pts = by_cat.get(cat_id, [])
        if not pts:
            continue

        hover_html = [
            f"<b>{p['label']}</b><br><br>"
            + wrap_html(p.get("description", ""), width=hover_width)
            for p in pts
        ]

        fig.add_trace(
            go.Scatter(
                x=[p["x"] for p in pts],
                y=[p["y"] for p in pts],
                mode="markers",
                name=cat_info["label"],
                marker=dict(
                    color=cat_info["color"],
                    size=marker_size,
                    opacity=marker_opacity,
                    line=dict(color="white", width=1.5),
                ),
                hovertemplate="%{customdata}<extra></extra>",
                customdata=hover_html,
            )
        )

    x_ticks = axes_cfg.get("x_ticks", [])
    y_ticks = axes_cfg.get("y_ticks", [])

    shared_axis = dict(
        showgrid=axes_cfg.get("show_grid", True),
        gridcolor=axes_cfg.get("grid_color", "#E8EEF4"),
        gridwidth=1,
        zeroline=False,
        showline=True,
        mirror=True,
        linecolor="#CBD5E1",
        linewidth=1,
        tickfont=dict(family=font_family, size=tick_size),
    )

    fig.update_layout(
        title=dict(
            text=plot_cfg.get("title", ""),
            font=dict(family=font_family, size=title_size),
            x=0.5,
            xanchor="center",
        ),
        width=plot_cfg.get("width", 960),
        height=plot_cfg.get("height", 620),
        paper_bgcolor=plot_cfg.get("background_color", "white"),
        plot_bgcolor=plot_cfg.get("plot_background_color", "white"),
        font=dict(family=font_family, size=tick_size),
        hoverlabel=dict(
            bgcolor=plot_cfg.get("hover_background", "rgba(27,42,74,0.95)"),
            font=dict(
                size=hover_size,
                family=font_family,
                color=plot_cfg.get("hover_text_color", "white"),
            ),
            bordercolor="rgba(0,0,0,0)",
        ),
        legend=dict(
            font=dict(family=font_family, size=legend_size),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#CBD5E1",
            borderwidth=1,
        ),
        xaxis=dict(
            **shared_axis,
            title=dict(
                text=axes_cfg.get("x_label", "X"),
                font=dict(family=font_family, size=axis_label_size),
                standoff=15,
            ),
            range=[axes_cfg.get("x_min", -4), axes_cfg.get("x_max", 18)],
            tickvals=[t["value"] for t in x_ticks],
            ticktext=[t["label"] for t in x_ticks],
            tickangle=axes_cfg.get("x_tick_angle", -40),
        ),
        yaxis=dict(
            **shared_axis,
            title=dict(
                text=axes_cfg.get("y_label", "Y"),
                font=dict(family=font_family, size=axis_label_size),
                standoff=10,
            ),
            range=[axes_cfg.get("y_min", -10), axes_cfg.get("y_max", 9)],
            tickvals=[t["value"] for t in y_ticks],
            ticktext=[t["label"] for t in y_ticks],
            tickangle=axes_cfg.get("y_tick_angle", 0),
        ),
        margin=dict(
            l=plot_cfg.get("margin_left", 80),
            r=plot_cfg.get("margin_right", 40),
            t=plot_cfg.get("margin_top", 70),
            b=plot_cfg.get("margin_bottom", 90),
        ),
    )

    return fig


# ── entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Viral evolution timescale scatter plot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--config",
        default="data.toml",
        help="Path to TOML config file (default: virus_timescale.toml)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="FILE",
        help=(
            "Output file. Use .html for interactive, "
            ".png / .pdf / .svg for static (requires kaleido: "
            "run 'pip install kaleido' or 'uv add kaleido')."
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

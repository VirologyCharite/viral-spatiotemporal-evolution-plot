"""Plot building functions for viral spatiotemporal evolution plots."""

import textwrap
from typing import Any

import plotly.graph_objects as go

from .config import process_points


def wrap_html(text: str, width: int = 55) -> str:
    """Word-wrap plain text and join lines with HTML <br> tags."""
    return "<br>".join(textwrap.wrap(text, width=width))


def build_figure(cfg: dict[str, Any]) -> go.Figure:
    """
    Build a Plotly figure from configuration data.

    Args:
        cfg: Configuration dictionary loaded from TOML

    Returns:
        Plotly Figure object ready for display or export
    """
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

    # Process points (including time string conversion)
    by_cat = process_points(cfg)

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
            title=dict(text=plot_cfg.get("legend_title", "")),
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
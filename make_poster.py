"""
A0-landscape scientific poster for the Solar Salt Heat Export project.

Outputs:
  poster.png   (200 dpi, ~ 9362 x 6622 px)
  poster.pdf   (vector text + raster figure embeds)

Run:  python make_poster.py
"""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle


def wrap(text: str, width: int) -> str:
    """Wrap each paragraph in ``text`` to ``width`` characters, preserving
    leading whitespace and blank-line paragraph separators. Bulleted lines
    that begin with a bullet glyph are wrapped with hanging indent so the
    continuation lines line up under the first character after the bullet."""
    paragraphs = text.split("\n\n")
    out_paragraphs = []
    for paragraph in paragraphs:
        out_lines = []
        for line in paragraph.split("\n"):
            stripped = line.lstrip()
            indent = line[: len(line) - len(stripped)]
            if not stripped:
                out_lines.append("")
                continue
            # Hanging indent for bullets ("•  text...")
            if stripped.startswith("•  "):
                first_indent = indent
                cont_indent = indent + "    "
            elif stripped[:1].isdigit() and stripped[1:3] in (".  ", ") "):
                first_indent = indent
                cont_indent = indent + "    "
            else:
                first_indent = indent
                cont_indent = indent
            wrapped = textwrap.fill(
                stripped,
                width=max(width - len(indent), 20),
                initial_indent="",
                subsequent_indent="",
                break_long_words=False,
                break_on_hyphens=False,
            )
            for i, sub in enumerate(wrapped.split("\n")):
                out_lines.append((first_indent if i == 0 else cont_indent) + sub)
        out_paragraphs.append("\n".join(out_lines))
    return "\n\n".join(out_paragraphs)

ROOT = Path(__file__).parent
FIG = ROOT / "figures"

# A0 landscape: 1189 mm x 841 mm  ->  46.81 x 33.11 inches
WIDTH_IN, HEIGHT_IN = 46.81, 33.11
DPI = 200

# Palette (matches the existing figures' aesthetic).
C_DARK = "#0E2A38"          # title bar
C_ACCENT = "#1F7A8C"        # section accents
C_ACCENT_2 = "#E07A1F"      # highlight callouts
C_BG = "#FAFAF7"            # poster background
C_PANEL = "#FFFFFF"         # panel background
C_PANEL_EDGE = "#D7D2C5"
C_TEXT = "#1A1A1A"
C_MUTED = "#5C5C5C"

# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------


def add_panel(fig, x, y, w, h, *, title=None, pad=0.006, title_color=C_ACCENT):
    """Add a white panel with a colored section header. Returns the inner
    content rect (x, y, w, h) in figure coordinates that callers should
    use to place text/images inside the panel."""
    # Panel background
    fig.patches.append(
        FancyBboxPatch(
            (x, y), w, h,
            transform=fig.transFigure,
            boxstyle="round,pad=0.0,rounding_size=0.004",
            linewidth=1.2,
            edgecolor=C_PANEL_EDGE,
            facecolor=C_PANEL,
            zorder=1,
        )
    )
    inner_y = y + pad
    inner_h = h - 2 * pad
    if title is not None:
        # Header bar
        header_h = 0.022
        fig.patches.append(
            Rectangle(
                (x, y + h - header_h), w, header_h,
                transform=fig.transFigure,
                linewidth=0,
                facecolor=title_color,
                zorder=2,
            )
        )
        fig.text(
            x + 0.008, y + h - header_h / 2, title.upper(),
            ha="left", va="center",
            fontsize=26, fontweight="bold", color="white",
            zorder=3,
        )
        inner_h = h - header_h - pad
    return x + pad, inner_y, w - 2 * pad, inner_h


def add_image(fig, path: Path, x, y, w, h, *, caption=None):
    """Place an image inside the rect (x,y,w,h), preserving aspect ratio,
    with an optional caption beneath. The image is letterboxed within the
    available area."""
    img = mpimg.imread(path)
    img_h, img_w = img.shape[:2]
    img_aspect = img_w / img_h

    fig_w_in = WIDTH_IN
    fig_h_in = HEIGHT_IN
    area_w_in = w * fig_w_in
    area_h_in = h * fig_h_in
    cap_reserve_in = 0.35 if caption else 0.0
    avail_h_in = area_h_in - cap_reserve_in

    # Fit image into (area_w_in, avail_h_in) preserving aspect.
    if area_w_in / avail_h_in > img_aspect:
        # height-limited
        draw_h_in = avail_h_in
        draw_w_in = draw_h_in * img_aspect
    else:
        draw_w_in = area_w_in
        draw_h_in = draw_w_in / img_aspect

    draw_w = draw_w_in / fig_w_in
    draw_h = draw_h_in / fig_h_in
    x_off = x + (w - draw_w) / 2
    y_off = y + cap_reserve_in / fig_h_in + (avail_h_in / fig_h_in - draw_h) / 2

    ax = fig.add_axes([x_off, y_off, draw_w, draw_h])
    ax.imshow(img)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_zorder(3)

    if caption:
        fig.text(
            x + w / 2, y + 0.004,
            caption,
            ha="center", va="bottom",
            fontsize=15, style="italic", color=C_MUTED,
            zorder=4,
        )


def add_text_block(fig, text, x, y, w, h, *, fontsize=18, leading=1.25,
                   color=C_TEXT, weight="normal", va="top", ha="left"):
    fig.text(
        x if ha == "left" else x + w / 2 if ha == "center" else x + w,
        y + h if va == "top" else y if va == "bottom" else y + h / 2,
        text,
        ha=ha, va=va,
        fontsize=fontsize, color=color, fontweight=weight,
        wrap=True, linespacing=leading,
        zorder=3,
    )


# ---------------------------------------------------------------------------
# Build the poster
# ---------------------------------------------------------------------------


def build():
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=C_BG)

    # ------------- TITLE BAR -------------
    title_h = 0.085
    fig.patches.append(
        Rectangle((0, 1 - title_h), 1, title_h,
                  transform=fig.transFigure,
                  linewidth=0, facecolor=C_DARK, zorder=1)
    )
    # Accent stripe
    fig.patches.append(
        Rectangle((0, 1 - title_h - 0.005), 1, 0.005,
                  transform=fig.transFigure,
                  linewidth=0, facecolor=C_ACCENT_2, zorder=1)
    )

    fig.text(
        0.025, 1 - title_h * 0.42,
        "Solar Thermochemical Heat Export via Closed-Loop Salt Hydration",
        ha="left", va="center",
        fontsize=64, fontweight="bold", color="white", zorder=3,
    )
    fig.text(
        0.025, 1 - title_h * 0.78,
        "Charging desert salt with sunlight, shipping it on autonomous "
        "wind-primary freighters, releasing heat in dirty-grid winter cities.",
        ha="left", va="center",
        fontsize=28, color="#D8E6EC", style="italic", zorder=3,
    )
    fig.text(
        0.975, 1 - title_h * 0.42,
        "Eric Neuman",
        ha="right", va="center",
        fontsize=30, fontweight="bold", color="white", zorder=3,
    )
    fig.text(
        0.975, 1 - title_h * 0.78,
        "Dotted Labs   ·   Concept paper v0.3   ·   2026",
        ha="right", va="center",
        fontsize=22, color="#D8E6EC", zorder=3,
    )

    # ------------- FOOTER -------------
    footer_h = 0.028
    fig.patches.append(
        Rectangle((0, 0), 1, footer_h,
                  transform=fig.transFigure,
                  linewidth=0, facecolor=C_DARK, zorder=1)
    )
    fig.text(
        0.025, footer_h / 2,
        "github.com/neuman/stirlingspike",
        ha="left", va="center",
        fontsize=20, color="white", zorder=3,
    )
    fig.text(
        0.5, footer_h / 2,
        "Pre-feasibility — modeling complete on revised transport architecture; "
        "salt-cycle bench validation pending.",
        ha="center", va="center",
        fontsize=18, color="#D8E6EC", style="italic", zorder=3,
    )
    fig.text(
        0.975, footer_h / 2,
        "Contact: eric@trydotted.com",
        ha="right", va="center",
        fontsize=20, color="white", zorder=3,
    )

    # ------------- BODY GRID -------------
    body_top = 1 - title_h - 0.012
    body_bot = footer_h + 0.012
    body_h = body_top - body_bot

    margin = 0.018
    gutter = 0.012
    # 3 columns
    col_w = (1 - 2 * margin - 2 * gutter) / 3
    col1_x = margin
    col2_x = margin + col_w + gutter
    col3_x = margin + 2 * (col_w + gutter)

    # ===========================================================
    # COLUMN 1 — Concept / TL;DR / System Diagram / Headline numbers
    # ===========================================================

    # Panel 1.1 — TL;DR
    p_h = 0.165
    p_y = body_top - p_h
    ix, iy, iw, ih = add_panel(fig, col1_x, p_y, col_w, p_h, title="TL;DR")
    add_text_block(
        fig,
        wrap(
            "•  Charge inorganic salt hydrates with desert sun. Ship the dry salt "
            "to cold cities on uncrewed wing-sail freighters. Release stored heat "
            "by hydrating the salt at a district-heating plant. Return the wet "
            "salt for recharge.\n\n"
            "•  Two viability tiers in v0.3:\n"
            "      (a) short-haul + passive pond + CaCl₂·6H₂O ↔ CaCl₂·2H₂O\n"
            "      (b) long-haul + linear-Fresnel CSP + CaCl₂·6H₂O ↔ CaCl₂\n\n"
            "•  Replacing cargo-as-fuel propulsion with autonomous wind-primary "
            "shipping is the v0.3 architectural pivot. It cuts long-haul LCOH "
            "nearly in half and unlocks the highest-CO₂-leverage routes.",
            width=70,
        ),
        ix, iy + 0.005, iw, ih - 0.005,
        fontsize=18, leading=1.32,
    )

    # Panel 1.2 — System diagram
    p_h = 0.20
    p_y -= (p_h + gutter)
    ix, iy, iw, ih = add_panel(fig, col1_x, p_y, col_w, p_h,
                               title="Reference system — Atacama → Southern Cone")
    add_image(fig, FIG / "fig07_system_summary.png", ix, iy, iw, ih,
              caption="Stage-by-stage block diagram of the closed-loop system.")

    # Panel 1.3 — Headline numbers (2 tiers)
    p_h = 0.275
    p_y -= (p_h + gutter)
    ix, iy, iw, ih = add_panel(fig, col1_x, p_y, col_w, p_h,
                               title="Headline numbers (end-to-end simulation)")
    headline = (
        "                                Short-haul best        Long-haul best\n"
        " ──────────────────────────────────────────────\n"
        " Working fluid                CaCl₂ passive            CaCl₂ deep CSP\n"
        " Route                        Atacama → S. Cone     Pilbara → N. China\n"
        " Distance                     1,800 km                  8,000 km\n"
        " LCOH                            $53.8 / MWh-th       $100.6 / MWh-th\n"
        " Round-trip thermal η         80%                       72%\n"
        " CO₂ avoided / 1 GW-th yr   832 kt                  1,533 kt\n"
        " Solar field area               8.6 km² (pond)        6.2 km² (CSP)\n"
        " Freshwater coproduction   5.4 Mm³/yr             2.9 Mm³/yr\n"
        " Autonomous fleet size      18 vessels               31 vessels\n"
        " Round-trip cycle days       16 d                       56 d\n"
    )
    add_text_block(fig, headline, ix, iy + 0.005, iw, ih - 0.005,
                   fontsize=17, leading=1.45, color=C_TEXT)

    # Panel 1.4 — Innovation callout
    p_h = body_h - (body_top - p_y) - gutter
    p_y -= (p_h + gutter)
    ix, iy, iw, ih = add_panel(fig, col1_x, p_y, col_w, p_h,
                               title="What is new", title_color=C_ACCENT_2)
    add_text_block(
        fig,
        wrap(
            "Closed-loop maritime thermochemical heat export has not, to our "
            "knowledge, been previously modeled end-to-end. Adjacent literature "
            "treats either (i) stationary salt storage at the plant, or "
            "(ii) hydrogen / ammonia carriers.\n\n"
            "Salt-hydrate carriers are uniquely suited to low-temperature "
            "district heat: the discharge temperature is the use temperature, "
            "with no exergy-destroying conversion to and from electricity or "
            "chemical fuel.",
            width=70,
        ),
        ix, iy + 0.005, iw, ih - 0.005,
        fontsize=18, leading=1.35,
    )

    # ===========================================================
    # COLUMN 2 — Methods / Working fluids / Chem-route grid / Energy waterfall
    # ===========================================================

    # Panel 2.1 — Methods
    p_h = 0.165
    p_y2 = body_top - p_h
    ix, iy, iw, ih = add_panel(fig, col2_x, p_y2, col_w, p_h, title="Methods")
    add_text_block(
        fig,
        wrap(
            "Two-track model:\n\n"
            "•  Modelica package (SolarSaltExport/) — declarative, acausal, the "
            "canonical specification of the energy and mass balances at each stage.\n\n"
            "•  Python mirror (sim/) — 1:1 correspondence to the Modelica "
            "components, used as the numerical runner for parameter sweeps and "
            "figure generation. Stages: solar charging field → outbound voyage "
            "→ hydration reactor → district-heat plant → return voyage.\n\n"
            "•  Six candidate chemistries × six routes evaluated on a common "
            "grid. Single largest residual uncertainty: multi-cycle salt "
            "degradation.",
            width=70,
        ),
        ix, iy + 0.005, iw, ih - 0.005,
        fontsize=18, leading=1.32,
    )

    # Panel 2.2 — Energy density figure
    p_h = 0.205
    p_y2 -= (p_h + gutter)
    ix, iy, iw, ih = add_panel(fig, col2_x, p_y2, col_w, p_h,
                               title="Candidate working fluids")
    add_image(fig, FIG / "fig01_energy_density.png", ix, iy, iw, ih,
              caption="Fig. 1 — Theoretical energy density of candidate salt-hydrate pairs.")

    # Panel 2.3 — Chem×route grid
    p_h = 0.22
    p_y2 -= (p_h + gutter)
    ix, iy, iw, ih = add_panel(fig, col2_x, p_y2, col_w, p_h,
                               title="Chemistry × route grid")
    add_image(fig, FIG / "fig02_chem_route_grid.png", ix, iy, iw, ih,
              caption="Fig. 2 — LCOH (left) and round-trip thermal efficiency (right) "
                      "across the chemistry × route matrix.")

    # Panel 2.4 — Energy waterfall
    p_h = body_h - (body_top - p_y2) - gutter
    p_y2 -= (p_h + gutter)
    ix, iy, iw, ih = add_panel(fig, col2_x, p_y2, col_w, p_h,
                               title="100 units DNI → delivered heat")
    add_image(fig, FIG / "fig10_energy_waterfall.png", ix, iy, iw, ih,
              caption="Fig. 10 — Energy waterfall from solar resource to delivered heat.")

    # ===========================================================
    # COLUMN 3 — Results: cruise speed / climate / deployment / conclusions / refs
    # ===========================================================

    # Panel 3.1 — Cruise speed sensitivity
    p_h = 0.205
    p_y3 = body_top - p_h
    ix, iy, iw, ih = add_panel(fig, col3_x, p_y3, col_w, p_h,
                               title="LCOH vs autonomous-vessel cruise speed")
    add_image(fig, FIG / "fig04_cruise_speed.png", ix, iy, iw, ih,
              caption="Fig. 4 — Sensitivity of LCOH to cruise speed across the route set "
                      "(≈ $5 / MWh per knot).")

    # Panel 3.2 — Climate impact
    p_h = 0.205
    p_y3 -= (p_h + gutter)
    ix, iy, iw, ih = add_panel(fig, col3_x, p_y3, col_w, p_h,
                               title="Climate leverage")
    add_image(fig, FIG / "fig08_climate_impact.png", ix, iy, iw, ih,
              caption="Fig. 8 — Cumulative CO₂ avoided vs deployment scenario.")

    # Panel 3.3 — Deployment trajectory
    p_h = 0.205
    p_y3 -= (p_h + gutter)
    ix, iy, iw, ih = add_panel(fig, col3_x, p_y3, col_w, p_h,
                               title="Deployment vs IEA NZE wedge")
    add_image(fig, FIG / "fig11_deployment_trajectory.png", ix, iy, iw, ih,
              caption="Fig. 11 — Fast scenario reaches ≈ 80% of the IEA NZE low-T heat wedge by 2050.")

    # Panel 3.4 — Conclusions + open questions + refs
    p_h = body_h - (body_top - p_y3) - gutter
    p_y3 -= (p_h + gutter)
    ix, iy, iw, ih = add_panel(fig, col3_x, p_y3, col_w, p_h,
                               title="Findings & next steps", title_color=C_ACCENT_2)
    add_text_block(
        fig,
        wrap(
            "Findings\n"
            "  1.  Two viability tiers, not one. Short-haul passive-pond CaCl₂ "
            "clears $54–66/MWh; long-haul deep-CSP CaCl₂ sits at $100–120/MWh.\n"
            "  2.  Cargo-as-fuel was the v0.2 showstopper. Autonomous wind-primary "
            "shipping eliminates it: round-trip efficiency rises to a uniform 58–80%.\n"
            "  3.  Freshwater coproduction (2–6 Mm³/yr per GW-th) is a real, "
            "monetisable co-revenue stream in water-scarce source regions.\n"
            "  4.  Achievable wedge ≈ 1.6 Gt CO₂/yr — ≈ 80% of the IEA NZE "
            "low-T heat decarbonization gap.\n\n"
            "Binding open questions\n"
            "  •  Multi-cycle salt stability (≥ 1,000 cycles).  Bench item.\n"
            "  •  Autonomous wind-cargo fleet scale-up (5,000+ ships by 2050).\n"
            "  •  Site-specific wind statistics in cruise-speed model.\n\n"
            "Next steps\n"
            "  •  Engage Ladon Robotics for vendor-grade vessel specs.\n"
            "  •  200-cycle CaCl₂ bench at a partner lab.\n"
            "  •  100 kW-th pilot at Mejillones, Chile with a single autonomous "
            "vessel.\n\n"
            "Selected references\n"
            "  N’Tsoukpoe et al. 2009; Donkers et al. 2017; Trausel et al. 2014; "
            "Cot-Gores et al. 2012; IEA NZE 2023.",
            width=74,
        ),
        ix, iy + 0.005, iw, ih - 0.005,
        fontsize=16, leading=1.30,
    )

    # ------------- SAVE -------------
    out_png = ROOT / "poster.png"
    out_pdf = ROOT / "poster.pdf"
    fig.savefig(out_png, dpi=DPI, facecolor=fig.get_facecolor())
    fig.savefig(out_pdf, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"wrote {out_png}")
    print(f"wrote {out_pdf}")


if __name__ == "__main__":
    build()

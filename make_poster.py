"""
A0-landscape scientific poster for the Solar Salt Heat Export project.

v2 layout — designed for layered comprehension:
  Layer 1 (5 s):  title + hero loop diagram + three giant claims
  Layer 2 (30 s): three supporting panels per discipline (methods, results, impact)
  Layer 3 (3 m):  embedded figures, findings, references

Outputs:
  poster.png   (200 dpi, ~ 9362 x 6622 px)
  poster.pdf

Run:  python make_poster.py
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).parent
FIG = ROOT / "figures"

# A0 landscape: 1189 mm x 841 mm  ->  46.81 x 33.11 inches
WIDTH_IN, HEIGHT_IN = 46.81, 33.11
DPI = 200

# Palette
C_DARK = "#0E2A38"          # title bar / footer
C_ACCENT = "#1F7A8C"        # primary section accent (teal)
C_ACCENT_2 = "#E07A1F"      # warm accent (charging / energy)
C_BG = "#FAFAF7"            # poster background
C_PANEL = "#FFFFFF"
C_PANEL_EDGE = "#D7D2C5"
C_TEXT = "#1A1A1A"
C_MUTED = "#5C5C5C"

# Stage colors for the hero diagram
C_SUN = "#F2C14E"           # solar resource — warm yellow
C_FIELD = "#E07A1F"         # charging field — burnt orange
C_SHIP = "#1F7A8C"          # autonomous freighter — teal
C_REACT = "#A23A2A"         # hydration reactor — deep red
C_CITY = "#3F5E78"           # city/district heat — steel blue


# ---------------------------------------------------------------------------
# Text wrapping helper
# ---------------------------------------------------------------------------


def wrap(text: str, width: int) -> str:
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
                break_long_words=False,
                break_on_hyphens=False,
            )
            for i, sub in enumerate(wrapped.split("\n")):
                out_lines.append((first_indent if i == 0 else cont_indent) + sub)
        out_paragraphs.append("\n".join(out_lines))
    return "\n\n".join(out_paragraphs)


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------


def add_panel(fig, x, y, w, h, *, title=None, pad=0.005, title_color=C_ACCENT):
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
        header_h = 0.020
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
            x + 0.007, y + h - header_h / 2, title.upper(),
            ha="left", va="center",
            fontsize=22, fontweight="bold", color="white",
            zorder=3,
        )
        inner_h = h - header_h - pad
    return x + pad, inner_y, w - 2 * pad, inner_h


def add_image(fig, path: Path, x, y, w, h, *, caption=None, caption_fs=14):
    img = mpimg.imread(path)
    img_h, img_w = img.shape[:2]
    img_aspect = img_w / img_h

    area_w_in = w * WIDTH_IN
    area_h_in = h * HEIGHT_IN
    cap_reserve_in = 0.30 if caption else 0.0
    avail_h_in = area_h_in - cap_reserve_in

    if area_w_in / avail_h_in > img_aspect:
        draw_h_in = avail_h_in
        draw_w_in = draw_h_in * img_aspect
    else:
        draw_w_in = area_w_in
        draw_h_in = draw_w_in / img_aspect

    draw_w = draw_w_in / WIDTH_IN
    draw_h = draw_h_in / HEIGHT_IN
    x_off = x + (w - draw_w) / 2
    y_off = y + cap_reserve_in / HEIGHT_IN + (avail_h_in / HEIGHT_IN - draw_h) / 2

    ax = fig.add_axes([x_off, y_off, draw_w, draw_h])
    ax.imshow(img)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_zorder(3)

    if caption:
        fig.text(
            x + w / 2, y + 0.003,
            caption,
            ha="center", va="bottom",
            fontsize=caption_fs, style="italic", color=C_MUTED,
            zorder=4,
        )


def add_text_block(fig, text, x, y, w, h, *, fontsize=18, leading=1.30,
                   color=C_TEXT, weight="normal", va="top", ha="left"):
    fig.text(
        x if ha == "left" else x + w / 2 if ha == "center" else x + w,
        y + h if va == "top" else y if va == "bottom" else y + h / 2,
        text,
        ha=ha, va=va,
        fontsize=fontsize, color=color, fontweight=weight,
        linespacing=leading,
        zorder=3,
    )


# ---------------------------------------------------------------------------
# Hero loop diagram — drawn from primitives for visual weight
# ---------------------------------------------------------------------------


def lighten(hex_color: str, amount: float = 0.85) -> str:
    """Return a lightened version of a hex colour, blended toward white."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)
    return f"#{r:02X}{g:02X}{b:02X}"


def draw_hero_diagram(fig, x, y, w, h):
    """Five-stage loop diagram, full width. The visual centerpiece of the
    poster. Drawn in figure axes coords from 0..100 (x), 0..40 (y)."""
    ax = fig.add_axes([x, y, w, h])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 40)
    ax.axis("off")
    ax.set_zorder(5)

    stages = [
        ("SOLAR RESOURCE",       "3,500 kWh/m²/yr\nArid coast: Atacama",                C_SUN),
        ("SOLAR CHARGING FIELD", "8.6 km² passive pond\nCaCl₂ → dehydrated salt",        C_FIELD),
        ("WIND-PRIMARY FREIGHTER","Autonomous, uncrewed\n18 vessels · 1,800 km · wind",  C_SHIP),
        ("HYDRATION REACTOR",    "Salt + H₂O → stored heat\n1 GW-th, η_react = 86%",     C_REACT),
        ("DISTRICT HEAT",        "832 kt CO₂ avoided / yr\n4.38 TWh delivered",          C_CITY),
    ]

    n = len(stages)
    box_w = 15.0
    box_h = 13.0
    box_top_y = 28.0
    box_bot_y = box_top_y - box_h
    gap = (100 - n * box_w) / (n + 1)

    centers = []
    for i, (label, sub, color) in enumerate(stages):
        cx = gap + i * (box_w + gap) + box_w / 2
        centers.append(cx)

        # Box
        ax.add_patch(FancyBboxPatch(
            (cx - box_w / 2, box_bot_y), box_w, box_h,
            boxstyle="round,pad=0.4,rounding_size=0.8",
            linewidth=3.0,
            edgecolor=color,
            facecolor=lighten(color, 0.82),
            zorder=6,
        ))

        # Stage number badge
        ax.text(
            cx - box_w / 2 + 1.2, box_top_y - 1.4,
            f"{i+1}",
            ha="center", va="center",
            fontsize=22, fontweight="bold",
            color="white",
            bbox=dict(boxstyle="circle,pad=0.4", fc=color, ec="none"),
            zorder=8,
        )

        # Stage label
        ax.text(
            cx, box_top_y - 3.4, label,
            ha="center", va="top",
            fontsize=22, fontweight="bold",
            color=C_TEXT, zorder=8,
        )
        # Sub-detail
        ax.text(
            cx, box_top_y - 7.5, sub,
            ha="center", va="top",
            fontsize=17, color=C_MUTED, linespacing=1.25, zorder=8,
        )

        # Forward arrow (between boxes, on top edge)
        if i < n - 1:
            next_cx = gap + (i + 1) * (box_w + gap) + box_w / 2
            arrow = FancyArrowPatch(
                (cx + box_w / 2 + 0.5, box_top_y - box_h / 2),
                (next_cx - box_w / 2 - 0.5, box_top_y - box_h / 2),
                arrowstyle="-|>", mutation_scale=30,
                linewidth=3.5, color="#3A3A3A", zorder=7,
            )
            ax.add_patch(arrow)

    # Closed-loop return arrow underneath
    return_y = box_bot_y - 6.5
    last_cx = centers[-1]
    first_cx = centers[0]
    # Down from last box
    ax.add_patch(FancyArrowPatch(
        (last_cx, box_bot_y - 0.3),
        (last_cx, return_y),
        arrowstyle="-", linewidth=3.0, color="#888", zorder=6,
    ))
    # Horizontal back across
    ax.add_patch(FancyArrowPatch(
        (last_cx, return_y),
        (first_cx, return_y),
        arrowstyle="-", linewidth=3.0, color="#888", zorder=6,
    ))
    # Up into first box
    ax.add_patch(FancyArrowPatch(
        (first_cx, return_y),
        (first_cx, box_bot_y - 0.3),
        arrowstyle="-|>", mutation_scale=30,
        linewidth=3.0, color="#888", zorder=6,
    ))
    # Label
    ax.text(
        (last_cx + first_cx) / 2, return_y - 2.2,
        "RETURN VOYAGE  ·  hydrated, discharged salt  ·  wind-only propulsion",
        ha="center", va="top",
        fontsize=20, color="#666", style="italic", zorder=8,
    )

    # Title above the diagram
    ax.text(
        50, 38,
        "Reference loop  ·  CaCl₂ passive pond  ·  Atacama → Southern Cone, 1,800 km",
        ha="center", va="top",
        fontsize=24, fontweight="bold", color=C_DARK,
        zorder=8,
    )


# ---------------------------------------------------------------------------
# Claim band — three big numbers below the hero
# ---------------------------------------------------------------------------


def draw_claim_band(fig, x, y, w, h):
    claims = [
        ("$54 / MWh",  "Delivered heat (LCOH) on the Atacama → Southern Cone reference route, "
                       "inside the $40–66 target band — no carbon price assumed.", C_ACCENT_2),
        ("80 %",        "Round-trip thermal efficiency, sun-on-pond to delivered-heat. "
                        "No electricity round-trip; the discharge temperature is the use temperature.", C_ACCENT),
        ("1.6 Gt CO₂", "Per-year carbon wedge achievable by 2050 in the Fast deployment scenario — "
                        "≈ 80 % of the IEA NZE low-temperature heat decarbonisation gap.", C_CITY),
    ]

    n = len(claims)
    gap = 0.012
    card_w = (w - (n - 1) * gap) / n

    for i, (big, sub, color) in enumerate(claims):
        cx = x + i * (card_w + gap)
        # Card background
        fig.patches.append(FancyBboxPatch(
            (cx, y), card_w, h,
            transform=fig.transFigure,
            boxstyle="round,pad=0.0,rounding_size=0.005",
            linewidth=0,
            facecolor=lighten(color, 0.88),
            zorder=2,
        ))
        # Left color bar
        fig.patches.append(Rectangle(
            (cx, y), 0.006, h,
            transform=fig.transFigure,
            linewidth=0, facecolor=color, zorder=3,
        ))
        # Big number
        fig.text(
            cx + 0.018, y + h * 0.62, big,
            ha="left", va="center",
            fontsize=58, fontweight="bold", color=color,
            zorder=4,
        )
        # Sub text (wrapped)
        sub_wrapped = wrap(sub, width=58)
        fig.text(
            cx + 0.018, y + h * 0.22, sub_wrapped,
            ha="left", va="center",
            fontsize=16, color=C_TEXT, linespacing=1.30,
            zorder=4,
        )


# ---------------------------------------------------------------------------
# Build the poster
# ---------------------------------------------------------------------------


def build():
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=C_BG)

    # ---------- TITLE BAR ----------
    title_h = 0.080
    fig.patches.append(Rectangle(
        (0, 1 - title_h), 1, title_h,
        transform=fig.transFigure, linewidth=0, facecolor=C_DARK, zorder=1,
    ))
    fig.patches.append(Rectangle(
        (0, 1 - title_h - 0.005), 1, 0.005,
        transform=fig.transFigure, linewidth=0, facecolor=C_ACCENT_2, zorder=1,
    ))

    fig.text(
        0.025, 1 - title_h * 0.40,
        "Solar Thermochemical Heat Export via Closed-Loop Salt Hydration",
        ha="left", va="center",
        fontsize=60, fontweight="bold", color="white", zorder=3,
    )
    fig.text(
        0.025, 1 - title_h * 0.78,
        "The discharge temperature is the use temperature  —  no electricity round-trip, no exergy loss.",
        ha="left", va="center",
        fontsize=30, color="#E8B86E", style="italic", zorder=3,
    )
    fig.text(
        0.975, 1 - title_h * 0.40,
        "Eric Neuman",
        ha="right", va="center",
        fontsize=28, fontweight="bold", color="white", zorder=3,
    )
    fig.text(
        0.975, 1 - title_h * 0.78,
        "Dotted Labs   ·   Concept paper v0.3   ·   2026",
        ha="right", va="center",
        fontsize=22, color="#D8E6EC", zorder=3,
    )

    # ---------- FOOTER ----------
    footer_h = 0.026
    fig.patches.append(Rectangle(
        (0, 0), 1, footer_h,
        transform=fig.transFigure, linewidth=0, facecolor=C_DARK, zorder=1,
    ))
    fig.text(
        0.025, footer_h / 2,
        "github.com/neuman/stirlingspike",
        ha="left", va="center",
        fontsize=18, color="white", zorder=3,
    )
    fig.text(
        0.5, footer_h / 2,
        "Pre-feasibility — end-to-end modeling complete; salt-cycle bench validation and "
        "autonomous-vessel vendor engagement are the binding next steps.",
        ha="center", va="center",
        fontsize=16, color="#D8E6EC", style="italic", zorder=3,
    )
    fig.text(
        0.975, footer_h / 2,
        "eric@trydotted.com",
        ha="right", va="center",
        fontsize=18, color="white", zorder=3,
    )

    # ---------- BAND GEOMETRY ----------
    body_top = 1 - title_h - 0.008
    body_bot = footer_h + 0.008

    hero_h = 0.300
    claim_h = 0.090
    content_h = body_top - body_bot - hero_h - claim_h - 2 * 0.010

    hero_y = body_top - hero_h
    claim_y = hero_y - claim_h - 0.010
    content_y_top = claim_y - 0.010

    margin = 0.018

    # ---------- HERO ----------
    draw_hero_diagram(fig, margin, hero_y, 1 - 2 * margin, hero_h)

    # ---------- CLAIM BAND ----------
    draw_claim_band(fig, margin, claim_y, 1 - 2 * margin, claim_h)

    # ---------- CONTENT BAND (3 columns × 2 rows) ----------
    gutter = 0.010
    col_w = (1 - 2 * margin - 2 * gutter) / 3
    col_x = [margin + i * (col_w + gutter) for i in range(3)]

    row_gutter = 0.010
    row_h = (content_h - row_gutter) / 2
    row1_y = content_y_top - row_h
    row2_y = row1_y - row_gutter - row_h

    # ==================== Row 1, Col 1: What's new ====================
    ix, iy, iw, ih = add_panel(fig, col_x[0], row1_y, col_w, row_h,
                               title="What is new", title_color=C_ACCENT_2)
    add_text_block(
        fig,
        wrap(
            "Closed-loop maritime thermochemical heat export has not, to our "
            "knowledge, been modeled end-to-end. Adjacent literature treats "
            "either (i) stationary salt storage at the plant, or "
            "(ii) hydrogen / ammonia carriers.\n\n"
            "Salt-hydrate carriers are uniquely suited to low-temperature "
            "district heat: the discharge temperature is the use temperature. "
            "There is no exergy-destroying conversion to electricity or "
            "chemical fuel — sunlight → bonds → heat, full stop.\n\n"
            "The v0.3 architectural pivot drops the v0.2 cargo-as-fuel "
            "auxiliary engine in favour of autonomous wind-primary "
            "freighters. Long-haul LCOH roughly halves; the highest-"
            "carbon-leverage routes (Pilbara → N. China, Namibia → NW Europe) "
            "become economically tractable.",
            width=64,
        ),
        ix, iy + 0.004, iw, ih - 0.004,
        fontsize=17, leading=1.32,
    )

    # ==================== Row 1, Col 2: Working fluids fig ====================
    ix, iy, iw, ih = add_panel(fig, col_x[1], row1_y, col_w, row_h,
                               title="Candidate working fluids")
    add_image(fig, FIG / "fig01_energy_density.png", ix, iy, iw, ih,
              caption="Fig. 1 — Theoretical energy density of candidate salt-hydrate pairs.")

    # ==================== Row 1, Col 3: Chem × route grid ====================
    ix, iy, iw, ih = add_panel(fig, col_x[2], row1_y, col_w, row_h,
                               title="Chemistry × route grid")
    add_image(fig, FIG / "fig02_chem_route_grid.png", ix, iy, iw, ih,
              caption="Fig. 2 — LCOH (left) and round-trip thermal efficiency (right) "
                      "across the chemistry × route matrix.")

    # ==================== Row 2, Col 1: Sensitivity to vessel cruise speed ====================
    ix, iy, iw, ih = add_panel(fig, col_x[0], row2_y, col_w, row_h,
                               title="LCOH vs vessel cruise speed")
    add_image(fig, FIG / "fig04_cruise_speed.png", ix, iy, iw, ih,
              caption="Fig. 4 — LCOH sensitivity to autonomous vessel cruise speed "
                      "(≈ $5 / MWh per knot, across the route set).")

    # ==================== Row 2, Col 2: Climate leverage + deployment ====================
    ix, iy, iw, ih = add_panel(fig, col_x[1], row2_y, col_w, row_h,
                               title="Climate leverage at scale")
    # Two stacked sub-images
    inner_h = ih - 0.005
    sub_h = (inner_h - 0.004) / 2
    add_image(fig, FIG / "fig08_climate_impact.png", ix, iy + sub_h + 0.004, iw, sub_h,
              caption="Fig. 8 — CO₂ avoided by route.", caption_fs=12)
    add_image(fig, FIG / "fig11_deployment_trajectory.png", ix, iy, iw, sub_h,
              caption="Fig. 11 — Fast scenario reaches ≈ 80 % of IEA NZE low-T heat wedge by 2050.",
              caption_fs=12)

    # ==================== Row 2, Col 3: Findings + open questions + refs ====================
    ix, iy, iw, ih = add_panel(fig, col_x[2], row2_y, col_w, row_h,
                               title="Findings · open questions · next steps",
                               title_color=C_ACCENT_2)
    add_text_block(
        fig,
        wrap(
            "Findings\n"
            "  1.  Two viability tiers, not one. Short-haul passive-pond CaCl₂ "
            "clears $54–66/MWh; long-haul deep-CSP CaCl₂ sits at $100–120/MWh.\n"
            "  2.  Cargo-as-fuel was the v0.2 showstopper. Autonomous wind-primary "
            "shipping eliminates it; round-trip efficiency rises to a uniform 58–80%.\n"
            "  3.  Freshwater coproduction (2–6 Mm³/yr per GW-th plant) is a real, "
            "monetisable co-revenue stream in arid source regions.\n\n"
            "Binding open questions\n"
            "  •  Multi-cycle salt stability (≥ 1,000 cycles).  Bench item.\n"
            "  •  Autonomous wind-cargo fleet scale-up (5,000+ vessels by 2050).\n"
            "  •  Site-specific wind statistics in the cruise-speed model.\n\n"
            "Next steps\n"
            "  •  200-cycle CaCl₂ bench validation at a partner lab.\n"
            "  •  Vendor engagement (Ladon Robotics or peer) for vessel-class specs.\n"
            "  •  100 kW-th pilot at Mejillones, Chile.\n\n"
            "Selected references\n"
            "  N'Tsoukpoe et al. 2009 · Donkers et al. 2017 · Trausel et al. 2014 · "
            "Cot-Gores et al. 2012 · IEA NZE 2023.",
            width=66,
        ),
        ix, iy + 0.004, iw, ih - 0.004,
        fontsize=15, leading=1.28,
    )

    # ---------- SAVE ----------
    out_png = ROOT / "poster.png"
    out_pdf = ROOT / "poster.pdf"
    fig.savefig(out_png, dpi=DPI, facecolor=fig.get_facecolor())
    fig.savefig(out_pdf, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"wrote {out_png}")
    print(f"wrote {out_pdf}")


if __name__ == "__main__":
    build()

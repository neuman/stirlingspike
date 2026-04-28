"""Poster-quality figure generation.

All figures use a consistent typographic hierarchy:
  - title 16pt
  - axis labels 12pt
  - tick labels 10pt
  - DPI 200 (suitable for A1/A0 poster + 1-page brief)
  - colorblind-safe palette (Okabe-Ito ordering)
"""

from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "axes.titlesize": 16,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.family": "DejaVu Sans",
})

OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#999999"]

FIG_DIR = Path("/home/user/stirlingspike/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)


def fig_energy_density_comparison(chemistries):
    fig, ax = plt.subplots(figsize=(8, 5))
    names = [c.short for c in chemistries]
    vals = [c.energy_density_kWh_per_t for c in chemistries]
    vols = [c.energy_density_GJ_per_m3 for c in chemistries]
    csp = [c.needs_csp for c in chemistries]
    colors = [OKABE_ITO[1] if x else OKABE_ITO[0] for x in csp]
    bars = ax.bar(names, vals, color=colors, edgecolor="black")
    for b, v, gv in zip(bars, vals, vols):
        ax.text(b.get_x() + b.get_width() / 2, v + 5, f"{v:.0f}\n({gv:.2f})",
                ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Specific energy (kWh per tonne dry charged salt)\n+ volumetric (GJ/m³) in parentheses")
    ax.set_title("Theoretical thermochemical energy density\nby candidate working fluid")
    legend_elems = [
        plt.Rectangle((0, 0), 1, 1, color=OKABE_ITO[0], label="Passive solar pond charging"),
        plt.Rectangle((0, 0), 1, 1, color=OKABE_ITO[1], label="Concentrating solar required"),
    ]
    ax.legend(handles=legend_elems, loc="upper left")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    out = FIG_DIR / "fig01_energy_density.png"
    plt.savefig(out)
    plt.close()
    return out


def fig_chem_route_grid(df: pd.DataFrame):
    """Heatmap of LCOH and round-trip efficiency over chem x route grid."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    pivot_lcoh = df.pivot(index="chem", columns="route", values="LCOH_USD_per_MWh")
    pivot_eta = df.pivot(index="chem", columns="route", values="round_trip_thermal_efficiency") * 100.0
    # Sort columns by mean LCOH (best routes first)
    col_order = pivot_lcoh.mean(axis=0).sort_values().index
    pivot_lcoh = pivot_lcoh[col_order]
    pivot_eta = pivot_eta[col_order]
    row_order = pivot_lcoh.mean(axis=1).sort_values().index
    pivot_lcoh = pivot_lcoh.loc[row_order]
    pivot_eta = pivot_eta.loc[row_order]

    for ax, p, title, fmt, cmap in zip(
        axes,
        [pivot_lcoh, pivot_eta],
        ["Levelised cost of delivered heat (USD / MWh)",
         "Round-trip thermal efficiency (%)"],
        ["{:.0f}", "{:.0f}"],
        ["YlOrRd", "YlGnBu"],
    ):
        im = ax.imshow(p.values, cmap=cmap, aspect="auto")
        ax.set_xticks(range(p.shape[1]))
        ax.set_xticklabels(p.columns, rotation=30, ha="right")
        ax.set_yticks(range(p.shape[0]))
        ax.set_yticklabels(p.index)
        for i in range(p.shape[0]):
            for j in range(p.shape[1]):
                ax.text(j, i, fmt.format(p.values[i, j]),
                        ha="center", va="center", fontsize=9,
                        color="black")
        ax.set_title(title)
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    fig.suptitle("Chemistry × geography sensitivity grid\n1 GW-thermal export plant @ destination",
                 fontsize=14)
    plt.tight_layout()
    out = FIG_DIR / "fig02_chem_route_grid.png"
    plt.savefig(out)
    plt.close()
    return out


def fig_distance_sensitivity(df_dist: pd.DataFrame):
    """Replaces v0.2 cargo-as-fuel figure. New transport architecture
    (autonomous wind-primary) makes voyage time the dominant cost driver,
    not propulsion energy. Plot ships-required-per-1-GW-th-plant vs
    distance, parameterized on cruise speed."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    speeds = sorted(df_dist["cruise_speed_kn"].unique())
    for i, speed in enumerate(speeds):
        sub = df_dist[df_dist["cruise_speed_kn"] == speed]
        axes[0].plot(sub["distance_km"], sub["cycle_days"],
                     marker="o", color=OKABE_ITO[i], label=f"{speed:.0f} kn cruise")
        axes[1].plot(sub["distance_km"], sub["ships_required_1GWth"],
                     marker="o", color=OKABE_ITO[i], label=f"{speed:.0f} kn cruise")
    axes[0].set_xlabel("Voyage distance (km)")
    axes[0].set_ylabel("Round-trip cycle (days)")
    axes[0].set_title("Voyage cycle time vs distance\n(autonomous wind, includes 6-day buffer)")
    axes[0].legend()
    axes[1].set_xlabel("Voyage distance (km)")
    axes[1].set_ylabel("Ships required per 1 GW-th plant")
    axes[1].set_title("Fleet size vs distance\n(handysize-equivalent autonomous vessels)")
    axes[1].legend()
    plt.tight_layout()
    out = FIG_DIR / "fig03_distance_sensitivity.png"
    plt.savefig(out)
    plt.close()
    return out


def fig_cruise_speed(df: pd.DataFrame):
    """LCOH vs autonomous-vessel cruise speed for primary routes."""
    fig, ax = plt.subplots(figsize=(8.5, 5))
    routes = df["route"].unique()
    for i, r in enumerate(routes):
        sub = df[df["route"] == r].sort_values("cruise_speed_kn")
        ax.plot(sub["cruise_speed_kn"], sub["LCOH"],
                marker="o", color=OKABE_ITO[i], label=r)
    ax.axhspan(40, 60, color="grey", alpha=0.15, label="paper target band")
    ax.axvline(7.0, color="black", linestyle="--", alpha=0.4)
    ax.text(7.05, ax.get_ylim()[1] * 0.95, "design point\n(7 kn)",
            ha="left", va="top", fontsize=9, color="grey")
    ax.set_xlabel("Autonomous vessel cruise speed (knots)")
    ax.set_ylabel("LCOH (USD / MWh-th)")
    ax.set_title("LCOH sensitivity to autonomous vessel cruise speed\n"
                 "(CaCl₂ passive pond chemistry; wind-only propulsion)")
    ax.legend()
    plt.tight_layout()
    out = FIG_DIR / "fig04_cruise_speed.png"
    plt.savefig(out)
    plt.close()
    return out


def fig_capacity_scale(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for i, key in enumerate(sorted(df["chem_key"].unique())):
        sub = df[df["chem_key"] == key].sort_values("capacity_MWth")
        axes[0].plot(sub["capacity_MWth"], sub["LCOH"],
                     marker="o", color=OKABE_ITO[i], label=key)
        axes[1].plot(sub["capacity_MWth"], sub["annual_avoided_CO2_kt"],
                     marker="o", color=OKABE_ITO[i], label=key)
    axes[0].set_xscale("log")
    axes[0].set_xlabel("Plant capacity (MW-thermal)")
    axes[0].set_ylabel("LCOH (USD / MWh)")
    axes[0].set_title("Cost scaling with plant size")
    axes[0].axhspan(40, 60, color="grey", alpha=0.15, label="paper target band")
    axes[0].legend()

    axes[1].set_xscale("log")
    axes[1].set_xlabel("Plant capacity (MW-thermal)")
    axes[1].set_ylabel("Avoided CO₂ (kt / yr)")
    axes[1].set_title("Carbon impact scaling")
    axes[1].legend()

    plt.tight_layout()
    out = FIG_DIR / "fig05_capacity_scale.png"
    plt.savefig(out)
    plt.close()
    return out


def fig_charge_depth(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    color_csp = df["needs_csp"].map(lambda x: OKABE_ITO[1] if x else OKABE_ITO[0])
    sc = ax.scatter(df["energy_density_kWh_per_t"], df["LCOH"],
                    c=color_csp, s=80, edgecolor="black")
    for _, row in df.iterrows():
        ax.annotate(f"{row['T_charge_full_C']:.0f}°C",
                    (row["energy_density_kWh_per_t"], row["LCOH"]),
                    xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.set_xlabel("Energy density (kWh / tonne)")
    ax.set_ylabel("LCOH (USD / MWh)")
    ax.set_title("CaCl₂ charge-depth tradeoff\nDeeper charging → higher density but requires CSP optics")
    legend_elems = [
        plt.Rectangle((0, 0), 1, 1, color=OKABE_ITO[0], label="Passive pond achievable"),
        plt.Rectangle((0, 0), 1, 1, color=OKABE_ITO[1], label="CSP required"),
    ]
    ax.legend(handles=legend_elems)
    plt.tight_layout()
    out = FIG_DIR / "fig06_charge_depth.png"
    plt.savefig(out)
    plt.close()
    return out


def fig_system_summary(df_grid: pd.DataFrame, best_row, route_obj):
    """Hero figure: Sankey-like material/energy flow chart of the best system."""
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.axis("off")
    box_w, box_h = 0.14, 0.22
    blocks = [
        ("Solar resource\n{:.0f} kWh/m²/yr".format(route_obj.DNI_kWh_per_m2_yr),
         0.02, 0.50, OKABE_ITO[4]),
        ("Solar charging field\n{:.1f} km² aperture\n{:.0%} solar→chem".format(
            best_row["pond_area_km2"], best_row["solar_to_chem_efficiency"]),
         0.21, 0.50, OKABE_ITO[1]),
        ("Autonomous wind\nshipping (Ladon-class)\n{} vessels, {:.0f} km\nwind-only".format(
            int(best_row["ships_required"]), route_obj.distance_km),
         0.40, 0.50, OKABE_ITO[2]),
        ("Hydration plant\n{} MW-thermal\nη_react·distrib = 86%".format(
            int(best_row["plant_capacity_MWth"])),
         0.59, 0.50, OKABE_ITO[0]),
        ("Delivered heat\n{:.2f} TWh/yr\n{:.0f} kt CO₂\navoided / yr".format(
            best_row["annual_heat_delivered_TWh"],
            best_row["annual_avoided_CO2_kt"]),
         0.78, 0.50, OKABE_ITO[3]),
    ]
    for txt, x, y, col in blocks:
        ax.add_patch(mpl.patches.FancyBboxPatch(
            (x, y), box_w, box_h, boxstyle="round,pad=0.01",
            facecolor=col, edgecolor="black", alpha=0.88))
        ax.text(x + box_w / 2, y + box_h / 2, txt, ha="center", va="center",
                fontsize=10, color="white", weight="bold")
    # Arrows between blocks
    for x_left in (0.02, 0.21, 0.40, 0.59):
        ax.annotate("", xy=(x_left + box_w + 0.03, 0.61), xytext=(x_left + box_w, 0.61),
                    arrowprops=dict(arrowstyle="->", lw=2.4, color="black"))
    # Return loop (destination back to source)
    ax.annotate(
        "", xy=(0.28, 0.42), xytext=(0.66, 0.42),
        arrowprops=dict(arrowstyle="->", lw=1.6, color="grey",
                         connectionstyle="arc3,rad=-0.30"))
    ax.text(0.47, 0.28, "Return voyage: hydrated discharged salt\n(wind-only propulsion)",
            ha="center", color="grey", fontsize=10, style="italic")
    # Freshwater coproduction arrow
    ax.annotate(
        "", xy=(0.30, 0.83), xytext=(0.28, 0.74),
        arrowprops=dict(arrowstyle="->", lw=1.8, color=OKABE_ITO[4]))
    ax.text(0.34, 0.86, "Freshwater coproduction: {:.2f} Mm³/yr   ({:.2f} m³/MWh)".format(
        best_row["annual_freshwater_Mm3"], best_row["freshwater_per_MWh_m3"]),
        ha="left", color=OKABE_ITO[4], fontsize=10, weight="bold")

    ax.text(0.5, 0.10,
            "LCOH = {:.0f} USD/MWh    |    round-trip η = {:.0%}    |    "
            "CO₂ payback = {:.1f} yr".format(
                best_row["LCOH_USD_per_MWh"],
                best_row["round_trip_thermal_efficiency"],
                best_row["co2_payback_years"]),
            ha="center", fontsize=13, weight="bold")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Reference system: {} on {}".format(best_row["chem"], best_row["route"]),
                 fontsize=15)
    plt.tight_layout()
    out = FIG_DIR / "fig07_system_summary.png"
    plt.savefig(out)
    plt.close()
    return out


def fig_climate_impact_pyramid(df_grid: pd.DataFrame):
    """Stack: per-plant -> 100-plant -> 1000-plant CO2 vs global emissions."""
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    best = df_grid.sort_values("LCOH_USD_per_MWh").iloc[0]
    per_plant_kt = best["annual_avoided_CO2_kt"]
    levels = ["1 plant\n(1 GW-th)", "10 plants", "100 plants", "1000 plants"]
    values = [per_plant_kt, per_plant_kt * 10, per_plant_kt * 100, per_plant_kt * 1000]
    pct_global = [v / (40e6) * 100 for v in values]   # 40 GtCO2/yr = 40e6 kt
    bars = ax.barh(levels, values, color=OKABE_ITO[0], edgecolor="black")
    for b, v, p in zip(bars, values, pct_global):
        ax.text(v * 1.02, b.get_y() + b.get_height() / 2,
                "{:.1f} MtCO₂/yr  ({:.2f}% of global emissions)".format(v / 1000, p),
                va="center", fontsize=10)
    ax.set_xscale("log")
    ax.set_xlabel("Annual avoided CO₂ (kt/yr) — log scale")
    ax.set_title("Climate leverage by deployment scale\nbest case: {} on {}".format(
        best["chem"], best["route"]))
    ax.set_xlim(per_plant_kt * 0.5, per_plant_kt * 1000 * 4)
    plt.tight_layout()
    out = FIG_DIR / "fig08_climate_impact.png"
    plt.savefig(out)
    plt.close()
    return out


def fig_energy_sankey(best_row, route_obj, chem_obj, voyage_obj):
    """Energy flow waterfall: 100 units of solar DNI → losses → delivered heat."""
    DNI = 100.0
    eta_opt = 0.55 if not chem_obj.needs_csp else (
        0.55 if chem_obj.T_charge_full_K > 700 else 0.62
    )
    optical_loss = DNI * (1 - eta_opt)
    stored_frac = best_row["solar_to_chem_efficiency"]
    receiver_loss = DNI * eta_opt - DNI * stored_frac
    stored = DNI * stored_frac
    transport_loss = stored * best_row["cargo_consumed_fraction"]
    delivered_chem = stored - transport_loss
    reactor_loss = delivered_chem * (1 - 0.92)
    after_reactor = delivered_chem - reactor_loss
    distribution_loss = after_reactor * (1 - 0.93)
    delivered_heat = after_reactor - distribution_loss

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.set_title("Energy waterfall: 100 units of solar DNI → delivered heat\n"
                 "{} on {}".format(chem_obj.short, route_obj.name),
                 fontsize=14)
    ax.axis("off")

    # Manual horizontal "waterfall" instead of Sankey for clarity
    stages = [
        ("Solar DNI on aperture", DNI, OKABE_ITO[1]),
        ("− Optical / cover losses", -optical_loss, "#cccccc"),
        ("− Receiver / reaction losses", -receiver_loss, "#cccccc"),
        ("Stored chemical (charged salt)", 0, OKABE_ITO[2]),
        ("− Cargo consumed for propulsion", -transport_loss, "#cccccc"),
        ("− Reactor inefficiency", -reactor_loss, "#cccccc"),
        ("− Distribution losses", -distribution_loss, "#cccccc"),
        ("Delivered heat to customer", 0, OKABE_ITO[3]),
    ]
    cum = [DNI]
    for _, v, _ in stages[1:]:
        if v == 0:
            continue
        cum.append(cum[-1] + v)
    cum_iter = iter(cum)

    x = 0
    bar_h = 0.25
    y_top = 0.65
    val_running = DNI
    bar_x = 0.02
    bar_w = 0.92

    # Compose the underlying single bar with colored segments
    seg_x = bar_x
    seg_y = 0.45
    seg_h = 0.25
    segs = [
        ("Optical / cover loss", optical_loss, "#9c9c9c"),
        ("Receiver / reaction loss", receiver_loss, "#bdbdbd"),
        ("Reactor inefficiency", reactor_loss, "#a6761d"),
        ("Distribution loss", distribution_loss, "#666666"),
        ("Delivered heat", delivered_heat, OKABE_ITO[3]),
    ]
    if transport_loss > 0.01:
        segs.insert(2, ("Transport loss", transport_loss, "#7570b3"))
    total = sum(s[1] for s in segs)
    pos = seg_x
    label_anchors = []
    for name, v, col in segs:
        w = bar_w * v / total
        ax.add_patch(mpl.patches.Rectangle(
            (pos, seg_y), w, seg_h, facecolor=col, edgecolor="black"))
        if w > 0.07:
            ax.text(pos + w / 2, seg_y + seg_h / 2,
                    "{}\n{:.1f}".format(name, v),
                    ha="center", va="center", fontsize=9,
                    color="white" if v > 5 else "black",
                    weight="bold")
        else:
            label_anchors.append((pos + w / 2, name, v))
        pos += w

    # External labels for tiny slices, evenly distributed below the bar
    if label_anchors:
        n = len(label_anchors)
        ys = [seg_y - 0.06 - 0.045 * i for i in range(n)]
        for (xc, name, v), yl in zip(label_anchors, ys):
            ax.annotate("{}: {:.2f}".format(name, v),
                        xy=(xc, seg_y), xytext=(xc, yl),
                        ha="center", fontsize=8,
                        arrowprops=dict(arrowstyle="-", lw=0.5, color="grey"))
    ax.text(0.5, 0.78, "Each unit = 1% of incident solar DNI", ha="center", fontsize=11)
    ax.text(0.5, 0.30,
            "End-to-end solar→delivered-heat efficiency: {:.1f}%".format(delivered_heat),
            ha="center", fontsize=14, weight="bold", color=OKABE_ITO[3])
    ax.text(0.5, 0.18,
            "(Round-trip storage efficiency: {:.0%}; "
            "stored energy / solar DNI: {:.0%})".format(
                best_row["round_trip_thermal_efficiency"],
                best_row["solar_to_chem_efficiency"]),
            ha="center", fontsize=10, color="grey")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    out = FIG_DIR / "fig10_energy_waterfall.png"
    plt.savefig(out)
    plt.close()
    return out


def fig_deployment_trajectory():
    """How much deployment is needed to materially decarbonize global heating?

    Sets the proposal's plausible reach against IEA-NZE wedges:
      - 2030 milestone: 50 GW-th deployed cumulative
      - 2040 milestone: 500 GW-th deployed cumulative
      - 2050 milestone: 2000 GW-th deployed cumulative

    Compares to: (a) global district heating ~600 GW-th installed; (b) global
    industrial sub-200 C process heat ~3000 GW-th; (c) IEA NZE 'low-T heat'
    decarbonization wedge ~2 GtCO2/yr by 2050.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # LHS: cumulative GW-thermal deployed under three scenarios
    years = np.arange(2026, 2056)
    slow = np.where(years <= 2030, 1 * (years - 2025),
                    np.where(years <= 2040, 5 + 5 * (years - 2030),
                             55 + 12 * (years - 2040)))   # GW-th
    base = np.where(years <= 2030, 4 * (years - 2025),
                    np.where(years <= 2040, 20 + 25 * (years - 2030),
                             270 + 70 * (years - 2040)))
    fast = np.where(years <= 2030, 10 * (years - 2025),
                    np.where(years <= 2040, 50 + 50 * (years - 2030),
                             550 + 145 * (years - 2040)))

    axes[0].plot(years, slow, color=OKABE_ITO[7], label="Slow (R&D-led)")
    axes[0].plot(years, base, color=OKABE_ITO[0], label="Base (utility-led)", lw=2)
    axes[0].plot(years, fast, color=OKABE_ITO[5], label="Fast (subsidy + carbon-priced)", lw=2)
    axes[0].axhline(600, color="grey", linestyle="--", alpha=0.6)
    axes[0].text(2026, 620, "Global district heating capacity ≈ 600 GW-th",
                 color="grey", fontsize=9)
    axes[0].axhline(3000, color="grey", linestyle=":", alpha=0.6)
    axes[0].text(2026, 3100, "Global industrial low-T process heat ≈ 3000 GW-th",
                 color="grey", fontsize=9)
    axes[0].set_yscale("log")
    axes[0].set_ylabel("Cumulative deployed capacity (GW-thermal)")
    axes[0].set_xlabel("Year")
    axes[0].set_title("Deployment trajectory scenarios")
    axes[0].legend(loc="lower right")

    # RHS: corresponding annual avoided CO2
    # 0.83 MtCO2/yr/GW-th avoided (Atacama best); average 0.6 across routes
    avg_intensity = 0.6  # MtCO2/yr per GW-th
    axes[1].plot(years, slow * avg_intensity, color=OKABE_ITO[7], label="Slow")
    axes[1].plot(years, base * avg_intensity, color=OKABE_ITO[0], label="Base", lw=2)
    axes[1].plot(years, fast * avg_intensity, color=OKABE_ITO[5], label="Fast", lw=2)
    axes[1].axhline(2000, color="red", linestyle="--", alpha=0.6)
    axes[1].text(2026, 2200, "IEA NZE low-T heat decarb wedge ≈ 2 Gt CO₂/yr",
                 color="red", fontsize=9)
    axes[1].set_ylabel("Annual avoided CO₂ (Mt/yr)")
    axes[1].set_xlabel("Year")
    axes[1].set_title("Climate impact pathway")
    axes[1].legend(loc="upper left")
    axes[1].set_yscale("log")

    fig.suptitle("Deployment scale required for material climate impact",
                 fontsize=14)
    plt.tight_layout()
    out = FIG_DIR / "fig11_deployment_trajectory.png"
    plt.savefig(out)
    plt.close()
    return out


def fig_diurnal_charge(field_sol):
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    t = field_sol["t_h"][:24 * 14]   # 2 weeks
    axes[0].fill_between(t, 0, field_sol["I_W_m2"][:len(t)], color=OKABE_ITO[1], alpha=0.4)
    axes[0].plot(t, field_sol["I_W_m2"][:len(t)], color=OKABE_ITO[1])
    axes[0].set_ylabel("DNI (W/m²)")
    axes[0].set_title("Solar charging dynamics — 2-week window\n(synthetic clear-sky diurnal forcing)")
    axes[1].plot(t, field_sol["m_charged_kg"][:len(t)] / 1e3, color=OKABE_ITO[0])
    axes[1].set_ylabel("Charged salt (tonnes, cumulative)")
    axes[1].set_xlabel("Hour of year")
    plt.tight_layout()
    out = FIG_DIR / "fig09_diurnal_charge.png"
    plt.savefig(out)
    plt.close()
    return out

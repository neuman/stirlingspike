"""End-to-end driver: run all sweeps, save results, generate figures.

Usage:
    python -m sim.main
"""

from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

from .chemistries import CHEMISTRIES, summarize as chem_summary
from .routes import ROUTES
from .solar import simulate_field_year
from .system import simulate_system
from .sweeps import (
    base_grid,
    sensitivity_distance,
    sensitivity_wind_assist,
    sensitivity_capacity_scale,
    sensitivity_charge_depth,
)
from . import figures as F


RESULTS_DIR = Path("/home/user/stirlingspike/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 70)
    print("Solar Salt Heat Export — annual cycle simulator")
    print("=" * 70)
    print()
    print("Working fluid candidates:")
    print(chem_summary())
    print()

    print("Running base chem×route grid (this is the meat)…")
    df_grid = base_grid()
    df_grid.to_csv(RESULTS_DIR / "grid.csv", index=False)
    print("  done. {} system configurations evaluated.".format(len(df_grid)))

    best = df_grid.sort_values("LCOH_USD_per_MWh").iloc[0]
    print()
    print("Best (lowest LCOH) configuration:")
    print(f"  Chemistry: {best['chem']}")
    print(f"  Route:     {best['route']}")
    print(f"  LCOH:      ${best['LCOH_USD_per_MWh']:.1f}/MWh")
    print(f"  Round-trip thermal efficiency: {best['round_trip_thermal_efficiency']*100:.1f}%")
    print(f"  Annual avoided CO2: {best['annual_avoided_CO2_kt']:.0f} kt/yr")

    print("Running sensitivity sweeps…")
    df_dist = sensitivity_distance()
    df_dist.to_csv(RESULTS_DIR / "sensitivity_distance.csv", index=False)
    df_wind = sensitivity_wind_assist()
    df_wind.to_csv(RESULTS_DIR / "sensitivity_wind.csv", index=False)
    df_scale = sensitivity_capacity_scale()
    df_scale.to_csv(RESULTS_DIR / "sensitivity_scale.csv", index=False)
    df_depth = sensitivity_charge_depth()
    df_depth.to_csv(RESULTS_DIR / "sensitivity_charge_depth.csv", index=False)

    # Diurnal sample for figure 9
    chem = CHEMISTRIES["MgOH2"]
    route = ROUTES["morocco_baltic"]
    field_sol = simulate_field_year(
        chem=chem, area_m2=5e6,
        annual_DNI_kWh_m2=route.DNI_kWh_per_m2_yr,
        T_amb_C=route.ambient_T_source_C,
        eta_optical=0.62, U_loss_W_m2_K=4.5,
        eta_chem=0.85, water_capture_fraction=0.55,
    )

    print("Generating figures…")
    F.fig_energy_density_comparison(list(CHEMISTRIES.values()))
    F.fig_chem_route_grid(df_grid)
    F.fig_distance_sensitivity(df_dist)
    F.fig_wind_assist(df_wind)
    F.fig_capacity_scale(df_scale)
    F.fig_charge_depth(df_depth)
    F.fig_system_summary(df_grid, best, ROUTES[best["route_key"]])
    F.fig_climate_impact_pyramid(df_grid)
    F.fig_deployment_trajectory()
    F.fig_diurnal_charge(field_sol)
    from .transport import simulate_voyage
    voyage = simulate_voyage(CHEMISTRIES[best["chem_key"]],
                              distance_km=ROUTES[best["route_key"]].distance_km)
    F.fig_energy_sankey(best, ROUTES[best["route_key"]],
                         CHEMISTRIES[best["chem_key"]], voyage)

    print(f"  figures written to {F.FIG_DIR}")
    print(f"  CSVs written to {RESULTS_DIR}")

    # Headline summary
    summary = {
        "best_LCOH_USD_per_MWh": float(best["LCOH_USD_per_MWh"]),
        "best_chem": str(best["chem"]),
        "best_route": str(best["route"]),
        "best_round_trip_efficiency": float(best["round_trip_thermal_efficiency"]),
        "best_annual_avoided_CO2_kt": float(best["annual_avoided_CO2_kt"]),
        "best_pond_area_km2": float(best["pond_area_km2"]),
        "best_freshwater_per_MWh_m3": float(best["freshwater_per_MWh_m3"]),
        "best_ships_required": int(best["ships_required"]),
        "best_cargo_consumed_fraction": float(best["cargo_consumed_fraction"]),
        "best_co2_payback_years": float(best["co2_payback_years"]),
    }
    (RESULTS_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    print()
    print("HEADLINE NUMBERS")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    return df_grid, best


if __name__ == "__main__":
    main()

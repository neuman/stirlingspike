"""Parameter sweeps to fill in TBDs in the v0.1 concept paper.

Sweep dimensions:
  - chemistry x route (full grid)
  - pond capex sensitivity
  - wind-assist fraction sensitivity
  - plant capacity scale-up
  - charge depth (for CaCl2 family)
  - distance sensitivity (cargo-as-fuel breakeven)
"""

from __future__ import annotations
import json
import math
from dataclasses import asdict
import numpy as np
import pandas as pd

from .chemistries import CHEMISTRIES
from .routes import ROUTES
from .system import simulate_system, DEFAULTS


def base_grid() -> pd.DataFrame:
    rows = []
    for chem_key in CHEMISTRIES:
        for route_key in ROUTES:
            r = simulate_system(chem_key, route_key, plant_capacity_MWth=1000.0)
            rows.append({
                "chem_key": chem_key,
                "route_key": route_key,
                **asdict(r),
            })
    return pd.DataFrame(rows)


def sensitivity_distance() -> pd.DataFrame:
    rows = []
    for chem_key in ("CaCl2_passive", "CaCl2_full", "MgOH2", "CaOH2"):
        for d in (500, 1000, 1500, 2000, 3000, 4000, 6000, 8000, 10000, 12000):
            r = simulate_system(
                chem_key, "morocco_baltic", plant_capacity_MWth=1000.0,
                overrides={},
            )
            # override distance via patch: run a one-off custom voyage
            from .system import simulate_system as _s
            from .chemistries import CHEMISTRIES as C
            from .routes import ROUTES as R
            from .transport import simulate_voyage
            chem = C[chem_key]
            voyage = simulate_voyage(chem, distance_km=d, wind_assist_fraction=0.45)
            rows.append({
                "chem_key": chem_key,
                "distance_km": d,
                "cargo_consumed_fraction": voyage.cargo_consumed_fraction,
                "voyage_days": voyage.cycle_days,
            })
    return pd.DataFrame(rows)


def sensitivity_wind_assist() -> pd.DataFrame:
    rows = []
    for chem_key in CHEMISTRIES:
        for waf in np.linspace(0.0, 0.9, 10):
            from .chemistries import CHEMISTRIES as C
            from .transport import simulate_voyage
            voyage = simulate_voyage(C[chem_key], distance_km=4000.0,
                                     wind_assist_fraction=waf)
            rows.append({
                "chem_key": chem_key,
                "wind_assist_fraction": waf,
                "cargo_consumed_fraction": voyage.cargo_consumed_fraction,
            })
    return pd.DataFrame(rows)


def sensitivity_capacity_scale() -> pd.DataFrame:
    rows = []
    for chem_key in ("CaCl2_passive", "MgOH2", "CaOH2"):
        for cap in (50, 100, 250, 500, 1000, 2000, 5000):
            r = simulate_system(chem_key, "morocco_baltic",
                                plant_capacity_MWth=cap)
            rows.append({
                "chem_key": chem_key,
                "capacity_MWth": cap,
                "LCOH": r.LCOH_USD_per_MWh,
                "pond_area_km2": r.pond_area_km2,
                "ships": r.ships_required,
                "annual_heat_TWh": r.annual_heat_delivered_TWh,
                "annual_avoided_CO2_kt": r.annual_avoided_CO2_kt,
            })
    return pd.DataFrame(rows)


def sensitivity_pond_capex() -> pd.DataFrame:
    rows = []
    for chem_key in ("CaCl2_passive", "MgOH2", "CaOH2"):
        for capex in (5, 10, 18, 30, 60, 100, 180, 240, 350):
            field_key = "pond_capex_USD_m2" if chem_key == "CaCl2_passive" \
                else ("csp_capex_USD_m2" if chem_key == "MgOH2"
                      else "tower_capex_USD_m2")
            overrides = {field_key: capex}
            r = simulate_system(
                chem_key, "morocco_baltic", plant_capacity_MWth=1000.0,
                overrides=overrides,
            )
            rows.append({
                "chem_key": chem_key,
                "field_capex_USD_m2": capex,
                "LCOH": r.LCOH_USD_per_MWh,
                "capex_source_M": r.capex_source_M_USD,
            })
    return pd.DataFrame(rows)


def sensitivity_charge_depth() -> pd.DataFrame:
    """Sensitivity to depth-of-charge for CaCl2 system, 0..1 along the
    hexa->di->mono->anhydrous staircase."""
    rows = []
    from dataclasses import replace
    base_chem = CHEMISTRIES["CaCl2_full"]
    for frac in np.linspace(0.15, 1.0, 10):
        T_charge = 313.15 + 220.0 * frac
        # Passive ponds physically can't reach >~370 K (water boils, pond
        # cover loses transparency). Above that, CSP optics are required.
        chem = replace(
            base_chem,
            n_water_max=6.0 * frac,
            T_charge_full_K=T_charge,
            needs_csp=(T_charge > 370.0),
        )
        # Patch CHEMISTRIES temporarily
        CHEMISTRIES["CaCl2_depth_swp"] = chem
        try:
            r = simulate_system("CaCl2_depth_swp", "morocco_baltic",
                                plant_capacity_MWth=1000.0)
            rows.append({
                "depth_fraction": frac,
                "energy_density_kWh_per_t": chem.energy_density_kWh_per_t,
                "T_charge_full_C": chem.T_charge_full_K - 273.15,
                "LCOH": r.LCOH_USD_per_MWh,
                "pond_area_km2": r.pond_area_km2,
                "round_trip": r.round_trip_thermal_efficiency,
                "needs_csp": chem.needs_csp,
            })
        finally:
            CHEMISTRIES.pop("CaCl2_depth_swp", None)
    return pd.DataFrame(rows)

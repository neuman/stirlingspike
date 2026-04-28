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
    """Voyage-cycle days and ships-required as a function of distance, for
    the autonomous wind-primary fleet at three cruise-speed assumptions.
    Replaces the v0.2 cargo-as-fuel-vs-distance sweep, which is moot under
    the new vessel architecture.
    """
    rows = []
    from .transport import simulate_voyage
    chem = CHEMISTRIES["CaCl2_passive"]
    for speed_kn in (5.0, 7.0, 9.0):
        for d in (500, 1000, 1500, 2000, 3000, 4000, 6000, 8000, 10000, 12000):
            voyage = simulate_voyage(chem, distance_km=d,
                                     cruise_speed_kn=speed_kn,
                                     wind_assist_fraction=1.0)
            voyages_per_ship_per_year = 365.0 / voyage.cycle_days
            # Reference plant: 1 GW-th, ~10 Mt salt/yr throughput
            annual_salt_t = 10.0e6
            voyages_required = annual_salt_t / voyage.cargo_dwt_t
            ships_required = voyages_required / voyages_per_ship_per_year
            rows.append({
                "cruise_speed_kn": speed_kn,
                "distance_km": d,
                "cycle_days": voyage.cycle_days,
                "voyages_per_ship_per_year": voyages_per_ship_per_year,
                "ships_required_1GWth": ships_required,
            })
    return pd.DataFrame(rows)


def sensitivity_cruise_speed() -> pd.DataFrame:
    """LCOH vs cruise speed for autonomous wind-primary vessels on the
    primary routes. Replaces the v0.2 wind-assist-fraction sweep, which is
    moot for wind-only vessels.
    """
    rows = []
    for route_key in ("atacama_southern_cone", "morocco_baltic", "egypt_blacksea"):
        for speed_kn in np.linspace(4.0, 11.0, 8):
            r = simulate_system(
                "CaCl2_passive", route_key, plant_capacity_MWth=1000.0,
                cruise_speed_kn=speed_kn, wind_assist_fraction=1.0,
            )
            rows.append({
                "route_key": route_key,
                "route": ROUTES[route_key].name,
                "cruise_speed_kn": speed_kn,
                "ships_required": r.ships_required,
                "LCOH": r.LCOH_USD_per_MWh,
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

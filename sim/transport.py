"""Maritime transport model.

Mirrors SolarSaltExport.Components.BulkCarrier.

v0.3 architecture change: cargo-as-fuel auxiliary propulsion is dropped in
favor of autonomous wind-primary vessels (Ladon-class). The vessel class
makes propulsion energy a non-issue from a thermodynamic standpoint — wind
is treated as free — but its lower average cruise speed (~7 kn vs 10 kn
for a conventional bulker with diesel + wind assist) makes voyage time and
in-transit inventory the new dominant cost drivers.

Parameters below are bracketed estimates representative of the autonomous
wind-cargo class. Vendor-specific data (e.g. from Ladon Robotics) should be
substituted once available.
"""

from __future__ import annotations
from dataclasses import dataclass
from .chemistries import SaltChemistry


KN_TO_KM_PER_H = 1.852


@dataclass
class VoyageResult:
    distance_km: float
    cargo_dwt_t: float
    cruise_speed_kn: float
    voyage_hours: float
    propulsion_GJ: float
    wind_GJ: float
    aux_GJ: float
    cargo_consumed_t: float
    cargo_consumed_fraction: float
    return_voyage_hours: float
    cycle_days: float
    crew_count: int


def simulate_voyage(
    chem: SaltChemistry,
    distance_km: float,
    cargo_dwt_t: float = 35000.0,
    cruise_speed_kn: float = 7.0,        # wind-primary autonomous, lower than conventional 10 kn
    wind_assist_fraction: float = 1.0,   # wind-only by design
    eta_aux_engine: float = 0.30,
    specific_resistance_kJ_t_km: float = 35.0,
    return_speed_kn: float | None = None,
    return_wind_assist_fraction: float | None = None,
    crew_count: int = 0,                  # autonomous = uncrewed
    weather_buffer_days: float = 6.0,     # wait-for-wind + autonomous load/unload + lay-days
) -> VoyageResult:
    """Voyage-resolved propulsion and time balance.

    For an autonomous wind-primary vessel (wind_assist_fraction=1.0), there
    is no cargo-as-fuel debit and propulsion energy is treated as zero
    operating cost. Cruise speed is lower than a conventional bulker, and
    the weather buffer is longer to account for wait-for-wind events.
    """
    voyage_hours = distance_km / (cruise_speed_kn * KN_TO_KM_PER_H)
    propulsion_GJ = specific_resistance_kJ_t_km * cargo_dwt_t * distance_km / 1.0e6
    wind_GJ = wind_assist_fraction * propulsion_GJ
    aux_GJ = (1.0 - wind_assist_fraction) * propulsion_GJ
    cargo_consumed_t = aux_GJ * 1000.0 / (
        eta_aux_engine * chem.energy_density_kJ_per_kg
    )
    cargo_consumed_fraction = cargo_consumed_t / cargo_dwt_t

    rs = return_speed_kn if return_speed_kn is not None else cruise_speed_kn
    return_voyage_hours = distance_km / (rs * KN_TO_KM_PER_H)
    cycle_days = (voyage_hours + return_voyage_hours) / 24.0 + weather_buffer_days

    return VoyageResult(
        distance_km=distance_km,
        cargo_dwt_t=cargo_dwt_t,
        cruise_speed_kn=cruise_speed_kn,
        voyage_hours=voyage_hours,
        propulsion_GJ=propulsion_GJ,
        wind_GJ=wind_GJ,
        aux_GJ=aux_GJ,
        cargo_consumed_t=cargo_consumed_t,
        cargo_consumed_fraction=cargo_consumed_fraction,
        return_voyage_hours=return_voyage_hours,
        cycle_days=cycle_days,
        crew_count=crew_count,
    )

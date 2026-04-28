"""Maritime transport model.

Mirrors SolarSaltExport.Components.BulkCarrier.

Specific propulsion energy of 35 kJ/(t.km) at 10 kn is consistent with open
literature for handysize (~35,000 dwt) bulk carriers. We treat wind assist as
a multiplicative reduction on fuel demand at the design wind condition.
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


def simulate_voyage(
    chem: SaltChemistry,
    distance_km: float,
    cargo_dwt_t: float = 35000.0,
    cruise_speed_kn: float = 10.0,
    wind_assist_fraction: float = 0.45,
    eta_aux_engine: float = 0.30,
    specific_resistance_kJ_t_km: float = 35.0,
    return_speed_kn: float | None = None,
    return_wind_assist_fraction: float | None = None,
) -> VoyageResult:
    voyage_hours = distance_km / (cruise_speed_kn * KN_TO_KM_PER_H)
    propulsion_GJ = specific_resistance_kJ_t_km * cargo_dwt_t * distance_km / 1.0e6
    wind_GJ = wind_assist_fraction * propulsion_GJ
    aux_GJ = (1.0 - wind_assist_fraction) * propulsion_GJ
    cargo_consumed_t = aux_GJ * 1000.0 / (
        eta_aux_engine * chem.energy_density_kJ_per_kg
    )
    cargo_consumed_fraction = cargo_consumed_t / cargo_dwt_t

    rs = return_speed_kn if return_speed_kn is not None else cruise_speed_kn
    rw = (
        return_wind_assist_fraction
        if return_wind_assist_fraction is not None
        else wind_assist_fraction
    )
    return_voyage_hours = distance_km / (rs * KN_TO_KM_PER_H)
    cycle_days = (voyage_hours + return_voyage_hours) / 24.0 + 5.0

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
    )

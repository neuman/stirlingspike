"""Destination hydration / district-heat plant model.

Mirrors SolarSaltExport.Components.HydrationReactor + DistrictHeatPlant.
"""

from __future__ import annotations
from dataclasses import dataclass
from .chemistries import SaltChemistry


@dataclass
class DischargeResult:
    P_heat_W: float
    m_dot_salt_in: float
    m_dot_water_consumed: float
    m_dot_salt_out: float
    annual_heat_TWh: float
    annual_salt_in_kt: float
    annual_salt_out_kt: float
    annual_water_kt: float


def simulate_plant(
    chem: SaltChemistry,
    plant_capacity_MWth: float = 100.0,
    seasonal_load_factor: float = 0.55,
    T_water_in_C: float = 10.0,
    eta_reactor: float = 0.92,
    eta_distribution: float = 0.93,
) -> DischargeResult:
    e_density_J_kg = chem.energy_density_kJ_per_kg * 1000.0
    water_kg_per_kg = chem.m_water_per_kg_salt
    sensible_J_kg_water = 4180.0 * max(chem.T_discharge_typ_K - (T_water_in_C + 273.15), 0.0)

    # Solve for steady-state salt mass flow that yields the requested capacity.
    target_W = plant_capacity_MWth * 1.0e6 * seasonal_load_factor
    chem_to_heat = eta_distribution * eta_reactor
    # P = chem_to_heat * (m_dot_salt * (e_density - water_kg_per_kg * sensible))
    spec_heat_J_kg = chem_to_heat * (e_density_J_kg
                                     - water_kg_per_kg * sensible_J_kg_water)
    if spec_heat_J_kg <= 0:
        raise ValueError("Negative specific heat output — check inputs.")
    m_dot_salt = target_W / spec_heat_J_kg

    m_dot_water = m_dot_salt * water_kg_per_kg
    m_dot_salt_out = m_dot_salt + m_dot_water

    seconds_per_year = 365.0 * 24.0 * 3600.0
    annual_heat_J = target_W * seconds_per_year
    annual_heat_TWh = annual_heat_J / 3.6e15
    annual_salt_in_kt = m_dot_salt * seconds_per_year / 1e6
    annual_salt_out_kt = m_dot_salt_out * seconds_per_year / 1e6
    annual_water_kt = m_dot_water * seconds_per_year / 1e6

    return DischargeResult(
        P_heat_W=target_W,
        m_dot_salt_in=m_dot_salt,
        m_dot_water_consumed=m_dot_water,
        m_dot_salt_out=m_dot_salt_out,
        annual_heat_TWh=annual_heat_TWh,
        annual_salt_in_kt=annual_salt_in_kt,
        annual_salt_out_kt=annual_salt_out_kt,
        annual_water_kt=annual_water_kt,
    )

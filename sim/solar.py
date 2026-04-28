"""Solar charging field model.

Implements the same energy balance as SolarChargingField.mo:

    q_abs    = eta_optical * I_solar * area
    q_loss   = U * area * (T_op - T_amb)
    q_useful = max(q_abs - q_loss, 0) * eta_chem
    dm_charged/dt = q_useful / e_density

The function `simulate_field_year` integrates this over a synthetic
diurnal-modulated annual DNI profile to produce annual charged-salt mass and
freshwater coproduction.
"""

from __future__ import annotations
import math
import numpy as np
from .chemistries import SaltChemistry


def diurnal_profile(t_hours: np.ndarray, peak_W_m2: float, latitude_deg: float = 28.0) -> np.ndarray:
    """Synthetic diurnal solar flux. Sinusoidal daylight, zero at night.
    Peak amplitude scaled to give the correct annual DNI integral when used
    with `peak_from_annual`. Includes a light seasonal modulation for the
    source-region operating range we care about.
    """
    day = (t_hours / 24.0) % 1.0
    sun_hours = 12.0 - 4.0 * abs(math.sin(math.radians(latitude_deg))) * np.cos(
        2 * np.pi * (t_hours / (365 * 24))
    )
    sun_hours = np.clip(sun_hours, 8.0, 14.0)
    rel = (day - (1 - sun_hours / 24) / 2) / (sun_hours / 24)
    flux = np.where((rel >= 0) & (rel <= 1), peak_W_m2 * np.sin(np.pi * rel), 0.0)
    season = 1.0 + 0.18 * np.cos(2 * np.pi * (t_hours / (365 * 24)) - np.pi / 4) \
             * (latitude_deg / 45.0)
    return flux * np.clip(season, 0.5, 1.5)


def peak_from_annual(annual_kWh_per_m2: float, latitude_deg: float = 28.0) -> float:
    """Solve for the peak W/m2 that yields the requested annual integral
    under our diurnal_profile model. We use a Monte-Carlo-free closed form:
    annual_J = peak * integral(sin) over (sun_hours/day * 365). With
    sun_hours ~ 11.5 for arid mid-latitude this gives:
        annual_kWh = peak * (2/pi) * sun_hours * 365 / 1000
    """
    sun_hours = 11.0 + 0.05 * (28.0 - latitude_deg)
    return annual_kWh_per_m2 * 1000.0 / ((2.0 / math.pi) * sun_hours * 365.0)


def simulate_field_year(
    chem: SaltChemistry,
    area_m2: float,
    annual_DNI_kWh_m2: float,
    T_amb_C: float,
    eta_optical: float,
    U_loss_W_m2_K: float,
    eta_chem: float,
    water_capture_fraction: float,
    T_op_K: float | None = None,
    latitude_deg: float = 28.0,
    n_steps: int = 8760,
    field_type: str = "auto",   # "pond" | "trough" | "tower" | "auto"
):
    """Integrate the solar charging energy balance over one year (hourly).

    For passive ponds, losses are q_loss = U * area * (T_op - T_amb), gated
    on positive net absorption. For concentrating fields the loss term is
    instead the standard linear thermal-efficiency form
        eta_thermal(I, T) = eta_optical - k * (T_op - T_amb) / I
    where k is an effective heat-loss coefficient at the receiver. Receiver
    losses scale with (T - T_amb), not with field aperture area.

    Returns dict of annual aggregates plus full timeseries (hourly).
    """
    if T_op_K is None:
        T_op_K = chem.T_charge_full_K
    T_amb_K = T_amb_C + 273.15
    dT = max(T_op_K - T_amb_K, 0.0)

    if field_type == "auto":
        if not chem.needs_csp:
            field_type = "pond"
        elif T_op_K > 700.0:
            field_type = "tower"
        else:
            field_type = "trough"

    t_h = np.linspace(0.0, 8760.0, n_steps, endpoint=False)
    peak = peak_from_annual(annual_DNI_kWh_m2, latitude_deg)
    I = diurnal_profile(t_h, peak, latitude_deg)

    if field_type == "pond":
        q_abs = eta_optical * I * area_m2
        q_loss = U_loss_W_m2_K * area_m2 * dT
        q_useful = np.maximum(q_abs - q_loss, 0.0) * eta_chem
    else:
        # CSP receiver: linear efficiency form.
        # k = effective receiver heat-loss coefficient (W/m2/K at aperture)
        # Trough: k ~ 0.7;  Tower: k ~ 0.45 (lower because of evacuated
        # receiver + higher optical concentration).
        k = 0.7 if field_type == "trough" else 0.45
        with np.errstate(divide="ignore", invalid="ignore"):
            eta_th = np.where(I > 50.0,
                              np.maximum(eta_optical - k * dT / I, 0.0),
                              0.0)
        q_useful = eta_th * I * area_m2 * eta_chem

    e_density_J_per_kg = chem.energy_density_kJ_per_kg * 1000.0
    dt = 3600.0  # s per hourly step
    m_charged = np.cumsum(q_useful * dt / e_density_J_per_kg)
    water_kg_per_kg = chem.m_water_per_kg_salt
    m_water = water_capture_fraction * m_charged * water_kg_per_kg

    annual_charge_J = float(np.sum(q_useful) * dt)
    annual_irradiance_J = float(np.sum(I * area_m2) * dt)

    return {
        "t_h": t_h,
        "I_W_m2": I,
        "q_useful_W": q_useful,
        "m_charged_kg": m_charged,
        "m_freshwater_kg": m_water,
        "annual_charged_kg": float(m_charged[-1]),
        "annual_freshwater_kg": float(m_water[-1]),
        "annual_charge_GJ": annual_charge_J / 1e9,
        "annual_DNI_GJ": annual_irradiance_J / 1e9,
        "solar_to_chem_efficiency": annual_charge_J / max(annual_irradiance_J, 1.0),
        "T_op_K": T_op_K,
    }

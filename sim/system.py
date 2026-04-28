"""Integrated system model.

Combines solar charging, maritime transport, and district-heating discharge
into an annual material/energy/economic balance for a single source-destination
pair.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from .chemistries import SaltChemistry, CHEMISTRIES
from .routes import Route, ROUTES
from .solar import simulate_field_year
from .transport import simulate_voyage
from .discharge import simulate_plant


@dataclass
class SystemResult:
    chem: str
    route: str
    plant_capacity_MWth: float

    # Solar field
    pond_area_km2: float
    solar_to_chem_efficiency: float
    annual_charge_TWh: float
    annual_freshwater_Mm3: float

    # Transport
    voyages_per_ship_per_year: float
    ships_required: int
    cargo_consumed_fraction: float

    # Discharge
    annual_heat_delivered_TWh: float
    annual_salt_throughput_kt: float

    # Round-trip
    round_trip_thermal_efficiency: float
    freshwater_per_MWh_m3: float

    # Economics
    capex_source_M_USD: float
    capex_dest_M_USD: float
    capex_ships_M_USD: float
    salt_inventory_M_USD: float
    annual_opex_M_USD: float
    LCOH_USD_per_MWh: float
    payback_year: float

    # Carbon
    annual_avoided_CO2_kt: float
    embodied_CO2_kt: float
    net_avoided_CO2_kt_per_yr: float
    co2_payback_years: float


# ---------------------- Economic & technical reference assumptions ---------------------- #

# All figures are deliberately conservative midpoints. They are exposed so a
# user can override per-call.
DEFAULTS = dict(
    # Source-side capex per m2 of charging field aperture
    pond_capex_USD_m2=18.0,         # passive pond + cover + condenser ductwork
    csp_capex_USD_m2=180.0,         # linear-Fresnel-grade CSP at scale
    tower_capex_USD_m2=240.0,       # tower CSP for >700 K chemistries
    # BoP at source: handling, ports, condensate water plant
    source_BoP_per_GW_th=120.0e6,   # USD per GW-thermal of equiv export capacity
    # Hydration plant capex per MW-th delivered
    dest_capex_USD_per_MWth=420.0e3,
    # Autonomous wind-primary cargo vessel (Ladon-class).
    # Capex premium (~1.5x) over a comparable conventional handysize covers
    # wing-sail rig, autonomy stack, sensor/comms, and certification overhead.
    # Vendor-specific number should replace this once Ladon engagement happens.
    ship_capex_M_USD=60.0,
    ship_lifetime_yr=25.0,
    # OPEX as fraction of capex (annual). Lower than conventional bulker
    # because autonomous = zero crew opex (~$1M/yr/ship saved on a handysize).
    opex_fraction=0.030,
    # Salt make-up rate per cycle (replaces degradation)
    makeup_fraction_per_cycle=0.001,
    # Carbon intensities for embodied capex (very rough)
    embodied_CO2_per_USD_capex_t_per_M=120.0,
    # Discount rate for LCOH
    discount_rate=0.07,
    # Project life
    project_life_yr=25.0,
)


def select_charge_capex(chem: SaltChemistry) -> float:
    if not chem.needs_csp:
        return DEFAULTS["pond_capex_USD_m2"]
    if chem.T_charge_full_K >= 673.0:  # need tower for >400 C
        return DEFAULTS["tower_capex_USD_m2"]
    return DEFAULTS["csp_capex_USD_m2"]


def system_efficiency_components(chem: SaltChemistry, voyage):
    """Return the multiplicative chain of round-trip efficiencies."""
    # Solar -> chemical (computed from solar field sim and embedded above)
    # Cargo consumed during transport (out + return cargo-as-fuel)
    transport_loss = voyage.cargo_consumed_fraction
    # Reactor + distribution
    reactor_chain = 0.92 * 0.93
    return transport_loss, reactor_chain


def simulate_system(
    chem_key: str,
    route_key: str,
    plant_capacity_MWth: float = 1000.0,
    seasonal_load_factor: float = 0.50,
    target_pond_area_km2: float | None = None,
    eta_optical: float | None = None,
    U_loss_W_m2_K: float = 4.5,
    eta_chem: float | None = None,
    water_capture_fraction: float | None = None,
    wind_assist_fraction: float = 1.0,           # autonomous wind-primary
    cargo_dwt_t: float = 35000.0,
    cruise_speed_kn: float = 7.0,                # autonomous wind, slower than 10 kn diesel
    overrides: dict | None = None,
) -> SystemResult:
    chem = CHEMISTRIES[chem_key]
    route = ROUTES[route_key]
    d = dict(DEFAULTS)
    if overrides:
        d.update(overrides)

    # Sensible defaults that depend on chemistry
    if eta_optical is None:
        eta_optical = 0.55 if not chem.needs_csp else (
            0.62 if chem.T_charge_full_K < 700 else 0.55
        )
    if eta_chem is None:
        eta_chem = 0.80 if not chem.needs_csp else 0.85
    if water_capture_fraction is None:
        water_capture_fraction = 0.85 if not chem.needs_csp else 0.55

    # Discharge: figure out salt mass flow needed
    plant = simulate_plant(
        chem=chem,
        plant_capacity_MWth=plant_capacity_MWth,
        seasonal_load_factor=seasonal_load_factor,
        T_water_in_C=route.ambient_T_dest_winter_C,
    )
    annual_salt_in_kt = plant.annual_salt_in_kt

    # Voyage: assume cycle days drive ship count
    voyage = simulate_voyage(
        chem=chem,
        distance_km=route.distance_km,
        cargo_dwt_t=cargo_dwt_t,
        cruise_speed_kn=cruise_speed_kn,
        wind_assist_fraction=wind_assist_fraction,
    )
    voyages_per_ship_per_year = 365.0 / voyage.cycle_days
    salt_per_voyage_t = cargo_dwt_t * (1.0 - voyage.cargo_consumed_fraction)
    annual_voyages_required = annual_salt_in_kt * 1000.0 / salt_per_voyage_t
    ships_required = max(1, int(round(annual_voyages_required / voyages_per_ship_per_year + 0.49)))

    # Solar field: size to deliver the required charged-salt tonnage at source,
    # accounting for cargo lost as ship fuel.
    annual_salt_required_at_source_kt = annual_salt_in_kt / max(1.0 - voyage.cargo_consumed_fraction, 0.05)

    # Iterate on area so that annual_charged_kg matches required.
    if target_pond_area_km2 is None:
        # First-pass area sizing using closed-form annual energy balance.
        # Net flux at peak DNI minus losses; integrated with the diurnal solver.
        # We start from a guess and rely on the solver to true it up.
        guess_km2 = 5.0 * (annual_salt_in_kt / 5000.0) * (chem.energy_density_kWh_per_t / 200.0) ** -1
        guess_km2 *= (2400.0 / max(route.DNI_kWh_per_m2_yr, 1500.0))
        guess_km2 = max(0.1, guess_km2)
        converged = False
        for _ in range(20):
            sol = simulate_field_year(
                chem=chem,
                area_m2=guess_km2 * 1e6,
                annual_DNI_kWh_m2=route.DNI_kWh_per_m2_yr,
                T_amb_C=route.ambient_T_source_C,
                eta_optical=eta_optical,
                U_loss_W_m2_K=U_loss_W_m2_K,
                eta_chem=eta_chem,
                water_capture_fraction=water_capture_fraction,
            )
            produced_kt = sol["annual_charged_kg"] / 1e6
            if produced_kt < 1e-6 or guess_km2 > 1e5:
                # Field cannot operate at this T/DNI combination — flag as
                # infeasible. Caller will surface as NaN LCOH.
                guess_km2 = float("nan")
                break
            ratio = annual_salt_required_at_source_kt / produced_kt
            guess_km2 *= ratio
            if abs(ratio - 1.0) < 0.01:
                converged = True
                break
        pond_area_km2 = guess_km2
        sol_final = sol
    else:
        pond_area_km2 = target_pond_area_km2
        sol_final = simulate_field_year(
            chem=chem,
            area_m2=pond_area_km2 * 1e6,
            annual_DNI_kWh_m2=route.DNI_kWh_per_m2_yr,
            T_amb_C=route.ambient_T_source_C,
            eta_optical=eta_optical,
            U_loss_W_m2_K=U_loss_W_m2_K,
            eta_chem=eta_chem,
            water_capture_fraction=water_capture_fraction,
        )

    # Round-trip efficiency
    eta_transport = 1.0 - voyage.cargo_consumed_fraction  # cargo lost as fuel
    eta_reactor_chain = 0.92 * 0.93
    annual_charge_TWh = sol_final["annual_charge_GJ"] * 1e9 / 3.6e15
    annual_heat_TWh = plant.annual_heat_TWh
    round_trip = annual_heat_TWh / max(annual_charge_TWh, 1e-9)

    # Freshwater
    annual_freshwater_kg = sol_final["annual_freshwater_kg"]
    annual_freshwater_m3 = annual_freshwater_kg / 1000.0
    fw_per_MWh = annual_freshwater_m3 / max(annual_heat_TWh * 1e6, 1.0)

    # Economics
    charge_capex_USD_m2 = select_charge_capex(chem)
    capex_field_M = pond_area_km2 * 1e6 * charge_capex_USD_m2 / 1e6
    capex_source_BoP_M = (plant_capacity_MWth / 1000.0) * d["source_BoP_per_GW_th"] / 1e6
    capex_source_M = capex_field_M + capex_source_BoP_M
    capex_dest_M = plant_capacity_MWth * d["dest_capex_USD_per_MWth"] / 1e6
    capex_ships_M = ships_required * d["ship_capex_M_USD"]
    # Salt inventory: 2 voyages worth in transit + 1 at each end
    inventory_t = cargo_dwt_t * (ships_required * 2 + 2)
    salt_inventory_M = inventory_t * chem.cost_per_ton / 1e6

    capex_total_M = capex_source_M + capex_dest_M + capex_ships_M + salt_inventory_M
    annual_opex_M = capex_total_M * d["opex_fraction"] + (
        annual_salt_in_kt * 1000.0 * d["makeup_fraction_per_cycle"] *
        chem.cost_per_ton / 1e6
    )

    # LCOH: levelized cost of heat over project life
    r = d["discount_rate"]
    n = d["project_life_yr"]
    crf = r * (1 + r) ** n / ((1 + r) ** n - 1)
    annual_capex_charge_M = capex_total_M * crf
    annual_total_cost_M = annual_capex_charge_M + annual_opex_M
    annual_heat_MWh = annual_heat_TWh * 1e6
    LCOH = annual_total_cost_M * 1e6 / max(annual_heat_MWh, 1.0)

    # Carbon
    avoided_CO2_kt = annual_heat_MWh * route.grid_carbon_kg_per_MWh / 1e6
    embodied_CO2_kt = capex_total_M * d["embodied_CO2_per_USD_capex_t_per_M"] / 1000.0
    net_kt = avoided_CO2_kt
    co2_payback_yr = embodied_CO2_kt / max(avoided_CO2_kt, 1e-9)

    payback_year = (capex_total_M * 1e6) / max(
        annual_heat_MWh * 60.0 - annual_opex_M * 1e6, 1.0
    )  # at 60 USD/MWh hypothetical sale price

    return SystemResult(
        chem=chem.short,
        route=route.name,
        plant_capacity_MWth=plant_capacity_MWth,
        pond_area_km2=pond_area_km2,
        solar_to_chem_efficiency=sol_final["solar_to_chem_efficiency"],
        annual_charge_TWh=annual_charge_TWh,
        annual_freshwater_Mm3=annual_freshwater_m3 / 1e6,
        voyages_per_ship_per_year=voyages_per_ship_per_year,
        ships_required=ships_required,
        cargo_consumed_fraction=voyage.cargo_consumed_fraction,
        annual_heat_delivered_TWh=annual_heat_TWh,
        annual_salt_throughput_kt=annual_salt_in_kt,
        round_trip_thermal_efficiency=round_trip,
        freshwater_per_MWh_m3=fw_per_MWh,
        capex_source_M_USD=capex_source_M,
        capex_dest_M_USD=capex_dest_M,
        capex_ships_M_USD=capex_ships_M,
        salt_inventory_M_USD=salt_inventory_M,
        annual_opex_M_USD=annual_opex_M,
        LCOH_USD_per_MWh=LCOH,
        payback_year=payback_year,
        annual_avoided_CO2_kt=avoided_CO2_kt,
        embodied_CO2_kt=embodied_CO2_kt,
        net_avoided_CO2_kt_per_yr=net_kt,
        co2_payback_years=co2_payback_yr,
    )

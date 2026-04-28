"""Geographic source-destination route property database.

Mirrors SolarSaltExport.Records.RouteProperties. Annual DNI and ambient
values are central estimates from open solar resource atlases (NSRDB / Global
Solar Atlas). Distances are typical maritime great-circle distances accounting
for Suez/Strait routing.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    name: str
    source_port: str
    destination_port: str
    distance_km: float
    DNI_kWh_per_m2_yr: float        # direct normal annual
    GHI_kWh_per_m2_yr: float        # global horizontal annual
    avg_wind_m_s: float
    heating_season_days: float
    grid_carbon_kg_per_MWh: float   # displaced primary heat carbon intensity
    seawater_T_C: float
    ambient_T_source_C: float
    ambient_T_dest_winter_C: float


ROUTES: dict[str, Route] = {
    "morocco_baltic": Route(
        name="Morocco -> Baltic",
        source_port="Dakhla / Tan Tan",
        destination_port="Gdansk / Rostock",
        distance_km=4000.0,
        DNI_kWh_per_m2_yr=2400.0,
        GHI_kWh_per_m2_yr=2100.0,
        avg_wind_m_s=8.5,
        heating_season_days=200.0,
        grid_carbon_kg_per_MWh=290.0,   # Polish CHP / coal mix displacement
        seawater_T_C=20.0,
        ambient_T_source_C=25.0,
        ambient_T_dest_winter_C=2.0,
    ),
    "tunisia_adriatic": Route(
        name="Tunisia -> Adriatic",
        source_port="Sfax / Gabes",
        destination_port="Trieste / Venice",
        distance_km=1700.0,
        DNI_kWh_per_m2_yr=2200.0,
        GHI_kWh_per_m2_yr=1900.0,
        avg_wind_m_s=6.5,
        heating_season_days=160.0,
        grid_carbon_kg_per_MWh=210.0,
        seawater_T_C=20.0,
        ambient_T_source_C=24.0,
        ambient_T_dest_winter_C=5.0,
    ),
    "egypt_blacksea": Route(
        name="Egypt -> Black Sea",
        source_port="Alexandria / Port Said",
        destination_port="Constanta / Burgas",
        distance_km=2300.0,
        DNI_kWh_per_m2_yr=2500.0,
        GHI_kWh_per_m2_yr=2200.0,
        avg_wind_m_s=7.5,
        heating_season_days=170.0,
        grid_carbon_kg_per_MWh=270.0,
        seawater_T_C=22.0,
        ambient_T_source_C=26.0,
        ambient_T_dest_winter_C=3.0,
    ),
    "atacama_southern_cone": Route(
        name="Atacama -> Southern Cone",
        source_port="Mejillones / Iquique",
        destination_port="Concepcion / Buenos Aires",
        distance_km=1800.0,
        DNI_kWh_per_m2_yr=3500.0,
        GHI_kWh_per_m2_yr=2400.0,
        avg_wind_m_s=8.0,
        heating_season_days=150.0,
        grid_carbon_kg_per_MWh=190.0,
        seawater_T_C=16.0,
        ambient_T_source_C=18.0,
        ambient_T_dest_winter_C=8.0,
    ),
    "namibia_nweurope": Route(
        name="Namibia -> NW Europe",
        source_port="Walvis Bay",
        destination_port="Hamburg / Rotterdam",
        distance_km=11500.0,
        DNI_kWh_per_m2_yr=3000.0,
        GHI_kWh_per_m2_yr=2300.0,
        avg_wind_m_s=8.5,
        heating_season_days=200.0,
        grid_carbon_kg_per_MWh=240.0,
        seawater_T_C=17.0,
        ambient_T_source_C=20.0,
        ambient_T_dest_winter_C=4.0,
    ),
    "australia_china": Route(
        name="Pilbara (AU) -> N. China",
        source_port="Port Hedland",
        destination_port="Tianjin / Qingdao",
        distance_km=8000.0,
        DNI_kWh_per_m2_yr=2900.0,
        GHI_kWh_per_m2_yr=2300.0,
        avg_wind_m_s=7.0,
        heating_season_days=150.0,
        grid_carbon_kg_per_MWh=350.0,   # coal-heavy
        seawater_T_C=24.0,
        ambient_T_source_C=28.0,
        ambient_T_dest_winter_C=-3.0,
    ),
}

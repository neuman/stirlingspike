within SolarSaltExport.Components;
model DistrictHeatPlant
  "Aggregator: HydrationReactor + buffer + heating load."

  parameter SolarSaltExport.Records.SaltChemistry chem;
  parameter Real plant_capacity_MWth = 100.0;
  parameter Real T_water_in_K = 283.15;
  parameter Real seasonal_load_factor = 0.55
    "Fraction of nameplate delivered as heat across the year, accounting for
     reduced shoulder-season load and short-term cycling.";

  HydrationReactor reactor(chem = chem, T_supply_K = chem.T_discharge_typ);

  Real annual_heat_delivered_TWh;
  Real annual_salt_in_kt;
  Real annual_salt_out_kt;
  Real annual_water_consumed_kt;

equation
  reactor.T_water_in = T_water_in_K;
  reactor.m_dot_salt_in = plant_capacity_MWth * 1.0e6 /
                          (chem.energy_density_kJ_per_kg * 1000.0)
                          * seasonal_load_factor;
  annual_heat_delivered_TWh = reactor.P_heat * 8760.0 / 1.0e6 / 1.0e6;
  annual_salt_in_kt  = reactor.m_dot_salt_in  * 31536000.0 / 1.0e6;
  annual_salt_out_kt = reactor.m_dot_salt_out * 31536000.0 / 1.0e6;
  annual_water_consumed_kt =
    reactor.m_dot_water_consumed * 31536000.0 / 1.0e6;
end DistrictHeatPlant;

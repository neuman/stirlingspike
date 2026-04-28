within SolarSaltExport.Components;
model BulkCarrier
  "Slow bulk carrier with wind-augmented + salt-hydration auxiliary propulsion.

   The model resolves a one-way leg to the integrated propulsion energy
   demand and the cargo fraction consumed for that demand.
  "

  parameter SolarSaltExport.Records.SaltChemistry chem;
  parameter Real distance_km = 3500.0;
  parameter Real cargo_dwt_t = 35000.0 "Deadweight cargo per voyage";
  parameter Real cruise_speed_kn = 10.0;
  parameter Real avg_wind_speed_m_s = 7.5;
  parameter Real wind_assist_fraction = 0.45
    "Fraction of propulsion energy supplied by wind sails / rotors at design
     condition. Values 0.2 (rotors only) -- 0.7 (sail-primary).";
  parameter Real eta_aux_engine = 0.30
    "Conversion efficiency from chemical heat-of-hydration to shaft power
     for an organic-Rankine or steam auxiliary drawing on stored salt energy.";
  parameter Real specific_resistance_kJ_per_t_km = 35.0
    "Specific propulsion energy demand per tonne-km at cruise speed for a
     handysize bulker (open literature, ~10 kn cruise).";

  // Outputs
  Real voyage_hours;
  Real propulsion_energy_GJ;
  Real wind_supplied_GJ;
  Real aux_supplied_GJ;
  Real cargo_consumed_t;
  Real cargo_consumed_fraction;

equation
  voyage_hours = distance_km / (cruise_speed_kn * 1.852);
  // Total propulsion energy needed for laden leg
  propulsion_energy_GJ = specific_resistance_kJ_per_t_km * cargo_dwt_t *
                          distance_km / 1.0e6;
  wind_supplied_GJ = wind_assist_fraction * propulsion_energy_GJ;
  aux_supplied_GJ = (1.0 - wind_assist_fraction) * propulsion_energy_GJ;
  // Cargo (charged salt) consumed to drive auxiliary engines:
  // (aux energy demand) / (eta * energy density of cargo)
  cargo_consumed_t = aux_supplied_GJ * 1000.0 /
                     (eta_aux_engine * chem.energy_density_kJ_per_kg);
  cargo_consumed_fraction = cargo_consumed_t / cargo_dwt_t;

  annotation(Documentation(info = "<html>
Voyage-resolved propulsion balance. The return (ballast) leg carries the
hydrated discharged salt; its propulsion is supplied by wind-only as the
hydrated form has near-zero usable chemical energy. The return leg is modeled
separately in the system aggregator.
</html>"));
end BulkCarrier;

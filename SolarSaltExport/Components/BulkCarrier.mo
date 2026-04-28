within SolarSaltExport.Components;
model BulkCarrier
  "Autonomous wind-primary cargo vessel (Ladon-class).

   Replaces the v0.1 cargo-as-fuel hybrid concept with a wind-only
   autonomous vessel. Propulsion energy is treated as a free environmental
   input; the dominant economic levers become cruise speed (which sets
   in-transit inventory cost), capex per ship, and weather-buffer time.
  "

  parameter SolarSaltExport.Records.SaltChemistry chem;
  parameter Real distance_km = 3500.0;
  parameter Real cargo_dwt_t = 35000.0 "Deadweight cargo per voyage";
  parameter Real cruise_speed_kn = 7.0
    "Average cruise speed under wind-only routing. Conservative midpoint for
     autonomous wing-sail or rotor-rigged vessels operating along seasonal
     trade-wind routes.";
  parameter Real avg_wind_speed_m_s = 7.5;
  parameter Real wind_assist_fraction = 1.0
    "Fraction of propulsion energy supplied by wind. = 1.0 for the
     autonomous-wind class.";
  parameter Real specific_resistance_kJ_per_t_km = 35.0
    "Specific propulsion energy demand per tonne-km at cruise speed
     (informational only; not debited against cargo for wind-only vessels).";
  parameter Integer crew_count = 0
    "= 0 for autonomous vessels; eliminates ~$1M/yr/ship crew opex.";
  parameter Real weather_buffer_days = 4.0
    "Wait-for-wind allowance per voyage. Higher than for crewed bulkers.";

  // Outputs
  Real voyage_hours;
  Real propulsion_energy_GJ;
  Real wind_supplied_GJ;
  Real aux_supplied_GJ "Always zero for the wind-only class";
  Real cargo_consumed_t "Always zero for the wind-only class";
  Real cargo_consumed_fraction "Always zero for the wind-only class";

equation
  voyage_hours = distance_km / (cruise_speed_kn * 1.852);
  propulsion_energy_GJ = specific_resistance_kJ_per_t_km * cargo_dwt_t *
                          distance_km / 1.0e6;
  wind_supplied_GJ = wind_assist_fraction * propulsion_energy_GJ;
  aux_supplied_GJ = 0.0;
  cargo_consumed_t = 0.0;
  cargo_consumed_fraction = 0.0;

  annotation(Documentation(info = "<html>
Wind-only autonomous cargo vessel (Ladon-class). The return (ballast) leg
carries the hydrated discharged salt and is also wind-propelled. Voyage time
becomes the binding economic variable, not propulsion energy.
</html>"));
end BulkCarrier;

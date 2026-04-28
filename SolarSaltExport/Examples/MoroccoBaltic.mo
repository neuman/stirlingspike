within SolarSaltExport.Examples;
model MoroccoBaltic
  "Reference scenario: Morocco/W.Sahara source -> Baltic ports.
   1 GW-thermal export-equivalent. Used as primary case in concept paper."
  extends Modelica.Icons.Example;

  parameter SolarSaltExport.Records.SaltChemistry chem =
    SolarSaltExport.Chemistries.CaCl2_full;

  SolarSaltExport.Components.SolarChargingField charging(
    chem = chem,
    area_m2 = 7.5e6,
    eta_optical = 0.62,
    eta_chem = 0.85,
    T_op_K = chem.T_charge_full);

  SolarSaltExport.Components.BulkCarrier ship(
    chem = chem,
    distance_km = 4000.0,
    cargo_dwt_t = 35000.0,
    cruise_speed_kn = 10.0,
    wind_assist_fraction = 0.45);

  SolarSaltExport.Components.DistrictHeatPlant plant(
    chem = chem,
    plant_capacity_MWth = 1000.0,
    T_water_in_K = 278.15,
    seasonal_load_factor = 0.50);

  // Synthetic forcing: average DNI profile (W/m2) and ambient T (K)
equation
  charging.I_solar = 270.0;  // W/m2 annual average for Sahara latitude
  charging.T_amb   = 298.15;
end MoroccoBaltic;

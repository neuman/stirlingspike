within SolarSaltExport.Records;
record RouteProperties
  "Geographic route between source (solar) and destination (heating) ports"

  parameter String name = "unnamed";
  parameter String source_port = "";
  parameter String destination_port = "";
  parameter Real distance_km = 0.0
    "Great-circle ish sea distance between ports";
  parameter Real DNI_annual_kWh_per_m2_yr = 0.0
    "Annual direct normal irradiance at the source site";
  parameter Real GHI_annual_kWh_per_m2_yr = 0.0
    "Annual global horizontal irradiance at the source site";
  parameter Real avg_wind_speed_m_per_s = 7.0
    "Annual average wind speed along the route at 10 m";
  parameter Real heating_season_days = 180.0
    "Days per year the destination operates a heating load";
  parameter Real grid_carbon_intensity_kg_per_MWh = 0.0
    "Average heat-equivalent grid carbon intensity at the destination
     (combined CHP / boiler displacement reference)";
  parameter Real source_seawater_temp_C = 18.0;
  parameter Real ambient_T_source_K = 298.15;
  parameter Real ambient_T_dest_winter_K = 273.15;

  annotation(Documentation(info = "<html>
Route record for a source/destination pair. Used by the system model to
parameterize charge field, transport, and discharge models simultaneously.
</html>"));
end RouteProperties;

model SimpleSystem
  // Parameters for the solar panel
  parameter Real panelArea = 1.0 "Area of the solar panel in m^2";
  parameter Real panelMass = 20.0 "Mass of the solar panel in kg";
  parameter Real panelSpecificHeat = 900.0 "Specific heat capacity of panel (aluminum) in J/(kg.K)";
  parameter Real panelAbsorptivity = 0.95 "Solar absorptivity of the panel";
  parameter Real panelEmissivity = 0.85 "Thermal emissivity of the panel";
  parameter Real panelThermalConductivity = 237.0 "Thermal conductivity of panel (aluminum) in W/(m.K)";
  parameter Real panelThickness = 0.005 "Thickness of the panel in m";
  parameter Real panelEfficiency = 0.18 "Solar panel energy conversion efficiency";
  
  
  // Parameters for the vessel
  parameter Real vesselVolume = 0.1 "Volume of the vessel in m^3";
  parameter Real vesselWallArea = 1.5 "Surface area of the vessel wall in m^2";
  parameter Real vesselWallThickness = 0.01 "Thickness of the vessel wall in m";
  parameter Real vesselWallThermalConductivity = 16.0 "Thermal conductivity of vessel wall (steel) in W/(m.K)";
  parameter Real contactArea = 0.2 "Contact area between panel and vessel in m^2";
  
  // Parameters for the glycol-water mixture (25% glycol)
  parameter Real mixtureDensity = 1038.0 "Density of 25% glycol-water mixture in kg/m^3";
  parameter Real mixtureSpecificHeat = 3740.0 "Specific heat capacity of 25% glycol-water mixture in J/(kg.K)";
  parameter Real mixtureVolume = 0.096 "Volume of the mixture (96% of vessel) in m^3";
  parameter Real mixtureMass = mixtureDensity*mixtureVolume "Mass of the mixture in kg ~100 kg";
  
  // NEW: Parameters for the buried cylinder
  parameter Real cylinderDiameter = 0.6096 "Cylinder diameter (24 inches) in m";
  parameter Real cylinderLength = 10.0 "Cylinder length in m";
  parameter Real cylinderRadius = cylinderDiameter/2 "Cylinder radius in m";
  parameter Real cylinderInsulationThickness = 0.05 "Insulation thickness (5cm) in m";
  parameter Real cylinderInsulationLength = 9.0 "Length of insulated portion in m";
  parameter Real cylinderExposedLength = cylinderLength - cylinderInsulationLength "Length of exposed portion in m";
  parameter Real cylinderVolume = Modelica.Constants.pi * cylinderRadius^2 * cylinderLength "Volume of cylinder in m^3";
  parameter Real cylinderMixtureVolume = 0.96 * cylinderVolume "Volume of mixture in cylinder (96%) in m^3";
  parameter Real cylinderMixtureMass = mixtureDensity * cylinderMixtureVolume "Mass of mixture in cylinder in kg";
  parameter Real cylinderWallThickness = 0.01 "Thickness of cylinder wall in m";
  parameter Real cylinderWallThermalConductivity = 16.0 "Thermal conductivity of cylinder wall (steel) in W/(m.K)";
  parameter Real cylinderInsulationThermalConductivity = 0.035 "Thermal conductivity of foam insulation in W/(m.K)";
  parameter Real cylinderInsulatedSurfaceArea = 2 * Modelica.Constants.pi * cylinderRadius * cylinderInsulationLength "Surface area of insulated portion in m^2";
  parameter Real cylinderExposedSurfaceArea = 2 * Modelica.Constants.pi * cylinderRadius * cylinderExposedLength "Surface area of exposed portion in m^2";
  parameter Real cylinderBottomArea = Modelica.Constants.pi * cylinderRadius^2 "Bottom area of cylinder in m^2";
  parameter Real cylinderTopArea = cylinderBottomArea "Top area of cylinder in m^2";
  parameter Real contactAreaCylinderVessel = 0.2 "Contact area between cylinder and vessel in m^2";
  parameter Real contactConductanceCylinderVessel = 200.0 "Thermal contact conductance between cylinder and vessel in W/(m^2.K)";
  parameter Real groundTemperature = (55.0 + 459.67) * 5/9 "Ground temperature (55F) in Kelvin";
  parameter Real groundThermalConductivity = 1.5 "Thermal conductivity of ground soil in W/(m.K)";
  parameter Real cylinderGroundContactConductance = 15.0 "Thermal contact conductance between cylinder and ground in W/(m^2.K)";
  
  // Environment parameters
  parameter Real stefanBoltzmannConstant = 5.67e-8 "Stefan-Boltzmann constant in W/(m^2.K^4)";
  parameter Real panelConvectionCoefficient = 12.0 "Convective heat transfer coefficient for panel in W/(m^2.K)";
  parameter Real vesselConvectionCoefficient = 8.0 "Convective heat transfer coefficient for vessel in W/(m^2.K)";
  parameter Real contactConductance = 200.0 "Thermal contact conductance between panel and vessel in W/(m^2.K)";
  
  // Import CombiTimeTable for reading external data
  import Modelica.Blocks.Sources.CombiTimeTable;
  
  // CombiTimeTable for reading ambient temperature and solar irradiance from CSV
  // Updated to match the specific CSV format with row numbers and # headers
  // Replace your CombiTimeTable with this implementation
  Modelica.Blocks.Sources.CombiTimeTable weatherData(
    tableOnFile = false,  // Use inline data instead of file
    table = [
      0, 15.0, 0.0;
      3600, 14.2, 0.0;
      7200, 13.8, 0.0;
      10800, 13.5, 0.0;
      14400, 13.0, 0.0;
      18000, 12.8, 0.0;
      21600, 13.2, 50.0;
      25200, 14.5, 250.0;
      28800, 16.2, 450.0;
      32400, 18.5, 650.0;
      36000, 20.6, 850.0;
      39600, 23.0, 950.0;
      43200, 25.5, 1000.0;
      46800, 26.8, 950.0;
      50400, 27.2, 850.0;
      54000, 26.5, 650.0;
      57600, 25.0, 450.0;
      61200, 23.2, 250.0;
      64800, 21.0, 100.0;
      68400, 19.5, 0.0;
      72000, 18.2, 0.0;
      75600, 17.4, 0.0;
      79200, 16.5, 0.0;
      82800, 15.8, 0.0;
      86400, 15.2, 0.0
    ],
    columns = {2, 3},  // Keep the column references consistent
    smoothness = Modelica.Blocks.Types.Smoothness.LinearSegments);
  
  // Variables: Temperatures
  Real panelTemperature(start=293.15, fixed=true) "Initial temperature of the solar panel in K";
  Real mixtureTemperature(start=293.15, fixed=true) "Initial temperature of the glycol-water mixture in K";
  Real cylinderMixtureTemperature(start=285.93, fixed=true) "Initial temperature of the cylinder mixture in K (starting at mean of ambient and ground)";
  Real ambientTemperature "Ambient temperature in K";
  Real solarIrradiance "Solar irradiance in W/m^2";
  
  // Variables: Heat flows
  Real totalSolarPower "Total solar power on panel in W";
  Real electricalPowerOutput "Electrical power output from panel in W";
  Real thermalPowerAbsorbed "Thermal power absorbed by panel in W";
  Real radiativeLossPanel "Radiative heat loss from panel in W";
  Real convectiveLossPanel "Convective heat loss from panel in W";
  Real heatTransferPanelToVessel "Heat transfer from panel to vessel in W";
  Real heatLossVessel "Heat loss from vessel to environment in W";
  
  // NEW: Variables for cylinder heat flows
  Real heatTransferVesselToCylinder "Heat transfer from vessel to cylinder in W";
  Real heatTransferCylinderToGround "Heat transfer from cylinder to ground in W";
  Real heatLossCylinderInsulated "Heat loss through insulated portion of cylinder in W";
  Real heatLossCylinderExposed "Heat loss through exposed portion of cylinder in W";
  
equation
  // Get ambient temperature and solar irradiance from CSV
  ambientTemperature = weatherData.y[1] + 273.15; // Convert from C to K
  solarIrradiance = weatherData.y[2];
  
  // Calculate solar power and energy conversion
  totalSolarPower = solarIrradiance * panelArea;
  electricalPowerOutput = totalSolarPower * panelEfficiency;
  thermalPowerAbsorbed = totalSolarPower * (panelAbsorptivity - panelEfficiency);
  
  // Heat transfer from panel to vessel
  heatTransferPanelToVessel = contactConductance * contactArea * (panelTemperature - mixtureTemperature);
  
  // Heat losses from panel to environment
  radiativeLossPanel = panelEmissivity * stefanBoltzmannConstant * panelArea * (panelTemperature^4 - ambientTemperature^4);
  convectiveLossPanel = panelConvectionCoefficient * panelArea * (panelTemperature - ambientTemperature);
  
  // Heat loss from vessel to environment
  heatLossVessel = vesselConvectionCoefficient * vesselWallArea * (mixtureTemperature - ambientTemperature);
  
  // NEW: Heat transfer from vessel to cylinder
  heatTransferVesselToCylinder = contactConductanceCylinderVessel * contactAreaCylinderVessel * (mixtureTemperature - cylinderMixtureTemperature);
  
  // NEW: Heat transfer from cylinder to ground (at bottom)
  heatTransferCylinderToGround = cylinderGroundContactConductance * cylinderBottomArea * (cylinderMixtureTemperature - groundTemperature);
  
  // NEW: Heat loss through insulated portion of cylinder
  // Using composite resistance for insulated wall: R = R_wall + R_insulation
  heatLossCylinderInsulated = cylinderInsulatedSurfaceArea * 
                             (cylinderMixtureTemperature - ambientTemperature) / 
                             (cylinderWallThickness/cylinderWallThermalConductivity + 
                              cylinderInsulationThickness/cylinderInsulationThermalConductivity);
  
  // NEW: Heat loss through exposed portion of cylinder
  heatLossCylinderExposed = vesselConvectionCoefficient * cylinderExposedSurfaceArea * 
                           (cylinderMixtureTemperature - ambientTemperature);
  
  // Energy balance for the panel
  panelMass * panelSpecificHeat * der(panelTemperature) = 
    thermalPowerAbsorbed - radiativeLossPanel - convectiveLossPanel - heatTransferPanelToVessel;
  
  // Energy balance for the glycol-water mixture in the vessel
  mixtureMass * mixtureSpecificHeat * der(mixtureTemperature) = 
    heatTransferPanelToVessel - heatLossVessel - heatTransferVesselToCylinder;
  
  // NEW: Energy balance for the glycol-water mixture in the cylinder
  cylinderMixtureMass * mixtureSpecificHeat * der(cylinderMixtureTemperature) = 
    heatTransferVesselToCylinder - heatTransferCylinderToGround - 
    heatLossCylinderInsulated - heatLossCylinderExposed;
  
  annotation(experiment(StartTime = 0, StopTime = 86400, Tolerance = 1e-6, Interval = 3600));
end SimpleSystem;
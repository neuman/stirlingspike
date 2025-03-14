model SimpleSystem
  // Parameters for the solar panel
  parameter Real panelArea = 1.0 "Area of the solar panel in m^2";
  parameter Real panelMass = 20.0 "Mass of the solar panel in kg";
  parameter Real panelSpecificHeat = 900.0 "Specific heat capacity of panel (aluminum) in J/(kg.K)";
  parameter Real panelAbsorptivity = 0.95 "Solar absorptivity of the panel";
  parameter Real panelEmissivity = 0.85 "Thermal emissivity of the panel";
  parameter Real panelThermalConductivity = 237.0 "Thermal conductivity of panel (aluminum) in W/(m.K)";
  parameter Real panelThickness = 0.005 "Thickness of the panel in m";
  parameter Real panelEfficiency = 0.18 "Solar panel energy conversion efficiency at standard test conditions (25°C)";
  parameter Real temperatureCoefficient = -0.004 "Temperature coefficient of efficiency (%/°C)";
  parameter Real referenceTemperature = 298.15 "Reference temperature (25°C) in K";
  
  
  // Parameters for the vessel
  parameter Real vesselVolume = 0.1 "Volume of the vessel in m^3";
  parameter Real vesselWallArea = 1.5 "Surface area of the vessel wall in m^2";
  parameter Real vesselWallThickness = 0.01 "Thickness of the vessel wall in m";
  parameter Real vesselWallThermalConductivity = 16.0 "Thermal conductivity of vessel wall (steel) in W/(m.K)";
  parameter Real contactArea = 0.4 "Contact area between panel and vessel in m^2";
  parameter Real stirlingContactArea = 0.15 "Contact area between vessel and Stirling engine in m^2";
  parameter Real vesselInsulationThickness = 0.1 "Thickness of vessel insulation in m";
  parameter Real vesselInsulationThermalConductivity = 0.035 "Thermal conductivity of vessel insulation in W/(m.K)";
  parameter Real vesselExposedArea = vesselWallArea - contactArea - stirlingContactArea "Area of vessel exposed to environment in m^2";
  parameter Real vesselInsulatedArea = vesselWallArea - vesselExposedArea "Area of vessel that is insulated in m^2";
  
  // Parameters for the glycol-water mixture (25% glycol)
  parameter Real mixtureDensity = 1038.0 "Density of 25% glycol-water mixture in kg/m^3";
  parameter Real mixtureSpecificHeat = 3740.0 "Specific heat capacity of 25% glycol-water mixture in J/(kg.K)";
  parameter Real mixtureVolume = 0.096 "Volume of the mixture (96% of vessel) in m^3";
  parameter Real mixtureMass = mixtureDensity*mixtureVolume "Mass of the mixture in kg ~100 kg";
  
  // Parameters for the buried cylinder
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
  
  // NEW: Parameters for the Stirling engine
  parameter Real stirlingEngineEfficiency = 0.5 "Efficiency of the Stirling engine";
  parameter Real stirlingMinimumTemperatureDifference = 10.0 "Minimum temperature difference for Stirling engine operation in K";
  parameter Real stirlingHeatTransferCoefficient = 200.0 "Heat transfer coefficient for Stirling engine in W/(m^2.K)";
  parameter Real stirlingContactAreaHot = 0.3 "Contact area between vessel and Stirling engine (hot side) in m^2";
  parameter Real stirlingContactAreaCold = 0.3 "Contact area between cylinder and Stirling engine (cold side) in m^2";
  parameter Real stirlingCarnotFactor = 0.4 "Factor of ideal Carnot efficiency achievable";
  
  // Environment parameters
  parameter Real stefanBoltzmannConstant = 5.67e-8 "Stefan-Boltzmann constant in W/(m^2.K^4)";
  parameter Real panelConvectionCoefficient = 12.0 "Convective heat transfer coefficient for panel in W/(m^2.K)";
  parameter Real vesselConvectionCoefficient = 3.0 "Convective heat transfer coefficient for vessel in W/(m^2.K)";
  parameter Real contactConductance = 500.0 "Thermal contact conductance between panel and vessel in W/(m^2.K)";
  
  // Import CombiTimeTable for reading external data
  import Modelica.Blocks.Sources.CombiTimeTable;
  
  // CombiTimeTable for reading ambient temperature and solar irradiance from CSV
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
  
  // Variables for cylinder heat flows
  Real heatTransferCylinderToGround "Heat transfer from cylinder to ground in W";
  Real heatLossCylinderInsulated "Heat loss through insulated portion of cylinder in W";
  Real heatLossCylinderExposed "Heat loss through exposed portion of cylinder in W";
  
  // NEW: Variables for Stirling engine heat flows and power
  Real stirlingTemperatureDifference "Temperature difference between hot and cold sides of the Stirling engine in K";
  Real stirlingHeatFlowHot "Heat flow from the vessel (hot side) to the Stirling engine in W";
  Real stirlingHeatFlowCold "Heat flow from the Stirling engine to the cylinder (cold side) in W";
  Real stirlingPowerOutput "Electrical power output from the Stirling engine in W";
  Real stirlingCarnotEfficiency "Carnot efficiency based on temperature difference";
  Real stirlingActualEfficiency "Actual efficiency of the Stirling engine";
  Real stirlingTotalPowerOutput "Total electrical power output from both solar panel and Stirling engine in W";
  
  // Simple function to smooth transitions
  function smoothStep
    input Real x;
    input Real x1;
    input Real y1;
    input Real x2;
    input Real y2;
    output Real y;
  algorithm
    y := y1 + (y2 - y1) * max(0, min(1, (x - x1)/(x2 - x1)));
  end smoothStep;
  
equation
  // Get ambient temperature and solar irradiance from weather data
  ambientTemperature = weatherData.y[1] + 273.15;  // Convert from Celsius to Kelvin
  solarIrradiance = weatherData.y[2];
  
  // Calculate solar power and energy conversion
  totalSolarPower = solarIrradiance * panelArea;
  electricalPowerOutput = totalSolarPower * panelEfficiency * (1 + temperatureCoefficient * (panelTemperature - referenceTemperature));
  thermalPowerAbsorbed = totalSolarPower * (panelAbsorptivity - panelEfficiency);
  
  // Heat transfer from panel to vessel (direct contact)
  heatTransferPanelToVessel = contactConductance * contactArea * (panelTemperature - mixtureTemperature);
  
  // Heat losses from panel to environment (with smoothing for radiative term)
  radiativeLossPanel = panelEmissivity * stefanBoltzmannConstant * panelArea * 
                      (max(panelTemperature, ambientTemperature)^4 - min(panelTemperature, ambientTemperature)^4);
  convectiveLossPanel = panelConvectionCoefficient * panelArea * (panelTemperature - ambientTemperature);
  
  // Heat loss from vessel to environment (now with insulation)
  heatLossVessel = vesselConvectionCoefficient * vesselExposedArea * (mixtureTemperature - ambientTemperature) +
                   vesselInsulatedArea * (mixtureTemperature - ambientTemperature) / 
                   (vesselWallThickness/vesselWallThermalConductivity + 
                    vesselInsulationThickness/vesselInsulationThermalConductivity);
  
  // Stirling engine calculations with smoothing
  stirlingTemperatureDifference = max(0, mixtureTemperature - cylinderMixtureTemperature);
  
  // Theoretical Carnot efficiency with smoothing
  stirlingCarnotEfficiency = smoothStep(
    stirlingTemperatureDifference,
    stirlingMinimumTemperatureDifference,
    0,
    stirlingMinimumTemperatureDifference + 5,
    1 - cylinderMixtureTemperature/mixtureTemperature
  );
  
  // Actual achievable efficiency
  stirlingActualEfficiency = min(stirlingEngineEfficiency, stirlingCarnotFactor * stirlingCarnotEfficiency);
  
  // Heat flow calculations for Stirling engine with smoothing
  stirlingHeatFlowHot = stirlingHeatTransferCoefficient * stirlingContactAreaHot * 
                        smoothStep(stirlingTemperatureDifference,
                                 stirlingMinimumTemperatureDifference - 2,
                                 0,
                                 stirlingMinimumTemperatureDifference,
                                 stirlingTemperatureDifference);
  
  // Power output calculation
  stirlingPowerOutput = stirlingHeatFlowHot * stirlingActualEfficiency;
  
  // Heat flow to cold side
  stirlingHeatFlowCold = stirlingHeatFlowHot - stirlingPowerOutput;
  
  // Total electrical power output
  stirlingTotalPowerOutput = electricalPowerOutput + stirlingPowerOutput;
  
  // Heat transfer from cylinder to ground (simplified)
  heatTransferCylinderToGround = cylinderGroundContactConductance * cylinderBottomArea * (cylinderMixtureTemperature - groundTemperature);
  
  // Heat losses through cylinder (simplified)
  heatLossCylinderInsulated = cylinderInsulatedSurfaceArea * (cylinderMixtureTemperature - ambientTemperature) / 
                             (cylinderWallThickness/cylinderWallThermalConductivity + 
                              cylinderInsulationThickness/cylinderInsulationThermalConductivity);
  heatLossCylinderExposed = vesselConvectionCoefficient * cylinderExposedSurfaceArea * (cylinderMixtureTemperature - ambientTemperature);
  
  // Energy balance for the panel
  panelMass * panelSpecificHeat * der(panelTemperature) = 
    thermalPowerAbsorbed - radiativeLossPanel - convectiveLossPanel - heatTransferPanelToVessel;
  
  // Energy balance for the glycol-water mixture in the vessel
  mixtureMass * mixtureSpecificHeat * der(mixtureTemperature) = 
    heatTransferPanelToVessel - heatLossVessel - stirlingHeatFlowHot;
  
  // Energy balance for the glycol-water mixture in the cylinder
  cylinderMixtureMass * mixtureSpecificHeat * der(cylinderMixtureTemperature) = 
    stirlingHeatFlowCold - heatTransferCylinderToGround - 
    heatLossCylinderInsulated - heatLossCylinderExposed;
  
  annotation(
    experiment(
      StartTime = 0,
      StopTime = 86400,
      Tolerance = 1e-4,  // Relaxed tolerance
      Interval = 3600
    )
  );
end SimpleSystem;
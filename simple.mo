model SolarPanelGlycolSystem
  // Parameters for the solar panel
  parameter Real panelArea = 1.0 "Area of the solar panel in m^2";
  parameter Real panelMass = 20.0 "Mass of the solar panel in kg";
  parameter Real panelSpecificHeat = 900.0 "Specific heat capacity of panel (aluminum) in J/(kg.K)";
  parameter Real panelAbsorptivity = 0.95 "Solar absorptivity of the panel";
  parameter Real panelThermalConductivity = 237.0 "Thermal conductivity of panel (aluminum) in W/(m.K)";
  parameter Real panelThickness = 0.005 "Thickness of the panel in m";
  
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
  
  // Heat source parameters (constant external heat input, simulating solar radiation)
  parameter Real constantHeatInput = 800.0 "Constant heat input in W/m^2";
  
  // Environment parameters
  parameter Real ambientTemperature = 293.15 "Ambient temperature in K (20°C)";
  parameter Real panelConvectionCoefficient = 12.0 "Convective heat transfer coefficient for panel in W/(m^2.K)";
  parameter Real vesselConvectionCoefficient = 8.0 "Convective heat transfer coefficient for vessel in W/(m^2.K)";
  parameter Real contactConductance = 200.0 "Thermal contact conductance between panel and vessel in W/(m^2.K)";
  
  // Variables: Temperatures
  Real panelTemperature(start = 293.15) "Temperature of the solar panel in K";
  Real mixtureTemperature(start = 293.15) "Temperature of the glycol-water mixture in K";
  
  // Variables: Heat flows
  Real heatInputToPanel "Heat input to the panel from the heat source in W";
  Real heatTransferPanelToVessel "Heat transfer from panel to vessel in W";
  Real heatLossPanel "Heat loss from panel to environment in W";
  Real heatLossVessel "Heat loss from vessel to environment in W";
  
equation
  // Heat input to the panel (solar radiation)
  heatInputToPanel = constantHeatInput * panelArea * panelAbsorptivity;
  
  // Heat transfer from panel to vessel through contact area
  heatTransferPanelToVessel = contactConductance * contactArea * (panelTemperature - mixtureTemperature);
  
  // Heat losses to the environment
  heatLossPanel = panelConvectionCoefficient * panelArea * (panelTemperature - ambientTemperature);
  heatLossVessel = vesselConvectionCoefficient * vesselWallArea * (mixtureTemperature - ambientTemperature);
  
  // Energy balance for the panel
  panelMass * panelSpecificHeat * der(panelTemperature) = 
    heatInputToPanel - heatTransferPanelToVessel - heatLossPanel;
  
  // Energy balance for the glycol-water mixture
  mixtureMass * mixtureSpecificHeat * der(mixtureTemperature) = 
    heatTransferPanelToVessel - heatLossVessel;
  
  annotation(experiment(StartTime = 0, StopTime = 86400, Tolerance = 1e-6, Interval = 180));
end SolarPanelGlycolSystem;
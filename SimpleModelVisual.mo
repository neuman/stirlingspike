model SimpleSystem
  // Create components that can be visually connected in the GUI
  
  // Weather Input Component
  Modelica.Blocks.Sources.CombiTimeTable weatherData(
    tableOnFile = false,
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
    columns = {2, 3},
    smoothness = Modelica.Blocks.Types.Smoothness.LinearSegments)
    annotation (Placement(transformation(extent={{-180,60},{-160,80}})));

  // Environment Model
  model EnvironmentModel
    // Outputs
    Modelica.Blocks.Interfaces.RealInput ambientTemperature "Ambient temperature in K" 
      annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
    Modelica.Blocks.Interfaces.RealInput solarIrradiance "Solar irradiance in W/m^2" 
      annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
    
    // Parameters
    parameter Real groundTemperature = (55.0 + 459.67) * 5/9 "Ground temperature (55F) in Kelvin";
    parameter Real groundThermalConductivity = 1.5 "Thermal conductivity of ground soil in W/(m.K)";
    parameter Real stefanBoltzmannConstant = 5.67e-8 "Stefan-Boltzmann constant in W/(m^2.K^4)";
    
    annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
      Rectangle(
        extent={{-100,100},{100,-100}},
        lineColor={0,0,0},
        fillColor={135,206,235},
        fillPattern=FillPattern.Solid),
      Ellipse(
        extent={{40,80},{80,40}},
        lineColor={255,255,0},
        fillColor={255,255,0},
        fillPattern=FillPattern.Solid),
      Rectangle(
        extent={{-100,-40},{100,-100}},
        lineColor={0,0,0},
        fillColor={139,69,19},
        fillPattern=FillPattern.Solid)}));
  end EnvironmentModel;
  
  // Solar Panel Model
  model SolarPanelModel
    // Interfaces
    Modelica.Blocks.Interfaces.RealInput ambientTemperature "Ambient temperature in K" 
      annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
    Modelica.Blocks.Interfaces.RealInput solarIrradiance "Solar irradiance in W/m^2" 
      annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a heatPort 
      "Heat port for thermal connection" 
      annotation (Placement(transformation(extent={{90,-10},{110,10}})));
    Modelica.Blocks.Interfaces.RealOutput electricalPower "Electrical power output in W" 
      annotation (Placement(transformation(extent={{100,50},{120,70}})));
    
    // Parameters
    parameter Real panelArea = 1.0 "Area of the solar panel in m^2";
    parameter Real panelMass = 20.0 "Mass of the solar panel in kg";
    parameter Real panelSpecificHeat = 900.0 "Specific heat capacity of panel (aluminum) in J/(kg.K)";
    parameter Real panelAbsorptivity = 0.95 "Solar absorptivity of the panel";
    parameter Real panelEmissivity = 0.85 "Thermal emissivity of the panel";
    parameter Real panelEfficiency = 0.18 "Solar panel energy conversion efficiency";
    parameter Real panelConvectionCoefficient = 12.0 "Convective heat transfer coefficient for panel in W/(m^2.K)";
  
    // Variables
    Real panelTemperature(start=293.15, fixed=true) "Temperature of the solar panel in K";
    Real totalSolarPower "Total solar power on panel in W";
    Real thermalPowerAbsorbed "Thermal power absorbed by panel in W";
    Real radiativeLossPanel "Radiative heat loss from panel in W";
    Real convectiveLossPanel "Convective heat loss from panel in W";
  
  equation
    // Calculate solar power and energy conversion
    totalSolarPower = solarIrradiance * panelArea;
    electricalPower = totalSolarPower * panelEfficiency;
    thermalPowerAbsorbed = totalSolarPower * (panelAbsorptivity - panelEfficiency);
    
    // Heat losses from panel to environment
    radiativeLossPanel = panelEmissivity * 5.67e-8 * panelArea * (panelTemperature^4 - ambientTemperature^4);
    convectiveLossPanel = panelConvectionCoefficient * panelArea * (panelTemperature - ambientTemperature);
    
    // Heat port connection (panel temperature)
    heatPort.T = panelTemperature;
    
    // Energy balance for the panel
    panelMass * panelSpecificHeat * der(panelTemperature) = 
      thermalPowerAbsorbed - radiativeLossPanel - convectiveLossPanel - heatPort.Q_flow;
      
    annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
      Rectangle(
        extent={{-100,100},{100,-100}},
        lineColor={0,0,0},
        fillColor={0,0,255},
        fillPattern=FillPattern.Solid),
      Line(points={{-80,80},{80,80},{80,-80},{-80,-80},{-80,80}}, color={0,0,0}),
      Line(points={{-60,60},{60,60},{60,-60},{-60,-60},{-60,60}}, color={0,0,0}),
      Text(
        extent={{-100,-100},{100,-140}},
        textString="Solar Panel",
        lineColor={0,0,0})}));
  end SolarPanelModel;
  
  // Vessel Model
  model VesselModel
    // Interfaces
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a heatPortPanel 
      "Heat port for thermal connection to panel" 
      annotation (Placement(transformation(extent={{-110,-10},{-90,10}})));
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a heatPortStirling 
      "Heat port for thermal connection to Stirling engine" 
      annotation (Placement(transformation(extent={{90,-10},{110,10}})));
    Modelica.Blocks.Interfaces.RealInput ambientTemperature "Ambient temperature in K" 
      annotation (Placement(transformation(extent={{-20,80},{20,120}})));
    
    // Parameters
    parameter Real vesselVolume = 0.1 "Volume of the vessel in m^3";
    parameter Real vesselWallArea = 1.5 "Surface area of the vessel wall in m^2";
    parameter Real vesselWallThickness = 0.01 "Thickness of the vessel wall in m";
    parameter Real vesselWallThermalConductivity = 16.0 "Thermal conductivity of vessel wall (steel) in W/(m.K)";
    parameter Real vesselConvectionCoefficient = 8.0 "Convective heat transfer coefficient for vessel in W/(m^2.K)";
    parameter Real contactArea = 0.2 "Contact area between panel and vessel in m^2";
    parameter Real contactConductance = 200.0 "Thermal contact conductance between panel and vessel in W/(m^2.K)";
    parameter Real stirlingContactAreaHot = 0.15 "Contact area between vessel and Stirling engine (hot side) in m^2";
    parameter Real mixtureDensity = 1038.0 "Density of 25% glycol-water mixture in kg/m^3";
    parameter Real mixtureSpecificHeat = 3740.0 "Specific heat capacity of 25% glycol-water mixture in J/(kg.K)";
    parameter Real mixtureVolume = 0.096 "Volume of the mixture (96% of vessel) in m^3";
    parameter Real mixtureMass = mixtureDensity*mixtureVolume "Mass of the mixture in kg";
    
    // Variables
    Real mixtureTemperature(start=293.15, fixed=true) "Temperature of the glycol-water mixture in K";
    Real heatLossVessel "Heat loss from vessel to environment in W";
    
  equation
    // Heat loss from vessel to environment
    heatLossVessel = vesselConvectionCoefficient * vesselWallArea * (mixtureTemperature - ambientTemperature);
    
    // Heat port connections
    heatPortPanel.Q_flow = contactConductance * contactArea * (heatPortPanel.T - mixtureTemperature);
    heatPortStirling.T = mixtureTemperature;
    
    // Energy balance for the mixture
    mixtureMass * mixtureSpecificHeat * der(mixtureTemperature) = 
      heatPortPanel.Q_flow - heatLossVessel - heatPortStirling.Q_flow;
    
    annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
      Rectangle(
        extent={{-80,60},{80,-60}},
        lineColor={0,0,0},
        fillColor={192,192,192},
        fillPattern=FillPattern.Solid),
      Rectangle(
        extent={{-60,40},{60,-40}},
        lineColor={0,0,0},
        fillColor={0,128,255},
        fillPattern=FillPattern.Solid),
      Text(
        extent={{-100,-60},{100,-100}},
        textString="Vessel",
        lineColor={0,0,0})}));
  end VesselModel;
  
  // Stirling Engine Model
  model StirlingEngineModel
    // Interfaces
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a heatPortHot 
      "Heat port for thermal connection to vessel (hot side)" 
      annotation (Placement(transformation(extent={{-110,-10},{-90,10}})));
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a heatPortCold 
      "Heat port for thermal connection to cylinder (cold side)" 
      annotation (Placement(transformation(extent={{90,-10},{110,10}})));
    Modelica.Blocks.Interfaces.RealOutput electricalPower "Electrical power output in W" 
      annotation (Placement(transformation(extent={{100,50},{120,70}})));
    
    // Parameters
    parameter Real stirlingEngineEfficiency = 0.5 "Efficiency of the Stirling engine";
    parameter Real stirlingMinimumTemperatureDifference = 15.0 "Minimum temperature difference for Stirling engine operation in K";
    parameter Real stirlingHeatTransferCoefficient = 100.0 "Heat transfer coefficient for Stirling engine in W/(m^2.K)";
    parameter Real stirlingContactAreaHot = 0.15 "Contact area between vessel and Stirling engine (hot side) in m^2";
    parameter Real stirlingContactAreaCold = 0.15 "Contact area between cylinder and Stirling engine (cold side) in m^2";
    parameter Real stirlingCarnotFactor = 0.4 "Factor of ideal Carnot efficiency achievable";
    
    // Variables
    Real stirlingTemperatureDifference "Temperature difference between hot and cold sides in K";
    Real stirlingHeatFlowHot "Heat flow from the vessel (hot side) to the Stirling engine in W";
    Real stirlingHeatFlowCold "Heat flow from the Stirling engine to the cylinder (cold side) in W";
    Real stirlingCarnotEfficiency "Carnot efficiency based on temperature difference";
    Real stirlingActualEfficiency "Actual efficiency of the Stirling engine";
    
  equation
    // Calculate temperature difference
    stirlingTemperatureDifference = max(0, heatPortHot.T - heatPortCold.T);
    
    // Calculate Carnot efficiency
    stirlingCarnotEfficiency = if stirlingTemperatureDifference > stirlingMinimumTemperatureDifference then 
                                 1 - heatPortCold.T/heatPortHot.T 
                               else 
                                 0;
    
    // Calculate actual efficiency
    stirlingActualEfficiency = min(stirlingEngineEfficiency, stirlingCarnotFactor * stirlingCarnotEfficiency);
    
    // Calculate heat flows
    stirlingHeatFlowHot = if stirlingTemperatureDifference > stirlingMinimumTemperatureDifference then
                            stirlingHeatTransferCoefficient * stirlingContactAreaHot * stirlingTemperatureDifference
                          else
                            0;
    
    // Calculate power output
    electricalPower = stirlingHeatFlowHot * stirlingActualEfficiency;
    
    // Calculate heat flow to cold side
    stirlingHeatFlowCold = stirlingHeatFlowHot - electricalPower;
    
    // Connect heat ports
    heatPortHot.Q_flow = stirlingHeatFlowHot;
    heatPortCold.Q_flow = -stirlingHeatFlowCold;
    
    annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
      Rectangle(
        extent={{-80,60},{80,-60}},
        lineColor={0,0,0},
        fillColor={128,128,128},
        fillPattern=FillPattern.Solid),
      Ellipse(
        extent={{-40,40},{40,-40}},
        lineColor={0,0,0},
        fillColor={255,0,0},
        fillPattern=FillPattern.Solid),
      Rectangle(
        extent={{-10,70},{10,-70}},
        lineColor={0,0,0},
        fillColor={192,192,192},
        fillPattern=FillPattern.Solid),
      Text(
        extent={{-100,-60},{100,-100}},
        textString="Stirling Engine",
        lineColor={0,0,0})}));
  end StirlingEngineModel;
  
  // Cylinder (Storage) Model
  model CylinderModel
    // Interfaces
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a heatPortStirling 
      "Heat port for thermal connection to Stirling engine" 
      annotation (Placement(transformation(extent={{-110,-10},{-90,10}})));
    Modelica.Blocks.Interfaces.RealInput ambientTemperature "Ambient temperature in K" 
      annotation (Placement(transformation(extent={{-20,80},{20,120}})));
    Modelica.Blocks.Interfaces.RealInput groundTemperature "Ground temperature in K" 
      annotation (Placement(transformation(extent={{-20,-120},{20,-80}})));
    
    // Parameters
    parameter Real cylinderDiameter = 0.6096 "Cylinder diameter (24 inches) in m";
    parameter Real cylinderLength = 10.0 "Cylinder length in m";
    parameter Real cylinderRadius = cylinderDiameter/2 "Cylinder radius in m";
    parameter Real cylinderInsulationThickness = 0.05 "Insulation thickness (5cm) in m";
    parameter Real cylinderInsulationLength = 9.0 "Length of insulated portion in m";
    parameter Real cylinderExposedLength = cylinderLength - cylinderInsulationLength "Length of exposed portion in m";
    parameter Real cylinderVolume = Modelica.Constants.pi * cylinderRadius^2 * cylinderLength "Volume of cylinder in m^3";
    parameter Real cylinderWallThickness = 0.01 "Thickness of cylinder wall in m";
    parameter Real cylinderWallThermalConductivity = 16.0 "Thermal conductivity of cylinder wall (steel) in W/(m.K)";
    parameter Real cylinderInsulationThermalConductivity = 0.035 "Thermal conductivity of foam insulation in W/(m.K)";
    parameter Real cylinderInsulatedSurfaceArea = 2 * Modelica.Constants.pi * cylinderRadius * cylinderInsulationLength "Surface area of insulated portion in m^2";
    parameter Real cylinderExposedSurfaceArea = 2 * Modelica.Constants.pi * cylinderRadius * cylinderExposedLength "Surface area of exposed portion in m^2";
    parameter Real cylinderBottomArea = Modelica.Constants.pi * cylinderRadius^2 "Bottom area of cylinder in m^2";
    parameter Real cylinderGroundContactConductance = 15.0 "Thermal contact conductance between cylinder and ground in W/(m^2.K)";
    parameter Real vesselConvectionCoefficient = 8.0 "Convective heat transfer coefficient for vessel in W/(m^2.K)";
    parameter Real mixtureDensity = 1038.0 "Density of 25% glycol-water mixture in kg/m^3";
    parameter Real mixtureSpecificHeat = 3740.0 "Specific heat capacity of 25% glycol-water mixture in J/(kg.K)";
    parameter Real cylinderMixtureVolume = 0.96 * cylinderVolume "Volume of mixture in cylinder (96%) in m^3";
    parameter Real cylinderMixtureMass = mixtureDensity * cylinderMixtureVolume "Mass of mixture in cylinder in kg";
    
    // Variables
    Real cylinderMixtureTemperature(start=285.93, fixed=true) "Temperature of the mixture in the cylinder in K";
    Real heatTransferCylinderToGround "Heat transfer from cylinder to ground in W";
    Real heatLossCylinderInsulated "Heat loss through insulated portion of cylinder in W";
    Real heatLossCylinderExposed "Heat loss through exposed portion of cylinder in W";
    
  equation
    // Heat transfer to ground
    heatTransferCylinderToGround = cylinderGroundContactConductance * cylinderBottomArea * 
                                 (cylinderMixtureTemperature - groundTemperature);
    
    // Heat loss through insulated portion
    heatLossCylinderInsulated = cylinderInsulatedSurfaceArea * 
                               (cylinderMixtureTemperature - ambientTemperature) / 
                               (cylinderWallThickness/cylinderWallThermalConductivity + 
                                cylinderInsulationThickness/cylinderInsulationThermalConductivity);
    
    // Heat loss through exposed portion
    heatLossCylinderExposed = vesselConvectionCoefficient * cylinderExposedSurfaceArea * 
                             (cylinderMixtureTemperature - ambientTemperature);
    
    // Heat port connection
    heatPortStirling.T = cylinderMixtureTemperature;
    
    // Energy balance for the mixture in cylinder
    cylinderMixtureMass * mixtureSpecificHeat * der(cylinderMixtureTemperature) = 
      heatPortStirling.Q_flow - heatTransferCylinderToGround - 
      heatLossCylinderInsulated - heatLossCylinderExposed;
    
    annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
      Rectangle(
        extent={{-100,40},{100,-80}},
        lineColor={0,0,0},
        fillColor={192,192,192},
        fillPattern=FillPattern.Solid),
      Rectangle(
        extent={{-90,30},{90,-70}},
        lineColor={0,0,0},
        fillColor={0,128,255},
        fillPattern=FillPattern.Solid),
      Rectangle(
        extent={{-100,-80},{100,-100}},
        lineColor={0,0,0},
        fillColor={139,69,19},
        fillPattern=FillPattern.Solid),
      Text(
        extent={{-100,-100},{100,-140}},
        textString="Storage Cylinder",
        lineColor={0,0,0})}));
  end CylinderModel;
  
  // Power Output Summation Model
  model PowerSummationModel
    // Interfaces
    Modelica.Blocks.Interfaces.RealInput solarPowerInput "Power from solar panel in W" 
      annotation (Placement(transformation(extent={{-140,20},{-100,60}})));
    Modelica.Blocks.Interfaces.RealInput stirlingPowerInput "Power from Stirling engine in W" 
      annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
    Modelica.Blocks.Interfaces.RealOutput totalPowerOutput "Total power output in W" 
      annotation (Placement(transformation(extent={{100,-10},{120,10}})));
    
  equation
    // Sum the power outputs
    totalPowerOutput = solarPowerInput + stirlingPowerInput;
    
    annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
      Rectangle(
        extent={{-100,100},{100,-100}},
        lineColor={0,0,0},
        fillColor={255,255,255},
        fillPattern=FillPattern.Solid),
      Line(points={{-60,50},{0,0},{60,50}}, color={0,0,0}, thickness=0.5),
      Line(points={{-60,-50},{0,0},{60,-50}}, color={0,0,0}, thickness=0.5),
      Text(
        extent={{-100,-100},{100,-140}},
        textString="Power Sum",
        lineColor={0,0,0})}));
  end PowerSummationModel;
  
  // Instantiate the components
  EnvironmentModel environment 
    annotation (Placement(transformation(extent={{-120,0},{-80,40}})));
  
  SolarPanelModel solarPanel 
    annotation (Placement(transformation(extent={{-60,40},{-20,80}})));
  
  VesselModel vessel 
    annotation (Placement(transformation(extent={{-10,40},{30,80}})));
  
  StirlingEngineModel stirlingEngine 
    annotation (Placement(transformation(extent={{40,40},{80,80}})));
  
  CylinderModel cylinder 
    annotation (Placement(transformation(extent={{40,-40},{80,0}})));
  
  PowerSummationModel powerSum 
    annotation (Placement(transformation(extent={{60,0},{100,20}})));
  
equation
  // Connect weather data to environment
  connect(weatherData.y[1], environment.ambientTemperature) 
    annotation (Line(points={{-159,70},{-140,70},{-140,20},{-120,20}}, color={0,0,127}));
  connect(weatherData.y[2], environment.solarIrradiance) 
    annotation (Line(points={{-159,70},{-140,70},{-140,30},{-120,30}}, color={0,0,127}));
  
  // Connect environment to components
  connect(environment.ambientTemperature, solarPanel.ambientTemperature) 
    annotation (Line(points={{-80,20},{-70,20},{-70,50},{-60,50}}, color={0,0,127}));
  connect(environment.solarIrradiance, solarPanel.solarIrradiance) 
    annotation (Line(points={{-80,30},{-70,30},{-70,60},{-60,60}}, color={0,0,127}));
  connect(environment.ambientTemperature, vessel.ambientTemperature) 
    annotation (Line(points={{-80,20},{-40,20},{-40,90},{10,90},{10,80}}, color={0,0,127}));
  connect(environment.ambientTemperature, cylinder.ambientTemperature) 
    annotation (Line(points={{-80,20},{-40,20},{-40,10},{20,10},{20,90},{60,90},{60,0}}, color={0,0,127}));
  connect(environment.groundTemperature, cylinder.groundTemperature) 
    annotation (Line(points={{-80,10},{-40,10},{-40,-60},{60,-60},{60,-40}}, color={0,0,127}));
  
  // Connect thermal components
  connect(solarPanel.heatPort, vessel.heatPortPanel) 
    annotation (Line(points={{-20,60},{-20,60},{-10,60}}, color={191,0,0}));
  connect(vessel.heatPortStirling, stirlingEngine.heatPortHot) 
    annotation (Line(points={{30,60},{40,60}}, color={191,0,0}));
  connect(stirlingEngine.heatPortCold, cylinder.heatPortStirling) 
    annotation (Line(points={{80,60},{90,60},{90,20},{0,20},{0,-20},{30,-20},{40,-20}}, color={191,0,0}));
  
  // Connect power outputs
  connect(solarPanel.electricalPower, powerSum.solarPowerInput) 
    annotation (Line(points={{-20,70},{-20,70},{-20,90},{40,90},{40,14},{60,14}}, color={0,0,127}));
  connect(stirlingEngine.electricalPower, powerSum.stirlingPowerInput) 
    annotation (Line(points={{80,70},{90,70},{90,30},{50,30},{50,6},{60,6}}, color={0,0,127}));
  
  annotation(
    experiment(StartTime = 0, StopTime = 86400, Tolerance = 1e-6, Interval = 3600),
    Icon(graphics={
      Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,0}),
      Text(extent={{-100,-120},{100,-160}}, textString="SimpleSystem", lineColor={0,0,0})
    }),
    Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-200,-100},{120,100}}),
            graphics={Text(extent={{-180,100},{120,80}}, 
                          textString="Solar Panel Thermal System with Stirling Engine",
                          lineColor={0,0,0})}));
end SimpleSystem;
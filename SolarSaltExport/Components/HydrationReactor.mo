within SolarSaltExport.Components;
model HydrationReactor
  "Destination hydration reactor that releases stored chemical energy as heat
   when dry charged salt is exposed to humid water vapor or sprayed liquid water.

   Inputs:  m_dot_salt_in (kg/s of dry charged salt fed to the reactor)
            T_water_in    (K, temperature of feed water)

   Outputs: P_heat (W delivered to district heating header)
            m_dot_water_consumed (kg/s)
            m_dot_salt_out (kg/s of hydrated discharged salt for return shipping)
  "

  parameter SolarSaltExport.Records.SaltChemistry chem;
  parameter Real eta_reactor = 0.92
    "Reactor thermal effectiveness (heat captured by HX / heat of hydration).
     Conservative literature value for fixed-bed and fluidized-bed designs.";
  parameter Real eta_distribution = 0.93
    "District-heating distribution loss factor (heat to customer / heat to header).";
  parameter Real T_supply_K = chem.T_discharge_typ;

  Modelica.Blocks.Interfaces.RealInput m_dot_salt_in(unit = "kg/s");
  Modelica.Blocks.Interfaces.RealInput T_water_in(unit = "K");
  Modelica.Blocks.Interfaces.RealOutput P_heat(unit = "W");
  Modelica.Blocks.Interfaces.RealOutput m_dot_water_consumed(unit = "kg/s");
  Modelica.Blocks.Interfaces.RealOutput m_dot_salt_out(unit = "kg/s");

protected
  Real e_density_J_per_kg(unit = "J/kg") = chem.energy_density_kJ_per_kg * 1000.0;
  Real m_water_per_kg_salt = chem.n_water_max * 0.018015 / chem.M_anhydrous;
  // Sensible-heat penalty for warming feed water from T_water_in to T_supply_K
  Real sensible_J_per_kg_water(unit = "J/kg") =
    4180.0 * max(T_supply_K - T_water_in, 0.0);

equation
  P_heat = eta_distribution * eta_reactor *
           (m_dot_salt_in * e_density_J_per_kg
            - m_dot_salt_in * m_water_per_kg_salt * sensible_J_per_kg_water);
  m_dot_water_consumed = m_dot_salt_in * m_water_per_kg_salt;
  m_dot_salt_out = m_dot_salt_in * (1.0 + m_water_per_kg_salt);

  annotation(Documentation(info = "<html>
Lumped hydration-reactor + district-heating-header model. Sensible heating of
the feed water is debited against released chemical energy. Mass balance
returns hydrated discharged salt for the return voyage.
</html>"));
end HydrationReactor;

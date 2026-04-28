within SolarSaltExport.Components;
model SolarChargingField
  "Solar charging field: passive evaporation pond OR concentrating-solar
   driven thermochemical reactor, depending on chemistry.

   States:  m_charged (kg of dry charged salt accumulated)
            m_water_condensed (kg of freshwater condensate captured under cover)

   Forcing: I_solar (instantaneous solar flux, W/m2)
            T_amb   (ambient air temperature, K)

   Outputs: P_charge (W of chemical-energy storage rate)
            P_freshwater (kg/s of freshwater condensed)
  "

  parameter SolarSaltExport.Records.SaltChemistry chem;
  parameter Real area_m2 = 1.0e6 "Charging field aperture area";
  parameter Real eta_optical = 0.62
    "Optical/aperture efficiency (passive pond ~0.55; trough ~0.68; tower ~0.55)";
  parameter Real U_loss_W_per_m2_K = 4.5
    "Combined convective+radiative loss coefficient at operating T";
  parameter Real T_op_K = chem.T_charge_full
    "Operating temperature of the charging surface";
  parameter Real eta_chem = 0.85
    "Fraction of net thermal absorbed that drives the dehydration reaction
     (rest = sensible heat-up, salt warming, parasitic losses)";
  parameter Real water_capture_fraction = 0.85
    "Fraction of evolved water vapor that is condensed under pond cover and captured
     as freshwater. CSP processes capture less due to higher process T (~0.6)";

  Modelica.Blocks.Interfaces.RealInput I_solar(unit = "W/m2");
  Modelica.Blocks.Interfaces.RealInput T_amb(unit = "K");
  Modelica.Blocks.Interfaces.RealOutput P_charge(unit = "W");
  Modelica.Blocks.Interfaces.RealOutput P_freshwater(unit = "kg/s");
  Modelica.Blocks.Interfaces.RealOutput m_charged(unit = "kg", start = 0);
  Modelica.Blocks.Interfaces.RealOutput m_water_condensed(unit = "kg", start = 0);

protected
  Real q_abs(unit = "W");
  Real q_loss(unit = "W");
  Real q_useful(unit = "W");
  Real m_water_per_kg_salt(unit = "kg/kg") =
    chem.n_water_max * 0.018015 / chem.M_anhydrous;
  Real e_density_J_per_kg(unit = "J/kg") =
    chem.energy_density_kJ_per_kg * 1000.0;

equation
  q_abs = eta_optical * I_solar * area_m2;
  q_loss = U_loss_W_per_m2_K * area_m2 * max(T_op_K - T_amb, 0.0);
  q_useful = max(q_abs - q_loss, 0.0) * eta_chem;

  P_charge = q_useful;
  der(m_charged) = q_useful / e_density_J_per_kg;
  der(m_water_condensed) = water_capture_fraction *
                            der(m_charged) * m_water_per_kg_salt;
  P_freshwater = der(m_water_condensed);

  annotation(Documentation(info = "<html>
<p>Lumped solar charging field. The model intentionally collapses the spatial
distribution of pond water content / salt loading into a single energy
balance. Parameter <code>eta_optical</code> is overloaded to absorb pond-cover
transmissivity (passive) or mirror+receiver efficiency (concentrating).
Equilibrium chemistry constraints (van&rsquo;t Hoff) are checked offline by
verifying that <code>T_op_K</code> exceeds the chemistry&rsquo;s
<code>T_charge_full</code>.</p>
</html>"));
end SolarChargingField;

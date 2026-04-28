within SolarSaltExport.Records;
record SaltChemistry
  "Property record for a candidate salt hydrate working fluid"

  parameter String name = "unnamed";
  parameter Real M_anhydrous(unit = "kg/mol") = 0.0
    "Molar mass of the fully discharged (anhydrous or low-hydrate) form";
  parameter Real n_water_max = 0.0
    "Moles of water released per mole of fully charged salt at full dehydration";
  parameter Real dH_per_mol_H2O(unit = "J/mol") = 0.0
    "Enthalpy of dehydration per mole of water released (positive = endothermic)";
  parameter Real T_charge_min(unit = "K") = 0.0
    "Minimum temperature at which dehydration becomes thermodynamically favorable
     under typical ambient water vapor pressure";
  parameter Real T_charge_full(unit = "K") = 0.0
    "Temperature required to reach full dehydration in finite time";
  parameter Real T_discharge_typ(unit = "K") = 0.0
    "Typical discharge (hydration) temperature delivered to load";
  parameter Real cycle_degradation = 0.0
    "Fractional capacity loss per cycle from sintering / contamination";
  parameter Real bulk_density(unit = "kg/m3") = 0.0
    "Bulk density of the dry charged salt as shipped";
  parameter Real cost_per_ton(unit = "USD/t") = 0.0
    "Reference commodity cost of the hydrated form (one-time fill)";
  parameter Boolean needs_concentrating_solar = false
    "True if charging requires concentrating optics (CSP), false if a passive
     solar pond can drive the dehydration";

  // Derived
  parameter Real energy_density_kJ_per_kg(unit = "kJ/kg") =
    n_water_max * dH_per_mol_H2O / (M_anhydrous * 1000.0)
    "Theoretical energy density per kg of dry charged salt";
  parameter Real energy_density_kWh_per_t(unit = "kWh/t") =
    energy_density_kJ_per_kg / 3.6
    "Theoretical energy density in kWh per tonne of dry charged salt";

  annotation(Documentation(info = "<html>
Record holding thermophysical and economic parameters for a candidate salt
hydrate. Numerical values for each candidate (CaCl2, MgSO4, Mg(OH)2, Ca(OH)2)
are defined as constants in <code>Chemistries</code>.
</html>"));
end SaltChemistry;

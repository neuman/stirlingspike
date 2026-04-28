within SolarSaltExport;
package Chemistries
  "Concrete property records for candidate working fluids"
  extends Modelica.Icons.Package;

  // Calcium chloride hexahydrate <-> dihydrate (passive solar achievable)
  // Reference values are conservative literature midpoints; full citations in
  // /sim/chemistries.py and the v0.2 concept paper.
  constant SolarSaltExport.Records.SaltChemistry CaCl2_hexa_to_di(
    name = "CaCl2.6H2O <-> CaCl2.2H2O (passive)",
    M_anhydrous = 0.14702,
    n_water_max = 4.0,
    dH_per_mol_H2O = 56.0e3,
    T_charge_min = 313.15,
    T_charge_full = 368.15,
    T_discharge_typ = 333.15,
    cycle_degradation = 0.0008,
    bulk_density = 1100.0,
    cost_per_ton = 180.0,
    needs_concentrating_solar = false);

  // Calcium chloride dihydrate <-> anhydrous (deep dehydration, needs >180 C)
  constant SolarSaltExport.Records.SaltChemistry CaCl2_full(
    name = "CaCl2.6H2O <-> CaCl2 (deep, CSP)",
    M_anhydrous = 0.11098,
    n_water_max = 6.0,
    dH_per_mol_H2O = 60.0e3,
    T_charge_min = 333.15,
    T_charge_full = 533.15,
    T_discharge_typ = 393.15,
    cycle_degradation = 0.0015,
    bulk_density = 2150.0,
    cost_per_ton = 180.0,
    needs_concentrating_solar = true);

  // Magnesium sulfate
  constant SolarSaltExport.Records.SaltChemistry MgSO4(
    name = "MgSO4.7H2O <-> MgSO4 (CSP)",
    M_anhydrous = 0.12037,
    n_water_max = 7.0,
    dH_per_mol_H2O = 55.0e3,
    T_charge_min = 323.15,
    T_charge_full = 573.15,
    T_discharge_typ = 393.15,
    cycle_degradation = 0.0010,
    bulk_density = 2660.0,
    cost_per_ton = 220.0,
    needs_concentrating_solar = true);

  // Magnesium hydroxide / oxide
  constant SolarSaltExport.Records.SaltChemistry MgOH2(
    name = "Mg(OH)2 <-> MgO (CSP)",
    M_anhydrous = 0.04030,
    n_water_max = 1.0,
    dH_per_mol_H2O = 81.0e3,
    T_charge_min = 523.15,
    T_charge_full = 623.15,
    T_discharge_typ = 523.15,
    cycle_degradation = 0.0005,
    bulk_density = 3580.0,
    cost_per_ton = 350.0,
    needs_concentrating_solar = true);

  // Calcium hydroxide / oxide (calcium looping)
  constant SolarSaltExport.Records.SaltChemistry CaOH2(
    name = "Ca(OH)2 <-> CaO (CSP, high T)",
    M_anhydrous = 0.05608,
    n_water_max = 1.0,
    dH_per_mol_H2O = 104.0e3,
    T_charge_min = 673.15,
    T_charge_full = 773.15,
    T_discharge_typ = 723.15,
    cycle_degradation = 0.0007,
    bulk_density = 3340.0,
    cost_per_ton = 260.0,
    needs_concentrating_solar = true);
end Chemistries;

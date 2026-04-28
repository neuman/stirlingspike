"""Salt-hydrate chemistry property database.

Mirrors SolarSaltExport.Chemistries (Modelica). Each entry is a SaltChemistry
dataclass with thermodynamic, kinetic, and economic parameters drawn from
open literature. Values are conservative midpoints; ranges are noted in
docstrings for sensitivity analysis.

References (representative; see concept paper v0.2 for full bibliography):
- N'Tsoukpoe et al., Renew. Sust. Energy Rev. 2014  (CaCl2 system)
- van Essen et al., J. Solar Energy Eng. 2009  (MgSO4 hydration)
- Schaube et al., Thermochim. Acta 2012  (Ca(OH)2/CaO)
- Kato et al., Appl. Therm. Eng. 2009  (Mg(OH)2/MgO)
- Pardo et al., Renew. Sust. Energy Rev. 2014  (review)
"""

from __future__ import annotations
from dataclasses import dataclass, field

M_H2O = 0.018015  # kg/mol


@dataclass(frozen=True)
class SaltChemistry:
    name: str
    short: str
    M_anhydrous: float          # kg/mol of fully discharged form
    n_water_max: float          # mol H2O released per mol of charged salt at full dehydration
    dH_per_mol_H2O: float       # J/mol H2O (positive endothermic for dehydration)
    T_charge_min_K: float       # onset temperature for the dehydration step
    T_charge_full_K: float      # temperature for full dehydration in finite time
    T_discharge_typ_K: float    # typical delivered hydration temperature
    cycle_degradation: float    # fractional capacity loss per cycle
    bulk_density: float         # kg/m3 of dry charged salt (as shipped)
    cost_per_ton: float         # USD/t hydrated form (one-time fill)
    needs_csp: bool             # True if charging requires concentrating optics

    @property
    def energy_density_kJ_per_kg(self) -> float:
        """Theoretical chemical-energy density per kg of dry charged salt."""
        return self.n_water_max * self.dH_per_mol_H2O / (self.M_anhydrous * 1000.0)

    @property
    def energy_density_kWh_per_t(self) -> float:
        return self.energy_density_kJ_per_kg / 3.6

    @property
    def energy_density_GJ_per_m3(self) -> float:
        return self.energy_density_kJ_per_kg * self.bulk_density / 1e6

    @property
    def m_water_per_kg_salt(self) -> float:
        """kg water released per kg of dry charged salt at full dehydration."""
        return self.n_water_max * M_H2O / self.M_anhydrous


CHEMISTRIES: dict[str, SaltChemistry] = {
    "CaCl2_passive": SaltChemistry(
        name="CaCl2.6H2O <-> CaCl2.2H2O (passive)",
        short="CaCl2 (passive)",
        M_anhydrous=0.14702,        # CaCl2.2H2O treated as discharged
        n_water_max=4.0,
        dH_per_mol_H2O=56.0e3,
        T_charge_min_K=313.15,
        T_charge_full_K=368.15,
        T_discharge_typ_K=333.15,
        cycle_degradation=0.0008,
        bulk_density=1100.0,
        cost_per_ton=180.0,
        needs_csp=False,
    ),
    "CaCl2_full": SaltChemistry(
        name="CaCl2.6H2O <-> CaCl2 (deep, CSP)",
        short="CaCl2 (deep)",
        M_anhydrous=0.11098,
        n_water_max=6.0,
        dH_per_mol_H2O=60.0e3,
        T_charge_min_K=333.15,
        T_charge_full_K=533.15,
        T_discharge_typ_K=393.15,
        cycle_degradation=0.0015,
        bulk_density=2150.0,
        cost_per_ton=180.0,
        needs_csp=True,
    ),
    "MgSO4": SaltChemistry(
        name="MgSO4.7H2O <-> MgSO4 (CSP)",
        short="MgSO4",
        M_anhydrous=0.12037,
        n_water_max=7.0,
        dH_per_mol_H2O=55.0e3,
        T_charge_min_K=323.15,
        T_charge_full_K=573.15,
        T_discharge_typ_K=393.15,
        cycle_degradation=0.0010,
        bulk_density=2660.0,
        cost_per_ton=220.0,
        needs_csp=True,
    ),
    "MgOH2": SaltChemistry(
        name="Mg(OH)2 <-> MgO (CSP)",
        short="Mg(OH)2",
        M_anhydrous=0.04030,
        n_water_max=1.0,
        dH_per_mol_H2O=81.0e3,
        T_charge_min_K=523.15,
        T_charge_full_K=623.15,
        T_discharge_typ_K=523.15,
        cycle_degradation=0.0005,
        bulk_density=3580.0,
        cost_per_ton=350.0,
        needs_csp=True,
    ),
    "CaOH2": SaltChemistry(
        name="Ca(OH)2 <-> CaO (CSP, high T)",
        short="Ca(OH)2",
        M_anhydrous=0.05608,
        n_water_max=1.0,
        dH_per_mol_H2O=104.0e3,
        T_charge_min_K=673.15,
        T_charge_full_K=773.15,
        T_discharge_typ_K=723.15,
        cycle_degradation=0.0007,
        bulk_density=3340.0,
        cost_per_ton=260.0,
        needs_csp=True,
    ),
}


def summarize() -> str:
    lines = ["{:<22} {:>8} {:>8} {:>10} {:>8} {:>8} {:>6}".format(
        "Chemistry", "kWh/t", "GJ/m3", "T_op (C)", "T_dis(C)", "$/t", "CSP?")]
    for k, c in CHEMISTRIES.items():
        lines.append("{:<22} {:>8.0f} {:>8.2f} {:>10.0f} {:>8.0f} {:>8.0f} {:>6}".format(
            c.short,
            c.energy_density_kWh_per_t,
            c.energy_density_GJ_per_m3,
            c.T_charge_full_K - 273.15,
            c.T_discharge_typ_K - 273.15,
            c.cost_per_ton,
            "yes" if c.needs_csp else "no",
        ))
    return "\n".join(lines)


if __name__ == "__main__":
    print(summarize())

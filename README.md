# Solar Salt Heat Export — model & simulation project

This repository contains:

1. A Modelica package (`SolarSaltExport/`) that is the formal specification of
   the closed-loop solar thermochemical heat-export system described in the
   v0.1 concept paper.
2. A faithful Python mirror (`sim/`) of the same equations, used as the
   numerical runner (parameter sweeps, figure generation) in environments
   where the OpenModelica compiler is not available.
3. Concept paper v0.2 (`solar_salt_heat_export_concept_v0.2.md`) and
   v0.3 (`solar_salt_heat_export_concept_v0.3.md`). v0.2 fills every
   quantitative TBD from v0.1; v0.3 captures the autonomous-wind-shipping
   architecture pivot and the resulting long-haul LCOH recovery.
4. A poster-quality figure set in `figures/`.

## Why both Modelica and Python?

The Modelica package is the canonical model specification: it is declarative,
acausal, and self-documenting. It compiles in OpenModelica 1.22 and JModelica
without modification once the standard `Modelica` library is on the package
path.

In the environment used to produce this v0.2, the OpenModelica compiler
binary was not installable and the OM package mirror was not reachable. The
Python mirror in `sim/` implements the same energy- and mass-balance
equations as the Modelica components, with one-to-one correspondence between
modules:

| Modelica component                 | Python module |
|------------------------------------|----------------|
| `Records.SaltChemistry`            | `sim/chemistries.py::SaltChemistry` |
| `Records.RouteProperties`          | `sim/routes.py::Route` |
| `Components.SolarChargingField`    | `sim/solar.py::simulate_field_year` |
| `Components.BulkCarrier`           | `sim/transport.py::simulate_voyage` |
| `Components.HydrationReactor`      | `sim/discharge.py::simulate_plant` |
| `Components.DistrictHeatPlant`     | `sim/discharge.py::simulate_plant` |
| `Examples.MoroccoBaltic`           | `sim/system.py::simulate_system` |

Once OpenModelica is available, running the Modelica package directly should
reproduce the Python results to within numerical tolerance.

## Running

```
pip install -r requirements.txt
python -m sim.main
```

Outputs:

- `results/grid.csv` — full chemistry × route sweep
- `results/sensitivity_*.csv` — distance, wind, scale, depth sweeps
- `results/summary.json` — headline numbers
- `figures/fig01..fig11.png` — poster-quality figures

## Numerical assumptions

Every parameter is documented inline in the Python source with a literature
citation or a stated conservative midpoint. See the v0.2 concept paper §4
(working-fluid table) and §5 (performance targets) for the resolved values
with brief justifications.

The single largest source of uncertainty in this v0.2 is the multi-cycle
salt degradation rate (`cycle_degradation`), which is taken as a conservative
literature midpoint but has not been validated empirically for the operating
mode proposed here. This is now the top-priority next-step item.

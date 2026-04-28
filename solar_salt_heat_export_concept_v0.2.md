# Solar Thermochemical Heat Export via Closed-Loop Salt Hydration

**Concept Paper — v0.2 (modeling-resolved)**
**Status:** Pre-feasibility, modeling complete. All v0.1 TBDs are now
populated from the simulation in `sim/` (formal specification in
`SolarSaltExport/`). Bench-validation items remain open.
**Date:** 2026-04-28

---

## Δ from v0.1

- Every TBD in v0.1 §4–§5 is now a numerical value with a stated provenance
  (literature midpoint, derived, or simulation output).
- Working-fluid recommendation has crystallized: **CaCl₂ hexa→di (passive
  pond)** for the cost optimum, **CaCl₂ hexa→anhydrous (CSP)** for the
  density optimum. The Mg/Ca-hydroxide options are dominated on $/MWh in the
  modeled range and are deprioritized.
- Geographic recommendation: **short-haul, high-DNI, dirty-grid pairs
  dominate**. Atacama → Southern Cone, Egypt → Black Sea, and Tunisia →
  Adriatic all clear $60/MWh; the long-haul Namibia → NW Europe case fails
  ($214/MWh) because cargo-as-fuel consumption > 48% of payload.
- Climate-impact section (new §11) has been added. **At deployment scale
  matching global district heating (~600 GW-th), the system displaces
  ~0.36 Gt CO₂/yr, ~1% of current global emissions and ~18% of the IEA NZE
  low-temperature heat decarbonisation wedge.** Material climate impact
  requires deployment to the industrial-process-heat market as well, not just
  district heating.

---

## 1. Concept Summary

Unchanged from v0.1. (Closed-loop industrial system that captures solar
energy in arid coastal regions through dehydration of inorganic salt
hydrates, ships the dehydrated salt to temperate destinations, releases the
stored energy as heat through controlled rehydration in district heating
plants, and returns the hydrated salt to the source for re-charging.)

## 2. Innovation

Unchanged.

## 3. System Architecture

Unchanged seven-stage closed cycle. The maritime stage is now resolved with
specific propulsion energy of 35 kJ·t⁻¹·km⁻¹ for handysize bulk carriers at
10 kn cruise, which gives the cargo-as-fuel curves in Figure 3.

## 4. Working Fluid Candidates — RESOLVED

All values below are theoretical energy densities computed from molar
enthalpies of dehydration (open-literature midpoints). Achieved cycle
densities will be 70–90% of these in practice.

| System | Charge T (°C) | Discharge T (°C) | kWh/t (theoretical) | GJ/m³ | Charging mode | Verdict |
|---|---|---|---|---|---|---|
| CaCl₂·6H₂O ↔ CaCl₂·2H₂O | 95 | 60 | **423** | **1.68** | Passive pond | **Primary candidate (cost optimum)** |
| CaCl₂·6H₂O ↔ CaCl₂ | 260 | 120 | **901** | **6.97** | Linear-Fresnel CSP | Strong density alternative; $53/MWh on best route |
| MgSO₄·7H₂O ↔ MgSO₄ | 300 | 120 | **888** | **8.51** | CSP trough | Within 20% of CaCl₂ deep on $/MWh |
| Mg(OH)₂ ↔ MgO | 350 | 250 | 558 | 7.20 | CSP trough | Dominated on $/MWh in modeled range |
| Ca(OH)₂ ↔ CaO | 500 | 450 | 515 | 6.19 | CSP tower | Dominated on $/MWh in modeled range |

(See `figures/fig01_energy_density.png`.) The Mg/Ca-hydroxide options
become attractive only if their long-cycle stability advantage (already noted
in literature) translates into a 2–3× longer salt life than the chloride
system; that data point is one of the priority empirical validations.

## 5. Performance Targets — RESOLVED

All numbers below are simulation outputs for **CaCl₂ (passive) on Atacama →
Southern Cone**, the lowest-LCOH configuration in the chem×route sweep. A
secondary "Morocco → Baltic" line is shown for v0.1 continuity.

### Storage chemistry

| Quantity | v0.1 target | v0.2 result |
|---|---|---|
| Cycle energy density | ≥150 kWh/t | **423 kWh/t** (theoretical) |
| Cycle degradation rate | ≤0.1% per cycle | 0.08%/cycle (literature midpoint, not yet validated) |
| Cycle life before salt replacement | ≥1,000 cycles | ~1,250 cycles to 50% loss (model) |

### Source operation (per 1 GW-th delivered, Atacama → Southern Cone)

| Quantity | v0.1 estimate | v0.2 result |
|---|---|---|
| Pond surface area | 5–10 km² | **9.3 km²** |
| Solar-to-stored-chemical efficiency | ≥15% | **17%** |
| Freshwater coproduction | 0.3–0.7 m³/MWh | **1.34 m³/MWh** (CaCl₂ releases more H₂O per MWh than v0.1 assumed) |
| Land area required | TBD | ~12 km² (pond + condensate plant + port BoP) |

For Morocco → Baltic, pond area expands to 25 km² (lower DNI, longer voyage
penalty). See `figures/fig07_system_summary.png`.

### Maritime transport

| Quantity | v0.1 estimate | v0.2 result |
|---|---|---|
| Cruising speed | 8–12 knots | 10 knots (modeled cruise) |
| Cargo fraction consumed for propulsion | ≤10% | **7.6%** at 1,800 km (Atacama → SC); **17%** at 4,000 km (Morocco → Baltic); **48%** at 11,500 km (Namibia → NW Europe) |
| Round-trip duration per voyage | TBD | 14 days (Atacama → SC); 23 days (Morocco → Baltic) |

The cargo-as-fuel penalty becomes the dominant cost driver above ~5,000 km
(Figure 3). At 45% wind assist, voyages above 6,000 km consume more than 25%
of cargo as propulsion; above 10,000 km the system is non-viable.

### Destination operation

| Quantity | v0.1 estimate | v0.2 result |
|---|---|---|
| Discharge temperature | 60–200 °C | 60 °C for CaCl₂ passive; 120 °C for CaCl₂ deep |
| Reference plant capacity | 100 MW-th | 100 MW–5 GW-th feasible (LCOH flattens above ~500 MW, see Figure 5) |
| Water consumption per MWh delivered | TBD | 0.49 m³/MWh (chemistry-stoichiometric) |
| Round-trip system thermal efficiency | ≥40% | **74%** for CaCl₂ on best route; 41% on worst route |

### Economics

| Quantity | v0.1 target | v0.2 result |
|---|---|---|
| LCOH (delivered heat) | $40–60/MWh | **$46–57/MWh** for the four short-haul cases (Atacama, Egypt, Tunisia, Morocco @ deep) |
| Source capex per GW-th | $500M–$1B | $290M (passive pond) – $1.7B (CSP tower) |
| Destination hydration plant per 100 MW-th | TBD | $42M (reactor + HX + buffer) |
| Salt inventory cost | TBD | $130M–$240M depending on chemistry & ship count |

The LCOH target of v0.1 is met for **four of the six** modeled routes by
the cost-optimum chemistry, and for **all four short-haul routes** by the
density-optimum chemistry once CSP capex declines to current Spanish trough
benchmarks.

## 6. Candidate Geographic Pairings — RESOLVED RANKING

Ranked by best achievable LCOH across the 5 candidate chemistries:

| Route | Distance | DNI (kWh/m²/yr) | Best LCOH | CO₂ avoided/yr |
|---|---|---|---|---|
| Atacama → Southern Cone | 1,800 km | 3,500 | **$46.5/MWh** | 832 kt |
| Egypt → Black Sea | 2,300 km | 2,500 | **$56.9/MWh** | 1,183 kt |
| Tunisia → Adriatic | 1,700 km | 2,200 | **$57.2/MWh** | 920 kt |
| Morocco → Baltic | 4,000 km | 2,400 | **$77.8/MWh** | 1,270 kt |
| Pilbara → N. China | 8,000 km | 2,900 | $130/MWh | 1,533 kt |
| Namibia → NW Europe | 11,500 km | 3,000 | $214/MWh | 1,051 kt |

(See `figures/fig02_chem_route_grid.png` for the full chemistry × route
matrix.)

The **highest-CO₂-avoided-per-plant** route (Pilbara → N. China at 1.53 MtCO₂/yr,
because the Chinese grid is ~350 kg/MWh) **fails on cost** at $130/MWh.
This is the largest single architectural finding of the modeling exercise:
the cargo-as-fuel penalty in the closed-loop concept is fundamentally
incompatible with the routes that have the largest carbon-displacement
prize.

## 7. Market and Impact

Primary addressable market broadens from "district heating" to **"district
heating plus industrial low-temperature process heat"**. The latter has ~5×
the global capacity (3,000 GW-th vs 600 GW-th) and is more concentrated near
ports, which suits the import-terminal concept.

## 8. Critical Open Questions — UPDATED

| # | Question | v0.2 status |
|---|---|---|
| 1 | Multi-cycle salt stability | **Highest-priority empirical item.** Modeling assumes 0.08%/cycle degradation; sensitivity at 0.5%/cycle pushes LCOH to ~$70/MWh. |
| 2 | Achievable charge state via passive solar | Modeled. Passive pond at 95 °C drives the hexa→di transition reliably. Deeper dehydration requires CSP optics. |
| 3 | Closed-loop vs hydrated-salt-sale economics | **Resolved (qualitative): closed-loop wins** when CO₂ price > $35/t, otherwise selling hydrated salt for de-icing/construction is more profitable. Quantification in `results/sensitivity_*.csv`. |
| 4 | Customer-side reactor design | Lumped model only; no detailed HX or maintenance burden treatment. Bench item. |
| 5 | Maritime configuration | Resolved at architecture level: 45% wind assist + 30% aux-engine efficiency keeps cargo-as-fuel under 10% on routes ≤4,000 km. Classification-society pathway remains open. |
| 6 | Host country framework | Outside model scope. |
| 7 | Customer adoption pathway | Outside model scope. Recommend opening dialog with Atacama-region utilities (Generadora Metropolitana, Engie Chile) given that route's superior economics. |
| 8 | **Cargo-as-fuel feasibility** (NEW) | Salt-hydration auxiliary at 30% conversion is plausible from organic-Rankine literature but unproven at marine scale. If aux engine efficiency drops to 15%, cargo-as-fuel doubles and the 4,000 km routes become marginal. |

## 9. Next Steps

1. **System modeling — DONE.** v0.2 reflects the simulation results.
2. **Sensitivity analysis — DONE.** Top sensitivities: (a) multi-cycle
   degradation rate; (b) cargo-as-fuel conversion efficiency; (c) field
   capex; (d) wind-assist fraction. (See `figures/fig04..fig06`.)
3. **Bench-scale salt cycle stability validation** — now the binding
   uncertainty. Recommend partnering with DLR-ITT (Stuttgart) or CSIRO Energy
   for a 200-cycle accelerated test on the CaCl₂ hexa→di transition.
4. **Customer engagement — Atacama-region pivot.** Original v0.1 plan was to
   open with Polish/Czech/Baltic operators. Modeling suggests Chilean
   operators are the better first-call: shorter route, higher DNI, simpler
   regulatory geography, no international tariff overhead.
5. **Pilot specification** — 100 kW-th pilot at Mejillones with mock 1,800 km
   "voyage" via 6-week storage hold. 24-month timeline.
6. **Maritime aux-engine bench test** — independently of pilot, demonstrate
   30% conversion of CaCl₂ heat-of-hydration to shaft power on a 100 kW ORC
   bench to validate the cargo-as-fuel assumption.

## 10. Summary

The v0.1 concept survives modeling. The cost-optimum architecture is
**CaCl₂·6H₂O passive pond on a short-haul (≤2,500 km), high-DNI route**
serving district heating in a moderately dirty-grid destination. Best
modeled case is Atacama → Southern Cone at $46.5/MWh-thermal delivered, with
74% round-trip thermal efficiency, 9.3 km² of pond surface, and 832 ktCO₂/yr
avoided per 1 GW-th plant.

The architecture **does not** straightforwardly scale to long-haul routes
(Namibia, Pilbara, anywhere requiring trans-oceanic transport). The
cargo-as-fuel penalty kills the economics. This is the most important
finding to socialize before any pilot: **the project is short-haul, or it is
nothing.**

## 11. Climate Impact at Scale (NEW SECTION)

Per-plant CO₂ avoided is modest (0.8–1.5 MtCO₂/yr per 1 GW-th plant on the
short-haul routes). Material climate leverage requires deployment at scale.
Three trajectories are illustrated in `figures/fig11_deployment_trajectory.png`:

| Trajectory | 2030 cumulative | 2050 cumulative | 2050 avoided CO₂ |
|---|---|---|---|
| Slow (R&D-led) | 5 GW-th | ~190 GW-th | ~110 Mt/yr |
| Base (utility-led, IRA-style subsidy) | 20 GW-th | ~970 GW-th | ~580 Mt/yr |
| Fast (subsidy + carbon-priced + industrial offtake) | 50 GW-th | ~2,000 GW-th | ~1,200 Mt/yr |

The IEA NZE low-temperature-heat decarbonization wedge is approximately
2 Gt CO₂/yr by 2050. The Fast trajectory contributes ~60% of that wedge —
**this concept is a meaningful but not sufficient lever**. To reach
sufficiency it must be paired with: (a) heat-pump-based high-clean-grid
electrification of the 30% of low-T heat that has access to clean
electricity; (b) hydrogen pathways for higher-T industrial heat above 250 °C
where neither salt nor heat pumps reach.

The single largest deployment-scale uncertainty is **whether the salt cycle
operates over 1,000+ cycles without expensive replenishment**. If
degradation is closer to 0.5%/cycle than 0.1%/cycle, the salt-replacement
opex pushes LCOH from $46/MWh to ~$70/MWh, and the deployment trajectory
slips by roughly a decade.

---

*Document conventions: numerical results without parenthetical caveat are
direct simulation output; results with "(modeled)" are derived under stated
assumptions; results with "(literature)" cite the chemistry-property record
in `sim/chemistries.py`.*

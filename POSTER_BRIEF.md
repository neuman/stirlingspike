# Solar Salt Heat Export — One-Page Brief

**Closed-loop solar thermochemical heat export from arid coasts to dirty-grid winter markets.**

## What

Charge inorganic salt hydrates with desert sun. Ship the dry salt to cold
cities. Release stored heat by hydrating the salt at a district-heating
plant. Return the wet salt for re-charging.

## Headline numbers (from end-to-end simulation)

| | Best case | Notes |
|---|---|---|
| Working fluid | CaCl₂·6H₂O ↔ CaCl₂·2H₂O | passive solar pond charging at 95 °C |
| Route | Atacama → Southern Cone | 1,800 km, DNI 3,500 kWh/m²/yr |
| Levelized cost of heat | **$46.5 / MWh-thermal** | competitive with current natural-gas heating |
| Round-trip thermal efficiency | **74%** | solar→stored→delivered after all losses |
| Annual CO₂ avoided per 1 GW-th plant | **832 kt** | displaces gas-fired district heating |
| Pond area | **9.3 km²** | + 12 km² port BoP |
| Freshwater coproduction | **5.9 Mm³/yr** = 1.34 m³/MWh | desert site, captured as condensate under pond cover |
| Cargo-as-fuel (wind + salt-hydration aux) | **7.6%** of cargo | for 1,800 km voyage |

## Figures

- `fig01_energy_density.png` — energy density of candidate working fluids
- `fig02_chem_route_grid.png` — LCOH and round-trip efficiency over chem×route grid
- `fig03_distance_sensitivity.png` — cargo-as-fuel penalty vs voyage distance
- `fig04_wind_assist.png` — sensitivity to wind-augmented propulsion
- `fig05_capacity_scale.png` — LCOH and CO₂ scaling with plant size
- `fig06_charge_depth.png` — CaCl₂ charge-depth tradeoff
- `fig07_system_summary.png` — hero diagram of reference system
- `fig08_climate_impact.png` — climate leverage by deployment scale
- `fig09_diurnal_charge.png` — solar-pond dynamics, 2-week window
- `fig10_energy_waterfall.png` — 100 units of solar DNI → delivered heat
- `fig11_deployment_trajectory.png` — cumulative deployment scenarios vs IEA NZE wedge

## Crisp findings

1. **Cost-optimum architecture exists**: CaCl₂ + passive ponds + short-haul
   shipping clears the $40-60/MWh band on 4 of 6 candidate routes.
2. **Long-haul fails**: Pilbara → N. China and Namibia → NW Europe both
   blow through the budget because cargo-as-fuel consumes >25% of payload.
   Ironically these are the highest-carbon-displacement-per-plant routes.
3. **Freshwater is real**: ~6 Mm³/yr per 1 GW-th plant from condensate.
   In water-scarce source regions this is potentially a co-revenue stream
   comparable in value to the heat itself.
4. **Climate leverage requires Industrial Process Heat as primary market,
   not just district heating**: the district-heating market caps total
   reachable impact at ~0.4 Gt CO₂/yr; including industrial low-T heat
   raises the ceiling to ~2 Gt CO₂/yr — the entire IEA NZE low-T heat wedge.

## Top empirical risk

Multi-cycle salt degradation. Modeling assumes 0.08%/cycle (literature
midpoint). At 0.5%/cycle the LCOH rises from $46 to ~$70/MWh and the project
slips a decade. Bench validation is the binding next step.

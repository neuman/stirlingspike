# Solar Salt Heat Export — One-Page Brief (v0.3)

**Closed-loop solar thermochemical heat export from arid coasts to
dirty-grid winter markets, transported by autonomous wind-primary cargo
vessels (Ladon-class).**

## What

Charge inorganic salt hydrates with desert sun. Ship the dry salt to cold
cities on uncrewed wing-sail freighters. Release stored heat by hydrating
the salt at a district-heating plant. Return the wet salt for re-charging.

## Headline numbers (from end-to-end simulation, v0.3)

| | Short-haul best | Long-haul best |
|---|---|---|
| Working fluid | CaCl₂·6H₂O ↔ CaCl₂·2H₂O (passive pond) | CaCl₂·6H₂O ↔ CaCl₂ (deep CSP) |
| Route | Atacama → Southern Cone (1,800 km) | Pilbara → N. China (8,000 km) |
| LCOH | **$53.8 / MWh-th** | **$100.6 / MWh-th** |
| Round-trip thermal efficiency | **80%** | 72% |
| Annual CO₂ avoided per 1 GW-th plant | 832 kt | **1,533 kt** |
| Pond / CSP field area | 8.6 km² | 6.2 km² |
| Freshwater coproduction | 5.4 Mm³/yr | 2.9 Mm³/yr |
| Fleet size (autonomous wind vessels) | 18 | 31 |
| Round-trip cycle days | 16 | 56 |

## Figures

- `fig01_energy_density.png` — energy density of candidate working fluids
- `fig02_chem_route_grid.png` — LCOH and round-trip efficiency over chem×route grid
- `fig03_distance_sensitivity.png` — voyage cycle days and fleet size vs distance
- `fig04_cruise_speed.png` — LCOH sensitivity to autonomous vessel cruise speed
- `fig05_capacity_scale.png` — LCOH and CO₂ scaling with plant size
- `fig06_charge_depth.png` — CaCl₂ charge-depth tradeoff
- `fig07_system_summary.png` — hero diagram of reference system
- `fig08_climate_impact.png` — climate leverage by deployment scale
- `fig09_diurnal_charge.png` — solar-pond dynamics, 2-week window
- `fig10_energy_waterfall.png` — 100 units of solar DNI → delivered heat
- `fig11_deployment_trajectory.png` — cumulative deployment scenarios vs IEA NZE wedge

## Crisp findings (v0.3)

1. **Two viability tiers, not one.** Short-haul + passive pond + low-density
   salt clears the $40-66/MWh band on 3 of 6 candidate routes. Long-haul +
   linear-Fresnel CSP + deep-dehydrated salt sits at $100-120/MWh — above
   target but no longer architecturally broken.
2. **Long-haul recovery is the v0.3 story.** Replacing cargo-as-fuel with
   autonomous wind-primary shipping cut Pilbara → N. China LCOH from
   $130 to $100/MWh and Namibia → NW Europe from $214 to $120/MWh. The
   highest-CO₂-displacement-per-plant routes are now reachable.
3. **Round-trip thermal efficiency is uniform across routes.** 58–80% on
   every chemistry × route combination, vs. 35–74% in v0.2. The cargo-as-fuel
   loss term that hurt long routes is gone.
4. **Freshwater is real**: 2–6 Mm³/yr per 1 GW-th plant from condensate, a
   plausible co-revenue stream in water-scarce source regions.
5. **Climate ceiling raised.** v0.2 wedge of ~1.2 Gt CO₂/yr now ~1.6 Gt
   CO₂/yr — about 80% of the IEA NZE low-T heat decarbonization wedge,
   contingent on the autonomous-wind fleet build-out happening.

## Top empirical risks

1. **Multi-cycle salt degradation.** 0.08%/cycle assumed; at 0.5%/cycle the
   LCOH rises by ~$25/MWh on every route. Binding bench item.
2. **Autonomous-wind-cargo fleet capacity.** v0.3 needs 15–60 ships per
   plant; vendor (e.g. Ladon Robotics) production capacity becomes a
   first-order deployment constraint.
3. **Cruise speed under realistic wind regimes.** Modeled at 7 kn average;
   sensitivity (Figure 4) is roughly $5/MWh per knot. Real route-specific
   wind statistics not yet plugged in.

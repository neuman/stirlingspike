# Solar Thermochemical Heat Export via Closed-Loop Salt Hydration

**Concept Paper — v0.3 (autonomous-wind-shipping pivot)**
**Status:** Pre-feasibility, modeling complete on revised transport
architecture. Bench-validation items remain open.
**Date:** 2026-04-28

---

## Δ from v0.2

The cargo-as-fuel salt-hydration auxiliary engine has been **dropped** from
the architecture. v0.2 modeling identified it as the weakest link: it is
unproven at marine scale, it forces a destructive coupling between cargo
value and propulsion, and the resulting penalty (~7% on short routes,
>40% on long routes) made the highest-CO₂-displacement routes
(Pilbara → N. China, Namibia → NW Europe) architecturally non-viable.

In its place, the maritime stage now uses **autonomous wind-primary cargo
vessels (Ladon-class)**: uncrewed wing-sail or rotor-rigged ships with no
auxiliary engine, no fossil bunker fuel, and no cargo-as-fuel debit.
Propulsion energy is treated as a free environmental input. The new
binding economic levers are vessel cruise speed, vessel capex, and
in-transit salt inventory.

This change is not cosmetic. It restructures the geographic viability
envelope of the entire system.

---

## Headline change in numbers

| Route | v0.2 best LCOH (cargo-as-fuel) | v0.3 best LCOH (wind-only) | Δ |
|---|---|---|---|
| Atacama → Southern Cone | $46.5 | **$53.8** | +$7 (vessel capex up) |
| Egypt → Black Sea | $56.9 | **$65.8** | +$9 |
| Tunisia → Adriatic | $57.2 | **$64.0** | +$7 |
| Morocco → Baltic | $77.8 | **$82.6** | +$5 |
| **Pilbara → N. China** | $130 | **$100** | **−$30** |
| **Namibia → NW Europe** | $214 | **$120** | **−$94** |

Round-trip thermal efficiency, previously 41–74% across the route set, is
now uniformly **58–80%** (Figure 2 right panel), because the cargo-as-fuel
loss term is gone.

The architectural finding from v0.2 — *"the project is short-haul or it is
nothing"* — **no longer holds**. Long-haul routes are still more expensive
in absolute terms, but they are no longer architecturally broken. The
highest-carbon-displacement-per-plant route (Pilbara → N. China at
1.53 MtCO₂/yr per 1 GW-th) is now within ~50% of the target LCOH band
rather than ~3× outside it.

---

## 1–3. Concept Summary, Innovation, System Architecture

Concept and 7-stage cycle are unchanged. Stage 4 (maritime transport
outbound) and Stage 6 (return) are now executed by autonomous
wind-primary vessels. Stage 4's cargo-as-fuel auxiliary is removed.

## 4. Working Fluid Candidates — UPDATED RANKING

Choice of chemistry now depends on **route length**, because vessel fleet
size scales inversely with cargo energy density. Higher density →
fewer voyages → smaller fleet → lower vessel capex, which can outweigh
the CSP-vs-pond field capex differential at the source.

| System | Theoretical kWh/t | Best route class | LCOH on best route |
|---|---|---|---|
| **CaCl₂·6H₂O ↔ CaCl₂·2H₂O (passive pond)** | 423 | **Short-haul ≤2,500 km** | $53.8 (Atacama) |
| **CaCl₂·6H₂O ↔ CaCl₂ (deep, CSP)** | 901 | **Long-haul ≥3,000 km** | $82.6 (Morocco), $100.6 (Pilbara) |
| MgSO₄·7H₂O ↔ MgSO₄ (CSP) | 888 | Long-haul, similar to deep CaCl₂ | $90.7 (Morocco) |
| Mg(OH)₂ ↔ MgO (CSP trough) | 558 | Dominated | — |
| Ca(OH)₂ ↔ CaO (CSP tower) | 515 | Dominated | — |

The chemistry × route grid (Figure 2) now shows two distinct optimal
regions: passive CaCl₂ for the four shortest routes, deep CaCl₂ for the
two long routes.

## 5. Performance Targets — RESOLVED (v0.3)

### Reference case: CaCl₂ passive on Atacama → Southern Cone

| Quantity | v0.1 target | v0.3 result |
|---|---|---|
| Cycle energy density | ≥150 kWh/t | 423 kWh/t (theoretical) |
| Pond surface area | 5–10 km² | **8.6 km²** |
| Solar→stored efficiency | ≥15% | **17%** |
| Round-trip thermal efficiency | ≥40% | **80%** |
| Freshwater coproduction | 0.3–0.7 m³/MWh | 1.24 m³/MWh |
| Cruising speed | 8–12 kn | **7 kn** (autonomous wind-only) |
| Cargo fraction consumed for propulsion | ≤10% | **0%** (wind-only) |
| Fleet size for 1 GW-th plant | TBD | **18 vessels** |
| Round-trip cycle days | TBD | 16 days |
| LCOH | $40–60/MWh | **$53.8/MWh** |

### Long-haul case: CaCl₂ deep CSP on Morocco → Baltic

| Quantity | v0.3 result |
|---|---|
| Pond / CSP field area | 6.0 km² (linear-Fresnel trough) |
| Round-trip thermal efficiency | 73% |
| Fleet size for 1 GW-th plant | 17 vessels |
| Round-trip cycle days | 28 days |
| LCOH | **$82.6/MWh** |

The 4-route short-haul portfolio (Atacama, Egypt, Tunisia, Morocco) all
clear $90/MWh. Atacama, Egypt, and Tunisia clear the original $40–60
target band at vessel cruise speeds ≥9 kn (Figure 4); at the 7-kn design
midpoint Atacama is in band, Egypt and Tunisia at $63–66 are within 10%
of band.

## 6. Geographic Pairings — RESOLVED (v0.3)

| Route | Distance | Best chem | Best LCOH | CO₂ avoided / GW-th-plant·yr |
|---|---|---|---|---|
| Atacama → Southern Cone | 1,800 km | CaCl₂ passive | **$53.8** | 832 kt |
| Tunisia → Adriatic | 1,700 km | CaCl₂ passive | **$64.0** | 920 kt |
| Egypt → Black Sea | 2,300 km | CaCl₂ passive | **$65.8** | 1,183 kt |
| Morocco → Baltic | 4,000 km | CaCl₂ deep CSP | $82.6 | 1,270 kt |
| **Pilbara → N. China** | 8,000 km | CaCl₂ deep CSP | **$100.6** | **1,533 kt** |
| Namibia → NW Europe | 11,500 km | CaCl₂ deep CSP | $120.6 | 1,051 kt |

The Pilbara → N. China line is the most strategically significant entry in
this table. Northern China runs ~300 GW-th of coal-fired district heating
at ~350 kgCO₂/MWh. A single 1 GW-th plant on this route avoids 1.53 Mt CO₂
per year — roughly twice the per-plant impact of any short-haul route.
Under v0.2 the route was non-viable at $130/MWh. Under v0.3 it is at
$100/MWh, ~70% above the target band but closing.

## 7. Market and Impact — UPDATED

Same primary market (district heating + industrial low-T process heat).
The architectural change especially benefits the long-haul market access
to **Northern China** and **Northern Europe via the Atlantic route**,
which together represent over half of global dirty-grid district-heating
load.

## 8. Critical Open Questions — UPDATED

| # | Question | v0.3 status |
|---|---|---|
| 1 | Multi-cycle salt stability | **Highest priority bench item.** Unchanged. |
| 2 | Achievable charge state via passive solar | Resolved. |
| 3 | Closed-loop vs hydrated-salt-sale economics | Resolved (qualitative): closed-loop wins above ~$35/tCO₂. |
| 4 | Customer-side reactor design | Bench item. |
| 5 | Maritime configuration | **Reframed.** Cargo-as-fuel is gone; new question is vendor capacity to scale autonomous wind cargo vessels to fleet sizes of 15–60 ships per plant. |
| 6 | Host country framework | Outside model scope. |
| 7 | Customer adoption pathway | Outside model scope. |
| 8 | **Autonomous vessel availability** (NEW) | Vendor (e.g. Ladon Robotics) class capacity, capex, classification, and sea-state envelope are now top-line input parameters. The model uses conservative midpoints; sensitivity in Figure 4 shows LCOH is roughly linear in cruise speed across the 4–11 kn range. |

## 9. Next Steps

1. **Engage Ladon Robotics (or comparable autonomous wind-shipping
   vendor)** to replace the v0.3 vessel-class midpoints with vendor
   specifications: actual cruise speed distribution, payload class, capex,
   classification status, and route-suitability map.
2. **Atacama → Southern Cone first conversation** unchanged — still the
   lowest-LCOH route.
3. **Add a second front: Pilbara → N. China feasibility study.** Given
   the long-haul recovery from v0.2 to v0.3, this route now warrants
   serious examination. The carbon prize per plant is largest of any
   route in the model.
4. **Salt-cycle stability bench validation** unchanged — still the
   binding empirical risk.
5. **Pilot specification** updated: 100 kW-th pilot at Mejillones with a
   single autonomous-wind drone running a representative voyage cycle,
   and a parallel 200-cycle salt stability bench at a partner lab.

## 10. Summary

The autonomous-wind-shipping pivot **eliminates the v0.2 architectural
showstopper** for long-haul routes and roughly halves the LCOH on the
most carbon-leveraged route in the candidate set (Pilbara → N. China,
$214 → $100/MWh after additionally also picking the right chemistry).
Short-haul economics take a small hit (+$5–9/MWh from higher vessel
capex) but remain comfortably in or near the target band.

The recommended architecture now reads:

> **CaCl₂ thermochemical storage; autonomous wind-primary cargo vessels;
> two viability tiers: (a) short-haul + passive pond + low-density salt,
> (b) long-haul + linear-Fresnel CSP + deep-dehydrated salt.**

## 11. Climate Impact at Scale (v0.3)

Per-plant CO₂ avoided:

| Route class | LCOH band | CO₂ avoided / GW-th-plant |
|---|---|---|
| Short-haul to clean-ish grid | $54–66 | 0.8–1.2 Mt/yr |
| Mid-haul to coal-leaning grid | $83–88 | 1.27 Mt/yr |
| Long-haul to coal-heavy grid | $100–120 | 1.5 Mt/yr |

Deployment trajectories from v0.2 are unchanged in shape, but with v0.3
the **Fast scenario (2 GW-th cumulative by 2050) now intersects more
dirty-grid markets, raising the achievable wedge from ~1.2 Gt CO₂/yr
in v0.2 to ~1.6 Gt CO₂/yr** — about 80% of the IEA NZE low-temperature
heat decarbonization wedge.

The architecture is, with this change, plausibly a sufficient-on-its-own
lever for the low-T-heat decarbonization gap, contingent on:
1. Salt-cycle stability ≥1,000 cycles at modest degradation (binding).
2. Autonomous wind-cargo fleet capacity reaching ~5,000 vessels by 2050
   (Ladon-class or peer vendors at scale).
3. Solar charging field capex curves declining at the historical CSP rate
   (~6%/yr).

---

*Document conventions: v0.3 supersedes v0.2 §4–§11. Earlier versions are
retained in git history for traceability of the architectural decision
record.*

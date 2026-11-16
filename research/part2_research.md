# Part 2 Research Notes (first pass, 2026-11-15)

Convention: **"Optimistic pick"** is the value the Part 2 notebook will use by default, following the optimism principle (take the optimistic end of each cited range). "Range" is what sources support. Items marked ⚠️ come from weak or secondary sources, or are my own estimates; check them before publishing.

---

## Headline findings

1. **Google's Suncatcher cost comparison leaves out the satellite hardware, so the solar arrays are left out too.**
   - The paper compares only *launch* $/kW-yr against *terrestrial energy* $/kW-yr: $810/kW-yr at $200/kg vs. $570–3,000/kW-yr on the ground.
   - It explicitly excludes "satellite design and manufacturing costs" (§4.4).
   - That gap is exactly your thesis. Even at $10/W, a 5-year array costs ~$2,000/kW-yr. At $40/W it's ~$8,000/kW-yr, which is 10× Suncatcher's launch figure. **This should anchor Part 2.**
2. **At 550 km dawn-dusk, radiation is not the problem.**
   - Suncatcher estimates ~150 rad(Si)/yr behind 10 mm of Al, or 750 rad over 5 years.
   - Trillium TPUs showed HBM irregularities only at 2 krad and no hard failures to 15 krad.
   - At 7,000 km (inner-belt protons) no clean dose number turned up. It is orders of magnitude worse, and the protons are very hard to shield. That makes the orbit trade a strong section.
3. **In dawn-dusk orbit the Sun is roughly perpendicular to the orbit plane.** Solar arrays (and radiators, which must be edge-on to the Sun) can fly **edge-on to the velocity vector**. Drag area is therefore small even for a huge satellite, an under-appreciated point in favor of a 550 km dawn-dusk orbit. ⚠️ My own reasoning; check it with the CAD attitude model.
4. **SpaceX filed with the FCC for up to 1 million orbital data center satellites** (Jan 30, 2026; accepted as FCC DA 26-113). They would sit at 500–2,000 km with optical links. This is useful context for "why might they go higher."
5. **Solestial was acquired by York Space Systems (closed June 4, 2026, ~$67M).** Its $40/W and 200 W/kg figures are still *targets* from a 2023 SBIR. No delivered price or flown array-level W/kg has been published.

---

## A. Solar arrays

| Tier | Array W/kg | $/W (array) | Radiation | Status / source |
|---|---|---|---|---|
| Heritage rigid 3J GaAs | ~50 | $250–450 (cell level) | Best | Surrey review, Acta Astronautica 2026 |
| Roll-out 3J (ROSA) | 100–120 headline; ~70–124 across the product table | ~$100+ ⚠️ | Good | Redwire ROSA product table; pv magazine |
| Starlink-class silicon | 78–100 (Gen 1.x) ⚠️ | unknown; ~$5–20 in analyst scenarios ⚠️ | ~2.6× worse than 3J for the same coverglass | secondary |
| Rad-tolerant annealing Si (Solestial) | **200 target** | **$40 target** | 96% Voc after a 10-yr-LEO-equivalent dose, annealing at ~80–90 °C (lab, open circuit) | SBIR 2023, CEA test |
| Commercial semi-flex Si (Starlight Classic) | ~280 blanket-only ⚠️ (900 g/m², 19%) | $11.20 ⚠️ | ? | secondary |
| Next-gen thin PV (Mach33 assumption) | — | $9 ⚠️ | ? | analyst assumption |

- Cell-level comparison (Surrey review): Si HJT ~920–1,000 W/kg vs. 3J ~455–505 W/kg. Terrestrial Si cells cost $0.28–0.39/W, but coverglass is the main remaining cost for space silicon.
- Satellite-level check: Suncatcher's Starlink v2 mini is ~28 kW / 575 kg, or **~49 W/kg for the *whole satellite***.
- **Optimistic pick: 200 W/kg, $10/W, 1%/yr degradation.**
  - $5/W is a stretch sensitivity.
  - $40/W is "Solestial target."
  - $100+/W is "heritage today."
  - Part 1 used $50/W.
- Area: keep 400 W/m² at the bus (Part 1).

## B. Radiation and degradation by orbit

| Orbit | Electronics TID | Array loss | Note |
|---|---|---|---|
| 550 km dawn-dusk SSO | ~150 rad/yr @10 mm Al (Suncatcher, 650 km) | 85–95% remaining after 5 yr ⚠️ | SSO's high inclination passes through the South Atlantic Anomaly and polar horns more often than low-inclination orbits do |
| 7,000 km | inner-belt protons; no clean number yet | analyst cites 23% proton + 11% electron loss in 1 yr at 10,000 km ⚠️ | ⬜ **Open:** SPENVIS run (free; you'd need an account) |

- **Optimistic pick at 550 km: 1%/yr array loss, and GPUs survive 5 years.**

## C. Thermal hardware

| Source | Areal density | kg/kW |
|---|---|---|
| Pumped-loop deployable panel, total system (thesis) | 1.9 kg/m² radiating (3.9 planform) | ~9.5 |
| Loop-heat-pipe deployable radiator (2001) | — | <10 |
| Redwire Q-Rad (product) | 3.5–4.9 | — |

- **Optimistic pick: keep 2.0 kg/m² *including* heat transport.**
  - The pumped-loop thesis supports ~1.9 kg/m² for a whole system.
  - Part 1's 476 kg for 132 kW is ~3.6 kg/kW, already well below the ~10 kg/kW heritage numbers.
  - Note that the 50 °C thesis radiator ran colder than our 60 °C one.

## D. Launch (Starship)

| Item | Range | Optimistic pick |
|---|---|---|
| Payload to LEO, reusable | >100 t (SpaceX official); 100–150 t; V3 ~200 t claimed ⚠️ | **150 t**; 200 t as a sensitivity |
| Payload bay | Starship Users Guide (rev 1.0, Fig. 4): 8 m envelope, full width only up to 8 m of height, then narrowing to 3.6 m at 17.24 m (~680 m³); extended option up to 22 m (~920 m³ if the extra height is all full-width) | **Guide envelope with the 22 m extended option (~920 m³).** See D.1 |
| SSO penalty vs. due-east | no published Starship number | ⬜ **Open:** estimate from Δv (polar/retrograde loses Earth's ~0.4 km/s rotation boost, plus plane geometry); likely ~15–25% ⚠️ |
| Price $/kg | today: expendable ~$600–1,000; Suncatcher: <$200 by ~2035; 10× reuse ≈ $60 cost / <$250 price; Musk target ~$100 (~$10M/flight); 100× reuse floor ~$15–38 | **$100/kg default**; sweep $2,500 → $15 |

### D.1 Starship payload envelope and launch loads (Starship Users Guide, rev 1.0, March 2020)
- **Envelope (Fig. 4), height station → radius [m]:** 0–8 → 4.00; 9 → 3.85; 10 → 3.68; 11 → 3.49; 12 → 3.27; 13 → 3.04; 14 → 2.78; 15 → 2.51; 16 → 2.20; 17.24 → 1.80.
  - Volume ≈ 680 m³ standard. "An extended payload volume is also available for payloads requiring up to 22 m of height": ≈ 920 m³ if the extra 4.76 m is all added to the full-width section ⚠️ (the guide gives no drawing of it).
  - **Effect on the notebook:** the flat-pack plate (6.4 × 4.6 m) only fits in the full-width section. The first flat-pack (6.4 × 4.6 m plate) fits 13 per flight (standard) or 21 (extended), against 35 in an idealized 8 m × 22 m cylinder. Applied in the notebook (Section 10.1) with the extended option; a re-laid-out 5.7 × 5.0 m plate, 0.50 m thick, fits 28. The tower fits 11.
- **Load factors (Fig. 5):** up to 6 g axial with ±0.5 g lateral; up to ±2 g lateral at 3.5 g axial; down to −2 g axial. The notebook's 6 g axial matches. Lateral loads are not used yet.
- **Payload:** "over 100 metric tons to LEO" at full reuse. No SSO figure.
- **Starlink V3 on Starship:** ~60 satellites per flight at ~1,800–2,000 kg each is SpaceX's target ⚠️ (secondary sources), so a ~2.7 t satellite at 35 per flight is plausible by mass.
- **Structure mass rule of thumb:** ~20% of dry mass for structure and mechanisms (SMAD, via secondary) ⚠️. The flat-pack CAD structure is 69 kg, under 3%, because only the corner posts are sized. The deck tubes under the compute trays would see ~1,200 MPa at 6 g against a 300 MPa allowable.

## E. Bus and drag
- Drag at 550 km: solar max density ~2–5×10⁻¹³ kg/m³ ⚠️. At A/m = 0.01 m²/kg that is ~6 m/s per year of Δv. It scales linearly with A/m, but see headline 3: the arrays can fly edge-on.
- ⬜ **Open:** an MSIS density value, plus actuator sizing from the CAD MOI.

## F. Terrestrial baseline ("viable" means beating this)

| Item | Range | Source |
|---|---|---|
| Datacenter shell & core (excl. IT, land) | $10.7M/MW (JLL 2025 global), $11.7M/MW (Cushman & Wakefield US avg), ~$20M/MW AI-optimized ⚠️ | JLL, C&W, Archdesk |
| Energy | $570–3,000/kW-yr ($0.06–0.25/kWh, PUE 1.09–1.4) | Suncatcher §4.4 |
| **Optimistic-for-space pick** | **$20M/MW build + $1,500/kW-yr energy, over 5 yr** | → the space premium can be ~**$27.5/W of compute** and still break even |

**Rough "what has to be true" preview:**
- The ground baseline works out to ~$27.5/W per watt of compute, to cover everything space-specific: arrays, radiators, bus, and launch.
- The arrays need ~1.1 W per W of compute.
- So **the array alone must cost well under ~$20/W**. The $40/W Solestial target fails on arrays alone, and $10/W leaves room for everything else.
- ⚠️ This is a back-of-envelope figure; the notebook will compute the real one.

## G. Comparators
- **Google Suncatcher:**
  - 650 km dawn-dusk SSO, 81-satellite 1 km cluster, TPU radiation results as above.
  - Launch learning curve ~20%.
  - <$200/kg by ~2035 needs ~370,000 t of extra cumulative launch mass (~180 Starship flights/yr).
- **Starcloud:**
  - Starcloud-1 (~60 kg, one H100) launched Nov 2, 2025.
  - Starcloud-2 carries the "largest commercial deployable radiator."
  - The 5 GW vision needs ~4 km × 4 km of arrays, with radiators about half that size.
  - $170M Series A at a $1.1B valuation (Mar 2026).
- **SpaceX:**
  - FCC filing for 1M satellites at 500–2,000 km.
  - First compute satellites reportedly in 2027 ⚠️.
  - Builds on Starlink V3 ⚠️.
- **Handmer:** ~$50,000/kW all-in for a V3-derived satellite with ~130 kW of solar ⚠️ (secondary).

---

## Open items
- [ ] SPENVIS runs (550 km SSO vs. 7,000 km): array fluence and electronics dose. Needs your account.
- [ ] Starship SSO payload penalty (Δv estimate in the notebook).
- [x] Dawn-dusk eclipse season at 550 km (Part 2 notebook, Section 3): ~98 days/yr with eclipses, up to ~22 min per orbit. **Annual sunlight is 95.1%**, about equal to Part 1's 95.3% at 7,000 km, not "near-continuous." Off-angle sunlight (β runs 59–90°) lowers compute availability to ~93% with wings that roll to follow the Sun (Section 3.4).
- [ ] Real sources for radiator hardware $/m² and bus cost. These were Part 1 placeholders, and they now decide the result once arrays are cheap.
- [ ] Read the Surrey review in full ("The return of silicon solar cells to space") for array-level, not cell-level, numbers.
- [ ] Solar-max density at 550 km from NRLMSIS.
- [x] Apply the real Starship envelope (D.1) to the packing, and re-optimize the flat-pack for it: 28 per flight (notebook Section 10.1).
- [ ] Size the flat-pack deck for bending and lateral loads (D.1).

## Sources
- Google Suncatcher paper: https://arxiv.org/abs/2511.19468 · blog: https://research.google/blog/exploring-a-space-based-scalable-ai-infrastructure-system-design/
- Surrey review: https://www.sciencedirect.com/science/article/abs/pii/S0094576526003644 · summary: https://phys.org/news/2026-09-silicon-solar-cells-satellite-power.html
- Solestial SBIR targets: https://www.militaryaerospace.com/power/article/14301265/nasa-selects-solestial-for-space-solar-array · annealing test: https://pv-magazine-usa.com/2023/03/28/ultrathin-solar-cells-self-repair-radiation-damage-in-space · SpaceWERX: https://www.militaryaerospace.com/power/article/55303658/spacewerx-awards-solestial-12-million-contract-to-advance-fast-build-solar-array-technology · York acquisition: https://orbital-intel.com/companies/solestial/
- Redwire ROSA: https://rdw.com/product-archive/power/rosa/ · https://pv-magazine-usa.com/2025/07/03/redwire-deploys-60-kw-roll-out-solar-array-for-the-first-lunar-orbit-space-station/
- Radiators: https://scholar.colorado.edu/downloads/k643b230p · https://saemobilus.sae.org/content/2001-01-2194 · https://satsearch.co/products/redwirespace-q-rad-deployable-radiator
- Starship: Users Guide rev 1.0 (https://www.spacex.com/media/starship_users_guide_v1.pdf, now offline; mirrored by the NYT document viewer) · https://www.universetoday.com/articles/want-to-buy-flights-on-starship-heres-the-new-spacex-payload-users-guide-no-prices-unfortunately · https://new.spacex.com/vehicles/starship · https://www.eoportal.org/other-space-activities/starship-of-spacex · https://en.wikipedia.org/wiki/SpaceX_Starship · https://payloadspace.com/what-to-expect-from-starship-v3/ · https://techcrunch.com/2026/05/26/starships-path-to-reusability-looks-murky-after-spacexs-s-1/
- Datacenter cost: https://irei.com/news/cushman-wakefield-releases-2026-data-center-development-cost-guide-citing-21-rise-in-per-mw-construction-costs/ · https://www.gleeds.com/media/umybrjx1/global-market-report-data-centres.pdf · https://archdesk.com/blog/global-ai-data-center-construction-2026
- Radiation: https://ntrs.nasa.gov/api/citations/20220011775/downloads/Mission_Radiation_Modeling_STI.pdf
- SpaceX FCC filing: https://docs.fcc.gov/public/attachments/DA-26-113A1.pdf · https://satnews.com/2026/01/31/spacex-files-fcc-application-for-million-satellite-orbital-data-center/ · https://www.datacenterdynamics.com/en/news/spacex-files-for-million-satellite-orbital-ai-data-center-megaconstellation/
- Starcloud: https://www.satnow.com/news/details/4968-starcloud-raises-170-million-usd-series-a-at-1-1-billion-usd-valuation · https://www.slashgear.com/2016792/nvidia-gpu-spacex-rocket-launch/
- Drag: https://ui.adsabs.harvard.edu/abs/1989JSpRo..26..439W/abstract · https://arxiv.org/pdf/2508.19549

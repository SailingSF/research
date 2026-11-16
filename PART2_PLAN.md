# GPUs in Space, Part 2: Plan

**Question for Part 2:** *At what combination of launch $/kg, solar-array $/W and W/kg, and orbit does a space GPU datacenter become viable?*
**Working thesis:** Solar arrays are the biggest single driver of the space premium, ahead of radiators. Launch cost works through mass, so arrays hurt twice: once as hardware and once as launch mass.

---

## 0. Where Part 1 actually landed (from the notebook)

Reference: 200 MW average compute, 7,000 km, 90 °C GPUs, sunlight-only, beta mix 30/45/20/5.

| Per satellite (weighted avg) | Mass | Hardware $ |
|---|---|---|
| Compute (NVL72-class, 120 kW) | 750 kg | $2.70M |
| Radiators (243 m² @ 2 kg/m²) | 476 kg | $0.48M |
| Solar arrays (132 kW @ 200 W/kg, $50/W) | 660 kg | $6.60M |
| Bus/structure (25% of total) | 629 kg | $0.50M |
| **Total** | **2,514 kg** | launch $13.7M @ $5,453/kg delivered |

Fleet: 1,750 sats, 4,400 t, $42.0B CAPEX, **$37.25B space premium** ($21.3M/sat).

**Preview of the "where the $37B goes" section.** Each component gets its own hardware cost, plus the launch cost of its mass, plus its proportional share of bus mass (÷0.75):

| Component | Hardware | Launch share | Total | % of premium |
|---|---|---|---|---|
| Solar arrays | $6.60M | $4.80M | **$11.4M** | **~54%** |
| Compute (launch only; the GPUs are paid for on Earth too) | — | $5.45M | $5.45M | ~26% |
| Radiators | $0.48M | $3.46M | $3.94M | ~19% |
| Bus fixed cost | $0.50M | — | $0.50M | ~2% |

So the arrays are already over half of the premium, and that is with the **optimistic** Part 1 array assumption.

### Corrections and caveats on the analyst's input
1. **The notebook already assumed a best-case array: 200 W/kg at $50/W**, anchored to Solestial's target. The analyst's tiers (50–110 W/kg, $100–450/W) are all *worse* than this. So their table really says "Part 1 was optimistic on arrays", which makes the thesis stronger.
2. **The array has to supply about 132 kW, not 114 kW.** 114 kW is the average delivered compute. The array must also carry the 120 kW nameplate plus 10% overhead.
3. **Solestial makes radiation-tolerant silicon cells, which it says self-anneal.** That means Part 1's $/W anchor is already a bet on cheap space silicon, and the clean "GaAs vs. silicon" split is muddier than the analyst suggests. This needs checking.
4. **Cell-level and array-level $/W are mixed together.** The $250–450/W figure is for cells. Terrestrial silicon at $0.x/W is not space-qualified. The real comparison is between space arrays at the array level: cells + coverglass + substrate + deployment + harness.
5. **The $5,500/kg is the price delivered to 7,000 km.** It is $2,500/kg to LEO multiplied by the 2.18× Hohmann/kick-stage factor. At 550 km that multiplier disappears.
6. **Radiation at 7,000 km also hits the GPUs (total dose and single-event effects), not only the arrays.** This may be a stronger argument against 7,000 km than array degradation is.
7. **SolidWorks will not give "true structure mass" by itself.** CAD returns the mass of the geometry you draw. Without structural analysis it is a better-founded bottom-up estimate, not ground truth. Its strongest uses are stowed volume, mass properties/MOI, and pictures.

### Gaps in Part 1 that Part 2 should close
- **No definition of "viable."** We need a terrestrial baseline: datacenter infrastructure $/MW plus electricity over the satellite's life, giving $/kW-yr. The premium is currently about **$186M per MW** of average compute.
- **No lifetime or amortization.** No array degradation, no satellite life, no GPU refresh cycle.
- **No heat-transport mass.** Pumped loops, fluid, cold plates, and manifolds are missing. Only the radiator panel mass is counted.
- **No drag or station-keeping.** This matters a lot for 700+ m² of surface at 550 km.
- **No volume constraint on launch.** A launch is limited by both mass and volume.
- Stale text: Section 7 markdown says compute costs $16,000/kW, but the code uses $22,500/kW.

---

## Phase 0: Setup and audit (~½ day)
- [ ] Create branch `part2`.
- [ ] **Install Python 3.14 on this Windows machine.** Only the Microsoft Store stub is present now. Then create the venv and add `pywin32` (SolidWorks COM) to `requirements.txt`. Add a PowerShell setup path to `README.md` and `scripts/` (per AGENTS.md).
- [ ] Rerun the Part 1 notebook top to bottom and confirm it reproduces $37.25B.
- [ ] **SolidWorks API smoke test.** SOLIDWORKS 2026 (3DEXPERIENCE "SOLIDWORKS Design") is installed at `E:\max\solidworks`, and `SldWorks.Application` is registered for COM. Check that we can:
  - attach from Python,
  - open a part,
  - rebuild after changing a global variable linked to an external file,
  - read mass properties,
  - save locally (3DEXPERIENCE licenses can restrict local saves).
  - Also check whether SOLIDWORKS Simulation is included in the license.
- [ ] Fix the $16k vs. $22.5k/kW text inconsistency in Part 1.

## Phase 1: Research (~3–5 days). Each item becomes a cited assumption row.
**A. Solar arrays** (the core of the post). Get array-level, not cell-level, numbers for:
| Tier | W/kg | W/m² | $/W (array) | Radiation tolerance |
|---|---|---|---|---|
| Heritage rigid 3J GaAs | | | | |
| Roll-out 3J (ROSA/iROSA, Redwire) | | | | |
| Starlink-class silicon (estimate) | | | | |
| Solestial-type rad-tolerant Si (annealing) | | | | |
| Speculative (thin-film / perovskite) | | | | |

**B. Radiation by orbit:** 550 km dawn-dusk SSO, ~2,000 km, 7,000 km, ~10,000 km (slot region).
- Array power loss per year by cell type and coverglass thickness. Use SPENVIS (free ESA tool with AE9/AP9-type models; you run it) or published degradation curves.
- GPU/accelerator dose tolerance. Google's Suncatcher TPU radiation testing is a useful anchor.

**C. Thermal hardware:** Check the 2 kg/m² radiator panel assumption against deployable heritage hardware. Add pumped-loop and heat-transport mass per kW.

**D. Launch:**
- Starship payload envelope (about 9 m diameter by ~17–22 m), payload mass to 550 km SSO, and the most optimistic published $/launch.
- A $/kg trajectory to sweep: $2,500 → $1,000 → $500 → $200 → $100.
- The "mature Starship" assumptions behind $200/kg.

**E. Bus:**
- Drag at 550 km for a large-area spacecraft, and the electric-propulsion propellant needed per year.
- Disturbance torques (gravity gradient, drag, solar pressure) to wheel/CMG sizing.
- Optical inter-satellite link mass.

**F. Terrestrial baseline for "viable":**
- Datacenter infrastructure $/MW, excluding IT.
- Industrial electricity $/kWh.
- PUE.
- Build time (a speed-to-power argument may matter more than cost).

**G. Comparators:**
- Google Project Suncatcher (dawn-dusk SSO, its own launch-cost break-even analysis).
- Starcloud (H100 already in orbit).
- SpaceX/xAI statements.
- Cite these and contrast them with our numbers.

## Phase 2: Model upgrades (~3–4 days)
- [ ] Create a standalone `space_gpu_datacenter_part2.ipynb`. Copy the Part 1 functions it needs (radiator sizing, sunlight fraction, launch cost) into it, with a note naming where each came from in Part 1. Assumptions stay in one centralized cell, with optimistic values flagged.
- [ ] **Cost attribution by subsystem**, including launch shares (the table above), as a chart.
- [ ] **Array technology tiers** as named scenarios: W/kg, W/m², $/W, degradation.
- [ ] **Lifetime model:** size arrays for end-of-life power via orbit radiation and cell type. Satellite life is a parameter (5 yr default, matching GPU refresh). Output **$/kW-yr of delivered compute**.
- [ ] **Orbit: 550 km dawn-dusk SSO is the primary case.** It offers near-continuous sun, low radiation, and no transfer penalty, but drag costs propellant.
  - Model the eclipse season as a short annual dip in sunlight fraction.
  - Then a "why we might go higher" section: compare against 7,000 km (Part 1 beta mix) on drag propellant, coverage, congestion, and radiation.
- [ ] **Launch packing:** sats per launch = min(mass-limited, volume-limited), using the stowed volume from CAD. Effective $/kg = launch price ÷ mass actually flown.
- [ ] **Break-even solver:** for a viability threshold (premium $/kW-yr ≤ terrestrial infrastructure + power), plot contours of:
  - launch $/kg vs. array $/W,
  - launch $/kg vs. array W/kg,
  - for each orbit.

## Phase 3: SolidWorks reference satellite (~1–2 weeks)
**Approach:** one parametric assembly driven by a text file that the notebook writes. It has two configurations, **Stowed** and **Deployed**.

```
notebook / space_dc_model.py
   └─ writes cad/params.txt  ("array_area_m2"=330, "rad_area_m2"=243, "n_gpu"=72, ...)
SolidWorks: Equations → Global Variables linked to cad/params.txt
   └─ cad/run_sw.py (pywin32): open assembly → rebuild → for each config:
        mass, CG, MOI, stowed bounding box → cad/mass_props.json
notebook reads mass_props.json → per-subsystem mass table, sats/launch, ADCS sizing
```

**Subassemblies.** Each gets real materials or areal densities so its mass is meaningful.
1. **Compute module:** a box with cold plates sized to 72 GPUs. Mass is held at the 750 kg assumption, but it gets real dimensions.
2. **Thermal:**
   - deployable radiator panels (Al honeycomb with embedded heat pipes, sized by `rad_area`),
   - hinges and deployment booms,
   - pumped-loop manifolds and fluid.
3. **Power:**
   - two wings, either roll-out (ROSA-like) or rigid,
   - boom, solar array drive (SADA), harness,
   - wing area = power ÷ W/m².
4. **Bus:**
   - primary structure (central cylinder or truss),
   - Hall thrusters plus xenon/krypton tank (sized from drag/Δv),
   - reaction wheels or CMGs, avionics, optical terminals.
5. **Launch envelope reference body:** the Starship payload bay, with N satellites stacked.
6. **Unmodeled mass margin:** harness, MLI, fasteners. State it as an explicit %.

**Outputs that feed back into the notebook**
- A bottom-up mass table vs. Part 1's flat 25% bus fraction.
- **Sats per Starship by volume vs. by mass.** This tells us whether $/kg understates the real launch cost.
- MOI → disturbance torques → actuator mass, which adds mass back to the bus. Iterate once.
- **Run 2–3 design points** (e.g. 100 / 200 / 400 W/kg arrays) and fit scaling laws (structure kg per m² of array). That turns the CAD results into notebook coefficients that the sweeps and explorer can use, not a single anecdote.
- Renders for the post (SOLIDWORKS Visualize is installed): stowed vs. deployed, and a fairing cutaway.

**Honest limits to state in the post:**
- No structural FEA, unless the license includes Simulation.
- Booms sized by rules of thumb (deployed-frequency targets).
- A concept-level design, not a flight design.

## Phase 4: Analysis (~2–3 days)
- [ ] Sweep launch $/kg from $5,000 to $100, for each array tier and each orbit. Plot space premium per MW and $/kW-yr against the terrestrial line.
- [ ] Recompute "where the money goes" using CAD-calibrated masses.
- [ ] Tornado chart: which single assumption moves the premium most.
- [ ] **"What would have to be true" table:** the combinations of launch $/kg, array $/W, array W/kg, and lifetime that reach break-even.
- [ ] Export break-even data and new sliders for the interactive explorer. The explorer lives in a separate repo (labs.goodatinvesting.com).

## Phase 5: Blog post (~3–4 days)
1. **Recap Part 1:** 1,750 sats and a $37B premium. Why "space premium" is the right framing.
2. **Where the $37B goes:** the attribution chart. Arrays are about half, even with optimistic assumptions.
3. **Solar arrays:** what flies today, what it costs, and why it is either a parts-cost problem (GaAs) or a launch-mass problem (silicon).
4. **The orbit trade:** sunlight vs. radiation vs. launch cost, comparing 7,000 km and 550 km dawn-dusk. Includes the GPUs' own radiation problem and Suncatcher's choice.
5. **Building one satellite in SolidWorks:**
   - renders,
   - mass table vs. the notebook,
   - does it fit in Starship,
   - the attitude-control knock-on.
6. **What would have to be true:** break-even contours and the updated explorer.
7. **What to watch:**
   - Starship price per launch,
   - space-silicon $/W,
   - radiation-tolerant accelerators,
   - in-orbit demos.

## Decisions (2026-11-15)
1. **Primary orbit: 550 km dawn-dusk SSO, the best case.** The post then explains why a real system may still need a higher orbit:
   - drag and station-keeping for large-area satellites,
   - a single terminator plane limits coverage and has an eclipse season,
   - congestion with LEO broadband shells and debris risk,
   - Part 1's 7,000 km result kept as the "higher orbit" comparison.
2. **Code: a standalone `space_gpu_datacenter_part2.ipynb`.** Part 1 stays untouched apart from the $16k/$22.5k text fix. The SolidWorks glue lives in `cad/run_sw.py`.
3. **Reference rocket: Starship only**, using its most optimistic published payload mass and volume. Note that launching into SSO (~97.6° inclination) carries less payload than a due-east launch; research how much.

### Optimism principle (applies everywhere)
Every assumption takes the **most optimistic end of its cited range**. Pessimistic values appear only in sensitivity charts. That gives the post its framing: *"even if everything goes right, here is what still has to be true."* Optimistic examples:
- Starship at $100–200/kg and full reuse,
- best-in-class array W/kg and $/W targets,
- 90 °C+ GPUs,
- no heat-transport or launch-adapter overhead beyond what is needed,
- long satellite life.

Every optimistic choice is labelled in the assumptions cell so readers can see what was granted.

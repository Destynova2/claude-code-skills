# Shared — Metaphor Catalog

> **Cross-skill reference.** The cli-* skills reason through biological, physical, and craft metaphors. Several reuse the *same* metaphor for the *same* underlying idea — this catalog keeps that vocabulary consistent so cross-skill output (especially `cli-cycle` reports) doesn't invent three names for one concept. Reference it as `../../shared/metaphors.md`. Adding a new metaphor? Check here first; reuse the shared meaning rather than coining a synonym.

## Shared metaphors (used by ≥2 skills — keep the meaning aligned)

| Metaphor | Shared meaning | Used by |
|---|---|---|
| **Homeostasis / set point** | a healthy steady state the system returns to; idempotent apply | wizard, resilience |
| **Immune system** | negative/pattern-based checks that catch what happy-path misses | wizard, resilience, pipeline |
| **Tardigrade (cryptobiosis)** | survive a hostile state and revive to an identical baseline (fault tolerance + reproducible restore) | pipeline, wizard, resilience |
| **Genome / contract** | the explicit, single-source definition of intended behaviour | resilience, oci, drift |
| **Germination / seed** | a fixed starting blueprint that unfolds the same way (setup, deterministic start) | wizard, demo (theatre: "same show every night") |
| **Mitosis** | scale the depth of output to the size of the input | hld, resilience, sync, pipeline (tiering) |
| **Pheromone trail** | a path each step reinforces; remove a step and followers get lost | prez (narrative), implicitly demo (beats) |

> When two skills touch the same concept, link to the shared definition in `../../shared/determinism.md` (reproducibility/idempotence) or `../../shared/gate-ladder.md` (proof rungs) rather than re-explaining.

## Skill-specific signature metaphors (identity — do not merge)

| Skill | Signature model | Domain |
|---|---|---|
| `cli-audit-tangle` | topoisomerase (cut points), fire-ant overload (god functions), railway deadlock (cycles), Fiedler vector | biology + spectral graph theory |
| `cli-audit-drift` | crow (intention gap), autophagy (damage isolation), protein folding (conformity), ubiquitin | cell biology |
| `cli-audit-wizard` | axolotl, least action, 2nd law of thermodynamics, Hick's/Miller's laws | biology + physics + HCI |
| `cli-forge-pipeline` | leafcutter / army ants, slime mold, honeybees, mycelium, spores | swarm biology |
| `cli-forge-resilience` | membrane, stress-strain, phase transition, hysteresis, memory cells | biology + materials physics |
| `cli-forge-oci-rootless` | stratigraphy & metallurgy: bedrock, strata, ore/gangue, fault lines, alloy, heat treatment | geology + metallurgy |
| `cli-forge-prez` | peacock display (max signal, min ink) | evolutionary biology |
| `cli-forge-demo` | the theatre: script/blocking, reset the stage, understudy, showstopper | performing arts |
| `cli-forge-chef` | brigade de cuisine (Chef / Sous-Chef / Commis) | kitchen craft |
| `cli-forge-quorum` | Byzantine consensus + Petri nets | distributed systems |
| `cli-forge-perf` | Knuth's roofline (Amdahl's law, latency hierarchy, hot path / cold path) | computer architecture + applied statistics |
| `cli-watermark` | adversary evolution (Gen 0-5), honey-tokens, paper town | security / cartography |

## Rule

A metaphor must **earn its keep** — it should make a hard idea graspable, not decorate. If a reader needs the metaphor explained more than the concept, drop it (KISS). Signature metaphors are part of each skill's identity; the shared ones in the first table must mean the same thing everywhere.

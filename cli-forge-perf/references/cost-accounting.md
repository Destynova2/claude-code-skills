# Comptabilité multi-dimensionnelle (€, watts, CO₂)

La perf n'est pas qu'une histoire de millisecondes : c'est une décision
**économique et physique**. Ce fichier documente le modèle derrière
`scripts/perfloop.py cost` et, surtout, ses **limites** — pour chiffrer un gain
honnêtement, pas pour faire du greenwashing.

## Le modèle (ordres de grandeur)

**Par requête (suppose du temps CPU économisé) :**
```
CPU-secondes/jour économisées = rps × 86400 × (Δt_ms / 1000)
kWh/an = CPU-heures/an × W_par_cœur / 1000 × PUE
€/an   = kWh/an × prix_€/kWh
kgCO₂/an = kWh/an × gCO₂/kWh / 1000
```

**Par instance supprimée (charge 24/7) :**
```
kWh/an = N_instances × W_instance × 8760 / 1000 × PUE
€/an   = kWh/an × prix_€/kWh  (+ facture cloud si €/instance-heure fourni)
```

## Chiffres de référence (2025-2026, à adapter)

| Paramètre | Valeur | Source / note |
|---|---|---|
| Intensité carbone **France** | ~20 gCO₂eq/kWh | RTE 2025, mix >95 % bas-carbone (nucléaire+renouv.) |
| Intensité carbone **UE+** | ~175 gCO₂e/kWh | moyenne UE+CH+NO+UK 2025 |
| Intensité carbone **monde** | ~445 gCO₂/kWh (2024) → ~400 (2027) | IEA |
| Prix élec **entreprise France** | ~0,15 €/kWh (tout compris) | sept. 2025 ; industriel/spot bien plus bas (~0,06-0,09) |
| **PUE** datacenter | ~1,1 (hyperscale) à ~1,5 (moyen) | défaut 1,2 |
| Puissance / cœur sous charge | ~10-15 W | très variable selon CPU ; à mesurer |
| Équivalent voiture thermique | ~120 gCO₂/km | pour traduire les kgCO₂ |

L'intensité carbone varie d'un facteur ~20 entre la France (~20) et un mix
charbonné (~600-800). **Le même calcul, déplacé de pays ou d'heure, change tout.**

## Les garde-fous (lis-les avant de claimer une économie)

- **Latence ≠ énergie.** Le modèle par requête suppose que le temps gagné était du
  **CPU occupé**. Si la latence économisée était de l'**attente I/O** (réseau, DB,
  disque), le CPU dormait déjà → l'énergie économisée est bien moindre. Ne convertis
  pas du wall-clock I/O-bound en kWh.
- **Carbone embarqué (embodied).** Fabriquer un serveur ou un GPU émet beaucoup —
  souvent comparable, voire supérieur, aux émissions d'usage sur la durée de vie
  (surtout edge / matériel court-vécu). **Supprimer une machine** économise ce
  carbone de fabrication amorti, pas seulement les watts. À l'inverse, optimiser le
  logiciel pour repousser un achat de hardware peut être le plus gros gain CO₂ —
  invisible dans un modèle qui ne compte que l'usage.
- **Effet rebond (Jevons).** Rendre une opération 10× moins chère pousse souvent à
  l'utiliser 10× plus → le total n'baisse pas forcément. Ne compte pas une économie
  que tu vas re-dépenser en volume.
- **Marginal vs moyen.** Le gCO₂/kWh *moyen* du réseau diffère du gCO₂/kWh
  *marginal* (ce qu'émet réellement le prochain kWh consommé). Pour une décision,
  le marginal est plus honnête. De même, **carbon-aware scheduling** : lancer les
  batchs quand le réseau est propre (heures/régions bas-carbone) peut diviser le
  CO₂ sans toucher au code.
- **Mesure réelle > modèle** quand l'enjeu est fort : RAPL (Intel), IPMI/BMC, PDU,
  ou les dashboards carbone du cloud donnent la conso réelle, le modèle n'est qu'une
  estimation.

## Cadrage décisionnel

Mets **€/an, watts, kgCO₂/an et coût/utilisateur** sur le **front de Pareto** à
côté des ms (cf. `experiment-method.md` §5). Trois usages :
1. **Prioriser** : 50 € de gain/an ne justifient pas 3 jours de travail + de la
   dette de lisibilité. Le coût d'ingénierie est un axe aussi.
2. **Justifier** : « cette optim retire 2 instances = ~790 €/an + ~158 kgCO₂/an »
   parle plus à un décideur que « −8 ms ».
3. **Savoir s'arrêter** : parfois « assez rapide, on ship » est la bonne réponse —
   l'optimisation a un coût, et la sobriété, c'est aussi ne pas sur-optimiser.

## Checklist coût
1. Le temps gagné est-il du **CPU** (sinon l'énergie économisée est faible) ?
2. Ai-je considéré le **carbone embarqué** (machine évitée) en plus de l'usage ?
3. Y a-t-il un **effet rebond** qui annule l'économie en volume ?
4. Mes chiffres gCO₂/kWh et €/kWh correspondent-ils à **ma région** (et marginal
   vs moyen) ?
5. Le gain **€/CO₂** justifie-t-il le coût d'ingénierie et la perte de lisibilité ?

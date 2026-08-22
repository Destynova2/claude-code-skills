# Data safety review templates / Canevas de travail

## Contents

- A. Décision de conception
- B. Matrice d'invariants
- C. Interleaving
- D. Machine à états
- E. Compatibilité de migration
- F. Pré-mortem
- G. Revue de code
- H. Homéostasie
- I. Rapport final

---

## A. Décision de conception

```markdown
# Database decision — <sujet>

## Verdict provisoire
SAFE | SAFE WITH CONDITIONS | UNSAFE

## Objectif

## Hors périmètre

## Entités, propriétaires et cardinalités

## Sources de vérité

## Sémantique de NULL

## Temps et cycle de vie

## Tenant, autorisation et confidentialité

## Suppression, rétention et restauration

## Accès dominants et volumes

## Hypothèses
```

## B. Matrice d'invariants

```markdown
| ID | Invariant | Portée | Toujours/éventuel | Garantie principale | Défense secondaire | Détection | Réparation | Preuve |
|---|---|---|---|---|---|---|---|---|
| I1 |  |  |  |  |  |  |  |  |
```

## C. Interleaving

```markdown
### Scénario C1 — <nom>

Invariant menacé : I...

| Temps | Acteur A | Acteur B | État PostgreSQL | Observation |
|---|---|---|---|---|
| T0 |  |  |  |  |

Mécanisme choisi :
Pourquoi il ferme la course :
Résultat si retry :
Test PostgreSQL :
```

## D. Machine à états

```markdown
| Commande | Source | Préconditions | Cible | Écritures | Effet externe | Idempotence |
|---|---|---|---|---|---|---|
```

## E. Compatibilité de migration

```markdown
| Application | Schéma | Lecture | Écriture | Verdict |
|---|---|---|---|---|
| ancienne | ancien |  |  | baseline |
| ancienne | nouveau |  |  |  |
| nouvelle | ancien |  |  |  |
| nouvelle | nouveau |  |  |  |
| mixte | nouveau |  |  |  |
```

## F. Pré-mortem

```markdown
| Mode de panne | Invariant | Cause | Prévention | Détection | Confinement | Réparation | Test |
|---|---|---|---|---|---|---|---|
```

## G. Revue de code

```markdown
### <BLOCKER|HIGH|MEDIUM|LOW> — <titre>

Emplacement :
Invariant :
Interleaving ou scénario :
Conséquence :
Correction minimale :
Correction structurelle :
Test de non-régression :
```

## H. Homéostasie

```markdown
| Invariant | Requête d'audit | Fréquence | Métrique/seuil | Alerte | Réparation | Dry-run | Replay |
|---|---|---|---|---|---|---|---|
```

## I. Rapport final

```markdown
# Verdict

# Décision de base de données

# Sources de vérité

# Matrice des invariants

# Lois de conservation

# Machine à états

# Concurrence et idempotence

# Garanties PostgreSQL

# Implémentation SQLx

# Plan de migration

# Tests de preuve

# Homéostasie

# Pré-mortem

# Points non prouvés

- À PROUVER SUR POSTGRESQL RÉEL — ...
```

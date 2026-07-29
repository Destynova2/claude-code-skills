# Worked example — réservation de la dernière unité d'un produit

Cet exemple montre le niveau de raisonnement attendu. Il ne remplace pas l'analyse du projet réel.

## 1. Verdict

`SAFE WITH CONDITIONS`

La réservation peut être rendue atomique avec un `UPDATE` conditionnel et une clé d'idempotence.
Le modèle reste conditionnel à la définition exacte de l'expiration des réservations et à un test
concurrent sur la version PostgreSQL du projet.

## 2. Décision de base de données

- `inventory` possède la quantité disponible par `(tenant_id, sku)`.
- `reservations` possède l'intention de réservation et son cycle de vie.
- Une réservation active diminue `available` exactement une fois.
- Une annulation ou expiration rend la quantité exactement une fois.
- Le tenant vient du contexte authentifié, jamais du payload seul.
- La clé d'idempotence est unique par tenant et commande `reserve_stock`.

## 3. Sources de vérité

| Fait | Source | Copies | Réparation |
|---|---|---|---|
| quantité disponible | `inventory.available` | métriques/cache | recalcul depuis journal de mouvements si présent |
| réservation | `reservations` | projection commande | replay depuis réservations/outbox |
| événement envoyé | `outbox_events` | broker | republication idempotente |

## 4. Invariants

| ID | Invariant | Portée | Garantie principale | Détection | Réparation |
|---|---|---|---|---|---|
| I1 | `available >= 0` | ligne | `CHECK` + update conditionnel | audit négatifs | blocage + reconstruction |
| I2 | une idempotency key ne réserve qu'une fois | tenant/opération | PK idempotence | collisions/hash | retour du résultat mémorisé |
| I3 | une réservation active décrémente une fois | multi-table | transaction + état/version | audit mouvements | replay compensatoire |
| I4 | aucun cross-tenant | multi-table | clés/FKs composites | audit tenant | quarantaine/correction |

## 5. Conservation

```text
stock_physique = disponible + réservé + sorti
```

Pour la commande `reserve(q)` :

```text
disponible_après = disponible_avant - q
réservé_après = réservé_avant + q
q > 0
 disponible_après >= 0
```

## 6. Machine à états

| Commande | Source | Cible | Condition |
|---|---|---|---|
| reserve | absent | active | stock suffisant + idempotence acquise |
| confirm | active | consumed | version courante |
| cancel | active | cancelled | restitution atomique |
| expire | active | expired | lease expiré + version courante |

`cancel` et `expire` sont concurrents : un seul doit restituer le stock.

## 7. Interleaving dangereux

### Sans update conditionnel

| Temps | A | B | État |
|---|---|---|---|
| T0 | lit `available=1` |  | 1 |
| T1 |  | lit `available=1` | 1 |
| T2 | écrit 0 |  | 0 |
| T3 |  | écrit 0 | 0 |

Deux réservations réussissent pour une unité.

### Avec update atomique

```sql
UPDATE inventory
SET available = available - 1
WHERE tenant_id = $1
  AND sku = $2
  AND available >= 1
RETURNING available;
```

Une seule transaction reçoit une ligne. L'autre reçoit zéro ligne et ne crée pas la réservation.

## 8. Frontière transactionnelle

Dans une même transaction :

1. acquérir la clé d'idempotence ;
2. décrémenter le stock conditionnellement ;
3. insérer `reservations(state='active')` ;
4. insérer l'événement d'outbox ;
5. enregistrer le résultat d'idempotence ;
6. commit.

Aucun appel au broker ou au service commande avant le commit.

## 9. SQLx

- utiliser une macro vérifiée pour l'update ;
- considérer zéro ligne comme `InsufficientStockOrMissingSku` ou le distinguer par diagnostic ;
- passer la même transaction à toutes les fonctions ;
- mapper les contraintes d'idempotence et de FK par nom ;
- ne pas reprendre une connexion au pool dans `insert_reservation`.

## 10. Migration

1. `EXPAND` : créer `reservations`, `idempotency_requests`, `outbox_events` ;
2. déployer le code capable de lire les nouvelles structures sans les exiger ;
3. `SWITCH` : activer la réservation atomique ;
4. observer les audits ;
5. `CONTRACT` : retirer l'ancien chemin de réservation.

## 11. Tests

- deux transactions tentent de réserver la dernière unité via une barrier ; une seule réussit ;
- même clé + même payload retourne le même résultat ;
- même clé + payload différent est rejetée ;
- crash simulé après commit avant réponse, puis retry ;
- `cancel` et `expire` concurrents ne restituent qu'une fois ;
- mauvais tenant ne peut lire ni modifier la réservation ;
- outbox rejouée ne crée pas deux effets côté consommateur.

## 12. Homéostasie

Audit périodique :

```sql
SELECT tenant_id, sku
FROM inventory
WHERE available < 0;
```

Audit métier supplémentaire : comparer disponible/réservé/sorti au journal de mouvements si le
journal est la source reconstructible.

## 13. Pré-mortem

| Panne | Invariant | Prévention | Détection | Réparation |
|---|---|---|---|---|
| double requête | I2/I3 | idempotency PK | collision métrique | résultat mémorisé |
| deux derniers stocks | I1/I3 | update conditionnel | test concurrent | aucune correction requise |
| commit puis réponse perdue | I2 | résultat idempotent | retry même clé | renvoyer résultat |
| cancel + expire | I3 | transition/version conditionnelle | audit mouvements | écriture compensatoire |
| publication doublée | effet externe | inbox consumer | compteur duplicates | ignorer doublon |

## 14. Points non prouvés

- À PROUVER SUR POSTGRESQL RÉEL — comportement exact du test concurrent sous le niveau d'isolation choisi.
- À PROUVER SUR POSTGRESQL RÉEL — stratégie de retry SQLx après deadlock/sérialisation.
- À PROUVER SUR POSTGRESQL RÉEL — impact du runner de migration sur les opérations concurrentes d'index.

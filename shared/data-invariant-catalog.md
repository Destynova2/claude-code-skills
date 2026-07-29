# Data invariant catalog / Catalogue d'invariants à examiner

Utiliser ce catalogue comme générateur de questions. Ne pas appliquer mécaniquement toutes les
règles ; retenir celles qui correspondent au domaine.

## Identité et cardinalité

- L'identifiant est-il unique globalement, par tenant, par parent ou par période ?
- Une relation est-elle exactement une, zéro ou une, une ou plusieurs, ou plusieurs ?
- Deux lignes peuvent-elles représenter le même fait avec une casse ou normalisation différente ?
- L'unicité concerne-t-elle seulement les lignes actives ?
- Une entité restaurée peut-elle reprendre son ancien identifiant fonctionnel ?
- Un enfant peut-il exister sans parent ?
- Une référence peut-elle traverser un tenant ?

## Valeurs, unités et bornes

- La valeur peut-elle être négative, nulle ou vide ?
- Quelle est l'unité : centimes, euros, grammes, pièces, secondes, pourcentage ?
- Une valeur change-t-elle de sens selon la devise, le pays ou la version ?
- Quel est le domaine exact d'un pourcentage : `[0,1]` ou `[0,100]` ?
- Quelle précision et quel arrondi sont légaux ?
- Une quantité peut-elle dépasser la capacité ?

## Temps

- S'agit-il d'un instant, d'une date civile, d'une durée ou d'une période ?
- La borne de fin est-elle incluse ou exclue ?
- Deux périodes peuvent-elles se chevaucher ?
- Le temps autoritatif vient-il de PostgreSQL, du client ou d'un fournisseur externe ?
- Un événement en retard peut-il réécrire le présent ?
- Quelle différence entre `occurred_at`, `received_at`, `recorded_at` et `effective_at` ?
- Les données sont-elles bitemporelles : validité métier et historique d'enregistrement ?

## États et workflow

- Quels états sont initiaux, intermédiaires et terminaux ?
- Quelles transitions sont irréversibles ?
- Une commande peut-elle être rejouée ?
- Deux commandes peuvent-elles partir du même état en concurrence ?
- Une transition dépend-elle d'une condition externe qui peut changer avant le commit ?
- Une correction doit-elle créer une transition compensatoire plutôt que réécrire l'historique ?

## Conservation

- Le stock, l'argent, le quota, les points ou les droits sont-ils conservés ?
- Le total des sous-éléments doit-il égaler un total parent ?
- Une réservation est-elle incluse ou séparée du disponible ?
- Les arrondis peuvent-ils créer ou perdre une unité minimale ?
- Une correction est-elle additive ou destructive ?
- Peut-on reconstruire le solde depuis un journal ?

## Idempotence et ordre

- Quel est l'identifiant stable de l'intention ?
- Deux requêtes avec la même clé mais des payloads différents sont-elles rejetées ?
- La clé est-elle unique par tenant et opération ?
- Un résultat en cours est-il attendu, partagé ou repris ?
- Les événements peuvent-ils arriver deux fois ou dans le désordre ?
- Une version ou un numéro de séquence empêche-t-il un événement ancien d'écraser le nouveau ?

## Multi-tenancy et autorisation

- Toutes les clés uniques incluent-elles la bonne portée tenant ?
- Les FKs empêchent-elles les références cross-tenant ?
- Les requêtes de mise à jour et suppression filtrent-elles le tenant ?
- Une valeur d'autorisation dérivée peut-elle devenir obsolète ?
- Le tenant est-il fourni par l'utilisateur ou dérivé d'un contexte authentifié ?
- Une restauration ou un import peut-il réaffecter des données au mauvais tenant ?

## Suppression, rétention et audit

- S'agit-il d'une suppression logique, purge physique, anonymisation ou expiration ?
- Les uniques et FKs restent-ils corrects après soft delete ?
- Une restauration crée-t-elle un conflit ?
- Quelles données doivent être conservées pour audit ?
- Une purge casse-t-elle la reconstruction d'un ledger ou d'une projection ?
- Les cascades sont-elles intentionnelles et bornées ?
- Les sauvegardes prolongent-elles la rétention réelle ?

## Données dérivées et projections

- Quelle est la source de reconstruction ?
- Quel est le délai maximal de convergence ?
- Comment mesurer le lag ou la dérive ?
- Le recalcul est-il idempotent ?
- Une projection peut-elle être utilisée pour autoriser une écriture critique ?
- Que voit l'utilisateur pendant une divergence ?

## Migration et coexistence

- L'ancienne application ignore-t-elle correctement la nouvelle colonne ?
- La nouvelle application peut-elle fonctionner avant la fin du backfill ?
- Deux représentations sont-elles écrites en double pendant la transition ?
- Quelle représentation gagne en cas de divergence ?
- La phase contract attend-elle une preuve de fin de coexistence ?
- Le rollback conserve-t-il les données écrites par la nouvelle version ?

## Observabilité et réparation

- Quelle requête prouve qu'aucune violation n'existe ?
- Quel seuil déclenche une alerte ?
- Qui possède l'alerte et le runbook ?
- La réparation peut-elle être exécutée en dry-run ?
- La réparation est-elle idempotente et journalisée ?
- Une réparation concurrente peut-elle aggraver la dérive ?

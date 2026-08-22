# PostgreSQL and SQLx patterns / Patrons PostgreSQL et SQLx

## Contents

- 1. Décrément atomique de stock
- 2. Transition optimiste
- 3. Unicité des lignes actives avec soft delete
- 4. Référence tenant-aware
- 5. Non-chevauchement temporel
- 6. Idempotency key
- 7. Transactional outbox
- 8. Inbox consommateur
- 9. File de workers
- 10. Backfill reprenable
- 11. Ajout progressif d'une contrainte
- 12. Mapping d'erreur SQLx
- 13. SQL dynamique sûr
- 14. Ledger

---

Ces patrons sont des points de départ. Adapter types, index, niveau d'isolation et erreurs au
projet. Ne pas les copier sans la matrice d'invariants.

## 1. Décrément atomique de stock

```sql
UPDATE inventory
SET available = available - $3,
    version = version + 1,
    updated_at = clock_timestamp()
WHERE tenant_id = $1
  AND sku = $2
  AND available >= $3
RETURNING available, version, updated_at;
```

Interprétation :

- une ligne retournée : réservation acquise ;
- zéro ligne : article absent, mauvais tenant ou stock insuffisant ;
- si le métier doit distinguer ces cas, ajouter une lecture de diagnostic après l'échec ou une
  requête structurée qui les distingue sans réintroduire la course.

Ne jamais faire `SELECT available`, puis `UPDATE` non conditionnel.

## 2. Transition optimiste

```sql
UPDATE orders
SET state = 'paid',
    version = version + 1,
    paid_at = clock_timestamp()
WHERE tenant_id = $1
  AND id = $2
  AND state = 'pending_payment'
  AND version = $3
RETURNING id, state, version, paid_at;
```

Zéro ligne est un conflit métier ou une absence, pas un succès silencieux.

## 3. Unicité des lignes actives avec soft delete

```sql
CREATE UNIQUE INDEX users_active_email_uq
ON users (tenant_id, lower(email))
WHERE deleted_at IS NULL;
```

Décider séparément :

- une adresse d'un compte supprimé peut-elle être réutilisée ?
- une restauration doit-elle échouer, fusionner ou renommer ?
- les requêtes oublient-elles parfois `deleted_at IS NULL` ?

## 4. Référence tenant-aware

```sql
CREATE TABLE projects (
    tenant_id uuid NOT NULL,
    id uuid NOT NULL,
    name text NOT NULL,
    PRIMARY KEY (tenant_id, id)
);

CREATE TABLE tasks (
    tenant_id uuid NOT NULL,
    id uuid NOT NULL,
    project_id uuid NOT NULL,
    title text NOT NULL,
    PRIMARY KEY (tenant_id, id),
    CONSTRAINT tasks_project_fk
      FOREIGN KEY (tenant_id, project_id)
      REFERENCES projects (tenant_id, id)
      ON DELETE RESTRICT
);
```

Une FK uniquement sur `project_id` ne prouve pas l'appartenance au même tenant.

## 5. Non-chevauchement temporel

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE reservations
ADD CONSTRAINT reservations_no_active_overlap
EXCLUDE USING gist (
    tenant_id WITH =,
    resource_id WITH =,
    tstzrange(starts_at, ends_at, '[)') WITH &&
)
WHERE (status = 'active');
```

Décider :

- les périodes vides sont-elles autorisées ?
- la fin est-elle exclusive ?
- quelles valeurs de `status` participent à l'exclusion ?
- l'extension est-elle disponible dans tous les environnements ?

## 6. Idempotency key

```sql
CREATE TABLE idempotency_requests (
    tenant_id uuid NOT NULL,
    operation text NOT NULL,
    idempotency_key text NOT NULL,
    request_hash bytea NOT NULL,
    status text NOT NULL CHECK (status IN ('processing', 'succeeded', 'failed')),
    response jsonb,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at timestamptz,
    expires_at timestamptz NOT NULL,
    CONSTRAINT idempotency_requests_pk
      PRIMARY KEY (tenant_id, operation, idempotency_key),
    CONSTRAINT idempotency_response_state_ck CHECK (
      (status = 'succeeded' AND response IS NOT NULL AND completed_at IS NOT NULL)
      OR status <> 'succeeded'
    )
);
```

Acquisition :

```sql
INSERT INTO idempotency_requests (
    tenant_id, operation, idempotency_key, request_hash, status, expires_at
)
VALUES ($1, $2, $3, $4, 'processing', $5)
ON CONFLICT DO NOTHING
RETURNING tenant_id, operation, idempotency_key;
```

Si aucune ligne n'est retournée : charger la ligne existante, comparer `request_hash`, puis définir
le comportement pour `processing`, `succeeded` et `failed`. Ne pas inventer un succès quand le
premier traitement est encore en cours.

## 7. Transactional outbox

```sql
CREATE TABLE outbox_events (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL,
    aggregate_type text NOT NULL,
    aggregate_id uuid NOT NULL,
    event_type text NOT NULL,
    event_version integer NOT NULL,
    payload jsonb NOT NULL,
    occurred_at timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    published_at timestamptz,
    attempts integer NOT NULL DEFAULT 0,
    last_error text
);

CREATE INDEX outbox_unpublished_idx
ON outbox_events (created_at, id)
WHERE published_at IS NULL;
```

Écrire l'état métier et l'outbox dans la même transaction. Le publisher doit tolérer les doublons ;
le consommateur doit dédupliquer avec `event_id` ou une clé métier stable.

## 8. Inbox consommateur

```sql
CREATE TABLE inbox_events (
    consumer text NOT NULL,
    event_id uuid NOT NULL,
    received_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (consumer, event_id)
);
```

Dans une même transaction : insérer l'inbox avec `ON CONFLICT DO NOTHING`, appliquer l'effet
seulement si l'insertion a réussi, puis commit.

## 9. File de workers

```sql
WITH picked AS (
    SELECT id
    FROM jobs
    WHERE state = 'ready'
      AND run_after <= clock_timestamp()
    ORDER BY priority DESC, run_after, id
    FOR UPDATE SKIP LOCKED
    LIMIT $1
)
UPDATE jobs j
SET state = 'running',
    worker_id = $2,
    started_at = clock_timestamp(),
    attempts = attempts + 1
FROM picked
WHERE j.id = picked.id
RETURNING j.*;
```

Analyser : famine des tâches anciennes, expiration du lease, reprise après crash, nombre maximal
d'essais et idempotence du travail.

## 10. Backfill reprenable

Principes :

- clé de progression stable ;
- lots bornés ;
- requête idempotente ;
- métriques de progression et d'erreur ;
- possibilité de reprendre après interruption ;
- absence de transaction géante ;
- validation de l'invariant avant contraction.

Exemple simplifié :

```sql
UPDATE accounts
SET normalized_email = lower(email)
WHERE id > $1
  AND id <= $2
  AND normalized_email IS DISTINCT FROM lower(email);
```

## 11. Ajout progressif d'une contrainte

Selon le type de contrainte et la version PostgreSQL, une stratégie peut être :

1. ajouter la structure compatible ;
2. backfiller ;
3. ajouter une contrainte non validée quand PostgreSQL le permet ;
4. corriger les violations ;
5. valider la contrainte ;
6. basculer l'application ;
7. contracter plus tard.

Vérifier le comportement exact du runner et de PostgreSQL :

```text
À PROUVER SUR POSTGRESQL RÉEL
```

## 12. Mapping d'erreur SQLx

Règle de conception : mapper à partir du SQLSTATE et, si disponible, du nom de contrainte.

Exemples de catégories métier :

- unique/idempotence ;
- FK/référence absente ;
- check/invariant de domaine ;
- exclusion/conflit temporel ;
- sérialisation/deadlock rejouable ;
- timeout/résultat potentiellement inconnu ;
- panne technique non rejouable automatiquement.

Ne pas transformer toutes les erreurs en `Conflict`.

## 13. SQL dynamique sûr

Avec `QueryBuilder`, lier les valeurs avec `push_bind`. Les noms de table, colonne ou direction de
tri ne peuvent pas être bindés : choisir uniquement parmi une allowlist codée en dur.

## 14. Ledger

Une table d'écritures immuables est souvent préférable à un solde mutable seul. Toutefois, une
simple contrainte ligne par ligne ne garantit pas qu'un lot d'écritures s'équilibre. Définir le
périmètre de posting, l'atomicité, la prévention des doubles postings et la vérification du total.
Pour un ledger critique, niveau L3 et preuve spécifique obligatoires.

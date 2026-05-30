# Base de données

Priorité #2. La DB est presque toujours le bottleneck d'une app. Et la règle des
latences s'applique : un round-trip réseau vers la DB coûte ~10 000× un accès RAM.
Le gain vient surtout de **ne pas chercher partout** et de **ne pas multiplier les
allers-retours**.

## 1. Indexer — ne jamais full-scan

C'est l'exemple canonique : chercher un utilisateur en parcourant toute la table
est O(n) ; avec un index sur la colonne, c'est O(log n).

```sql
-- AVANT (implicite) : sans index sur email, le SGBD lit TOUTE la table (seq scan)
SELECT * FROM users WHERE email = 'a@b.com';   -- O(n) lignes lues

-- FIX : créer l'index → recherche par arbre B-tree, O(log n)
CREATE INDEX idx_users_email ON users(email);
```

Vérifie toujours avec le plan d'exécution : `EXPLAIN ANALYZE SELECT ...`. Tu veux
voir `Index Scan` / `Index Only Scan`, pas `Seq Scan` sur une grande table.

**Règles d'indexation :**
- Indexe les colonnes des clauses `WHERE`, `JOIN ON`, `ORDER BY`, `GROUP BY`.
- **Index composite** : l'ordre des colonnes compte. Un index `(a, b)` sert
  `WHERE a` et `WHERE a AND b`, mais **pas** `WHERE b` seul (règle du préfixe
  gauche).
- **Covering index** : si l'index contient toutes les colonnes lues, le SGBD
  répond sans toucher la table (`Index Only Scan`).
- Un index a un coût : il ralentit les `INSERT/UPDATE` et prend de la place.
  N'indexe pas tout — indexe ce qui est interrogé.
- Une fonction ou un `LIKE '%...'` en début de motif **casse** l'usage de
  l'index (`WHERE lower(email) = ...` → utilise un index fonctionnel, ou stocke
  en minuscules).

## 2. Ne sélectionner que le nécessaire

- **`SELECT col1, col2` au lieu de `SELECT *`** : moins de données lues,
  transférées, désérialisées ; permet des covering indexes.
- **`LIMIT` / pagination** : ne ramène jamais 1 M de lignes pour en afficher 20.
  Préfère la pagination par **keyset** (`WHERE id > :last_id ORDER BY id LIMIT 20`)
  au `OFFSET` qui devient O(n) sur les grandes pages.
- **Filtre côté DB, pas côté app** : `WHERE`, `GROUP BY`, agrégats (`COUNT`,
  `SUM`) en SQL. Ramener tout pour filtrer en mémoire = transférer pour rien.

## 3. Tuer le N+1 (le piège ORM n°1)

Le problème : 1 requête pour la liste, puis 1 requête par élément pour ses
relations → N+1 round-trips.
```python
# AVANT : N+1 — 1 requête pour les posts, puis 1 par post pour l'auteur
posts = Post.objects.all()          # 1 requête
for p in posts:
    print(p.author.name)            # +1 requête PAR post  →  N requêtes

# APRÈS : eager loading, 1 ou 2 requêtes au total
posts = Post.objects.select_related("author").all()   # Django: JOIN
# ou prefetch_related pour du many-to-many ; en SQL brut : un JOIN explicite
```
Symptôme à repérer : une rafale de requêtes quasi identiques dans le slow log.
Outils : `select_related`/`prefetch_related` (Django), `JOIN FETCH` (JPA),
`includes`/`eager_load` (ActiveRecord), DataLoader (GraphQL).

## 4. Batcher écritures et lectures

Un round-trip par opération est tué par les latences réseau. Regroupe :
```sql
-- AVANT : 1000 INSERT = 1000 round-trips
INSERT INTO t(a) VALUES (1);  -- ×1000
-- APRÈS : 1 INSERT multi-lignes (ou COPY pour du gros volume)
INSERT INTO t(a) VALUES (1),(2),(3), ... ,(1000);
```
- Lectures multiples par clé → `WHERE id IN (...)` ou un seul JOIN, pas une
  boucle de `SELECT ... WHERE id = ?`.
- Écritures massives → `COPY` (Postgres) / `LOAD DATA` (MySQL) >> `INSERT`.
- Regroupe dans une **transaction** pour amortir le coût de commit (mais évite
  les transactions trop longues qui tiennent des verrous).

## 5. Connexions & exécution

- **Connection pooling** (PgBouncer, HikariCP, pool applicatif) : ouvrir une
  connexion coûte cher (handshake TCP + auth). Réutilise via un pool.
- **Prepared statements** : parse/plan une fois, exécute N fois. Évite aussi
  l'injection SQL.
- **Index manquants vs requête mal écrite** : commence toujours par
  `EXPLAIN ANALYZE`. Cherche : seq scans, estimations de lignes très fausses
  (stats périmées → `ANALYZE`), tris sur disque (`external merge`), boucles
  imbriquées sur de gros volumes.

## 6. Au-delà de la requête

- **Cache applicatif** (Redis/Memcached) pour les lectures chaudes et répétées →
  évite la DB entièrement. *Cf. `memory-cache.md`.*
- **Vues matérialisées** pour des agrégats coûteux recalculés rarement.
- **Dénormalisation ciblée** : dupliquer une donnée pour éviter un JOIN coûteux
  sur le hot path (compromis cohérence/vitesse, à assumer).
- **Partitionnement / sharding** quand une table devient trop grosse pour
  l'index seul.
- **Réplicas en lecture** pour répartir la charge read-heavy.

## Checklist DB
1. Chaque requête lente passe-t-elle par un `EXPLAIN ANALYZE` ? (seq scan ?)
2. Les colonnes de `WHERE/JOIN/ORDER BY` sont-elles indexées ?
3. Y a-t-il un N+1 (rafale de requêtes quasi identiques) ?
4. Sélectionne-t-on et transfère-t-on plus que nécessaire (`SELECT *`, pas de
   `LIMIT`) ?
5. Les écritures/lectures en boucle sont-elles batchées ?
6. Y a-t-il un pool de connexions et des prepared statements ?
7. Une lecture chaude pourrait-elle être servie par un cache au lieu de la DB ?

# Mémoire & cache

Priorité #3. Deux idées : (a) **ne pas refaire un travail déjà fait** (cacher le
résultat) et (b) **garder les données près du CPU** (RAM > disque, et dans la RAM,
la localité compte). Tout découle des latences (cf. SKILL.md).

## 1. RAM plutôt que disque / réseau

Un accès RAM ≈ 100 ns ; un SSD ≈ 16 µs (≈160×) ; un round-trip DB ≈ 0,5 ms
(≈5000×). Donc : ce qu'on relit souvent, on le garde en mémoire.

```python
# AVANT : relit + parse le fichier de config à CHAQUE appel
def get_config():
    with open("config.json") as f:   # I/O disque à chaque fois
        return json.load(f)

# APRÈS : chargé une fois, servi depuis la RAM ensuite
from functools import lru_cache
@lru_cache(maxsize=1)
def get_config():
    with open("config.json") as f:
        return json.load(f)
```
Pareil pour : résultats de requêtes chaudes (Redis/Memcached), assets, templates
compilés, modèles, regex compilées. **Limite à respecter** : la RAM est finie →
politique d'éviction (LRU/LFU/TTL) obligatoire pour ne pas exploser la mémoire.

À l'inverse, **ne charge pas tout en RAM** quand le dataset dépasse la mémoire :
*stream* (lecture par chunks / itérateur), `mmap` pour mapper un gros fichier sans
le copier intégralement, pagination. Le bon choix dépend du ratio
taille/fréquence d'accès.

## 2. Mémoïsation & calcul une seule fois

Cacher la sortie d'une **fonction pure** par ses arguments. Transforme du
recalcul redondant en lookup O(1).
```python
# Fibonacci naïf : O(2ⁿ) — recalcule les mêmes sous-problèmes des millions de fois
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)

# Mémoïsé : O(n) — chaque valeur calculée une fois
from functools import cache
@cache
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)
```
Conditions : fonction **déterministe et sans effet de bord**. Attention à
l'invalidation si les entrées sous-jacentes changent (la mémoïsation suppose que
le même input donne le même output pour toujours).

## 3. Les couches de cache (de la plus proche à la plus loin)

| Couche | Exemple | Quand |
|---|---|---|
| CPU cache | localité des données (cf. §4) | code chaud, gros tableaux |
| Mémoïsation in-process | `lru_cache`, Map | fonction pure répétée |
| Cache local process | dict + TTL | données partagées par un process |
| Cache distribué | Redis, Memcached | partagé entre instances/services |
| HTTP / CDN | `Cache-Control`, ETag, CloudFront | réponses web, assets |
| Materialized view | DB | agrégats coûteux |

**Stratégies** : `cache-aside` (l'app gère lecture puis remplissage),
`write-through` (écrit cache + DB ensemble), `write-back` (écrit cache, persiste
plus tard). **Invalidation** = le vrai problème du cache : choisis TTL, ou
invalidation explicite à l'écriture, ou versionnage de clé. Méfie-toi du *cache
stampede* (expiration simultanée → rush sur la source) : jitter sur les TTL,
verrou de recompute, ou *stale-while-revalidate*.

## 4. Cache locality (CPU) — pour le hot path numérique

Le CPU lit la RAM par **lignes de cache** (~64 octets). Accéder à des données
contiguës est beaucoup plus rapide qu'à des données éparpillées (cache misses).

- **Structure of Arrays (SoA) > Array of Structures (AoS)** quand tu traites un
  seul champ sur des millions d'éléments : ranger tous les `x` ensemble évite de
  charger les champs inutiles dans le cache.
```rust
// AoS : pour sommer tous les x, on charge aussi y et z (gaspillage de cache)
struct P { x: f32, y: f32, z: f32 }
let pts: Vec<P> = ...;
// SoA : les x sont contigus → un seul stream cache-friendly + vectorisable
struct Points { xs: Vec<f32>, ys: Vec<f32>, zs: Vec<f32> }
```
- **Parcours dans l'ordre mémoire** : balaye une matrice ligne par ligne (row-major)
  et pas colonne par colonne — l'ordre des boucles change tout.
- **Struct packing** : ordonne les champs du plus grand au plus petit pour
  réduire le padding et la taille → plus d'éléments par ligne de cache.

## 5. Allocations

Allouer/libérer coûte cher et fragmente. Sur le hot path :
- **Pré-alloue** la capacité connue (`Vec::with_capacity(n)`, `list` dimensionnée)
  pour éviter les réallocations + copies à chaque croissance.
- **Réutilise les buffers** (object pool, buffer réutilisé entre itérations) au
  lieu d'allouer dans la boucle.
- **Évite les copies** : passe par référence/slice, utilise des vues
  (`&str`/slice) plutôt que de cloner, zero-copy quand possible.
- **Évite les conversions/box** répétées (boxing, sérialisations intermédiaires).

## Checklist mémoire & cache
1. Relit-on un fichier / refait-on une requête identique qu'on pourrait cacher ?
2. Cette fonction pure et coûteuse est-elle mémoïsée ?
3. Le cache a-t-il une politique d'éviction et une stratégie d'invalidation ?
4. Charge-t-on tout en RAM alors qu'un stream/pagination suffirait (ou l'inverse) ?
5. (Hot path) Les données sont-elles parcourues dans l'ordre mémoire ? SoA utile ?
6. Alloue-t-on dans la boucle au lieu de pré-allouer / réutiliser ?

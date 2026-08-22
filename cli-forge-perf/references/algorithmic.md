# Algorithmique & structures de données

## Contents

- 1. Réduire la complexité (Big-O)
- 2. Choisir la bonne structure de données
- 3. Transformations de boucles
- 4. Éviter le travail inutile
- 5. Branchless & prédiction de branchement (hot path uniquement)
- Checklist algorithmique

---

Le levier #1. Un meilleur algorithme bat toujours une micro-optimisation : passer
de O(n²) à O(n log n) sur 1 M d'éléments, c'est ~50 000× moins d'opérations.

## 1. Réduire la complexité (Big-O)

Ordre de grandeur des classes, du meilleur au pire :
`O(1)` < `O(log n)` < `O(n)` < `O(n log n)` < `O(n²)` < `O(2ⁿ)` < `O(n!)`.

Le réflexe : **chaque boucle imbriquée sur les données est suspecte**. Une double
boucle sur `n` éléments = O(n²). Souvent évitable avec un index (Map/Set) qui
transforme une recherche interne O(n) en O(1).

**Exemple — détecter des doublons / intersections :**
```python
# AVANT : O(n²) — pour chaque élément, on reparcourt toute la liste
def a_doublon(items):
    for i in range(len(items)):
        for j in range(i+1, len(items)):
            if items[i] == items[j]:
                return True
    return False

# APRÈS : O(n) — un set, appartenance en O(1)
def a_doublon(items):
    vus = set()
    for x in items:
        if x in vus:
            return True
        vus.add(x)
    return False
```

**Two-sum, jointures, "trouve les éléments communs entre A et B"** : même schéma.
Indexe une des collections dans un Set/Map, puis parcours l'autre une fois → O(n+m)
au lieu de O(n·m).

## 2. Choisir la bonne structure de données

La structure dicte la complexité des opérations. Choisis selon l'accès dominant :

| Besoin dominant | Structure | Lookup | Insert |
|---|---|---|---|
| Recherche par clé | Hash map / dict | O(1) | O(1) |
| Test d'appartenance | Hash set | O(1) | O(1) |
| Ordre + range queries | Arbre balancé / BTreeMap | O(log n) | O(log n) |
| FIFO / queue | Deque / ring buffer | — | O(1) |
| Plus petit/grand en continu | Heap (priority queue) | O(1) peek | O(log n) |
| Préfixes / autocomplete | Trie | O(longueur) | O(longueur) |
| "Probablement présent ?" (filtre) | Bloom filter | O(1) | O(1) |

**Cas typique — "plein de `if x == 'a' elif x == 'b' ...'" :** une chaîne de `if`
est O(n) en nombre de branches et illisible. Remplace par un **dispatch table**
(dict de fonctions) → O(1) et extensible :
```python
# AVANT : chaîne de if, O(k) branches, dur à étendre
def handle(cmd, ctx):
    if cmd == "start": return do_start(ctx)
    elif cmd == "stop": return do_stop(ctx)
    elif cmd == "pause": return do_pause(ctx)
    # ... 20 autres
    else: return do_default(ctx)

# APRÈS : table de dispatch, O(1), une seule ligne pour ajouter un cas
HANDLERS = {"start": do_start, "stop": do_stop, "pause": do_pause}
def handle(cmd, ctx):
    return HANDLERS.get(cmd, do_default)(ctx)
```

**Bloom filter** : quand tu veux éviter un accès coûteux (DB, disque) pour des
clés probablement absentes. Le filtre répond "absent à coup sûr" ou "peut-être
présent" en O(1) RAM, et tu ne touches le stockage lent que pour les "peut-être".

## 3. Transformations de boucles

### Sortir les invariants de la boucle
Tout ce qui ne dépend pas de l'itération se calcule **une fois**, avant.
```js
// AVANT : items.length et la regex recalculés/recompilés à chaque tour
for (let i = 0; i < items.length; i++) {
  if (/^\d+$/.test(items[i])) { /* ... */ }
}
// APRÈS
const n = items.length;
const re = /^\d+$/;
for (let i = 0; i < n; i++) {
  if (re.test(items[i])) { /* ... */ }
}
```

### Fusionner les passes (loop fusion)
`map().filter().reduce()` sur des données massives crée des collections
intermédiaires et parcourt 3 fois. Une seule passe (ou un itérateur paresseux qui
fusionne, type `Iterator` Rust / générateurs Python) parcourt 1 fois sans alloc
intermédiaire.

### Sortir tôt (short-circuit)
`any`/`some`/`find` s'arrêtent au premier succès. N'utilise pas un `reduce`
complet ou un comptage total si tu veux juste savoir "est-ce qu'il en existe un".

### Plusieurs `if` séquentiels → un seul parcours
Si tu enchaînes plusieurs boucles `for` sur la même collection (une par
condition), fusionne-les en une seule boucle avec plusieurs `if` à l'intérieur :
n passes → 1 passe.

### Loop unrolling / batch
Marginal et souvent fait par le compilo. À ne tenter que sur hot path mesuré.
Plus utile : traiter par **batch** (par blocs) pour amortir les coûts fixes
(syscalls, allocations, round-trips).

## 4. Éviter le travail inutile

- **Lazy evaluation** : ne calcule que ce qui est consommé (générateurs, streams,
  itérateurs paresseux). Évite de matérialiser 1 M de lignes pour n'en lire 10.
- **Mémoïsation** : cache le résultat d'une fonction pure par ses arguments.
  Transforme une récursion exponentielle (Fibonacci naïf O(2ⁿ)) en O(n).
  *Détaillé dans `memory-cache.md`.*
- **Programmation dynamique** : remplace la récursion redondante par une table.
- **Pré-calcul / lookup table** : si une fonction coûteuse a un domaine d'entrée
  petit et fixe, calcule toutes les sorties une fois et stocke-les. *Cf.
  `math-physics.md` pour les tables trigonométriques.*

## 5. Branchless & prédiction de branchement (hot path uniquement)

Un branchement mal prédit coûte ~10-20 cycles (pipeline flush). Sur du code chaud
et data-dependent, transformer un `if` en arithmétique peut aider :
```c
// AVANT : branche
int max = (a > b) ? a : b;
// APRÈS (branchless) : pas de saut conditionnel
int max = a ^ ((a ^ b) & -(a < b));
```
**Attention** : illisible, gain souvent nul (le compilo le fait déjà), et parfois
contre-productif. Ne fais ça **qu'avec un bench à l'appui**. Plus efficace en
amont : trier les données pour rendre les branches prédictibles, ou supprimer la
branche par un design différent.

## Checklist algorithmique
1. Y a-t-il une boucle imbriquée évitable par un index (Set/Map) ?
2. La structure de données correspond-elle à l'opération dominante ?
3. Calcule-t-on quelque chose plusieurs fois qu'on pourrait calculer une fois ?
4. Peut-on sortir tôt / être paresseux au lieu de tout matérialiser ?
5. Peut-on fusionner plusieurs passes en une seule ?

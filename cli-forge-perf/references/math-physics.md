# Math, physique & calcul numérique

Micro-optimisations CPU : **en dernier**, sur hot path mesuré (graphismes,
géo/spatial, simulation, ML, traitement signal). Le principe transverse :
**remplacer une opération chère par une équivalente moins chère** sans changer le
résultat utile.

## Coût relatif des opérations (ordre de grandeur)

`add/sub/mul` (entiers/flottants) ≪ `div`/`mod` ≪ `sqrt` ≪ `sin/cos/tan/exp/log`
≪ `pow`. Une fonction transcendante (trigo, exp) peut coûter **10 à 100×** une
multiplication. D'où les astuces ci-dessous.

## 1. Comparer des distances : garde le carré, jette le `sqrt`

L'exemple canonique (ta carte / loc). La distance euclidienne est
`d = sqrt(dx² + dy²)`. Le `sqrt` est cher. Or **pour comparer ou trier des
distances, le carré conserve l'ordre** (la fonction racine est monotone
croissante) : pas besoin de la racine.

```python
# AVANT : sqrt à chaque candidat — inutile si on veut juste le plus proche
def plus_proche(p, points):
    return min(points, key=lambda q: math.sqrt((p.x-q.x)**2 + (p.y-q.y)**2))

# APRÈS : distance au carré — même résultat, sans le sqrt
def plus_proche(p, points):
    return min(points, key=lambda q: (p.x-q.x)**2 + (p.y-q.y)**2)

# "Dans un rayon r ?" → compare au carré aussi :
#   dans_rayon = (dx*dx + dy*dy) <= r*r      (au lieu de sqrt(...) <= r)
```
Tu ne calcules la vraie racine que **si** tu dois afficher la distance réelle.
Pareil : pas besoin de normaliser un vecteur (division par sa norme = sqrt + div)
si tu veux juste comparer des longueurs.

## 2. Éviter la trigonométrie

`cos`/`sin` sont parmi les plus chères. Trois leviers :

**(a) Reformuler avec un produit scalaire.** L'angle entre deux vecteurs sert
souvent juste à savoir "même direction ? perpendiculaire ? lequel est le plus
aligné ?". Le **dot product** (`a·b = ax*bx + ay*by`) donne `|a||b|cosθ` sans
`acos` : son signe et sa valeur suffisent pour comparer/trier des angles sans
jamais calculer d'angle.
```python
# "le point devant moi ?" → pas besoin d'angle, le signe du dot suffit
devant = (dir.x*to.x + dir.y*to.y) > 0
```

**(b) Lookup table** si le domaine est borné et discret (ex. angles entiers en
degrés) : pré-calcule `sin`/`cos` une fois dans un tableau de 360 (ou 256)
entrées, puis indexe. O(1), zéro transcendante au runtime.

**(c) Approximation polynomiale** (Taylor, minimax) quand une petite erreur est
acceptable : un polynôme de degré 3-5 approche `sin` sur `[-π,π]` avec quelques
mul/add seulement.

**Distance géo (lat/lon) :** la formule de Haversine est lourde (plusieurs trigo +
sqrt). Pour de **petites distances** ou des comparaisons locales, l'approximation
équirectangulaire suffit (`x = Δλ·cos(φ_moy)`, `y = Δφ`, `d ≈ R·sqrt(x²+y²)`) — un
seul `cos` au lieu de plusieurs, et on garde le carré si on ne fait que comparer.

## 3. Puissances, divisions, modulo

- **`x²` = `x*x`**, pas `pow(x, 2)` (pow passe par exp/log). De même `x³ = x*x*x`.
- **Division par une constante** : multiplie par l'inverse pré-calculé
  (`* 0.5` au lieu de `/ 2.0`) quand c'est dans une boucle.
- **Puissances de 2** : `n * 2 == n << 1`, `n / 2 == n >> 1` (entiers non signés),
  `n % 2 == n & 1`. Plus généralement `x % 2^k == x & (2^k - 1)`. Le `&`/`<<` sont
  quasi gratuits vs `div`/`mod`. (Le compilo le fait souvent pour les constantes —
  vérifie avant de l'écrire à la main.)
- **Évite `div`/`mod` dans les boucles serrées** : reformule (accumulateur,
  incrément) plutôt qu'un modulo par itération.

## 4. Bit manipulation

- Test puissance de 2 : `x && (x & (x-1)) == 0`.
- Flags compacts : un entier comme bitset (set/clear/test via `|`, `&~`, `&`).
- Multiplier/diviser par 2^k via shifts (cf. §3).
- `popcount`, `clz`/`ctz` (intrinsics CPU) pour compter/scanner des bits en O(1).

## 5. `sqrt` et inverse : intrinsics modernes

Le légendaire *fast inverse square root* (Quake III, `0x5f3759df`) est **obsolète**
sur les CPU/GPU récents : les instructions matérielles `rsqrt`/`sqrt` (SSE/AVX,
NEON) sont plus rapides ET plus précises. Utilise les intrinsics ou laisse le
compilo vectoriser — n'écris pas le hack à la main. La leçon qui reste : *évite le
sqrt quand le carré suffit* (§1).

## 6. SIMD & vectorisation

Une instruction SIMD traite 4/8/16 valeurs d'un coup (SSE/AVX/AVX-512, NEON).
Sur des calculs réguliers en masse (somme, dot product, filtres), c'est un gros
gain.
- **Laisse le compilo auto-vectoriser** : `-O3 -march=native`, boucles simples
  sans dépendances ni branches, données contiguës et alignées (lien direct avec
  la **cache locality** et le **SoA**, cf. `memory-cache.md`).
- Sinon, intrinsics ou bibliothèques (`std::simd`, `ndarray`/NumPy, BLAS, Eigen).
- **NumPy / opérations vectorisées** : en Python, remplacer une boucle scalaire
  par une opération NumPy sur tableau, c'est passer du Python interprété à du C
  vectorisé → souvent 10-100×.

## 7. Précision vs vitesse

- **Entiers > flottants** quand c'est possible (compteurs, money en centimes,
  fixed-point) : pas d'erreur d'arrondi, ops plus rapides.
- **`f32` vs `f64`** : `f32` = moitié de bande passante mémoire et souvent 2× le
  débit SIMD. Utilise `f32` si la précision suffit (graphismes, ML inference).
- **Approximations bornées** : beaucoup de domaines (rendu, audio, ML) tolèrent
  une erreur. Choisis la précision minimale acceptable, pas la maximale par défaut.

## Checklist math/calcul
1. Compare-t-on des distances ? → garde le **carré**, supprime `sqrt`.
2. Utilise-t-on `sin/cos/acos` là où un **dot product** ou une lookup table suffit ?
3. `pow(x,2)` ou `/const` dans une boucle → `x*x` / `* inverse`.
4. Division/modulo par puissance de 2 → shift / mask.
5. La boucle numérique est-elle vectorisable (`-O3 -march=native`, données SoA) ?
6. A-t-on besoin de `f64` ou `f32`/entier suffit ?
7. (Toujours) ces micro-optims sont-elles sur un hot path **mesuré** ?

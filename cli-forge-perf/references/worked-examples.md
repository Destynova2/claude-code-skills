# Worked examples (traces de bout en bout)

Le reste du skill donne des principes ; ici, des traces complètes
**symptôme → mesure → diagnostic → fix → re-mesure → leçon**. Les exemples
marqués *(mesuré)* ont été chronométrés par A/B interleavé + test de
permutation (protocole de `bench-protocol.md`) et sont reproductibles ; les
autres sont *(illustratif)* ou *(publié)* faute de DB/GPU sous la main.

## Exemple 1 — Le N+1 (illustratif)

**Symptôme.** Une page « liste de 50 commandes avec le nom du client » met 1,2 s.
Le slow query log montre une rafale de ~51 requêtes quasi identiques.

**Mesure & diagnostic.** Tracing : 1 requête pour les commandes, puis **1 requête
par commande** pour son client → N+1 round-trips. Chaque aller-retour DB ≈ 0,5 ms
de latence réseau ; 51 × (0,5 ms + exécution) domine le temps de page. Goulot :
**I/O-bound** (round-trips), pas CPU. (cf. `database.md` §3)

**Fix.** Eager loading — un `JOIN` (ou `select_related`/`prefetch_related`) ramène
tout en **1 requête** :
```sql
SELECT o.*, c.name FROM orders o JOIN customers c ON c.id = o.customer_id LIMIT 50;
```

**Re-mesure (illustratif).** 51 requêtes → 1 ; ~1,2 s → ~30 ms. Le gain ne vient
pas d'une requête « plus rapide » mais de **ne pas faire 50 allers-retours**.

**Leçon.** Le levier #2 (ne pas faire l'I/O) bat tout réglage de requête. Le
symptôme — une rafale de requêtes jumelles — est la signature à reconnaître.

## Exemple 2 — Ordre de boucle `i`/`j` & layout (mesuré, résultat surprenant)

**L'intuition.** `Σᵢ Σⱼ A[i][j] == Σⱼ Σᵢ A[i][j]` : valeur mathématiquement
**identique** (les sommes commutent). Mais parcourir une matrice colonne par
colonne (column-major) au lieu de ligne par ligne (row-major) casse la localité
cache → on s'attend à un parcours strided plus lent. « Vrai et faux à la fois »
(cf. `experiment-method.md` §7).

**Mesure.** Réduction d'une matrice 4000×4000 en numpy, parcours contigu
(`a.sum(axis=1)`) vs strided (`a.sum(axis=0)`), via
une mesure A/B interleavée (protocole `bench-protocol.md`) :
```
strided (axis=0) : médiane 210.5 ms
contigu (axis=1) : médiane 207.2 ms
[verdict] Δ -1.6%  | permutation p = 0.24  => NON significatif : dans le bruit
```

**Diagnostic.** L'effet attendu **ne se matérialise pas** : p=0.24, le test refuse
le gain. Pourquoi ? La réduction de numpy est **déjà cache-aware** (sommation par
blocs, gestion du strided optimisée). L'abstraction a déjà gagné la bataille du
layout à ta place.

**Leçon (double).** (1) **Mesure, ne suppose pas** : l'intuition cache était
correcte en théorie, fausse ici en pratique — le test de permutation a évité un faux positif.
(2) L'ordre de boucle redevient un **vrai 5-10×** quand c'est **toi** qui
contrôles le parcours mémoire (boucle C/Rust manuelle sur un grand tableau,
row-major vs column-major). La règle « valeur identique, comportement différent »
tient ; son ampleur dépend de qui gère la mémoire.

## Exemple 3 — Quantization LLM, tok/s (publié)

**Symptôme.** Un 70B en FP16 sature la bande passante mémoire ; le decode plafonne
les tok/s (cf. `llm-inference.md` : le decode est *memory-bandwidth-bound*).

**Diagnostic.** Chaque token relit tous les poids depuis la mémoire → le débit est
borné par les octets/token, pas par le calcul. Réduire la précision réduit
directement les octets transférés.

**Fix & re-mesure (benchmarks publiés).** Passer FP16 → **FP8** sur Hopper : de
l'ordre de **+33 % de tok/s** et **−8 % de TTFT** pour une perte de qualité
minime ; INT4 (GGUF `Q4_K_M`) va plus loin pour l'edge, à surveiller côté
qualité. Et « les kernels comptent » : mêmes poids quantifiés, un meilleur kernel
(Marlin) ≈ 2,5× le débit.

**Leçon.** Quand un goulot est *bandwidth-bound*, on réduit les **octets
transférés** (quantization = compression des poids), pas le nombre d'opérations.
Roofline appliqué (cf. `systems-hardware.md`).

## Exemple 4 — Recherche linéaire → set (mesuré, reproductible)

**Symptôme.** Un filtre teste l'appartenance dans une liste ; ça rame dès que la
liste grossit.

**Mesure.** `q in liste` (O(n)) vs `q in set` (O(1)), 10 000 tests sur 20 000
éléments, via une mesure A/B interleavée (`hyperfine` pour la boîte noire CLI, ou un harnais in-process) :
```
liste (scan O(n)) : médiane 1.024 s
set   (O(1))      : médiane 18.8 ms
[verdict] Δ -98.2%  | permutation p = 0.013  => significatif. ~54× plus rapide.
```

**Diagnostic & fix.** Recherche linéaire dans une grande collection → indexe dans
un `set`/`dict` (table de hachage). C'est le levier #1 (algorithmique, cf.
`algorithmic.md`).

**Leçon + piège de mesure.** Gain réel et significatif (~54×). Mais note : les
18,8 ms du set sont **majoritairement le démarrage de l'interpréteur Python**, pas
le lookup — le ratio *algorithmique* pur est encore plus grand. C'est exactement
le piège « benchmark au niveau commande inclut le startup » (`benchmarking-traps.md`
§6) : pour isoler l'opération, mesure **in-process**.

## À retenir transversalement
- Le plus gros gain vient de **ne pas faire le travail** (N+1 : pas d'aller-retour ;
  scan : pas de parcours) — pas de « faire pareil plus vite ».
- **Mesure systématiquement** : l'effet attendu peut être dans le bruit (ex. 2),
  et le test de permutation te protège du faux positif.
- Le **type de goulot** dicte le levier : I/O (ex. 1) ≠ bande passante (ex. 3) ≠
  algorithme (ex. 4).

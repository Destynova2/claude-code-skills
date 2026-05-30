# Pièges de mesure (red-team tes propres chiffres)

Complément de `experiment-method.md`. Là-bas : les pièges **statistiques**
(interpréter les données). Ici : les pièges de **mesure** (la donnée elle-même
est fausse avant toute interprétation). Un benchmark non audité ment plus souvent
qu'il ne dit vrai. Avant de croire un gain, passe cette liste.

## 1. Le compilateur a supprimé ton benchmark (dead-code elimination)

Si le résultat du calcul mesuré n'est **utilisé nulle part**, l'optimiseur a le
droit de supprimer tout le calcul. Tu mesures alors une boucle vide → "1000×
plus rapide", faux. Fix : **consomme le résultat** (renvoie-le, accumule-le,
écris-le dans un volatile, `std::hint::black_box` en Rust, `benchmark.Keep` en
Go). Symptôme classique : un temps absurdement bas, indépendant de la taille de
l'entrée.

## 2. Constant folding / hoisting

Avec des **entrées constantes**, le compilateur pré-calcule au build, ou sort le
calcul de la boucle (invariant). Tu mesures un `mov`, pas ton algo. Fix : fais
varier les entrées au runtime, depuis une source que le compilo ne voit pas
(argument, fichier, RNG seedé).

## 3. Warmup oublié (le premier run ment)

Le premier passage paie des coûts uniques qui ne se reproduiront pas en prod
stable — ou l'inverse. À chauffer avant de mesurer : **JIT** (JVM, V8, PyPy)
qui compile à chaud, **cache CPU** et **TLB**, **prédicteur de branchement**,
**page faults** (first-touch mémoire), **montée en fréquence turbo**, connexions
/ pools établis. Fix : runs de warmup explicitement jetés (W=3-10 selon le régime). Mais
distingue : si la prod fait surtout des appels *à froid*, c'est le froid qu'il
faut mesurer.

## 4. Coordinated omission (le piège latence n°1 — Gil Tene)

En mesure de latence sous charge : si ton générateur de charge **attend** la fin
d'une requête lente avant d'envoyer la suivante, il **n'envoie pas** pendant le
stall → les requêtes qui auraient souffert ne sont jamais comptées. Résultat :
p99 magnifique, réalité catastrophique. C'est pourquoi des "p99 à 2 ms"
s'effondrent en prod. Fix : mesure la latence depuis l'**instant d'envoi prévu**
(pas l'instant d'envoi réel), corrige l'histogramme (HdrHistogram le fait), ou
utilise un générateur à débit constant indépendant des réponses.

## 5. Observer effect (mesurer change la mesure)

L'instrumentation déforme ce qu'elle observe : un profiler **instrumentant**
(comptage par appel) peut multiplier le temps des petites fonctions et fausser le
hot path ; trop de logs/traces ralentissent le chemin chaud. Fix : préfère un
profiler **sampling** (échantillonnage statistique, overhead quasi nul) pour
trouver le hot path ; mesure l'overhead de ton instrumentation ; n'instrumente
pas ce que tu chronomètres au plus fin.

## 6. Résolution & overhead du chronomètre

Chronométrer une opération sub-microseconde avec une horloge grossière, ou dont
l'appel coûte plus que l'opération, donne du bruit pur. Fix : mesure un **batch
de N itérations** et divise ; utilise `perf_counter_ns` / `rdtsc` ; mesure
d'abord l'overhead du timer lui-même et soustrais-le.

## 7. A/B confondu (tu compares deux moments, pas deux variantes)

Tu as lancé A le matin, B l'après-midi : charge, température CPU, voisin bruyant,
autre déploiement ont changé. Le "gain" est un artefact temporel. Fix :
**interleave** les runs (A,B,A,B… — `hyperfine` le fait nativement, sinon code-le), randomise
l'ordre, lance dans le même environnement, à la même fraîcheur de cache.

## 8. État de cache (chaud vs froid)

Le 2ᵉ run lit depuis le page cache / le cache applicatif → "plus rapide", mais ce
n'est pas représentatif d'un accès à froid. Inversement, mesurer toujours à froid
sur-estime le coût d'un chemin qui sera chaud en prod. Fix : décide et **contrôle
explicitement** l'état de cache (vide-le, ou pré-chauffe-le, de façon cohérente
entre A et B), selon ce que vit la prod.

## 9. Charge & concurrence non représentatives

Mesurer à 1 requête/s ne dit **rien** du comportement à saturation (où les
queues, les locks et le GC explosent). Mesurer en mono-thread un service qui
tourne à 32 cœurs en prod non plus. Fix : trace une **courbe de charge** (latence
vs débit), trouve le coude (la saturation) ; teste avec la concurrence réelle.

## 10. GC / pauses & autres queues

La moyenne masque les pauses stop-the-world (GC, compaction, checkpoint).
Une médiane parfaite peut cacher un p99.9 désastreux. Fix : rapporte p99/p99.9,
mesure assez longtemps pour capter les événements rares, surveille les pauses GC.

## 11. Benchmarker la mauvaise chose

Le micro-benchmark est rapide mais souvent **non représentatif** : données
synthétiques uniformes, tout en cache, sans contention, sans I/O réelle. Tu
optimises un cas qui n'existe pas. Fix : profile la **vraie charge** (cf.
`profiling.md`), benchmarke des entrées réalistes (tailles, distributions,
ratios de cache hit), et préfère un macro-benchmark de bout en bout pour la
décision finale.

## 12. Workaround net-négatif présenté comme fix

Un contournement qui *résout* un bug mais coûte plus que ce qu'il rapporte n'est
**pas un fix** — c'est une régression. Variations universelles, valables dans
toutes les stacks :

- Upcaster en précision supérieure (`f32` au lieu de `bf16`) pour contourner un
  bug d'accumulation → résultat correct, débit ↓.
- Désactiver le cache HTTP pour contourner un bug d'invalidation → latence ×10.
- Retomber sur l'algo O(n²) pour contourner un bug du O(n log n) → coût quadratique.
- Forcer un seul thread pour contourner une data race → débit divisé par N.
- Désactiver le JIT pour contourner un bug de compilation → cold-start permanent.
- `sleep(N)` pour contourner une race → débit ↓ + race toujours là.

**Règles :**

- **Mesure l'impact net** : gain de correction − coût du contournement. Si net
  négatif → ce n'est **pas** un fix.
- **Ne le présente jamais** comme « bug corrigé » / « port réussi » / « ça marche
  maintenant ». Étiquette-le `WORKAROUND, target: real fix` avec un ticket de
  suivi nommé.
- **Ne le merge pas en main** sans gate explicite (env var, feature flag, doc
  visible). Sinon il devient permanent et plus personne ne cherchera le vrai fix.
- Le done-gate (`../../shared/done-gate.md` phase 3) attrape ça par construction :
  *« gain non significatif → revert »*. Si la mesure est **négative**, la règle
  se durcit : revert obligatoire **ou** tag explicite avec engagement de suivi.

**Symptôme à reconnaître :** le diff montre une amélioration (le bug ne se
reproduit plus), le bench montre une régression (le débit baisse), et le PR
est mergé parce que *« ça marche maintenant »*. Quand le rapport de PR célèbre
la sortie du bug sans citer le coût du contournement → c'est ce piège.

## Checklist anti-pièges (avant de claimer un gain)
1. Le résultat est-il **consommé** (sinon DCE) et les **entrées variables**
   (sinon constant folding) ?
2. **Warmup** fait — et est-ce le bon régime (chaud vs froid) pour la prod ?
3. Latence sous charge : ai-je évité la **coordinated omission** ?
4. La mesure elle-même est-elle propre (sampling profiler, batch pour le timer,
   overlay d'instrumentation négligeable) ?
5. A/B **interleavé** dans le même environnement (pas deux moments) ?
6. Charge/concurrence/état de cache **représentatifs** de la prod ?
7. Je rapporte une **distribution** (p95/p99), et le Δ dépasse le bruit
   (test de permutation ou Mann-Whitney U — pas un t-test : la distribution n'est pas gaussienne) ?

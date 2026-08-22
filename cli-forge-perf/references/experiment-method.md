# Optimiser comme une recherche : hypothèse → expérience → preuve

## Contents

- 1. Hypothèse falsifiable (et chercher à la réfuter)
- 1b. Discipline de la conclusion (« définitif » ≠ « plausible »)
- 2. Borne théorique d'abord (raisonner par l'absurde)
- 3. La table de mixage : ablation contrôlée
- 3b. Comparer deux stacks (langue + lib) : pin emboîté
- 3c. Port-by-comparison : ne pas quit à la frontière framework
- 4. Gérer l'aléa (variance) — dans les deux sens
- 5. Mesurer en plusieurs dimensions (4D, 5D, 6D…)
- 6. Challenger les chiffres : les pièges statistiques
- 7. "Vrai et faux à la fois" : l'équivalence abstraite trompe
- 8. La boucle complète
- Checklist expérimentation

---

Mode **convergent**. Quand on ne sait pas, on n'optimise pas au pif : on
expérimente avec rigueur. Méthode scientifique appliquée à la perf. Les idées
viennent de `idea-generation.md` ; ici on les **réfute ou on les prouve**.

## 1. Hypothèse falsifiable (et chercher à la réfuter)

Formule : *"si je fais X, alors la métrique Y change de Z, parce que [mécanisme]."*
Une affirmation qu'aucune mesure ne pourrait contredire n'a aucune valeur
(Popper). **Cherche activement à la réfuter**, pas à la confirmer — le biais de
confirmation fait "voir" des gains qui n'existent pas. Une hypothèse qui survit à
une vraie tentative de réfutation est solide ; une qu'on n'a fait que caresser ne
vaut rien.

## 1b. Discipline de la conclusion (« définitif » ≠ « plausible »)

Avant d'écrire **« root cause trouvé »**, **« définitif »**, **« certain »** ou
**« impossible »** : écris explicitement le test qui prouverait l'hypothèse
**fausse** et fais-le passer. Si tu ne sais pas l'écrire — ou tu refuses de le
lancer — tu n'as pas de root cause, tu as une hypothèse qui te plaît.

Le piège est universel et survient dans n'importe quelle stack (Rust ↔ Python,
Go ↔ C, JVM ↔ natif, frontend ↔ backend, kernel ↔ userspace, browser ↔ node,
client ↔ serveur) : un test confirme la *corrélation* entre une variable et un
résultat, et la corrélation est interprétée comme *causalité*. Sans test de
réfutation, le claim « définitif » dure jusqu'au prochain test contradictoire —
qui arrive toujours.

**Règle pratique** : pour chaque claim « définitif », nomme explicitement
(a) **2-3 hypothèses alternatives** que ce claim est censé éliminer, (b) le
**test qui les élimine**. Si la liste est vide, le claim n'est pas une
conclusion — c'est un slogan.

**Tests interdits** (ils confirment au lieu de réfuter) :
- *« le seul fix qui marche est X → la cause est X »* — non, ça prouve juste
  que X corrèle. Test correct : isole CE qui change avec X (un axe à la fois)
  et teste les variantes qui le séparent du résultat.
- *« j'ai essayé Y et Z, ça ne marche pas → c'est forcément W »* — argument par
  élimination sans vérification que Y/Z étaient testés correctement.
- *« 70 tests verts → c'est correct »* — les tests vérifient ce qu'ils ont été
  conçus pour vérifier, pas l'invariant qui te manque.

## 2. Borne théorique d'abord (raisonner par l'absurde)

Avant de coder, calcule le **gain maximal possible**. Suppose l'optim parfaite :
combien gagnes-tu au mieux ? Amdahl, roofline, limite physique donnent le
plafond. Si le plafond est faible, **abandonne avant d'écrire une ligne**.
Reductio : "si cette piste était la bonne, alors [conséquence] — or
[contradiction observée] — donc fausse." Élimine par l'absurde les hypothèses qui
ne tiennent pas debout, à coût nul.

## 3. La table de mixage : ablation contrôlée

Pense chaque optimisation comme un **fader sur une table de mixage**. Pour savoir
ce que fait un fader, tu le bouges **seul**.

- **Une variable à la fois.** Si tu changes 3 choses et que ça accélère, tu ne
  sais pas laquelle (ni si l'une dégrade et une autre compense). Isole.
- **Ablation** : retire un facteur, mesure le delta → sa contribution réelle.
- **Sweep** : balaye une plage de valeurs d'un paramètre, trace la courbe (un
  optimum est rarement aux extrêmes).
- **Interactions** : deux faders peuvent interagir (l'un n'aide que si l'autre est
  poussé). Un plan factoriel les révèle, mais l'espace explose vite → priorise les
  facteurs à fort effet attendu.
- **Calibrer à la volée** : garde un harnais de bench qui rejoue ta charge en
  quelques secondes, pour bouger un fader et voir l'effet immédiatement. La
  boucle courte est ce qui rend l'expérimentation productive.

## 3b. Comparer deux stacks (langue + lib) : pin emboîté

Cas fréquent : *« pourquoi mon binaire Rust est plus lent que l'équivalent
Python ? »* (ou : Go vs Rust, JVM vs natif, framework A vs B). Trois confondants
empilés peuvent tous donner l'écart : le **code** (ton implémentation), la
**lib** (binding/wrapper), la **version** de la lib sous-jacente (ex. : un
binding Rust plafonné à mlx-c 0.25 vs Python à mlx 0.31). Ne tire **aucune**
conclusion sur le code avant d'avoir épluché les deux autres.

Protocole — pin par couches du plus extérieur au plus intérieur :

1. **Pin version** sur les deux stacks (vX vs vY *côté Python seul*, sur le
   *même* modèle, *même* entrée). Si l'écart disparaît → c'est la lib/version,
   pas ton code. **Stop, sors.**
2. **Pin format/architecture** (même version, modèle dense classique vs nouveau
   format suspecté). Si l'écart n'apparaît que sur le nouveau → c'est un
   kernel/chemin de code spécifique à ce format.
3. **Pin composant** (le forward avec et sans un sous-bloc — MoE, linear-attn,
   shared-expert, etc.). Le sous-bloc dont l'inclusion change le verdict **est**
   le coupable.

Deux règles non négociables :
- **Un échec de chargement est une donnée**, pas un blocage. *« Architecture non
  supportée par cette version »* tranche l'hypothèse « c'est la version »
  côté cette branche — sans qu'aucun chiffre ne soit mesuré.
- **Avant de bumper la lib** (forker un binding, vendorer une dépendance C,
  etc.) : **profile d'abord** le kernel suspect intra-version (cf.
  `bench-protocol.md` § Routage GPU). Bumper sans profil = pari coûteux ; profile
  d'abord, puis bump *si et seulement si* le kernel s'avère intrinsèquement plus
  lent dans la version pinned.

## 3c. Port-by-comparison : ne pas quit à la frontière framework

Cas symétrique du §3b. Un appel **marche** dans le stack A (souvent un binding
officiel : Python/nanobind, Node/N-API, JVM/JNI, Ruby/FFI…) et **casse** dans le
stack B (souvent un binding tiers : crate Rust, module Go cgo, package Swift…) —
**mêmes données, mêmes args, même fonction native sous-jacente**. Le réflexe
*« je ne peux pas sans débugger les internes du framework »* est presque toujours
faux : le lever est **le diff entre les deux chemins**, pas une nouvelle
intuition.

Procédure (langage-agnostique) :

1. **Capture le call au niveau natif dans les deux mondes.** Selon l'OS et la
   stack :
   - `lldb` / `gdb` breakpoint sur la fonction native commune (toutes plateformes).
   - `dtruss` (macOS) / `strace` (Linux) / Process Monitor (Windows) sur le binaire.
   - Patch du binding qui marche pour écrire les args struct sur stderr
     (pointeurs, flags, strides, dtype, stream, capability bits…).

   Tu obtiens **deux dumps** sur la *même* entrée.

2. **Diff binaire** des structs. Tout champ qui diffère est suspect *et*
   falsifiable : aligne-le côté qui casse, re-test, refute ou confirme. Un par
   un, pas plusieurs (cf. §3 ablation).

3. **Pour les handles opaques** (tensors / arrays / buffers GPU / sockets /
   handles OS — `mlx_array`, `torch.Tensor`, `np.ndarray`, `tf.Tensor`,
   `cl_mem`, `VkBuffer`, `HANDLE`…) : casse le lineage / le graph parent en
   sérialisant + re-chargeant via le format public (safetensors, npy, raw
   bytes, protobuf). Tu obtiens une struct fraîche dont la généalogie est
   connue, identique côté A et B.

**Règles non négociables :**

- **« Au-delà du raisonnable »** / **« limite atteinte »** à la frontière d'un
  framework qui marche ailleurs = quit injustifié. La frontière est l'endroit
  où on sort le profiler bas niveau, **pas** l'endroit où on abandonne.
- Le **workaround** est acceptable **temporairement** (cf. `benchmarking-traps.md`
  §12), mais tagué explicitement avec ticket de suivi, sinon il devient permanent.
- **Le binding qui marche est ton oracle.** Si A marche et B casse, A fait
  *forcément* quelque chose en plus — soit explicitement (init, eval,
  contiguous), soit implicitement (stream par défaut, device par défaut,
  capability bits, layout normalization). Diffe les **sources des deux
  bindings**, pas seulement les call paths observés.

## 4. Gérer l'aléa (variance) — dans les deux sens

L'aléa est un outil, à augmenter ou diminuer selon l'objectif :

- **Diminuer l'aléa pour mesurer proprement.** Tu veux que la *seule* chose qui
  varie soit ton fader. Fixe les seeds, isole l'environnement (CPU pinning, pas de
  bruit de fond), warm-up avant mesure, plusieurs runs, surveille le
  throttling/turbo thermique, vide ou pré-chauffe les caches de façon cohérente.
- **Augmenter l'aléa pour explorer et stresser.** Inputs randomisés
  (fuzzing, property-based testing), charges variées, chaos engineering,
  recherche aléatoire d'hyperparamètres. L'aléa contrôlé révèle les cas limites,
  la robustesse et les hypothèses cachées.
- **Rapporte une distribution, jamais un point.** Médiane + p95/p99 + écart-type,
  pas seulement la moyenne. Un "gain" plus petit que le bruit de mesure n'existe
  pas — mesure l'écart-type *avant* de croire à un delta.

## 5. Mesurer en plusieurs dimensions (4D, 5D, 6D…)

La perf n'est jamais un seul nombre. Les axes typiques : **latence**, **débit**,
**mémoire**, **énergie**, **coût**, **précision/qualité**, **robustesse**,
**maintenabilité**, et la **perception** (latence *ressentie* ≠ latence réelle :
un streaming, une barre de progression, un rendu optimiste changent le perçu sans
changer le temps machine).

- Optimiser un axe en dégrade souvent un autre → c'est un **front de Pareto** :
  l'ensemble des solutions où l'on ne peut améliorer un axe sans en sacrifier un
  autre. Choisis un point selon tes priorités ; **ne collapse pas tout en un seul
  scalaire trop tôt** (une moyenne pondérée cache les trade-offs).
- Déclare explicitement quel axe tu optimises et lesquels tu acceptes de dégrader.

## 6. Challenger les chiffres : les pièges statistiques

Deux résultats peuvent mentir de façon opposée :

- **Mêmes statistiques ≠ mêmes données.** L'**Anscombe's quartet** (1973) et le
  **Datasaurus Dozen** (Matejka & Fitzmaurice, 2017, *"Same Stats, Different
  Graphs"*) : des jeux de données aux moyenne/variance/corrélation identiques à
  deux décimales, mais aux formes radicalement différentes une fois tracées (l'un
  dessine un dinosaure). **Visualise toujours la distribution**, ne te fie jamais
  à un agrégat seul.
- **Corrélation ≠ causalité.** Deux courbes qui se ressemblent (semblent "iso")
  peuvent n'avoir aucun lien — voir les *spurious correlations* de Tyler Vigen.
  Avant d'attribuer un gain à ta modif : qu'est-ce qui a changé d'autre (cache
  chaud, charge différente, voisin bruyant, autre déploiement) ? Élimine les
  facteurs confondants.
- **Moyenne vs queue** : la moyenne ment sur les p99 ; en perf, ce sont les
  queues qui pénalisent (tail latency).
- **Benchmark non représentatif** : le synthétique n'est pas la prod. Mesure sur
  ta vraie charge, tes vraies longueurs/distributions d'entrée.

## 7. "Vrai et faux à la fois" : l'équivalence abstraite trompe

Deux choses égales sous une mesure peuvent diverger sous une autre — **challenge
toute "équivalence"** : équivalente *selon quelle mesure*, avec *quel comportement
opérationnel* ?

Exemple canonique : `Σᵢ Σⱼ A[i][j] == Σⱼ Σᵢ A[i][j]` — les sommes commutent, la
**valeur est identique**. Mais l'ordre des boucles `i`/`j` a un **comportement de
cache opposé** (parcours row-major vs column-major) : même résultat
mathématique, perf radicalement différente (cf. `memory-cache.md` §4).
Mathématiquement vrai, computationnellement faux. Même piège entre : "même
complexité O()" mais constantes/queues différentes ; "même intégrale" mais
distributions différentes ; "même API" mais coûts cachés opposés.

## 8. La boucle complète

hypothèse falsifiable → borne théorique (jette si plafond faible) → expérience
contrôlée (un fader) → mesure multi-D + distribution → réfute ou prouve →
généralise *prudemment* → recommence. **Documente les échecs** : une optim qui ne
marche pas est une information (elle élague l'espace pour la suite).

## Checklist expérimentation
1. Mon hypothèse est-elle falsifiable, et ai-je essayé de la **réfuter** ?
2. Ai-je calculé la **borne max** du gain avant de coder ?
3. Une seule variable à la fois (ablation/sweep) — ou suis-je en train de tout
   bouger en aveugle ?
4. Ai-je contrôlé l'aléa (seeds, isolation, runs multiples) et rapporté une
   distribution (p95/p99), pas une moyenne ?
5. Quels axes (latence/débit/mémoire/énergie/coût/perçu) — et lesquels j'accepte
   de dégrader (Pareto) ?
6. Ai-je **visualisé** les données (pas juste les stats) et écarté les confondants
   (corrélation ≠ causalité) ?
7. **Discipline de la conclusion** (§1b) : pour chaque claim « définitif », ai-je
   nommé 2-3 alternatives et le test qui les élimine ?
8. **Workaround net** (cf. `benchmarking-traps.md` §12) : si mon « fix » est un
   contournement, ai-je mesuré le coût net (gain − coût) et tagué
   `WORKAROUND, target: real fix` ?
9. **Frontière framework** (§3c) : si je suis tenté de quit à « limite atteinte »
   sur une stack qui marche ailleurs, ai-je vraiment diffé les structs / call
   paths des deux bindings, pas juste essayé des variantes dans mon code ?

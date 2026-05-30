# Pensée latérale : dissoudre les contraintes implicites

Extension radicale du mode divergent (`idea-generation.md`). On s'impose presque
toujours deux murs invisibles sans s'en rendre compte :
1. **le niveau** auquel on accepte d'écrire le code ;
2. **le domaine** d'où on accepte que viennent les solutions.

Ce fichier fait tomber les deux. Tout ce qui en sort est une **hypothèse** à
valider ensuite par `experiment-method.md` — la pensée latérale génère, elle ne
prouve pas.

## 1. Liberté verticale — réécrire à n'importe quel niveau

Le niveau d'abstraction qu'on t'a donné **n'est pas une contrainte**. Une fois le
hot path isolé (le 1 % qui compte, cf. `profiling.md`), tu peux le réécrire au
niveau qui donne le plus de levier, en laissant les 99 % restants en haut niveau.
Le mixed-level est normal : orchestration confortable en haut, kernel chaud en
bas. L'échelle, du haut vers le bas :

- **Langage plus rapide via FFI** : Python → extension Rust/C (PyO3, Cython,
  cffi). Tu gardes Python autour, tu descends pour la boucle chaude.
- **Descendre en C** depuis un langage managé pour un kernel critique.
- **Intrinsics SIMD / `asm!` inline** pour le noyau le plus chaud (cf.
  `math-physics.md`, `systems-hardware.md`).
- **IR / bytecode** : LLVM IR, WASM, bytecode ajustés à la main.
- **Patch binaire / édition hexa** : NOP une instruction, patcher une constante,
  corriger un binaire qu'on ne peut pas recompiler. Rare, mais valide.
- **Codegen / métaprogrammation** : générer du code **spécialisé au build**
  (macros, `const generics`, monomorphisation, JIT, spécialisation de template)
  au lieu de code générique évalué au runtime.
- **Monter d'un niveau (DSL)** : exprimer le problème dans un langage dédié qui
  compile vers du code optimal — une requête qu'un moteur optimise, un graphe de
  tenseurs, un automate de regex. Parfois la meilleure optim est *plus*
  d'abstraction, pas moins.
- **Hardware** : offload FPGA / ASIC / GPU pour le kernel vraiment chaud.
- **Changer la représentation des données** : l'encodage octet/bit est à toi —
  bit-packing, varint, format binaire custom, colonne, SoA. « Hexa peu importe » :
  tu n'es pas obligé d'accepter la structure de données fournie.

**Garde-fou.** Chaque niveau descendu coûte en maintenabilité, portabilité,
sûreté. Ne descends que pour un hot path **mesuré**, isole-le derrière une
interface propre, et garde une **impl de référence haut niveau** pour tester
l'équivalence (mêmes entrées → mêmes sorties). Et certaines contraintes ne se
dissolvent pas : le constant-time crypto, la sûreté mémoire, la correction. Les
contourner n'est pas de l'optimisation, c'est un bug en attente.

## 2. Liberté horizontale — détourner d'autres domaines & équipements

Les solutions existent souvent dans un champ sans rapport, ou dans le matériel
que tu as **déjà**, utilisé pour ce qu'il n'a pas été conçu.

**Exemple phare — le WiFi comme capteur.** La CSI (Channel State Information)
d'un WiFi standard permet de détecter une présence, un mouvement, une position,
voire la respiration ou une chute — sans caméra ni capteur dédié, en réutilisant
le matériel existant. C'est même standardisé (IEEE 802.11bf). Pourquoi ça ne vient
pas à l'esprit en premier ? Parce qu'on classe « WiFi » sous *réseau*, jamais sous
*capteur*. La catégorie mentale est le mur.

Le pattern : **inventorie les effets de bord et capacités latentes** de ce que tu
possèdes, puis demande « qu'est-ce que ça pourrait mesurer/faire d'autre ? »
- Side-channel temporel → une *feature* (sonder l'état du cache, mesurer la
  contention), pas seulement une faille.
- Télémétrie / logs déjà émis → signal gratuit pour autre chose.
- Cycles GPU/CPU idle → offload de calcul opportuniste.
- Émissions son / vibration / EM / consommation → capteur.

**Transfert inter-domaines** : emprunte des modèles à des champs lointains —
logistique (routing, files d'attente), physique (recuit, diffusion, propagation
d'ondes), biologie (gossip, immunité — `bio-inspired.md`), économie (enchères pour
l'allocation de ressources), théorie du contrôle (PID pour l'autoscaling),
théorie de l'information (compression = modélisation). Deux questions quand tu
bloques :
1. **Qui a un problème structurellement identique dans un domaine totalement
   différent ?** (et comment l'a-t-il résolu ?)
2. **Quelle capacité ai-je déjà sous la main, mais rangée dans la mauvaise
   catégorie ?**

## 3. Inversion radicale & le « 5e cerveau »

Prendre le problème à l'envers — **deux fois** :
- **1ʳᵉ inversion** : « comment rendre X le plus lent possible ? » → la liste est
  ta liste de fixes (déjà dans `idea-generation.md`).
- **2ᵉ inversion (radicale)** : questionne **le problème lui-même**, pas la
  solution. « Et si X n'avait pas besoin d'exister ? et si l'exigence était mal
  posée ? et si on supprimait la feature qui crée le besoin ? » Le plus gros gain
  vient souvent de **ne pas avoir le problème**.

**Provocation latérale** (De Bono) : quitte volontairement la voie logique avec
une hypothèse absurde — « et si la mémoire était infinie ? nulle ? si ça tournait
à l'envers ? si c'était aléatoire, gratuit, instantané ? » — pour sauter vers une
approche neuve, puis ramène l'idée vers le faisable.

**Le « 5e cerveau »** : ne reste pas seul avec ton cerveau analytique par défaut.
Recrute délibérément une intelligence externe/latérale — un LLM ou un outil comme
partenaire de pensée — pour générer des analogies inter-domaines qu'on n'atteint
pas en raisonnant en ligne droite, confronter des angles opposés, et prendre du
recul méta sur le cadrage du problème.

## Garde-fou final

La pensée latérale est **bon marché à produire et chère à croire**. Une idée
sauvage (WiFi sensing, patch hexa, offload FPGA, analogie d'un autre domaine) est
une **hypothèse**, pas un résultat : envoie-la systématiquement dans la boucle de
`experiment-method.md` (borne théorique → expérience → mesure). Et ne confonds
pas « dissoudre une contrainte arbitraire » avec « ignorer une contrainte qui
existe pour une raison » (sécurité, correction, vie privée, légal). Dissoudre, ce
n'est pas oublier *pourquoi* le mur était là.

## Checklist pensée latérale
1. À quel **niveau** ai-je supposé devoir écrire — et lequel donnerait plus de
   levier sur ce hot path précis (FFI, asm, codegen, DSL, hardware, représentation) ?
2. Quelle **capacité que je possède déjà** est rangée dans la mauvaise catégorie
   (effet de bord exploitable, équipement détournable) ?
3. Quel **autre domaine** a un problème structurellement identique, déjà résolu ?
4. Ai-je inversé **le problème lui-même** (2ᵉ inversion), pas seulement la
   solution ?
5. Chaque idée latérale part-elle bien en **validation** (et ne casse aucune
   contrainte légitime) ?

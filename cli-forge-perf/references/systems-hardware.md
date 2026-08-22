# Systèmes & limites physiques

## Contents

- 1. Identifier la limite physique
- 2. Rééquilibrer entre proc / RAM / disque (les trade-offs)
- 3. Syscalls : moins et mieux
- 4. Exploiter les accélérateurs hardware
- 5. NUMA & affinité (multi-socket / gros serveurs)
- 6. Footprint binaire & démarrage
- 7. Énergie / conso
- Checklist systèmes/hardware

---

Axe transverse bas niveau : quand on cherche à **taper les limites du hardware**
et à équilibrer les ressources. L'idée centrale : chaque ressource (calcul, RAM,
bande passante, I/O) a un **plafond physique** ; l'optimisation consiste à savoir
de quel plafond on est proche et à **rééquilibrer le travail** vers la ressource
la moins saturée.

## 1. Identifier la limite physique

Pour chaque ressource, compare l'usage réel au plafond théorique :

| Ressource | Plafond | Mesure |
|---|---|---|
| Calcul | FLOPS/IPC max du CPU/GPU | `perf stat` (IPC), compteurs PMU |
| Bande passante mémoire | GB/s du contrôleur | `likwid`, STREAM benchmark |
| I/O disque | IOPS / débit du SSD | `fio`, `iostat` |
| Réseau | Gbps du lien | `iperf`, métriques NIC |

Si tu es à **30 %** d'un plafond → il y a du gras, optimise l'usage. Si tu es à
**95 %** → tu touches le mur physique : la seule issue est de **faire moins de
travail** (moins de données, meilleur algo), pas de "faire plus vite".

## 2. Rééquilibrer entre proc / RAM / disque (les trade-offs)

Le cœur de l'optimisation systèmes : déplacer la charge vers la ressource non
saturée. Ça dépend de quel côté du **roofline** tu es (cf. profiling.md).

- **Recompute vs transfert** : si tu es *bandwidth-bound*, **recalculer** une
  valeur peut être plus rapide que la **lire/transférer** (le CPU a du rab). Si
  tu es *compute-bound*, l'inverse : **pré-calcule et stocke** (lookup table,
  mémoïsation). Même opération, décision opposée selon le goulot.
- **Compression** : compresser réduit la bande passante (disque→RAM, réseau,
  RAM→CPU) au prix de cycles CPU. **Gagnant si bandwidth-bound** (DB analytique,
  réseau, gros datasets) : formats colonne (Parquet), LZ4/zstd, bit-packing
  d'entiers. Perdant si déjà compute-bound.
- **Hiérarchie mémoire** (registre > L1 > L2 > L3 > RAM > SSD > réseau) : garde
  le *working set* au niveau le plus haut possible. Le **tiling/blocking**
  (découper un calcul pour que le bloc tienne en cache) transforme une
  multiplication de matrices memory-bound en compute-bound → gros gain. Lien
  direct avec la cache locality (memory-cache.md).
- **Co-localisation calcul/données** : ne fais pas transiter de gros volumes sur
  le réseau pour les traiter ailleurs. **Push down** le calcul vers la donnée
  (agrégats dans la DB, compute near storage) plutôt que de tout rapatrier.

> Exemple type : "j'augmente le calcul, j'augmente la RAM, je diminue la bande
> passante entre les deux" = on échange du compute/du stockage cache contre du
> transfert. C'est exactement le levier roofline appliqué aux 3 niveaux.

## 3. Syscalls : moins et mieux

Chaque appel système = transition user↔kernel coûteuse. Sur de l'I/O intensive,
le nombre de syscalls domine souvent le temps. Mesure avec `strace -c`.

- **Buffering / batching** : écris par gros blocs (`BufWriter`, `writev`/`readv`)
  au lieu d'un syscall par octet/ligne.
- **`io_uring`** (Linux) : I/O asynchrone soumise en batch → des milliers de
  syscalls deviennent quelques soumissions. Énorme pour les serveurs I/O-bound.
- **`mmap`** : mappe un fichier en mémoire au lieu de `read`/`write` répétés
  (utile en lecture aléatoire sur gros fichier).
- **Zero-copy** : `sendfile`/`splice` évitent les copies user↔kernel (proxy,
  serveur de fichiers).

## 4. Exploiter les accélérateurs hardware

Beaucoup de libs ont un **fallback software lent** si elles ne détectent pas (ou
n'activent pas à la compilation) les instructions dédiées. C'est le piège du "ça
devrait être rapide mais ça rame".

| Domaine | Instructions / accélérateur | Gain typique si activé |
|---|---|---|
| Crypto symétrique | **AES-NI**, VAES | 5-20× vs software |
| Hash | **SHA extensions** | 2-8× |
| Crypto GCM/CRC | **CLMUL**, CRC32 hardware | plusieurs × |
| Calcul vectoriel | **AVX2/AVX-512**, NEON | 4-16× (cf. math-physics.md) |
| Massivement parallèle | **GPU/NPU/TPU** (CUDA/Metal/ROCm) | ordres de grandeur (ML, rendu) |

**Le cas crypto** : une lib qui déchiffre lentement utilise probablement une impl
pure-software au lieu d'AES-NI. À vérifier :
- la lib **détecte le CPU au runtime** (ex. OpenSSL `OPENSSL_ia32cap`, ou un
  build qui sonde les features) ;
- le binaire est compilé avec les bonnes cibles (`-maes`, `target-cpu=native`,
  features SIMD activées) ;
- ce n'est pas une crate/lib "pure software" choisie par portabilité.

Méthode générale : si une opération **standard** (crypto, hash, compression,
matmul) est anormalement lente, **soupçonne un fallback software** → vérifie les
flags de build et la détection runtime avant toute autre optim.

## 5. NUMA & affinité (multi-socket / gros serveurs)

Accéder à la RAM d'un autre nœud NUMA est plus lent que la RAM locale. Sur du
multi-socket : pin les threads et alloue la mémoire sur le bon nœud
(`numactl`, affinité CPU, allocations NUMA-aware). Vérifie aussi le faux partage
(false sharing — cf. async-concurrency.md).

## 6. Footprint binaire & démarrage

Pour l'embarqué, les conteneurs, le cold start (FaaS) :
- **LTO** + `codegen-units=1` + `opt-level=z`/`s` + `panic=abort` (Rust) ;
  strip des symboles ; static linking ciblé.
- Réduire les dépendances (cf. dependencies.md) → moins de code à charger/lier.
- Conteneurs : multi-stage, base **distroless / FROM scratch** → image minimale,
  cold start et surface d'attaque réduits.
- Outils : `cargo bloat`, `size`, `du`.

## 7. Énergie / conso

Sur batterie ou en datacenter : **race-to-idle** (finir vite pour laisser le CPU
dormir), réduire les wakeups/timers, regrouper les I/O. Moins de travail = moins
de watts. Souvent corrélé à la vitesse, mais pas toujours (un burst efficace bat
un calcul étalé qui empêche le sleep).

## Checklist systèmes/hardware
1. À quel % du plafond physique suis-je sur la ressource limitante ?
2. Suis-je bandwidth-bound ? → compresser / recompute / tiling / push-down.
3. `strace -c` : trop de syscalls ? → buffering, io_uring, mmap, zero-copy.
4. Les libs "standard" (crypto, hash, compression, matmul) exploitent-elles le
   hardware (AES-NI, SIMD, GPU) ou tombent-elles en fallback software ?
5. Multi-socket : threads/mémoire NUMA-aware ?
6. Footprint : build release optimisé, image conteneur minimale ?

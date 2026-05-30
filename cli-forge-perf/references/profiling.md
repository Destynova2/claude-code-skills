# Profiling, tracing & diagnostic du bottleneck

Niveau 0. **On ne devine pas, on mesure.** Cette étape décide *où* dans la
hiérarchie se trouve réellement le goulot — donc quelle optim a le droit
d'exister. Sauter cette étape = optimiser au hasard.

## 1. "Pourquoi X est plus lent que Y ?" (ex. Python plus rapide que Rust)

Quand un langage/lib réputé rapide est plus lent qu'attendu, **ce n'est presque
jamais le langage** : c'est un facteur caché. Méthodo :

1. **Reproduis un bench fiable** : `hyperfine` (CLI) ou Criterion (Rust),
   warm-up, mêmes entrées, plusieurs runs, isole le code mesuré du reste (I/O,
   logs). Compare des p50/p95, pas un run unique.
2. **Profile les DEUX côtés** et compare les flamegraphs : où part le temps ?
3. **Vérifie les suspects classiques** (par ordre de fréquence) :

| Suspect | Symptôme | Fix |
|---|---|---|
| **Build debug** (Rust) | `cargo build` sans `--release` → 10-100× plus lent | builder en `--release` |
| **Python qui appelle du C** | NumPy/regex/polars = C optimisé sous le capot | tu compares C vs ton Rust naïf, pas Python vs Rust |
| **Allocations/clones cachés** | `String`/`Vec` réalloués, `.clone()` en boucle | `&str`/slices, pré-alloc, réutilise les buffers |
| **I/O non bufferisée** | `println!`/write par ligne, lock stdout | `BufWriter`, écrire par blocs |
| **Mauvais algo/structure** | O(n²) masqué, mauvais conteneur | corrige l'algo (cf. algorithmic.md) |
| **Overhead FFI/sérialisation** | temps aux frontières (PyO3, JSON) | batch les passages de frontière |
| **Flags de compilation** | pas de LTO, pas `target-cpu=native` | cf. dependencies.md / systems-hardware.md |

Le réflexe : **un résultat contre-intuitif = un facteur caché à instrumenter**,
pas une conclusion sur le langage.

## 2. Tracing distribué (OpenTelemetry)

Pour les systèmes répartis/microservices, le profiler CPU local ne voit qu'une
brique. Le tracing relie les **spans** d'une requête de bout en bout (propagation
de contexte entre services) et révèle où part la latence — le plus souvent dans
un appel réseau/DB en attente, pas dans le CPU.

- Instrumente avec **OpenTelemetry** (traces + métriques + logs corrélés),
  exporte vers Jaeger/Tempo/Grafana.
- Regarde les **p95/p99**, pas la moyenne : ce sont les queues (tail latency) qui
  pénalisent les utilisateurs. Une moyenne basse cache souvent des p99 atroces.
- **Exemplars** : relie une métrique lente à la trace exacte qui l'a produite.
- Trouve le span dominant du *chemin critique* (le plus long, pas la somme des
  parallèles), puis zoome dedans avec un profiler.

## 3. Profilers selon la couche

| Question | Outil |
|---|---|
| Où le CPU passe-t-il son temps ? | `perf` + flamegraph, `cargo flamegraph`, `py-spy`, async-profiler (JVM) |
| Qui alloue / fuit ? | `dhat`, `heaptrack`, `valgrind --tool=massif` |
| Sur quoi ça **attend** (off-CPU) ? | off-CPU profiling, `perf sched`, blocked-time analysis |
| Combien de syscalls / lesquels ? | `strace -c`, `ltrace` |
| Latences kernel/réseau sans toucher le code | **eBPF** : `bpftrace`, `bcc` |
| Le CPU travaille-t-il bien ? | `perf stat` → IPC, cache-miss rate, branch-miss |

Le couple **CPU profiler + off-CPU profiler** est clé : l'un montre où ça calcule,
l'autre où ça attend. Un service "lent" à 5 % de CPU est off-CPU (I/O/lock), pas
CPU-bound — optimiser le calcul n'y changera rien.

## 4. Classer le bottleneck (roofline) avant de choisir l'optim

Détermine la **nature** du goulot → ça pointe vers le bon niveau de la hiérarchie :

| Nature | Signe | Va voir |
|---|---|---|
| **CPU-bound** | CPU à ~100 %, IPC correct | algorithmic.md → puis math-physics.md |
| **Memory-bound** | CPU à fond mais IPC bas, cache-miss élevé | memory-cache.md (locality) |
| **Bandwidth-bound** | bus mémoire/réseau saturé, peu de calcul/octet | systems-hardware.md (compression, recompute) |
| **I/O-bound** | CPU faible, attente disque/DB/réseau | database.md + async-concurrency.md |
| **Lock-bound** | threads en attente, peu de progrès | async-concurrency.md (contention) |
| **Syscall-bound** | beaucoup de temps kernel (`strace -c`) | systems-hardware.md (batching syscalls) |

**Roofline model** : un calcul est plafonné soit par le débit CPU (FLOPS max)
soit par la bande passante mémoire, selon son *arithmetic intensity* (FLOP par
octet transféré). Si tu es sous le "toit bande passante", optimiser le calcul ne
sert à rien — c'est le transfert qu'il faut réduire. Ça évite des journées
perdues à accélérer un calcul qui n'est pas la limite.

## Checklist diagnostic
1. Ai-je une baseline chiffrée et reproductible (hyperfine/Criterion) ?
2. Pour un écart surprenant : ai-je vérifié build release, allocs, I/O,
   "Python qui appelle du C" avant de blâmer le langage ?
3. Est-ce CPU-bound, memory-bound, bandwidth-bound, I/O-bound, lock- ou
   syscall-bound ? (sinon je ne sais pas quoi optimiser)
4. Sur du distribué : ai-je le span dominant du chemin critique (p99) en tracing ?
5. Le code est-il on-CPU (calcule) ou off-CPU (attend) ?

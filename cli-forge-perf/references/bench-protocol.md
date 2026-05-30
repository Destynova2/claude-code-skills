# Protocole de bench (langue-agnostique)

L'actif réutilisable de la mesure de perf n'est ni un outil ni un langage — c'est la **méthode** (warmup, distribution, A/B interleavé, test de permutation, anti-DCE) et la **règle de verdict** (Δ dans le bruit ⇒ pas de gain). Ce fichier définit le protocole, **route vers l'outil natif** selon le langage/cas, et donne des **squelettes prêts à copier** dans la langue voulue.

## Frontière de mesure & portabilité (avant de choisir un outil)

Deux contraintes décident le choix :
- **Frontière de mesure.** Mesurer une commande externe (boîte noire) inclut le
  **démarrage du process** : inutilisable sous la milliseconde (cf.
  `benchmarking-traps.md` §6). Pour un hot path fin, il faut mesurer **in-process,
  dans le langage cible**.
- **Portabilité réelle.** Aucun runtime n'est portable partout : Python n'existe pas dans un conteneur FROM scratch, sur un nœud minimal ou en embarqué. Un binaire Rust ne tourne pas sur la JVM. Pour une cible minimale, le bench doit être **natif** (compilé dans l'artefact, ou intégré au framework de test du langage).

Pour la boîte noire CLI quand l'environnement le permet : **hyperfine** (Rust, binaire statique) est le défaut — warmup, A/B avec ratio + σ, JSON exportable, pas de dépendance interpréteur.

## Le protocole (identique quel que soit le langage)

1. **Warmup** : W itérations jetées (JIT, cache, fréquence — cf. `benchmarking-traps.md`).
2. **Échantillons** : N≥20-30 mesures conservées.
3. **Distribution** : rapporte **médiane + p95/p99 + σ**, jamais une moyenne seule.
4. **A/B** : **interleave** (A,B,A,B…) ; compare les **médianes** ; significativité
   par **test de permutation** ou **Mann-Whitney U**. Δ dans le bruit → *pas de gain*.
5. **Anti-pièges** : **consomme le résultat** (sinon dead-code elimination) et
   **fais varier l'entrée** (sinon constant folding).

## Routage : quel outil pour quel cas

| Cas | Outil natif recommandé | Comparaison/significativité |
|---|---|---|
| Rust, micro in-process | **Criterion** (stats rigoureuses) ou `divan` | baseline intégré, détecte les régressions |
| Go | `testing.B` + **benchstat** | benchstat fait un **test U de Mann-Whitney** |
| C/C++ | **Google Benchmark** (ou `clock_gettime` à la main) | à la main / scripts |
| JVM | **JMH** | intervalles de confiance |
| JS/TS | **mitata** / tinybench | intégré |
| CLI / boîte noire | **hyperfine** | ratio + σ, A/B intégré |
| Python | **pytest-benchmark** / `timeit` | intégré |
| **macOS GPU / Metal** | **`xctrace record --template 'Metal System Trace'`** (headless, sans Xcode) | timeline GPU exportable XML/JSON, agrégation par **compute pipeline label = nom du kernel** |
| **Linux GPU / CUDA** | **`nsys profile`** (Nsight Systems CLI) | timeline kernel + traces NVTX, exportable via `nsys stats` |

Préfère **toujours** un framework natif mûr (Criterion, JMH, benchstat) à une
boucle maison : ils gèrent warmup, outliers et stats bien mieux. Le squelette
« à la main » n'est qu'un fallback air-gap quand tu ne peux pas ajouter la dépendance.

### Piège GPU à éviter (inspection ≠ profil)

Pour une question de **« où va le temps GPU par kernel ? »**, utilise un *profiler* (timeline temporelle, agrégation par label de pipeline) — **pas un *inspecteur*** (replay GUI d'un dispatch pour lire buffers/textures/shader-line cost). Le piège classique :

| Outil | Question répondue | Tu en as besoin si… |
|---|---|---|
| **macOS** `xctrace Metal System Trace` (profiler) | où passe le temps ? | tu cherches le hotspot kernel — **headless, agent-friendly** |
| **macOS** `.gputrace` + GPU Debugger Xcode (inspecteur) | que contient ce dispatch ? | tu veux lire un buffer ou auditer un shader ligne par ligne — **GUI-only** |
| **CUDA** `nsys profile` (Nsight Systems) | où passe le temps ? | profil temporel kernel-level |
| **CUDA** Nsight Graphics (inspecteur) | que contient cette frame ? | inspection draw/dispatch |

Ce sont **deux outils pour deux questions distinctes**, pas deux niveaux d'un même outil. Tomber dans le mauvais (par exemple ouvrir un `.gputrace` 17 Go pour chercher un goulot de débit) brûle des heures pour zéro signal exploitable.

Pour le principe général « quand passer du headless au GUI ? » et les conditions de rung 5, voir `../../shared/escalation-ladder.md` — `xctrace` = rung 1, GPU debugger / `.gputrace` = rung 5, et le réflexe « j'attaque direct en GUI » est un anti-pattern documenté.

## Squelettes prêts à copier

**Rust — Criterion (recommandé)** — `Cargo.toml`: `[dev-dependencies] criterion="0.5"`,
`[[bench]] name="b" harness=false`
```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};
fn bench(c: &mut Criterion) {
    let input = make_input();              // données réalistes ET variables
    let mut g = c.benchmark_group("hot_path");
    g.bench_function("v1", |b| b.iter(|| black_box(v1(black_box(&input)))));
    g.bench_function("v2", |b| b.iter(|| black_box(v2(black_box(&input)))));
    g.finish();
}
criterion_group!(benches, bench);
criterion_main!(benches);
// cargo bench -- --save-baseline avant ; <modif> ; cargo bench -- --baseline avant
```

**Rust — std seul (fallback air-gap, zéro dépendance)**
```rust
use std::{hint::black_box, time::Instant};
fn bench(name: &str, warmup: u32, n: usize, mut f: impl FnMut()) {
    for _ in 0..warmup { f(); }
    let mut s: Vec<f64> = (0..n).map(|_| { let t = Instant::now(); f(); t.elapsed().as_secs_f64() }).collect();
    s.sort_by(|a, b| a.partial_cmp(b).unwrap());
    println!("{name}: médiane {:.3} ms  p95 {:.3} ms", s[n/2]*1e3, s[(n as f64*0.95) as usize]*1e3);
}
// bench("v1", 100, 1000, || { black_box(v1(black_box(&input))); });
```

**Go** — `testing.B` + benchstat (Mann-Whitney U)
```go
var sink Result // empêche la DCE
func BenchmarkV1(b *testing.B) { in := makeInput(); b.ResetTimer(); for range b.N { sink = v1(in) } }
// go test -bench=. -count=10 > old.txt ; <modif> ; > new.txt ; benchstat old.txt new.txt
```

**C** — `clock_gettime(CLOCK_MONOTONIC)`
```c
#include <time.h>
static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec + t.tv_nsec*1e-9; }
// warmup, puis N runs: double t=now(); volatile r = f(input); samples[i]=now()-t;  (volatile => pas de DCE)
// qsort puis médiane/p95 ; faire varier input pour éviter le constant folding.
```

**CLI / boîte noire** — hyperfine
```sh
hyperfine --warmup 3 -N 'cmdA' 'cmdB'          # -N: pas de shell (overhead minimal)
hyperfine --export-json r.json 'cmdA' 'cmdB'   # exploitable par script
```

Les squelettes ci-dessus sont prêts à copier — sélectionne la langue cible selon le tableau de routage et adapte les paramètres (W warmup, N runs) au régime visé.

## Checklist protocole
1. Frontière correcte : in-process (sub-ms / hot path) vs boîte noire (CLI) ?
2. Outil **natif mûr** quand il existe (Criterion/JMH/benchstat) plutôt qu'une boucle maison ?
3. Warmup + N échantillons + distribution (p95/p99), pas une moyenne ?
4. A/B interleavé + significativité (permutation / Mann-Whitney) ?
5. Résultat consommé (anti-DCE) et entrée variable (anti-constant-folding) ?

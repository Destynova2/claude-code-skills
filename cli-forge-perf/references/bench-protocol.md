# Protocole de bench (langue-agnostique)

`perfloop.py` n'est qu'**une** implémentation d'un protocole. L'actif réutilisable
n'est pas le Python — c'est la **méthode de mesure** et la **règle de verdict**,
qui s'implémentent dans n'importe quel langage. Ce fichier définit le protocole,
**route vers l'outil natif** selon le langage/cas, et donne des **squelettes prêts
à copier** (« génère la preuve dans la langue que tu veux »).

## Pourquoi un driver générique, et où il s'arrête

Un *driver* de bench est de l'orchestration : il dort en attendant le sous-process.
Sa propre vitesse n'a **aucune** importance → le langage du driver est accessoire.
Ce qui compte :
- **La frontière de mesure.** Mesurer une commande externe (boîte noire) inclut le
  **démarrage du process** : inutilisable sous la milliseconde (cf.
  `benchmarking-traps.md` §6). Pour un hot path fin, il faut mesurer **in-process,
  dans le langage cible**.
- **La portabilité réelle.** « Zéro dépendance » côté Python suppose python3
  présent — faux dans un conteneur FROM scratch, sur un nœud minimal ou en
  embarqué. Là, le bench doit être **natif** (compilé dans l'artefact).

Donc : `perfloop.py` = **runner CLI zéro-setup pour de la boîte noire** quand
python3 est là. Pour le sub-ms, l'in-process et les cibles minimales → outil natif
ci-dessous.

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
| CLI / boîte noire | **hyperfine** | ratio + σ ; sinon `perfloop.py` (permutation) |
| Python | **pytest-benchmark** / `timeit` | intégré |

Préfère **toujours** un framework natif mûr (Criterion, JMH, benchstat) à une
boucle maison : ils gèrent warmup, outliers et stats bien mieux. Le squelette
« à la main » n'est qu'un fallback air-gap quand tu ne peux pas ajouter la dépendance.

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
# fallback sans hyperfine : perfloop.py ab "cmdA" "cmdB" --interleave
```

Le générateur `scripts/perfgen.py` émet ces squelettes (`--lang rust|rust-std|go|c|hyperfine`).
C'est de l'outillage **build-time** : il tourne sur ta machine de dev et produit du
code **natif** qui s'exécute avec zéro Python (donc valable en air-gap/embarqué).

## Checklist protocole
1. Frontière correcte : in-process (sub-ms / hot path) vs boîte noire (CLI) ?
2. Outil **natif mûr** quand il existe (Criterion/JMH/benchstat) plutôt qu'une boucle maison ?
3. Warmup + N échantillons + distribution (p95/p99), pas une moyenne ?
4. A/B interleavé + significativité (permutation / Mann-Whitney) ?
5. Résultat consommé (anti-DCE) et entrée variable (anti-constant-folding) ?

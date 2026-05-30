#!/usr/bin/env python3
"""perfgen — génère un squelette de bench NATIF dans la langue voulue.

Réponse à « pourquoi Python et pas générique ? » : le langage du driver est
accessoire, l'actif est le protocole (voir references/bench-protocol.md). Ce
générateur est de l'outillage *build-time* : il tourne sur ta machine de dev et
produit du code natif qui s'exécute avec ZÉRO Python (valable air-gap/embarqué).

Usage:
  perfgen.py --lang rust|rust-std|go|c|hyperfine [--name hot_path] [-o fichier]

Tous les squelettes implémentent le même protocole (warmup, N échantillons,
médiane/p95, anti-DCE) et renvoient vers l'outil natif mûr quand il existe.
"""
import argparse, sys

T = {
"rust": '''// Cargo.toml : [dev-dependencies] criterion = "0.5"
//              [[bench]] name = "{name}" harness = false   (fichier: benches/{name}.rs)
use criterion::{{black_box, criterion_group, criterion_main, Criterion}};

fn {name}(c: &mut Criterion) {{
    let input = make_input(); // données réalistes ET variables (anti constant-folding)
    let mut g = c.benchmark_group("{name}");
    g.bench_function("v1", |b| b.iter(|| black_box(v1(black_box(&input)))));
    g.bench_function("v2", |b| b.iter(|| black_box(v2(black_box(&input)))));
    g.finish();
}}
criterion_group!(benches, {name});
criterion_main!(benches);
// cargo bench -- --save-baseline avant ; <modif> ; cargo bench -- --baseline avant
// Criterion rapporte si la variation est statistiquement significative.
''',
"rust-std": '''// Fallback zéro-dépendance (air-gap) : std seul.
use std::{{hint::black_box, time::Instant}};

fn bench(name: &str, warmup: u32, n: usize, mut f: impl FnMut()) {{
    for _ in 0..warmup {{ f(); }}
    let mut s: Vec<f64> = (0..n)
        .map(|_| {{ let t = Instant::now(); f(); t.elapsed().as_secs_f64() }})
        .collect();
    s.sort_by(|a, b| a.partial_cmp(b).unwrap());
    println!("{{name}}: médiane {{:.3}} ms  p95 {{:.3}} ms",
             s[n / 2] * 1e3, s[(n as f64 * 0.95) as usize] * 1e3);
}}

fn main() {{
    let input = make_input();
    bench("v1", 100, 1000, || {{ black_box(v1(black_box(&input))); }});
    bench("v2", 100, 1000, || {{ black_box(v2(black_box(&input))); }});
}}
''',
"go": '''// go test -bench=. -count=10 > old.txt ; <modif> ; > new.txt ; benchstat old.txt new.txt
// benchstat applique un test U de Mann-Whitney (significativité).
package {name}_test

import "testing"

var sink Result // empêche la dead-code elimination

func BenchmarkV1(b *testing.B) {{
    in := makeInput() // données réalistes ET variables
    b.ResetTimer()
    for range b.N {{
        sink = v1(in)
    }}
}}
''',
"c": '''/* cc -O2 -march=<baseline> {name}.c -o {name} */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static double now(void) {{
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
}}
static int cmp(const void *a, const void *b) {{
    double d = *(const double *)a - *(const double *)b; return (d > 0) - (d < 0);
}}

int main(void) {{
    const int W = 100, N = 1000;
    double s[N];
    Input in = make_input();                 /* données variables */
    for (int i = 0; i < W; i++) {{ volatile Result r = f(in); (void)r; }}
    for (int i = 0; i < N; i++) {{
        double t = now(); volatile Result r = f(in); (void)r; /* volatile => pas de DCE */
        s[i] = now() - t;
    }}
    qsort(s, N, sizeof(double), cmp);
    printf("médiane %.3f ms  p95 %.3f ms\\n", s[N/2]*1e3, s[(int)(N*0.95)]*1e3);
    return 0;
}}
''',
"hyperfine": '''# Boîte noire / CLI : hyperfine fait warmup, stats et ratio.
hyperfine --warmup 3 -N 'cmdA' 'cmdB'          # -N : pas de shell (overhead minimal)
hyperfine --export-json result.json 'cmdA' 'cmdB'   # exploitable par script
# Fallback sans hyperfine (et si python3 présent) :
#   perfloop.py ab "cmdA" "cmdB" --interleave
''',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True, choices=sorted(T.keys()))
    ap.add_argument("--name", default="hot_path")
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args()
    code = T[a.lang].format(name=a.name)
    if a.out:
        with open(a.out, "w") as f:
            f.write(code)
        print(f"[perfgen] écrit dans {a.out} ({a.lang})", file=sys.stderr)
    else:
        sys.stdout.write(code)


if __name__ == "__main__":
    main()

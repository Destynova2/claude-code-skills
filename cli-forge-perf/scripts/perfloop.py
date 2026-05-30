#!/usr/bin/env python3
"""perfloop — harnais de bench A/B + distribution, stdlib uniquement.

Le skill perf-optimization est passif ; ce script le rend actif. Il mesure le
wall-clock d'une commande sur N runs et rapporte la DISTRIBUTION (médiane, p95,
p99, écart-type) — jamais une moyenne seule. En mode A/B, un test de permutation
(non-paramétrique, sans dépendance) dit si la différence dépasse le bruit.

Usage:
  perfloop.py run "<cmd>" [-n 30] [--warmup 3] [--shell]
  perfloop.py ab  "<cmdA>" "<cmdB>" [-n 30] [--warmup 3] [--shell] [--interleave]
  perfloop.py autotune "<v1>" "<v2>" "<v3>" ... [-n 30]   # benche N variantes, classe, teste
  perfloop.py sweep "<cmd --threads={}>" 1 2 4 8 16 [-n 20] # balaye un paramètre, sort la courbe
  perfloop.py cost --saved-ms 12 --rps 500 [--instances-removed 2 ...] # chiffre €/kWh/CO2

Exemples:
  perfloop.py run "./target/release/grob --bench"
  perfloop.py ab "python slow.py" "python fast.py" -n 50 --interleave
  perfloop.py autotune "sort_v1" "sort_v2" "sort_v3"        # ablation automatique
  perfloop.py sweep "./bench --workers={}" 1 2 4 8 16        # trouve l'optimum

Limites (lis references/benchmarking-traps.md AVANT de croire un chiffre):
- perfloop = runner CLI zéro-setup pour de la BOÎTE NOIRE, et suppose python3
  présent. Pour le sub-ms, l'in-process, ou une cible SANS python (conteneur
  FROM scratch, embarqué) -> references/bench-protocol.md + scripts/perfgen.py
  (squelettes NATIFS : Criterion/Rust, Go+benchstat, C, hyperfine).
- commandes < ~1 ms : l'overhead de subprocess domine -> bench in-process
  (Criterion en Rust, pytest-benchmark, hyperfine si dispo).
- environnement calme requis (pas de charge concurrente) ; pin le CPU si besoin
  (taskset/numactl) et désactive le turbo si les runs sont instables.
- --interleave (mode ab) alterne A,B,A,B... pour annuler une dérive temporelle
  (montée en température, voisin bruyant) : à privilégier.
"""
import argparse, random, shlex, statistics as st, subprocess, sys, time


def time_once(cmd, use_shell):
    t0 = time.perf_counter()
    r = subprocess.run(
        cmd if use_shell else shlex.split(cmd),
        shell=use_shell,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    dt = time.perf_counter() - t0
    if r.returncode != 0:
        sys.exit(f"[perfloop] commande échouée (exit {r.returncode}) : {cmd}")
    return dt


def pct(xs, p):
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * p / 100.0
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def fmt(x):
    return f"{x * 1e3:.3f} ms" if x < 1 else f"{x:.4f} s"


def summary(name, xs):
    print(f"\n[{name}] n={len(xs)}")
    print(f"  médiane {fmt(pct(xs, 50))}    moyenne {fmt(st.mean(xs))}")
    print(f"  p95     {fmt(pct(xs, 95))}    p99     {fmt(pct(xs, 99))}")
    print(f"  min     {fmt(min(xs))}    max {fmt(max(xs))}    σ {fmt(st.pstdev(xs))}")


def perm_test(a, b, iters=20000):
    """p-value : probabilité d'observer un écart de médianes >= l'observé sous
    l'hypothèse nulle (A et B tirés de la même distribution)."""
    obs = abs(st.median(a) - st.median(b))
    pool = list(a) + list(b)
    na = len(a)
    hits = 0
    for _ in range(iters):
        random.shuffle(pool)
        if abs(st.median(pool[:na]) - st.median(pool[na:])) >= obs:
            hits += 1
    return obs, (hits + 1) / (iters + 1)


def measure(cmd, n, warmup, use_shell, label):
    print(f"[perfloop] warmup ×{warmup} puis {n} runs : {label}", file=sys.stderr)
    for _ in range(warmup):
        time_once(cmd, use_shell)
    return [time_once(cmd, use_shell) for _ in range(n)]


def measure_interleaved(cmda, cmdb, n, warmup, use_shell):
    print(f"[perfloop] interleave : warmup puis {n}×(A,B)", file=sys.stderr)
    for _ in range(warmup):
        time_once(cmda, use_shell)
        time_once(cmdb, use_shell)
    a, b = [], []
    for _ in range(n):
        a.append(time_once(cmda, use_shell))
        b.append(time_once(cmdb, use_shell))
    return a, b


def bar(value, vmax, width=38):
    n = int(round(width * value / vmax)) if vmax else 0
    return "#" * max(n, 1)


def autotune(cmds, n, warmup, use_shell):
    res = [(c, measure(c, n, warmup, use_shell, c)) for c in cmds]
    res.sort(key=lambda kv: st.median(kv[1]))
    best_cmd, best_xs = res[0]
    worst = max(st.median(xs) for _, xs in res)
    print("\n=== classement (médiane croissante = plus rapide) ===")
    for c, xs in res:
        m = st.median(xs)
        tag = "  <= meilleur" if c == best_cmd else ""
        print(f"  {fmt(m):>12}  {bar(m, worst)}  {c}{tag}")
    print("\n=== significativité vs meilleur (test de permutation) ===")
    for c, xs in res:
        if c == best_cmd:
            continue
        _, p = perm_test(best_xs, xs)
        v = "≈ dans le bruit (= au meilleur)" if p >= 0.05 else f"plus lent (p={p:.4f})"
        print(f"  {c} : {v}")
    print(f"\n[gagnant] {best_cmd}  (médiane {fmt(st.median(best_xs))})")
    print("  audite avant de conclure : references/benchmarking-traps.md")


def sweep(template, values, n, warmup, use_shell):
    if "{}" not in template:
        sys.exit("[perfloop] sweep : le template doit contenir {} à substituer.")
    print(f"[perfloop] sweep de '{template}' sur {values}", file=sys.stderr)
    rows = [(v, st.median(measure(template.replace("{}", str(v)), n, warmup, use_shell,
            template.replace("{}", str(v))))) for v in values]
    worst = max(m for _, m in rows)
    best = min(rows, key=lambda vm: vm[1])
    print("\n=== courbe (valeur -> médiane) ===")
    for v, m in rows:
        tag = "  <= optimum" if (v, m) == best else ""
        print(f"  {str(v):>8} : {fmt(m):>12}  {bar(m, worst)}{tag}")
    print(f"\n[optimum] valeur = {best[0]}  (médiane {fmt(best[1])})")
    print("  l'optimum est rarement à un extrême : élargis la plage si c'en est un.")


def run_cost(saved_ms, rps, wpc, pue, eur_kwh, gco2_kwh,
             inst, watts_inst, eur_inst_h):
    print("\n=== comptabilité multi-dimensionnelle d'une optim ===")
    print(f"hypothèses : PUE={pue}, {eur_kwh} €/kWh, {gco2_kwh} gCO2/kWh "
          f"(défauts France ; EU≈175, monde≈445 gCO2/kWh)")
    kwh = eur = 0.0
    if saved_ms and rps:
        cpu_h_year = rps * 86400 * (saved_ms / 1000.0) * 365 / 3600.0
        k = cpu_h_year * wpc / 1000.0 * pue
        kwh += k; eur += k * eur_kwh
        print(f"\n[charge] {saved_ms} ms économisés × {rps} req/s (suppose du temps CPU) :")
        print(f"  {cpu_h_year:,.0f} CPU-h/an  ->  {k:,.0f} kWh/an  ->  {k*eur_kwh:,.0f} €/an  "
              f"->  {k*gco2_kwh/1000:,.0f} kgCO2/an")
    if inst:
        k = inst * watts_inst * 8760 / 1000.0 * pue
        kwh += k; eur += k * eur_kwh
        print(f"\n[instances] {inst} × {watts_inst} W 24/7 :")
        print(f"  {k:,.0f} kWh/an  ->  {k*eur_kwh:,.0f} € élec/an  ->  {k*gco2_kwh/1000:,.0f} kgCO2/an")
        if eur_inst_h:
            c = inst * eur_inst_h * 8760
            eur += c
            print(f"  + {c:,.0f} €/an de facture cloud")
    print(f"\n[total] {eur:,.0f} €/an  |  {kwh:,.0f} kWh/an  |  {kwh*gco2_kwh/1000:,.0f} kgCO2/an")
    if kwh:
        print(f"        ≈ {kwh*gco2_kwh/1000/0.12:,.0f} km en voiture thermique évités (120 gCO2/km)")
    print("  ⚠ ordre de grandeur : latence ≠ énergie (I/O-wait ≠ CPU busy), carbone "
          "embarqué et effet rebond non comptés. Détail : references/cost-accounting.md")


def main():
    ap = argparse.ArgumentParser(description="bench A/B stdlib")
    sub = ap.add_subparsers(dest="mode", required=True)

    pr = sub.add_parser("run")
    pr.add_argument("cmd")
    pr.add_argument("-n", type=int, default=30)
    pr.add_argument("--warmup", type=int, default=3)
    pr.add_argument("--shell", action="store_true")

    pa = sub.add_parser("ab")
    pa.add_argument("cmda")
    pa.add_argument("cmdb")
    pa.add_argument("-n", type=int, default=30)
    pa.add_argument("--warmup", type=int, default=3)
    pa.add_argument("--shell", action="store_true")
    pa.add_argument("--interleave", action="store_true")

    pt = sub.add_parser("autotune")
    pt.add_argument("cmds", nargs="+")
    pt.add_argument("-n", type=int, default=30)
    pt.add_argument("--warmup", type=int, default=3)
    pt.add_argument("--shell", action="store_true")

    pw = sub.add_parser("sweep")
    pw.add_argument("template", help="commande avec {} à substituer")
    pw.add_argument("values", nargs="+")
    pw.add_argument("-n", type=int, default=20)
    pw.add_argument("--warmup", type=int, default=2)
    pw.add_argument("--shell", action="store_true")

    pc = sub.add_parser("cost")
    pc.add_argument("--saved-ms", type=float, default=0.0)
    pc.add_argument("--rps", type=float, default=0.0)
    pc.add_argument("--watts-per-core", type=float, default=12.0)
    pc.add_argument("--pue", type=float, default=1.2)
    pc.add_argument("--eur-kwh", type=float, default=0.15)
    pc.add_argument("--gco2-kwh", type=float, default=30.0)
    pc.add_argument("--instances-removed", type=int, default=0)
    pc.add_argument("--watts-instance", type=float, default=250.0)
    pc.add_argument("--eur-instance-hour", type=float, default=0.0)

    args = ap.parse_args()

    if args.mode == "run":
        xs = measure(args.cmd, args.n, args.warmup, args.shell, args.cmd)
        summary(args.cmd, xs)
        return

    if args.mode == "autotune":
        autotune(args.cmds, args.n, args.warmup, args.shell)
        return

    if args.mode == "sweep":
        sweep(args.template, args.values, args.n, args.warmup, args.shell)
        return

    if args.mode == "cost":
        run_cost(args.saved_ms, args.rps, args.watts_per_core, args.pue,
                 args.eur_kwh, args.gco2_kwh, args.instances_removed,
                 args.watts_instance, args.eur_instance_hour)
        return

    # mode == "ab"
    if args.interleave:
        a, b = measure_interleaved(args.cmda, args.cmdb, args.n, args.warmup, args.shell)
    else:
        a = measure(args.cmda, args.n, args.warmup, args.shell, "A=" + args.cmda)
        b = measure(args.cmdb, args.n, args.warmup, args.shell, "B=" + args.cmdb)

    summary("A " + args.cmda, a)
    summary("B " + args.cmdb, b)

    ma, mb = st.median(a), st.median(b)
    obs, p = perm_test(a, b)
    rel = (mb - ma) / ma * 100 if ma else float("nan")
    print(f"\n[verdict] Δmédiane = {fmt(obs)}  ({rel:+.1f}% de A vers B)")
    print(f"          test de permutation p = {p:.4f}")
    if p >= 0.05:
        print("          => différence NON significative : dans le bruit. "
              "Pas de gain prouvé.")
    else:
        gagnant = "B" if mb < ma else "A"
        print(f"          => significatif (p<0.05). Plus rapide : {gagnant}. "
              "Vérifie quand même les pièges (warmup, DCE, représentativité).")


if __name__ == "__main__":
    main()

# Profil projet (contraintes pré-câblées)

Fichier local (préfixe `_`) : pré-charge le terrain technique récurrent pour que
le skill parte directement des bonnes contraintes. À adapter — ce n'est pas une
loi, et ça **ne dispense pas de mesurer** sur la vraie cible (le GATE du SKILL.md
s'applique quand même).

## Contexte & stack

- **Langage de prédilection : Rust** (perf + sûreté mémoire). Hot paths réécrits
  en Rust ; orchestration éventuellement plus haut niveau (cf. `lateral-thinking.md`
  liberté verticale).
- **Plateforme** : Talos Linux, Cilium, FluxCD, OpenBao, Kyverno, Terraform/
  OpenTofu, Harbor, VictoriaMetrics, Garage.
- **Conteneurs** : FROM scratch / distroless, cible ~quelques MB (objectif type
  « 6 MB FROM scratch »). Licence AGPL-3.0 (+ option commerciale).
- **Contexte d'exécution** : souverain / **air-gapped** / régulé (fintech,
  santé). Conséquences directes :
  - pas de CDN ni de service managé cloud assumable → miroirs offline, artefacts
    autoportants ;
  - **builds reproductibles** et supply-chain maîtrisée (cf. `dependencies.md`) ;
  - **surface d'attaque minimale = aussi un gain de footprint/perf** (DevSecOps et
    perf alignés ici).

## Défauts perf qui découlent des contraintes

- **Build Rust release** : LTO + `codegen-units=1` + `panic=abort` + `opt-level=3`.
  **Attention `target-cpu`** en air-gapped/portable : `target-cpu=native` n'est
  valide que si l'hôte de build == l'hôte d'exécution. Pour un artefact portable,
  fixe une **baseline explicite** (`x86-64-v2/v3`, ou features ARM ciblées) — sinon
  tu perds la vectorisation ou tu crashes sur un CPU plus ancien. (cf.
  `systems-hardware.md`, `dependencies.md`)
- **Profiling** : `cargo flamegraph` (CPU), `dhat`/`heaptrack` (allocs), Criterion
  (micro-bench in-process, mieux que le wall-clock pour le sub-ms), `cargo bloat`
  (footprint). **Contrainte air-gap** : ces outils doivent être dans l'image
  offline (`hyperfine` statique pour la boîte noire, Criterion compilé dans le binaire de test pour l'in-process).
- **Crypto** (audit logs signés type ECDSA-P256) : si le **débit** de signature/
  vérif devient un goulot, évalue **Ed25519 + batch verification** (plus rapide,
  constant-time plus simple), **BLAKE3** pour le hash/Merkle des logs, et
  **vérifie que l'AES-NI/SIMD est réellement utilisé** dans le build air-gapped
  (pas de fallback software silencieux). Le **constant-time** reste non négociable.
  (cf. `crypto-throughput.md`)
- **Footprint conteneur** : FROM scratch, static (musl), strip + LTO ; `cargo bloat`
  pour traquer le poids. Image plus petite = cold start plus rapide + surface
  réduite. (cf. `systems-hardware.md` §6, `dependencies.md`)
- **Inférence LLM locale** (Apple Silicon, mémoire unifiée) : **MLX** ou
  **llama.cpp (Metal)** + quantization **GGUF** ; la mémoire unifiée évite le
  transfert PCIe (KV cache + poids partagés). Pour une **voice pipeline**
  (STT→LLM→TTS), optimise le **TTFT** + les **tok/s du decode** + le **prefix
  caching** du system prompt (latence perçue). (cf. `llm-inference.md`)
- **Observabilité** : VictoriaMetrics déjà en place pour les métriques ; ajoute du
  **tracing OpenTelemetry** pour la latence au niveau span (p95/p99) et **eBPF**
  pour les syscalls sans instrumenter le code. (cf. `profiling.md`)

## Rappels

- Le **type de goulot** se reclasse à chaque cas (cf. `profiling.md`) — ne
  présuppose pas que « c'est CPU » parce que c'est du Rust.
- Convention de nommage des projets (ouvertures d'échecs ECO A00…) : cosmétique,
  sans effet perf.
- Ce profil **pré-charge du contexte** ; il ne remplace ni la mesure, ni le GATE,
  ni l'audit des chiffres (`benchmarking-traps.md`).

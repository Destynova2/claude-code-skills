# Inférence LLM — optimiser les tok/s

## Contents

- Le modèle mental : prefill vs decode
- Niveau modèle
- Niveau système / serving
- Niveau application — le ROI le plus élevé
- Hardware & moteur
- Diagnostic : où va le temps GPU, sans deviner ?
- Checklist tok/s

---

Domaine spécialisé. Le fil rouge : **la génération (decode) est limitée par la
bande passante mémoire, pas par le calcul** — chaque token relit tous les poids
+ le KV cache depuis la mémoire. C'est pourquoi réduire la précision
(quantization) augmente directement les tok/s. Lien direct avec le roofline
(`systems-hardware.md`).

## Le modèle mental : prefill vs decode

Deux phases aux profils opposés :

| Phase | Nature | Métrique | Levier |
|---|---|---|---|
| **Prefill** (traite le prompt en parallèle) | compute-bound, sature les tensor cores | **TTFT** (time to first token) | batch, FlashAttention, chunked prefill |
| **Decode** (génère 1 token à la fois) | **memory-bandwidth-bound** | **TPOT / tok/s** | quantization, KV cache, speculative decoding |

Trois métriques à ne pas confondre : **TTFT** (réactivité), **tok/s par requête**
(vitesse perçue), **throughput agrégé** (tok/s tous clients confondus). Le
batching échange la vitesse individuelle contre le débit collectif.

## Niveau modèle

- **Quantization** — le plus gros levier local. FP16/BF16 → **FP8** (stable,
  +~30 % tok/s sur Hopper) → **INT4** (GGUF `Q4_K_M`, GPTQ, AWQ) pour l'edge/le
  local. Moins d'octets par poids = moins de bande passante = plus de tok/s.
  Compromis qualité minime à 8 bits, à surveiller à 4 bits.
- **Les kernels comptent autant que l'algo** : les mêmes poids quantifiés tournent
  bien plus vite avec des kernels optimisés (ex. Marlin). Ne juge pas une méthode
  sans son kernel.
- **MoE (Mixture of Experts)** : n'active qu'une fraction des paramètres par token
  → plus de tok/s à capacité donnée.
- **Modèle plus petit / distillé** : souvent la meilleure optim. Un 7-9B
  quantifié suffit pour beaucoup de tâches et tient sur du matériel modeste.

## Niveau système / serving

- **KV cache** : réutilise les clés/valeurs des tokens passés au lieu de
  recalculer l'attention sur tout le contexte → decode en O(n) au lieu de O(n²).
  Indispensable. Mais il **grossit avec le contexte** et finit par saturer la
  mémoire → goulot principal à grande échelle.
- **PagedAttention** (vLLM) : gère le KV cache en pages (comme la pagination OS)
  → moins de fragmentation, plus de requêtes concurrentes.
- **Continuous / in-flight batching** : recompose le batch à chaque étape au lieu
  d'attendre la fin des requêtes → sature le GPU. Gros gain de throughput agrégé
  (ordre de 2 000-2 800 tok/s sur H100 à ~100 requêtes concurrentes).
- **Speculative decoding** : un petit modèle « draft » propose k tokens, le gros
  les valide en un seul forward → 2-3× tok/s sans perte de qualité (variantes :
  Medusa, EAGLE, lookahead).
- **FlashAttention** : attention fusionnée et IO-aware → moins d'allers-retours
  vers la mémoire haute bande passante (HBM).
- **Prefix caching / RadixAttention** (SGLang) : réutilise le KV cache d'un
  préfixe commun (system prompt, contexte RAG partagé, multi-turn) entre requêtes.
- **Parallélisme** : tensor parallel (couche répartie sur plusieurs GPU),
  pipeline parallel (couches en étages), pour les gros modèles.
- **CUDA graphs / `torch.compile`** : éliminent l'overhead de lancement des
  nombreux petits kernels du decode.

## Niveau application — le ROI le plus élevé

Souvent oublié et pourtant prioritaire : **optimise les tokens par tâche, pas
seulement les tokens par seconde**. Un moteur rapide sur un contexte gonflé coûte
plus qu'un moteur lent sur un contexte compact.

- **Réduis le contexte envoyé** : élague l'historique, compacte les prompts,
  n'inclus que les fonctions/passages utiles (pas le fichier entier). Une grande
  part des tokens d'entrée est typiquement du gaspillage.
- **Prompt / prefix caching** : réutilise le préfixe commun (system prompt) côté
  serveur.
- **Semantic caching** : sers une réponse cachée pour une requête sémantiquement
  proche (embeddings + recherche vectorielle) → évite l'inférence (forte
  réduction de coût sur workloads répétitifs). Lien avec `memory-cache.md`.
- **Sorties structurées / contraintes** : génère moins de tokens, plus
  déterministes.

## Hardware & moteur

- **Bande passante mémoire = le nerf de la guerre.** Compare la mémoire à charger
  par token au débit mémoire du device → ça plafonne les tok/s (roofline).
- **Apple Silicon (mémoire unifiée)** : poids et KV cache partagent la RAM
  unifiée → pas de transfert PCIe CPU↔GPU. Pour de l'inférence locale, vise
  **MLX** ou **llama.cpp (Metal)** + quantization GGUF ; la grande RAM unifiée
  permet de gros modèles/contextes. Pour une **voice pipeline** (STT→LLM→TTS),
  c'est le **TTFT** + les tok/s du decode qui font la latence perçue : privilégie
  un petit modèle quantifié et le prefix caching du system prompt.
- **NVIDIA** : TensorRT-LLM (throughput max après compilation), FP8 sur Hopper.
- **Choix du moteur de serving (2026)** : vLLM si tu changes souvent de modèle ;
  SGLang si tes workloads ont des préfixes partagés (chat, RAG, multi-turn) ;
  TensorRT-LLM si un seul modèle en prod et le throughput prime.

## Diagnostic : où va le temps GPU, sans deviner ?

Quand un binaire d'inférence est trop lent (cross-langage, cross-version, ou
nouvelle architecture), suis cet ordre — chaque étape élimine une hypothèse à
coût bas avant de toucher au code.

1. **Classifier la phase** avant de mesurer fin :
   - **TTFT élevé** → prefill **compute-bound** → chemin FlashAttention / batch /
     chunked prefill.
   - **tok/s decode bas** → **memory-bandwidth-bound**. Borne du gain
     = `débit_mémoire / octets_par_token` (roofline). À 70-80 % de la borne, le
     levier n'est plus le code — c'est quantization ou hardware. *Arrête de chasser
     un gain qui n'existe pas.*
2. **Ablation par pin emboîté** (cf. `experiment-method.md` §3b) — la matrice
   à planifier en une seule passe :
   - Pin **version du runtime** (vX vs vY sur le *même* modèle, *même* entrée — peu importe la stack Python, Rust, Go, JVM…) → version isolée.
   - Pin **architecture** (modèle dense connu vs nouveau format) → archi isolée.
   - Pin **composant** (forward avec/sans MoE, avec/sans linear-attn, avec/sans
     shared-expert) → kernel suspect isolé.
   Un test qui **échoue à charger** (« archi non supportée par cette version »)
   **est une donnée**, pas un blocage — c'est ce qui tranche.
3. **Profiler per-kernel** une fois et une seule, **headless** :
   - **macOS / Metal** : `xctrace record --template "Metal System Trace"` → export
     XML → agrège par compute pipeline label → tableau **kernel | count | temps
     GPU cumulé | %**.
   - **Linux / CUDA** : `nsys profile` + `nsys stats` → idem.
   - Routage détaillé : `bench-protocol.md` § Routage.

### Anti-pattern « `.gputrace` ≠ profiler »

Sur macOS, un `.gputrace` (capturé via `MTLCaptureManager` ou Xcode) répond à
« *que contient* ce dispatch ? » — buffers, textures, pipeline state, coût par
ligne de shader. Un Metal System Trace répond à « *où passe* le temps ? » —
distribution par kernel. **Deux outils, deux questions distinctes**, pas deux
niveaux du même outil. Symptôme du piège : 40 min à piloter Xcode pour ouvrir
un trace 17 Go au lieu de 2 min d'`xctrace` headless. Sur CUDA, **Nsight
Graphics ≠ Nsight Systems** — même distinction.

## Checklist tok/s
1. Mon goulot est-il le **decode** (memory-bandwidth) ou le **prefill** (TTFT) ?
2. Ai-je quantifié au niveau acceptable (FP8, voire INT4) avec de bons kernels ?
3. KV cache + PagedAttention + continuous batching activés côté serving ?
4. Speculative decoding / prefix caching applicables à mon workload ?
5. **Ai-je d'abord réduit les tokens par tâche** (contexte, caching) avant
   d'optimiser la vitesse brute ?
6. Le matériel est-il exploité (mémoire unifiée Mac / FP8 Hopper / bon moteur) ?

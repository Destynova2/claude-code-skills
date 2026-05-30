# Crypto — optimiser le débit (ops/s & GB/s)

Domaine spécialisé. La crypto est CPU-bound mais dispose d'**accélérateurs
hardware dédiés** (cf. `systems-hardware.md` §4). Le plus gros levier n'est
souvent pas « calculer plus vite » mais **choisir le bon algorithme** et
**éviter le fallback software**.

> ⚠️ **Contrainte non négociable : constant-time.** En crypto, on n'optimise
> JAMAIS au prix de la résistance aux attaques par canaux auxiliaires (timing).
> Toute optim qui branche, indexe une table ou court-circuite en fonction de
> données **secrètes** introduit une faille. Une implémentation lente mais
> constant-time bat une implémentation rapide qui fuit la clé. Utilise des libs
> éprouvées (ring, libsodium, BoringSSL) plutôt que de rouler la tienne.

## 1. Choix d'algorithme = le levier principal

| Besoin | Rapide AVEC accél. hardware | Rapide en software / ARM | Note |
|---|---|---|---|
| Chiffrement symétrique (AEAD) | **AES-GCM** (AES-NI + CLMUL) | **ChaCha20-Poly1305** | choisis selon le CPU cible |
| Hash | **SHA-256** (SHA-NI) | **BLAKE3** (SIMD, multi-thread) | BLAKE3 = très haut débit, parallèle |
| Signature | — | **Ed25519** | signer/vérifier rapides, batch verification |

- **AES-GCM vs ChaCha20** : sur un CPU avec AES-NI, AES-GCM domine ; sans (vieux
  ARM, embarqué, certains mobiles), ChaCha20-Poly1305 est plus rapide ET
  constant-time par construction. Une bonne stack négocie selon le hardware
  (c'est ce que fait TLS).
- **BLAKE3** : conçu pour le débit — SIMD, structure en arbre de Merkle interne,
  parallélisable sur plusieurs cœurs. Excellent pour hasher de gros volumes ou
  construire des arbres de Merkle / logs d'audit. SHA-256 reste pertinent avec
  SHA-NI ou pour la compatibilité.
- **Signatures — Ed25519 vs ECDSA P-256** : Ed25519 est généralement plus rapide
  (surtout en vérification et en **batch verification** : valider N signatures
  ensemble bien plus vite que N vérifs isolées), plus simple à implémenter en
  constant-time, et déterministe. ECDSA P-256 reste justifié pour des contraintes
  de conformité/interop (FIPS, certificats X.509, hardware qui ne fait que P-256).
  Si un audit log signé devient un goulot en débit de signature/vérif, Ed25519 +
  batch verification est le gain net — sous réserve des exigences de conformité.

## 2. Patterns de débit

- **Hybride : minimise l'asymétrique.** Les ops asymétriques (RSA, ECDH,
  signatures) sont lentes ; le symétrique est rapide. Le schéma standard : un
  échange asymétrique pour établir une clé de session, puis tout le bulk en
  symétrique. Ne signe/chiffre pas en asymétrique ce qui peut l'être en
  symétrique.
- **Batch verification** : regroupe les vérifications de signatures (Ed25519 le
  supporte nativement) → gros gain quand on vérifie des milliers de signatures.
- **Précomputation fixed-base** : pour de la multiplication scalaire répétée sur
  la même base (clé fixe), des tables précalculées accélèrent (les bonnes libs le
  font déjà).
- **Pipelining / parallélisme** : les modes parallélisables (CTR, GCM) chiffrent
  des blocs indépendamment → vectorisables et multi-thread. Les modes chaînés
  (CBC) sont séquentiels → préfère un mode parallélisable pour le débit.
- **Réutilise le key schedule** : étendre une clé (key expansion) a un coût ;
  réutilise le contexte de chiffrement pour plusieurs messages avec la même clé
  au lieu de le reconstruire.
- **Amorti les handshakes** : TLS session resumption / 0-RTT, réutilisation de
  connexions (cf. `database.md`/`dependencies.md`) — le handshake asymétrique est
  le coût dominant d'une connexion courte.
- **Offload kernel/hardware** : kTLS (chiffrement TLS dans le kernel, zero-copy),
  HSM/accélérateurs (Intel QAT) pour de très gros volumes.

## 3. Vérifier l'accélération hardware (le piège classique)

Une lib crypto « lente » utilise souvent une impl pure-software faute d'avoir
activé/détecté les instructions dédiées :
- AES-NI, SHA-NI, CLMUL/VAES, PMULL (ARM) — cf. `systems-hardware.md` §4.
- Vérifie : détection CPU runtime (OpenSSL `OPENSSL_ia32cap`), flags de build
  (`target-cpu=native`, `-maes`), et que tu n'as pas choisi une crate
  « portable pure-software » par défaut.
- Mesure le débit (GB/s en bulk, ops/s en asymétrique) avec et sans accélération
  pour confirmer.

## Checklist crypto
1. L'algo est-il adapté au hardware cible (AES-NI présent → AES-GCM, sinon
   ChaCha20) ?
2. Pour le hash en volume / Merkle : BLAKE3 envisagé ?
3. Signatures en goulot : Ed25519 + batch verification possible (vs conformité) ?
4. Minimise-t-on l'asymétrique (hybride, sessions réutilisées) ?
5. La lib exploite-t-elle réellement l'accélération hardware (pas de fallback) ?
6. **Aucune optim ne branche sur des données secrètes (constant-time préservé) ?**

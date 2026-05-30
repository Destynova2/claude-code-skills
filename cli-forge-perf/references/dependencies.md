# Dépendances & footprint

Axe transverse. Un empilement de libs non maîtrisé pèse sur la perf (code à
charger/parser, couches d'abstraction, allocations) ET sur la taille, le build,
la sécurité. Trois questions : *pourquoi cette dep ? peut-on mutualiser ? est-elle
exploitée à son maximum ?*

## 1. Pourquoi cette dépendance ? (justifier chaque lib)

Pour chaque dep, le coût caché : surface d'attaque, deps transitives, temps de
build, taille binaire, maintenance, risque supply-chain. Questions :

- Qu'apporte-t-elle **vraiment** ? Utilise-t-on 3 fonctions d'une lib de 200 ?
- Le besoin se réécrit-il en quelques lignes maîtrisées (left-pad effect) ?
- La dep tire-t-elle un **arbre transitif** énorme pour peu de valeur ?
- Inversement : ne pas réécrire un truc critique (crypto, parsing) qu'une lib
  éprouvée fait mieux et plus sûr. Le but n'est pas zéro dep, c'est *zéro dep
  injustifiée*.

Outils : `cargo tree`, `npm ls`, `pipdeptree`, `go mod graph`.

## 2. Mutualiser / dédupliquer

L'empilement crée des redondances coûteuses :

- **Libs concurrentes pour le même besoin** : 3 clients HTTP, 2 libs de date, 2
  sérialiseurs JSON, 2 frameworks de log → converge sur **une**. Moins de code,
  moins de styles, cache mieux.
- **Versions multiples de la même lib** dans l'arbre transitif (duplication) →
  unifie les contraintes de version. `cargo tree -d` (duplicates), `npm dedup`,
  résolutions/overrides du lockfile. Réduit binaire + temps de compile.
- **Fonctionnalités qui se recouvrent** : une grosse lib "couteau suisse" alors
  qu'on n'utilise qu'un module → prends le module ciblé ou désactive les
  features inutiles.

## 3. Les libs sont-elles "à leur maximum" ?

Une bonne lib mal configurée est lente. Avant de remplacer, vérifie qu'on
l'exploite correctement :

- **Features / flags de compilation** : active les features perf (SIMD, "native",
  backend rapide) et **désactive** les features inutiles qui alourdissent. Ex.
  `default-features = false` + features ciblées (Rust).
- **Build release optimisé** : LTO, `codegen-units=1`, `target-cpu=native`,
  `opt-level=3` (cf. systems-hardware.md). Une lib compilée sans ça laisse de la
  perf sur la table.
- **Accélération hardware** : la lib utilise-t-elle AES-NI/SIMD/GPU ou un
  fallback software ? (cf. systems-hardware.md §4 — le cas crypto).
- **Réutilisation des ressources** : réutilise les clients lourds (HTTP, DB,
  connexions TLS) au lieu d'en créer un par appel (cf. memory-cache.md §5 &
  database.md). Un `reqwest::Client` recréé à chaque requête tue le pool de
  connexions.
- **Bonne API** : préfère l'API **batch/streaming** de la lib à l'API unitaire
  (un `execute_many` vs N `execute`, un itérateur vs tout charger).

## 4. Aplatir les couches d'abstraction

Chaque couche (ORM → driver → pool → socket ; ou wrapper → wrapper → lib) ajoute
indirection, allocations et copies. Sur le **hot path mesuré** :

- Court-circuite une couche quand elle coûte cher : requête SQL brute vs ORM
  pour la requête critique, appel direct vs façade générique.
- Méfie-toi des wrappers "pour faire propre" qui empilent 4 niveaux pour un
  appel : aplatir réduit l'overhead et clarifie.
- Garde l'abstraction là où elle paie (lisibilité, sécurité) ; retire-la là où
  elle ne fait que coûter. Compromis à assumer, pas dogme.

## 5. Footprint (binaire, build, sécurité)

Moins de deps → binaire plus petit, démarrage/cold-start plus rapide, build & CI
plus rapides, surface d'attaque réduite (argument DevSecOps).

- Mesure : `cargo bloat` (poids par crate/fonction), bundle analyzer (JS),
  `du -sh node_modules`, taille d'image conteneur.
- Élimine le code mort (tree shaking, dead-code elimination, `--gc-sections`).
- Conteneur minimal (distroless / FROM scratch) une fois les deps réduites.

## Checklist dépendances
1. Chaque dep est-elle justifiée (valeur vs coût caché + arbre transitif) ?
2. Y a-t-il des libs redondantes ou des versions dupliquées à unifier
   (`cargo tree -d`, `npm dedup`) ?
3. Les libs clés sont-elles configurées au max (features, build release, hardware,
   réutilisation des clients, API batch) ?
4. Des couches d'abstraction inutiles sur le hot path peuvent-elles être aplaties ?
5. Le footprint (binaire/image/build) est-il mesuré et réduit ?

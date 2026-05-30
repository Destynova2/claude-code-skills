# Générer des idées d'optimisation

Mode **divergent**. Quand le catalogue n'a pas la réponse, on produit des pistes —
beaucoup, larges, audacieuses. La validation vient après (`experiment-method.md`).
Règle : **génère sans filtrer, filtre sans générer.** Mélanger tue les bonnes
idées trop tôt.

Produis toujours **plusieurs hypothèses concurrentes** (3-5), pas une seule. La
première idée est rarement la meilleure ; l'espace des solutions se révèle en
explorant des angles opposés.

## Les leviers de génération (à passer en revue systématiquement)

- **Premiers principes.** Remonte à la limite physique/théorique. Quelle est la
  borne incompressible (latence physique, débit mémoire, borne de complexité,
  entropie de l'info) ? Combien de travail est *vraiment* nécessaire ? Souvent on
  découvre qu'on fait 100× le travail minimal. (Lien roofline,
  `systems-hardware.md`.)
- **Suppression / simplification — le levier #1.** La meilleure optimisation est
  de **supprimer le travail**, pas de l'accélérer. "Quelle partie peut
  disparaître ? quel appel, quelle couche, quelle feature, quel champ est
  superflu ?" Enlève, puis remets seulement si une mesure le justifie. Le code le
  plus rapide est celui qui n'existe pas.
- **Inversion.** Au lieu de "comment accélérer X ?", demande "qu'est-ce qui rend
  X le plus lent possible ?" puis élimine exactement ça. Ou : "comment
  garantirais-je que ça ne marche jamais vite ?" — la liste obtenue est ta liste
  de fixes.
- **Relâcher une contrainte.** "Et si on acceptait une approximation ? un
  résultat probabiliste ? une cohérence éventuelle ? une perte de précision ?"
  Relâcher débloque des classes entières d'optim : bloom filter (faux positifs
  ok), cache (donnée légèrement périmée ok), `f32` au lieu de `f64`, eventual
  consistency, échantillonnage au lieu d'exhaustif.
- **Changer le *quand*.** Déplace le moment du travail : pré-calcul (build-time
  vs runtime), lazy (à la demande), batch (différé groupé), spéculatif (à
  l'avance pendant un temps mort), incrémental (ne recalcule que le delta).
- **Changer le *où*.** Déplace le calcul : près de la donnée (push-down,
  edge, near-data), vers une autre ressource (GPU, accélérateur), vers un autre
  niveau de la hiérarchie mémoire (cf. trade-offs `systems-hardware.md`).
- **Analogie / transfert de domaine.** "Ce problème ressemble à quel problème
  déjà résolu ailleurs ?" Beaucoup d'optim majeures sont des emprunts : la
  pagination OS → PagedAttention (LLM) ; la métallurgie → le recuit simulé ; la
  propagation épidémique → les protocoles gossip (cf. `bio-inspired.md`). Le
  biomimétisme est *une* source d'analogies parmi d'autres (physique, biologie,
  économie, logistique).
- **Le saut "10×".** Au lieu de gratter 10 %, demande "qu'est-ce qu'il faudrait
  pour 10× ?". Ça force un changement d'**approche** (algo, architecture, modèle)
  plutôt qu'un micro-tweak. Le 10 % vient des réglages ; le 10× vient du
  repensé.
- **Combiner / fusionner.** Deux passes en une, deux requêtes en une, deux
  services colocalisés, deux structures unifiées. Chaque fusion supprime un coût
  fixe (round-trip, alloc, sérialisation).

## Recherche externe (chercher puis vérifier)

Quand le sujet dépasse le connu (technique de pointe, domaine spécialisé),
**cherche** : papiers, benchmarks, état de l'art, code de référence. Mais :
- ne crois pas un chiffre marketing sur parole → **re-benchmarke** sur ta charge ;
- méfie-toi des résultats "trop beaux" (cherry-picking, conditions idéales) ;
- croise les sources, privilégie l'original (papier, doc) à l'agrégateur.
La recherche alimente la génération d'idées ; l'expérience tranche.

## S'autoriser l'absurde

Une idée "bête" ou contre-intuitive est permise en phase divergente — elle se
réfute en phase de validation, à bas coût. Beaucoup d'optim réelles semblaient
absurdes au départ ("recalculer est plus rapide que lire", "stocker plus pour
transférer moins"). Note-la, teste-la, jette-la si elle échoue. Le coût d'une
mauvaise idée testée est faible ; le coût d'une bonne idée jamais émise est élevé.

## Checklist génération
1. Ai-je remonté aux premiers principes (quel est le minimum de travail réel) ?
2. Qu'est-ce que je peux **supprimer** avant d'optimiser quoi que ce soit ?
3. Ai-je essayé l'inversion et le relâchement d'une contrainte ?
4. Puis-je déplacer le travail (quand / où) ?
5. À quel problème déjà résolu ailleurs ça ressemble ?
6. Ai-je au moins 3 hypothèses divergentes à envoyer en validation ?

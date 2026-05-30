# Patterns bio-inspirés (biomimétisme)

Angle à cadrer honnêtement. Le biomimétisme en informatique est un champ réel
mais **très inégal** : une poignée de patterns sont solides et tournent en prod ;
une grande partie de la littérature « métaheuristique inspirée de l'animal X »
(grey wolf, whale, firefly, salp swarm…) est du **folklore** — du re-packaging de
quelques idées de base (PSO/algos génétiques/recuit) sous des métaphores
marketing. Ne prends jamais une métaphore biologique comme excuse pour éviter de
chercher le bon algo exact ou le bon modèle.

**Quand le bio-inspiré est pertinent (3 cas) :**
1. **Optimisation combinatoire dure** (NP-difficile, espace énorme,
   non-différentiable) où les méthodes exactes ne passent pas à l'échelle.
2. **Coordination décentralisée robuste** entre nombreux nœuds/agents, sans chef
   d'orchestre, tolérante aux pannes.
3. **Adaptation** dans un environnement qui change (auto-régulation).

Pour 95 % des problèmes de perf quotidiens (boucles, requêtes, cache, I/O), le
biomimétisme n'a rien à voir : applique la hiérarchie classique du SKILL.md.

## Ce qui marche vraiment (utilisé en prod)

- **Gossip / protocoles épidémiques** (propagation virale). Dissémination
  d'information et détection de membres dans les systèmes distribués : chaque
  nœud « contamine » quelques voisins au hasard → l'info se propage de façon
  exponentielle, robuste, sans coordinateur. Base de SWIM, de Cassandra, de
  Consul/Serf. Le pattern bio-inspiré le plus solide et le plus répandu.
- **Stigmergie / blackboard** (insectes sociaux : coordination via traces
  laissées dans l'environnement, pas par messages directs). Des agents
  collaborent en lisant/écrivant un **état partagé** plutôt qu'en se parlant
  point à point → couplage faible, passage à l'échelle, résilience. C'est le
  pattern « tableau noir » des architectures multi-agents.
- **Métaheuristiques évolutionnaires & recuit simulé** : algorithmes génétiques,
  evolution strategies (CMA-ES), recuit simulé (analogie thermodynamique),
  particle swarm (PSO). Pour explorer un espace de solutions vaste et accidenté :
  tuning d'hyperparamètres, placement/scheduling, design de circuits, NAS. À
  utiliser quand le gradient n'existe pas ou que l'exact ne scale pas — pas comme
  réflexe par défaut. **Choisis-en un ou deux éprouvés** (GA, CMA-ES, recuit,
  PSO) ; ignore la jungle des variantes animalières.
- **Ant Colony Optimization (ACO)** : phéromones simulées pour du routing
  adaptatif et des problèmes type TSP/VRP. Niche mais réel quand le graphe change
  et qu'on veut une bonne solution évolutive.
- **Systèmes immunitaires artificiels** : modèle « soi vs non-soi » pour la
  détection d'anomalies/intrusions. Niche, en sécurité.
- **Quorum sensing** (bactéries : déclencher une action collective au-delà d'un
  seuil de densité). Analogie utile pour des décisions collectives par seuil
  (activer un comportement quand assez de nœuds sont d'accord).

## Résilience inspirée du vivant (souvent déjà dans tes outils)

Beaucoup de patterns SRE/cloud sont du biomimétisme qui ne dit pas son nom :
- **Homéostasie → autoscaling / feedback control** (réguler autour d'une cible).
- **Réflexe de protection → circuit breaker** (couper pour protéger le reste).
- **Régénération → self-healing** (redémarrage auto, réconciliation d'état).
- **Diversité/redondance → tolérance aux pannes** (réplicas, multi-AZ).
- **Race-to-idle / rythmes circadiens → scheduling énergétique** (cf.
  `systems-hardware.md`).

## Agencements & structures

- **Packing hexagonal** (nid d'abeille = pavage optimal du plan) : grilles
  hexagonales pour l'indexation géospatiale (ex. H3) — meilleure uniformité de
  voisinage que des carrés. Lien avec `math-physics.md` (géo).
- **Phyllotaxie / spirales** : distribution régulière de points (échantillonnage).

## Le piège à éviter

- **Métaphore ≠ performance.** Un algo « inspiré des loups » n'est pas meilleur
  parce qu'il a une jolie histoire. Compare-le honnêtement à un GA/PSO/recuit
  standard et à une méthode exacte — souvent il n'apporte rien.
- **No free lunch** : aucune métaheuristique n'est universellement meilleure.
  Le choix dépend du problème ; valide par benchmark (cf. `profiling.md`).
- **Sur-ingénierie** : ne sors pas un essaim de particules pour un problème qu'un
  tri + index résout. Le bio-inspiré est un outil de niche, pas un couteau suisse.

## Checklist bio-inspiré
1. Mon problème est-il vraiment dans les 3 cas (combinatoire dure / coordination
   décentralisée / adaptation) ? Sinon → hiérarchie classique.
2. Pour de la dissémination/détection distribuée : un protocole gossip
   conviendrait-il ?
3. Pour de la coordination multi-agents : stigmergie/blackboard plutôt que
   messages point à point ?
4. Pour de l'optimisation dure : ai-je comparé une métaheuristique **éprouvée**
   (GA/CMA-ES/recuit/PSO) à l'exact, par benchmark — sans me laisser séduire par
   une variante animalière exotique ?

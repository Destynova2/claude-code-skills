# Async, concurrence & parallélisme

Priorité #4. Deux problèmes distincts à ne pas confondre :
- **I/O-bound** (on attend le réseau/disque/DB) → **async / concurrence** :
  recouvrir l'attente, lancer plusieurs I/O en parallèle.
- **CPU-bound** (on calcule) → **parallélisme** : répartir le calcul sur
  plusieurs cœurs.

Mauvais diagnostic = mauvaise solution (ajouter des threads à un code I/O-bound ne
sert à rien ; faire de l'async sur du calcul pur non plus).

## 1. I/O concurrente : ne pas attendre en série

Le cas le plus fréquent et le plus rentable. Si tu fais 100 appels réseau
indépendants l'un après l'autre, tu additionnes 100 latences. Lance-les ensemble.

```python
# AVANT : séquentiel — total = somme des latences (ex. 100 × 50 ms = 5 s)
results = [await fetch(url) for url in urls]

# APRÈS : concurrent — total ≈ la plus lente (ex. ~50 ms)
results = await asyncio.gather(*(fetch(u) for u in urls))
```
Équivalents : `Promise.all` (JS), `tokio::join!` / `JoinSet` (Rust),
`CompletableFuture.allOf` (Java), `errgroup` (Go). **Borne la concurrence** (pool,
sémaphore) pour ne pas saturer la cible ni épuiser les sockets/fichiers.

## 2. Async I/O vs threads

- **Async (event loop)** : idéal pour des milliers de connexions I/O-bound
  (serveurs web, proxies). Un thread gère beaucoup de tâches en jonglant sur les
  points d'attente. Très peu d'overhead mémoire par tâche.
- **Threads** : utiles pour du CPU-bound (vrai parallélisme si pas de GIL) ou
  pour isoler du code bloquant. Plus lourds (stack par thread, context switches).
- **Piège** : un appel **bloquant** dans une boucle async bloque TOUT l'event loop.
  Déporte le travail bloquant/CPU dans un thread pool (`run_in_executor`,
  `spawn_blocking` en Rust/tokio).

## 3. Parallélisme CPU-bound

Pour saturer les cœurs sur du calcul :
- **Data parallelism** : découpe les données et traite les morceaux en parallèle.
  `rayon` (`par_iter`) en Rust, `multiprocessing`/`concurrent.futures` en Python
  (le GIL empêche le vrai parallélisme threads → processus ou extensions natives),
  parallel streams en Java.
- **Map-reduce** : map en parallèle, reduce ensuite.
- **Limite = nombre de cœurs** : au-delà, tu n'accélères plus, tu ajoutes du
  context switching. Dimensionne le pool sur les cœurs disponibles.
- **Faux partage (false sharing)** : deux threads écrivant des variables sur la
  même ligne de cache se ralentissent mutuellement. Aligne/sépare les données par
  thread.

## 4. Réduire le coût de la synchronisation

La contention sur les verrous tue le parallélisme (les threads font la queue).
- **Réduis la section critique** : ne tiens le lock que le minimum.
- **Sharding du lock** : un verrou par bucket plutôt qu'un verrou global.
- **Structures lock-free / atomiques** : compteurs atomiques, `RwLock` (lectures
  concurrentes), `concurrent`/channel au lieu de mémoire partagée verrouillée.
- **Partage par message plutôt que par état** : queues/channels (le modèle Go,
  les actors) évitent une grosse partie des verrous.
- **Immutabilité** : les données immuables se partagent sans verrou.

## 5. Recouvrir et lisser la charge (UI, web, services)

- **Lazy loading** : ne charge/calcule que quand c'est demandé (au scroll, au
  clic). *Cf. `frontend-web.md`.*
- **Debounce** : attends que l'activité se calme avant d'agir (saisie de
  recherche : 1 appel après la frappe, pas 1 par lettre).
- **Throttle** : limite la fréquence (scroll, resize : max 1 traitement / 16 ms).
- **Background jobs / queues** : sors le travail lourd du chemin de réponse.
  L'utilisateur reçoit une réponse immédiate ; le job tourne en file (Celery,
  Sidekiq, SQS, NATS). Indispensable pour emails, exports, traitements lourds.
- **Streaming** : commence à renvoyer dès les premiers résultats (HTTP chunked,
  Server-Sent Events, génération token par token) au lieu d'attendre le tout.
- **Prefetch / spéculatif** : précharge ce qui sera probablement demandé pendant
  un temps mort.

## 6. Pièges de concurrence

- **Race conditions / data races** : protège l'état partagé (atomiques, locks,
  channels). Un bug de perf qui devient un bug de correction.
- **Deadlocks** : ordonne toujours l'acquisition des verrous de la même façon.
- **Overhead > gain** : paralléliser une tâche trop petite coûte plus en
  orchestration qu'elle ne rapporte. Mesure.
- **Backpressure** : si le producteur va plus vite que le consommateur, borne les
  files pour ne pas exploser la mémoire.

## Checklist async/concurrence
1. Le code est-il I/O-bound ou CPU-bound ? (la solution diffère)
2. Des I/O indépendantes sont-elles faites en série au lieu d'être groupées ?
3. Un appel bloquant tourne-t-il dans une boucle async (= blocage global) ?
4. Le parallélisme CPU est-il borné au nombre de cœurs ?
5. Y a-t-il de la contention de verrou réductible (section critique, sharding) ?
6. Le travail lourd peut-il passer en background job / streaming ?
7. Saisie/scroll : debounce/throttle en place ?

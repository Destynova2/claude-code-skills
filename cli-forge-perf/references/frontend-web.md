# Frontend & web

Axe transverse, piloté par la mesure (Lighthouse / Core Web Vitals). La perf web
se décompose en : **moins d'octets** (réseau), **plus tôt** (chemin critique),
**moins de travail sur le main thread** (JS), **pas de saccades** (layout/paint).

## 1. Mesurer : Lighthouse & Core Web Vitals

Lance Lighthouse (DevTools / CI) et regarde les Core Web Vitals — ce sont les
métriques que Google mesure réellement chez les utilisateurs :

| Métrique | Mesure | Cible | Principaux leviers |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | vitesse d'affichage du contenu principal | < 2,5 s | image/police optimisée, critical CSS, CDN, preload |
| **INP** (Interaction to Next Paint) | réactivité aux interactions | < 200 ms | moins de JS, découpe les tâches longues, web workers |
| **CLS** (Cumulative Layout Shift) | stabilité visuelle | < 0,1 | dimensions sur images/embeds, `font-display`, pas d'insertion qui pousse le contenu |

Complète avec l'onglet **Network** (cascade des requêtes) et **Performance**
(tâches longues sur le main thread). Mesure en conditions réalistes (throttling
réseau/CPU), pas seulement sur ta fibre + M-series.

## 2. Réduire le JavaScript (le plus gros levier sur INP/LCP)

Le JS est cher : téléchargé, parsé, compilé, exécuté sur le main thread (qui sert
aussi à répondre aux clics). Moins de JS = page plus réactive.

- **Code splitting + lazy load** : ne charge pas tout le bundle au démarrage.
  Découpe par route/composant, charge à la demande.
```js
// AVANT : tout le module chargé au boot, même si jamais utilisé
import Chart from "./HeavyChart";
// APRÈS : chargé seulement quand on en a besoin (dynamic import)
const Chart = React.lazy(() => import("./HeavyChart"));
```
- **Tree shaking** : élimine le code mort (imports nommés, bundler en mode prod).
  Importe `import { debounce } from "lodash-es"`, pas `import _ from "lodash"`.
- **Minification + compression** : minify (Terser) + **Brotli/gzip** côté serveur.
- **Découpe les tâches longues** : une tâche JS > 50 ms bloque les interactions.
  Fractionne (`scheduler.yield`, `setTimeout`, `requestIdleCallback`), ou déporte
  le calcul lourd dans un **Web Worker** (hors main thread).
- **`defer` / `async`** sur les `<script>` : ne bloque pas le parsing HTML.
  `defer` pour ce qui dépend du DOM/ordre, `async` pour l'indépendant (analytics).

## 3. Optimiser le chemin critique de rendu

Le navigateur ne peint pas tant que le CSS/JS bloquant n'est pas résolu.
- **Critical CSS inline** : embarque le CSS du above-the-fold dans le `<head>`,
  charge le reste en async. Évite un aller-retour bloquant.
- **Preload / preconnect** : `<link rel="preload">` pour la ressource LCP (image
  hero, police), `preconnect` vers les origines tierces critiques.
- **Évite le CSS/JS render-blocking** non essentiel ; charge-le après le first
  paint.

## 4. Images & médias (souvent le plus gros poids et le LCP)

- **Formats modernes** : WebP/AVIF >> JPEG/PNG (souvent -50 à -80 % de poids).
- **Responsive** : `srcset`/`sizes` pour servir la bonne taille selon l'écran (ne
  sers pas du 4000 px à un mobile).
- **`loading="lazy"`** sur les images hors écran ; **eager + preload** pour
  l'image LCP.
- **Dimensions explicites** (`width`/`height` ou `aspect-ratio`) → évite le CLS.
- **Compresse** (mozjpeg, sharp), sers via **CDN**, et utilise `<video>` /
  formats compressés au lieu de GIF.

## 5. Réseau & caching

- **CDN** : sers les assets statiques au plus près de l'utilisateur (la latence
  est dominée par la distance, cf. les latency numbers du SKILL.md).
- **HTTP cache** : `Cache-Control: immutable` + hash dans le nom de fichier pour
  les assets versionnés ; `ETag`/`stale-while-revalidate` pour le reste.
- **HTTP/2-3** : multiplexing → moins pénalisant de servir plusieurs petits
  fichiers ; HTTP/3 (QUIC) réduit la latence d'établissement.
- **Réduis le nombre de requêtes** sur le chemin critique ; supprime les
  redirections inutiles.
- **Cache navigateur / Service Worker** pour les visites répétées et l'offline.

## 6. Rendu & runtime

- **SSR / SSG / streaming SSR** : génère le HTML côté serveur (ou au build) pour
  un LCP rapide ; hydrate ensuite. SSG quand le contenu est statique.
- **Virtualisation des listes** : n'affiche que les éléments visibles (react-window,
  TanStack Virtual) au lieu de monter 10 000 lignes dans le DOM.
- **Évite les re-renders inutiles** (React : `memo`, `useMemo`, clés stables ;
  éviter de recréer des objets/fonctions à chaque render).
- **Évite layout thrashing** : ne fais pas lire-puis-écrire le layout en boucle
  (`offsetHeight` puis style puis `offsetHeight`...) → batch les lectures puis les
  écritures ; anime via `transform`/`opacity` (composités GPU), pas `top`/`left`.
- **`content-visibility: auto`** pour sauter le rendu du contenu hors écran.

## 7. Polices

- **`font-display: swap`** (texte visible immédiatement, pas de flash invisible).
- **Sous-ensembles** (subsetting) + formats **woff2** ; preload la police critique.
- Limite le nombre de familles/graisses chargées.

## Checklist frontend
1. Lighthouse passé ? LCP < 2,5 s / INP < 200 ms / CLS < 0,1 ?
2. Bundle JS découpé (code splitting) et lazy-loadé ? tree shaking + minify +
   Brotli ?
3. Tâches longues fractionnées / déportées en Web Worker ?
4. Images en WebP/AVIF, responsive, lazy (sauf LCP), dimensions explicites ?
5. Critical CSS inline, scripts en `defer`/`async`, preload de la ressource LCP ?
6. Assets servis par CDN avec un bon `Cache-Control` ?
7. Listes longues virtualisées ? re-renders maîtrisés ? animations sur `transform` ?

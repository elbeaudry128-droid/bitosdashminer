# BitOS Cloud v3 — Options de déploiement simples

## 🥇 Option A — GitHub Pages (automatique, recommandé)

Un workflow GitHub Actions est déjà configuré dans `.github/workflows/pages.yml`.

### Activation (2 clics, 1 seule fois)

1. Va sur **https://github.com/elbeaudry128-droid/bitosdashFINAL/settings/pages**
2. Dans **Source**, sélectionne : **"GitHub Actions"**
3. C'est tout.

Dès ton prochain `git push`, le workflow va déployer automatiquement.

### Ton URL publique

```
https://elbeaudry128-droid.github.io/bitosdashFINAL/
```

### Depuis ton TCL60

- Ouvre l'URL dans **Chrome**
- Menu ⋮ → **Ajouter à l'écran d'accueil**
- L'app s'installe comme une vraie app native

### Déploiement manuel

Tu peux aussi déclencher le déploiement manuellement :
- https://github.com/elbeaudry128-droid/bitosdashFINAL/actions
- Sélectionne "Deploy to GitHub Pages" → "Run workflow"

---

## 🥈 Option B — Fichier HTML autonome (aucun serveur)

Le fichier **`bitos-standalone.html`** (434 KB) contient **TOUT** :
- HTML + CSS + app.js + manifest inlined

### Utilisation

**Sur ton PC :**
- Double-clic sur `bitos-standalone.html` → Chrome s'ouvre
- Ou glisse-dépose le fichier sur Chrome

**Sur ton TCL60 :**
1. Envoie-toi le fichier par mail / WhatsApp / Google Drive / USB
2. Ouvre-le avec Chrome

**Limitation :** en mode `file://`, certaines APIs externes bloquent CORS. Pour une expérience complète, utilise GitHub Pages (Option A).

---

## Comparatif des 5 options

| Option | Setup | URL | Mobile | APIs live | Recommandé pour |
|---|---|---|---|---|---|
| **A. GitHub Pages** | 2 clics | fixe publique | ✅ | ✅ (avec fallbacks) | **Usage quotidien** |
| **B. Standalone HTML** | 0 | aucune | ✅ (fichier) | ⚠ CORS limité | **Test rapide / offline** |
| C. Serveur Python | CLI | locale | via LAN | ✅ complet | Dev avancé |
| D. Netlify Drop | drag&drop | aléatoire | ✅ | ✅ | Démo publique |
| E. Termux Android | CLI phone | locale | direct | ✅ complet | Pas de PC |

---

## Workflow de fichiers

Après activation de GitHub Pages, ton repo contiendra :

```
bitosdashFINAL/
├── .github/workflows/pages.yml    ← auto-deploy (créé)
├── bitos-standalone.html          ← HTML tout-en-un (créé)
├── index.html                      ← version web
├── app.js                          ← frontend
├── manifest.json
├── sw.js
├── bitosdash.py                    ← serveur Python (optionnel)
├── server.py                       ← version non-fusionnée
├── run.sh                          ← launcher Python
└── OPEN.md / DEPLOY.md             ← docs
```

Sur GitHub Pages seront déployés : `index.html`, `app.js`, `manifest.json`, `sw.js`, `bitos-standalone.html`.

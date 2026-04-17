# BitOS Cloud v3 — Ready-to-Use

## Démarrage ultra-rapide

### Linux / macOS (1 commande)

```bash
./run.sh
```

Cela lance le serveur sur `http://localhost:8765` et ouvre le navigateur.

### Windows / manuel

```bash
python3 bitosdash.py --open
```

---

## IMPORTANT — HTTP, PAS HTTPS

```
  ✓ http://localhost:8765      ← BON
  ✗ https://localhost:8765     ← NE FONCTIONNE PAS
```

Le serveur est en **HTTP** par défaut. Pour activer HTTPS, ajoutez `--https` :

```bash
python3 bitosdash.py --https --lan
```

---

## Modes de lancement

### Mode local (ton PC uniquement)
```bash
./run.sh
# ou
python3 bitosdash.py --open
```
→ http://localhost:8765

### Mode LAN (TCL60, iPad, autre PC) sans auth
```bash
./run.sh lan
# ou
python3 bitosdash.py --lan --no-auth
```
→ `http://<IP-LAN>:8765`

### Mode LAN avec mot de passe + QR code
```bash
./run.sh lan-auth
# ou
python3 bitosdash.py --lan --qr
```

### Mode HTTPS complet
```bash
./run.sh https
# ou
python3 bitosdash.py --https --lan --qr
```

---

## Accès depuis TCL60 (Chrome Android)

1. Sur ton PC :
   ```bash
   ./run.sh lan
   ```
2. Note l'**IP LAN** affichée
3. Sur ton TCL60, ouvre **Chrome** et tape :
   ```
   http://<IP-LAN>:8765
   ```
4. Menu ⋮ → **Ajouter à l'écran d'accueil** → BitOS devient une PWA plein écran

### Trouver ton IP LAN

```bash
hostname -I | awk '{print $1}'
```

---

## Déploiement minimal (2 fichiers seulement)

```
bitosdashFINAL/
├── bitosdash.py   ← serveur + HTML/manifest/SW embarqués (47 KB)
└── app.js         ← logique frontend (418 KB)
```

Tout le reste est optionnel. Ces 2 fichiers suffisent.

---

## Endpoints du serveur

| Route | Description |
|---|---|
| `/` | Dashboard (index.html embarqué) |
| `/app.js` | Logique frontend |
| `/manifest.json` | PWA manifest (embarqué) |
| `/sw.js` | Service Worker (embarqué) |
| `/status` | JSON état serveur |
| `/api/proxy-test` | Test de connectivité des APIs externes |
| `/login` | Page de connexion (mode LAN) |
| `/logout` | Déconnexion |

### Proxies CORS
| Route locale | Cible upstream |
|---|---|
| `/proxy/hiveos` | `https://api2.hiveos.farm/api/v2` |
| `/proxy/coingecko` | `https://api.coingecko.com/api/v3` |
| `/proxy/kaspa` | `https://api.kaspa.org` |
| `/proxy/xmr-pool` | `https://supportxmr.com/api` |
| `/proxy/kas-pool` | `https://api-kas.k1pool.com/api` |
| `/proxy/xmrchain` | `https://xmrchain.net/api` |
| `/proxy/asic/<ip>/<path>` | ASIC HTTP local |

---

## Diagnostic rapide

```bash
# Le serveur répond-il ?
curl http://localhost:8765/status

# Les APIs externes marchent-elles ?
curl http://localhost:8765/api/proxy-test

# Quel PID tient le port 8765 ?
lsof -ti:8765

# Arrêter le serveur
kill $(lsof -ti:8765)
```

---

## Options de `bitosdash.py`

```
--port N        Port custom (défaut: 8765)
--lan           Accès depuis le réseau local
--qr            QR code pour mobile
--https         HTTPS auto-signé
--open          Ouvre le navigateur automatiquement
--log FILE      Fichier de log
--no-watch      Désactive le watchdog
--password PWD  Mot de passe (mode LAN)
--no-auth       Désactive l'auth en mode LAN
```

---

## Dépannage

**Le dashboard ne s'affiche pas (page blanche)**
- Ouvre la console Chrome (F12) et cherche les erreurs
- Vérifie que `app.js` est bien chargé : http://localhost:8765/app.js doit renvoyer du code

**"Cette page n'est pas accessible"**
- Tu as tapé `https://` au lieu de `http://`. Utilise `http://localhost:8765`

**"Port déjà utilisé"**
- `kill $(lsof -ti:8765)` puis relance

**Proxy APIs en erreur 502**
- Normal dans un environnement sandbox/cloud (firewall de sortie)
- En local chez toi, les 6 proxies répondent en 200 OK

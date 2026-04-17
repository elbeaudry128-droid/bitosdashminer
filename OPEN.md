# BitOS Cloud v3 — Liens d'ouverture

> Serveur local démarré sur le port `8765` — Linux/Cloud

## Acces direct

| Lien | Description |
|---|---|
| **[Ouvrir le Dashboard](http://localhost:8765/)** | Dashboard principal |
| **[Statut serveur](http://localhost:8765/status)** | JSON état + uptime |
| **[Test des proxies](http://localhost:8765/api/proxy-test)** | Vérif APIs externes |
| **[Login (mode LAN)](http://localhost:8765/login)** | Page d'authentification |

## Endpoints proxy (CORS contournés)

| Route | Cible upstream |
|---|---|
| `/proxy/hiveos` | `https://api2.hiveos.farm/api/v2` |
| `/proxy/coingecko` | `https://api.coingecko.com/api/v3` |
| `/proxy/kaspa` | `https://api.kaspa.org` |
| `/proxy/xmr-pool` | `https://supportxmr.com/api` |
| `/proxy/kas-pool` | `https://api-kas.k1pool.com/api` |
| `/proxy/xmrchain` | `https://xmrchain.net/api` |
| `/proxy/asic/<ip>/<path>` | ASIC HTTP local (Antminer S21) |

## Commandes de lancement

```bash
# Localhost simple (sans auth)
python3 server.py

# LAN avec mot de passe + QR code mobile
python3 server.py --lan --qr

# LAN avec mot de passe explicite
python3 server.py --lan --password MonMotDePasse

# HTTPS auto-signé + LAN + auth
python3 server.py --https --lan --qr

# Port custom
python3 server.py --port 8080

# Avec ouverture auto du navigateur
python3 server.py --open

# Avec fichier de log
python3 server.py --lan --log /tmp/bitos.log
```

## Stack des fichiers

```
bitosdashFINAL/
├── server.py        # Serveur HTTP Python (proxy CORS, auth, HTTPS, watchdog)
├── index.html       # Shell du dashboard (PWA, nav, KPI grid)
├── app.js           # Logique frontend (~8400 lignes : mining, wallets, charts)
├── manifest.json    # PWA manifest
└── sw.js            # Service Worker (offline, stale-while-revalidate)
```

## Vérification rapide

```bash
curl http://localhost:8765/status
curl http://localhost:8765/api/proxy-test
```

## Arrêt du serveur

```bash
# Trouver le PID
lsof -ti:8765

# Tuer le processus
kill $(lsof -ti:8765)
```

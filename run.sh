#!/usr/bin/env bash
# BitOS Cloud v3 — Ready-to-use launcher
set -e
cd "$(dirname "$0")"

PORT="${BITOS_PORT:-8765}"
MODE="${1:-local}"  # local | lan | https

echo ""
echo "  ┌─────────────────────────────────────────┐"
echo "  │   BitOS Cloud v3 — Ready-to-Use         │"
echo "  └─────────────────────────────────────────┘"
echo ""

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
  echo "  ERREUR: python3 introuvable. Installez Python 3.8+ et réessayez."
  exit 1
fi

# Check required files
if [ ! -f "bitosdash.py" ]; then
  echo "  ERREUR: bitosdash.py manquant dans $(pwd)"
  exit 1
fi
if [ ! -f "app.js" ]; then
  echo "  ERREUR: app.js manquant dans $(pwd)"
  exit 1
fi

# Kill any process on the port
if command -v lsof >/dev/null 2>&1; then
  OLD_PID=$(lsof -ti:"$PORT" 2>/dev/null || true)
  if [ -n "$OLD_PID" ]; then
    echo "  Port $PORT déjà utilisé (PID $OLD_PID) — arrêt..."
    kill "$OLD_PID" 2>/dev/null || true
    sleep 1
  fi
fi

case "$MODE" in
  lan)
    echo "  Mode: LAN (sans auth)"
    echo "  URL locale: http://localhost:$PORT"
    echo "  URL LAN:    http://$(hostname -I 2>/dev/null | awk '{print $1}'):$PORT"
    echo ""
    exec python3 bitosdash.py --lan --no-auth --port "$PORT"
    ;;
  lan-auth)
    echo "  Mode: LAN avec mot de passe"
    exec python3 bitosdash.py --lan --qr --port "$PORT"
    ;;
  https)
    echo "  Mode: HTTPS + LAN"
    exec python3 bitosdash.py --https --lan --qr --port "$PORT"
    ;;
  local|*)
    echo "  Mode: Local uniquement"
    echo "  URL: http://localhost:$PORT"
    echo ""
    echo "  ⚠  UTILISEZ http://  PAS https://"
    echo ""
    exec python3 bitosdash.py --open --port "$PORT"
    ;;
esac

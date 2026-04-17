#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════
# BitOS Cloud v3 — Installation automatique pour Termux
# Copiez cette commande dans Termux :
#   curl -sSL https://raw.githubusercontent.com/elbeaudry128-droid/bitosdashFINAL/claude/bitos-v3-hiveos-mining-9sRF0/setup-termux.sh | bash
# ═══════════════════════════════════════════════════════

set -e

echo ""
echo "  ┌───────────────────────────────────────────┐"
echo "  │  BitOS Cloud v3 — Installation Termux     │"
echo "  └───────────────────────────────────────────┘"
echo ""

# 1. Update + install deps
echo "  [1/4] Installation des paquets..."
pkg update -y -q 2>/dev/null || apt update -y -qq
pkg install -y -q python git termux-api 2>/dev/null || apt install -y -qq python git termux-api

# 2. Clone or update repo
echo "  [2/4] Telechargement de BitOS..."
REPO_DIR="$HOME/bitosdash"
if [ -d "$REPO_DIR/.git" ]; then
  cd "$REPO_DIR"
  git pull origin claude/bitos-v3-hiveos-mining-9sRF0 2>/dev/null || true
else
  git clone -b claude/bitos-v3-hiveos-mining-9sRF0 \
    https://github.com/elbeaudry128-droid/bitosdashFINAL.git "$REPO_DIR" 2>/dev/null
  cd "$REPO_DIR"
fi

# 3. Verify files
echo "  [3/4] Verification des fichiers..."
MISSING=0
for f in bitos-termux.py app.js index.html; do
  if [ ! -f "$f" ]; then
    echo "    MANQUANT: $f"
    MISSING=1
  else
    SIZE=$(wc -c < "$f")
    echo "    OK: $f ($SIZE bytes)"
  fi
done
if [ "$MISSING" = "1" ]; then
  echo ""
  echo "  ERREUR: fichiers manquants. Re-essayez:"
  echo "  rm -rf $REPO_DIR && bash setup-termux.sh"
  exit 1
fi

# 4. Launch
echo "  [4/4] Lancement du serveur..."
echo ""
echo "  ════════════════════════════════════════════"
echo "  BitOS va ouvrir Chrome automatiquement."
echo "  Si Chrome ne s'ouvre pas, tape dans Chrome :"
echo ""
echo "    http://localhost:8765"
echo ""
echo "  Pour arreter : Ctrl+C"
echo "  Pour relancer : cd ~/bitosdash && python bitos-termux.py"
echo "  ════════════════════════════════════════════"
echo ""

python bitos-termux.py

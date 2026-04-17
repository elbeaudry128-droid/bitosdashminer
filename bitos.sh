#!/data/data/com.termux/files/usr/bin/bash
# Raccourci de lancement rapide BitOS
# Place ce fichier dans ~/bin/ pour taper juste: bitos
cd ~/bitosdash 2>/dev/null || cd "$(dirname "$0")"
python bitos-termux.py "$@"

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -f .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt
printf '\nAbra http://127.0.0.1:5000 no navegador. Para encerrar, pressione Ctrl+C.\n'
exec .venv/bin/python run.py

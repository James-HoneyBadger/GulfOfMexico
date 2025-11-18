#!/usr/bin/env bash
# Launch Gulf of Mexico Web IDE

cd "$(dirname "$0")"
source .venv/bin/activate
python -m gulfofmexico.ide --web

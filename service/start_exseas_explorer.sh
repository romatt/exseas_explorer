#!/bin/bash
set -euo pipefail

BASE_DIR=/opt/exseas_explorer
APP_DIR=${BASE_DIR}/exseas_explorer
VENV_DIR=${BASE_DIR}/venv

if [ ! -x "$VENV_DIR/bin/gunicorn" ]; then
    echo "venv not usable at $VENV_DIR — run deploy first" >&2
    exit 1
fi

if [ -d "$APP_DIR/.venv" ]; then
    echo "venv not usable at $APP_DIR/.venv — remove" >&2
    exit 1
fi

cd ${APP_DIR}
exec "$VENV_DIR/bin/gunicorn" exseas_explorer.app:app --bind 127.0.0.1:8002 --workers 4 --forwarded-allow-ips 127.0.0.1


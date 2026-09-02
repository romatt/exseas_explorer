#!/bin/bash
set -euo pipefail

BASE_DIR=/opt/exseas_explorer

APP_DIR=${BASE_DIR}/exseas_explorer
VENV_DIR=${BASE_DIR}/venv

# create fixed venv dir - only once (poetry uses a variable name)
if [ ! -d "${VENV_DIR}" ]; then
    python3.12 -m venv "${VENV_DIR}"
fi

cd "$APP_DIR"

git fetch origin --tags
git reset --hard origin/main

# activate environment
source "${VENV_DIR}/bin/activate"

poetry sync --without=dev --compile

restorecon -Rv ${BASE_DIR}
systemctl restart exseas_explorer
systemctl is-active --quiet exseas_explorer || {
    echo "service failed to start" >&2
    journalctl -u exseas_explorer -n 30 --no-pager >&2
    exit 1
}

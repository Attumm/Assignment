#!/bin/bash
set -e

rm -rf .venv_dev
python3 -m venv .venv_dev
source .venv_dev/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
#pip install -e ".[dev]"

deactivate

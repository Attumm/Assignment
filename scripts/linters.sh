#!/bin/bash
set -e

if [ ! -d ".venv_dev" ]; then
     echo "Virtual environment not found. Running build script..."
     bash ./scripts/build_dev.sh
fi


source .venv_dev/bin/activate


# Type Check
python -m mypy --strict src

# Doctype Check
darglint src/quote/

# Multiple linters
python -m pylama -i E501,E231 src

# Security Check
bandit -r src/quote

# Docstring Check
#pydocstyle src/quote/

deactivate



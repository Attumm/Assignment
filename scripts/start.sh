#!/bin/bash
set -e

if [ ! -d ".venv_dev" ]; then
     echo "Virtual environment not found. Running build script..."
     bash ./scripts/build_dev.sh
fi

.venv_dev/bin/uvicorn src.quote.main:app --host 0.0.0.0

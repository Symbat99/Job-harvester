#!/usr/bin/env bash
# Пример запуска на macOS
PROJECT_DIR="$(cd "$(dirname "$0")"; pwd)"
source "$PROJECT_DIR/venv/bin/activate"
python "$PROJECT_DIR/main.py"

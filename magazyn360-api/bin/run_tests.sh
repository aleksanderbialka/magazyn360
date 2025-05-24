#!/bin/bash

# This script runs the tests for the magazyn360-api project.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/.."

source /var/www/magazyn360_api/venv/bin/activate
pytest --cov=magazyn360_api --cov-report=html --cov-report=term-missing .

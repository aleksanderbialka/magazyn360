#!/bin/bash

# This script runs the tests for the magazyn360-api project.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/.."

source /var/www/magazyn360/app/magazyn360_env/bin/activate
pytest --cov=magazyn360_api --cov-report=term-missing --junitxml=pytest-results.xml

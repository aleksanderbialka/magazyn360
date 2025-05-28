#!/bin/bash

# This script runs the tests for the magazyn360-api project.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/.."

source /var/www/magazyn360/app/magazyn360_env/bin/activate
pytest -p pytest_github_actions_annotate_failures --junitxml=results/pytest-results.xml --html=results/pytest-report.html

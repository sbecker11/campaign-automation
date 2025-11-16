#!/bin/bash

# Run all unit tests (with coverage by default)
#
# Usage:
#   ./run_tests_w_coverage.sh         # run with coverage (terminal + HTML report)
#   ./run_tests_w_coverage.sh --quick # run pytest -q without coverage

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Require an active virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ No active virtual environment detected."
    echo "   Please activate your venv first, e.g.:"
    echo "   source venv/bin/activate"
    exit 1
fi

if [[ "$1" == "--quick" ]]; then
    pytest -q
else
    pytest --cov=src --cov-report=term-missing --cov-report=html
    echo ""
    echo "✅ Coverage HTML report:"
    echo ""
    echo "open file://$PROJECT_ROOT/htmlcov/class_index.html"
fi

#!/bin/bash
# Test runner script for WordUp

set -e

echo "🧪 Running WordUp Test Suite"
echo "============================="

# Change to project directory
cd "$(dirname "$0")/.."

# Set Python path to include src directory
export PYTHONPATH=.

# Run tests with coverage
echo "Running all tests with coverage..."
uv run pytest -v --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "✅ Test run complete!"
echo "📊 Coverage report saved to htmlcov/index.html"
echo ""
echo "To run specific test files:"
echo "  PYTHONPATH=. uv run pytest tests/test_models.py -v"
echo "  PYTHONPATH=. uv run pytest tests/test_routes.py -v"
echo "  PYTHONPATH=. uv run pytest tests/test_srs.py -v"
echo "  PYTHONPATH=. uv run pytest tests/test_app.py -v"
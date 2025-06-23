#!/bin/bash

# Script to run tests in the container

echo "Starting unit tests for voting app..."

# Run pytest with coverage and detailed output
python -m pytest test_app.py -v \
    --cov=app \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=xml \
    --junit-xml=test-results.xml

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "✅ All tests passed successfully!"
    echo "📊 Coverage report generated in htmlcov/ directory"
else
    echo "❌ Some tests failed. Check the output above for details."
    exit 1
fi
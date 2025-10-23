#!/bin/bash
# Type checking script for the project

echo "Running mypy type checking on source code..."
mypy src/

echo ""
echo "Type checking complete!"
echo ""
echo "To check specific files:"
echo "  mypy src/app.py"
echo ""
echo "To check with less strict settings:"
echo "  mypy --ignore-missing-imports src/"
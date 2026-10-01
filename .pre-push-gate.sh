#!/bin/bash
# Pre-push gate for rfc-8141-urn-pure
# Run manually: bash .pre-push-gate.sh

set -e

echo "=== Pre-push gate ==="

# Check README.md exists
if [ ! -f README.md ]; then
    echo "FAIL: README.md missing"
    exit 1
fi

# Check LICENSE exists
if [ ! -f LICENSE ]; then
    echo "FAIL: LICENSE missing"
    exit 1
fi

# Check pyproject.toml dependencies = []
DEPS=$(python3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(len(d.get('project',{}).get('dependencies',[])))")
if [ "$DEPS" -ne 0 ]; then
    echo "FAIL: dependencies must be empty, found $DEPS"
    exit 1
fi

# Check pytest exits 0
python3 -m pytest -q --tb=short || {
    echo "FAIL: pytest failed"
    exit 1
}

echo "=== Pre-push gate PASSED ==="
exit 0

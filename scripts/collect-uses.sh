#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get absolute path of this script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

cd "$SCRIPT_DIR"/../..
find . -name '*.py' | grep -v dh-python-dh | grep -v venv | xargs grep --no-filename --only-matching '\(^\| \)dh\.[a-zA-Z0-9_]\+' | sed 's/^ //' | sort | uniq --count | sort --human-numeric-sort --reverse
echo "----------------------------------------"
find . -name '*.py' | grep -v dh-python-dh | grep -v venv | xargs grep --no-filename --only-matching '\(^\| \)dh\.[a-zA-Z0-9_]\+\.[a-zA-Z0-9_]\+' | sed 's/^ //' |  sort | uniq --count | sort --human-numeric-sort --reverse

#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get absolute path of this script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PACKAGE_DIR=$(cd "$SCRIPT_DIR"/.. && pwd)

cd "$PACKAGE_DIR" && ./install.sh

PYTHONSTARTUP="$SCRIPT_DIR"/.pythonstartup
cd "$SCRIPT_DIR" && python3


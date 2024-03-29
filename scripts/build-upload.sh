#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get absolute path of this script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
source "$SCRIPT_DIR"/setenv.sh

cd "$PACKAGE_DIR" && twine upload dist/dh-*-py3-none-any.whl

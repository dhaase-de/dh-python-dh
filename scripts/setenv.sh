#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# important dirs of this Python package (absolute paths)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PACKAGE_DIR=$(cd "$SCRIPT_DIR"/.. && pwd)
SOURCE_DIR="$PACKAGE_DIR/dh/"
DOC_DIR="$PACKAGE_DIR/doc/"


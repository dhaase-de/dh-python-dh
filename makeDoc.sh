#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get absolute path of this script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PACKAGE_DIR="$SCRIPT_DIR/dh/"
DOC_DIR="$SCRIPT_DIR/doc/"

# install package because it will be imported by autodoc
"$SCRIPT_DIR"/install.sh

sphinx-apidoc --force --separate -o "$DOC_DIR"/source "$PACKAGE_DIR" "$PACKAGE_DIR"/tests "$PACKAGE_DIR"/thirdparty/*/
cd "$DOC_DIR" && make html && make singlehtml

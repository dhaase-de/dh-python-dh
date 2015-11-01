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

# create doc source files from the docstrings
sphinx-apidoc --force -o "$DOC_DIR"/source "$PACKAGE_DIR" "$PACKAGE_DIR"/tests "$PACKAGE_DIR"/thirdparty/*/

# create code check report
echo "Pylint report" > "$DOC_DIR"/source/pylint.rst
echo "=============" >> "$DOC_DIR"/source/pylint.rst
echo "" >> "$DOC_DIR"/source/pylint.rst
echo "Detailed messages" >> "$DOC_DIR"/source/pylint.rst
echo "-----------------" >> "$DOC_DIR"/source/pylint.rst
"$SCRIPT_DIR"/check.sh >> "$DOC_DIR"/source/pylint.rst || true

# create doc
cd "$DOC_DIR" && make html && make singlehtml

#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get important dirs of this Python package (absolute paths)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
source "$SCRIPT_DIR"/setenv.sh

# install package because it will be imported by autodoc
#"$SCRIPT_DIR"/build-install.sh

# create doc source files from the docstrings
sphinx-apidoc --force -o "$DOC_DIR"/source "$SOURCE_DIR" "$SOURCE_DIR"/tests "$SOURCE_DIR"/thirdparty/*/

# create code check report
echo "Pylint report" > "$DOC_DIR"/source/pylint.rst
echo "=============" >> "$DOC_DIR"/source/pylint.rst
echo "" >> "$DOC_DIR"/source/pylint.rst
echo "Detailed messages" >> "$DOC_DIR"/source/pylint.rst
echo "-----------------" >> "$DOC_DIR"/source/pylint.rst
"$SCRIPT_DIR"/check-pylint.sh >> "$DOC_DIR"/source/pylint.rst || true

# create doc
cd "$DOC_DIR" && make html && make singlehtml

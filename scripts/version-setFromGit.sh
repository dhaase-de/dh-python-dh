#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get important dirs of this Python package (absolute paths)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
source "$SCRIPT_DIR"/setenv.sh

# get git executable
GIT="$(which git)"

# get version number from git
cd "$PACKAGE_DIR" && VERSION=$("$GIT" describe --tags --dirty | sed s'/-/+/' | sed s'/-/./g')

# write version number to file
VERSION_FILE="$PACKAGE_DIR"/dh/"VERSION.txt"
cat <<EOF >"$VERSION_FILE"
# !!! WARNING: DO NOT EDIT, DO NOT COMMIT THIS FILE !!!
#
# This file is used as place to store the exact 'git-describe' version number
# when building or installing this package. The script 'version-setFromGit.sh'
# writes the current version into this file. When the build or install scripts
# from the 'scripts' dir are used, the version script is always called as first
# step. So for builds (e.g. wheel builds) and non-develop installs, the version
# number is always automatically set to the correct value.
#
# The only situation where you might want to call the version script manually
# is when this package is installed in develop mode (i.e. something like a
# symlink is created in the site-packages dir) and the 'dh.__version__'
# variable should be up-to-date with the actual version.
#
# !!! WARNING: DO NOT EDIT, DO NOT COMMIT THIS FILE !!!

$VERSION

EOF
echo "Saved version number '$VERSION' to file '$VERSION_FILE'"

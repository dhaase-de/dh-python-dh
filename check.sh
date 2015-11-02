#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get absolute path of this script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PACKAGE_DIR="$SCRIPT_DIR/dh/"

# run pylint and format output in rst format (ready to be included in the documentation)
pylint "$PACKAGE_DIR" --good-names="_,a,b,c,i,j,k,m,n,x,y,z,A,B,C,I,J,K,M,N,X,Y,Z" --ignore="thirdparty,tests" --persistent=no --msg-template='    * [{C}] {module}:{obj}:{line},{column}: *{msg}* ({msg_id}, {symbol})' | sed 's/^\*\*\*\*\*\*\*\*\*\*\*\*\* \(.*\)$/\n\* \1\n/' | sed 's/^Report$//' | sed 's/^======$//'

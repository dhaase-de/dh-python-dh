#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get important dirs of this Python package (absolute paths)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
source "$SCRIPT_DIR"/setenv.sh

# run pylint and format output in rst format (ready to be included in the documentation)
pylint "$SOURCE_DIR" --max-line-length=160 --good-names="_,a,b,c,i,j,k,m,n,x,y,z,A,B,C,I,J,K,M,N,X,Y,Z" --ignore="thirdparty,tests" --persistent=no --msg-template='    * [{C}] {module}:{obj}:{line},{column}: *{msg}* ({msg_id}, {symbol})' | sed 's/^\*\*\*\*\*\*\*\*\*\*\*\*\* \(.*\)$/\n\* \1\n/' | sed 's/^Report$//' | sed 's/^======$//'

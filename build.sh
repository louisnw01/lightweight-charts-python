#!/usr/bin/env bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ERROR="${RED}[ERROR]${NC} "
INFO="${CYAN}[INFO]${NC} "
WARNING="${WARNING}[WARNING]${NC} "

rm -rf dist/bundle.js dist/typings/

if [[ $? -eq 0 ]]; then
    echo -e "${INFO}deleted bundle.js and typings.."
else
    echo -e "${WARNING}could not delete old dist files, continuing.."
fi

npx rollup -c rollup.config.js
if [[ $? -ne 0 ]]; then
    exit 1
fi

cp dist/bundle.js src/general/styles.css lightweight_charts/js
if [[ $? -eq 0 ]]; then
    echo -e "${INFO}copied bundle.js, style.css into python package"
else
    echo -e "${ERROR}could not copy dist into python package ?"
    exit 1
fi
echo -e "\n${GREEN}[BUILD SUCCESS]${NC}"


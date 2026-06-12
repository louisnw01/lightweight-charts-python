#!/usr/bin/env bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ERROR="${RED}[ERROR]${NC} "
INFO="${CYAN}[INFO]${NC} "
WARNING="${YELLOW}[WARNING]${NC} "

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

# Copy the LWC v5 standalone production build into the Python package
LWC_STANDALONE="node_modules/lightweight-charts/dist/lightweight-charts.standalone.production.js"
if [[ -f "$LWC_STANDALONE" ]]; then
    cp "$LWC_STANDALONE" lightweight_charts_csava/js/lightweight-charts.js
    echo -e "${INFO}copied lightweight-charts v5 standalone into python package"
else
    echo -e "${WARNING}could not find LWC standalone file at ${LWC_STANDALONE}"
fi

cp dist/bundle.js src/general/styles.css lightweight_charts_csava/js
if [[ $? -eq 0 ]]; then
    echo -e "${INFO}copied bundle.js, styles.css into python package"
else
    echo -e "${ERROR}could not copy dist into python package ?"
    exit 1
fi
echo -e "\n${GREEN}[BUILD SUCCESS]${NC}"

#!/bin/bash

# ./call_api.sh <estado> <tamanhoDaPagina>

curl -X 'GET' \
  "https://api.obrasgov.gestao.gov.br/obrasgov/api/projeto-investimento?uf=$1&pagina=0&tamanhoDaPagina=$2" \
  -H 'accept: */*' | jq '.' >"../data/$(date +%d_%H_%M).json"

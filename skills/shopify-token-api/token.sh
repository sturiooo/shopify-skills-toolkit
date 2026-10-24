#!/usr/bin/env bash
# Stały token Admin API (custom distribution + authorization code grant).
# Procedura: references/staly-token-krok-po-kroku.md
#
#   token.sh url      <sklep>.myshopify.com <client_id> <redirect_uri> [zakresy]
#   token.sh exchange <sklep>.myshopify.com <client_id> <code>        # secret: zmienna SHOPIFY_CLIENT_SECRET albo pytanie (ukryte)
#   token.sh verify   <sklep>.myshopify.com <token>
#
# Niczego nie zapisuje na dysk. Wymiana BEZ expiring=1, więc token nie wygasa.
set -euo pipefail

DEFAULT_SCOPES="read_products,write_products,read_inventory,write_inventory,read_locations,read_product_listings,write_product_listings,read_publications,write_publications,read_files,write_files,read_translations,write_translations,read_metaobjects,write_metaobjects,read_metaobject_definitions"
API_VERSION="${SHOPIFY_API_VERSION:-2026-07}"

usage() { sed -n '4,8p' "$0"; exit 1; }
[ $# -ge 1 ] || usage
cmd="$1"; shift

case "$cmd" in
  url)
    [ $# -ge 3 ] || usage
    shop="$1"; cid="$2"; redirect="$3"; scopes="${4:-$DEFAULT_SCOPES}"
    echo "1) NAJPIERW link instalacyjny z Dystrybucji (Partners), bez ekranu zgody -> przekierowanie na app URL."
    echo "2) Potem ten link, zatwierdź Zainstaluj:"
    echo "https://${shop}/admin/oauth/authorize?client_id=${cid}&scope=${scopes}&redirect_uri=${redirect}&state=$(date +%s)"
    ;;
  exchange)
    [ $# -ge 3 ] || usage
    shop="$1"; cid="$2"; code="$3"
    secret="${SHOPIFY_CLIENT_SECRET:-}"
    if [ -z "$secret" ]; then read -r -s -p "Client secret: " secret; echo; fi
    curl -s -X POST "https://${shop}/admin/oauth/access_token" \
      --data-urlencode "client_id=${cid}" \
      --data-urlencode "client_secret=${secret}" \
      --data-urlencode "code=${code}"
    echo
    ;;
  verify)
    [ $# -ge 2 ] || usage
    shop="$1"; token="$2"
    curl -s -H "X-Shopify-Access-Token: ${token}" -H "Content-Type: application/json" \
      "https://${shop}/admin/api/${API_VERSION}/graphql.json" \
      -d '{"query":"{ shop { name myshopifyDomain } productsCount { count } }"}'
    echo
    curl -s -H "X-Shopify-Access-Token: ${token}" "https://${shop}/admin/oauth/access_scopes.json" \
      | python3 -c "import sys,json; s=[x['handle'] for x in json.load(sys.stdin)['access_scopes']]; print(len(s),'zakresów:',','.join(s))"
    ;;
  *) usage ;;
esac

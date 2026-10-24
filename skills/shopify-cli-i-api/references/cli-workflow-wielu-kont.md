# Shopify CLI: workflow wielu kont, pull/push, Admin GraphQL bez aplikacji (2026-06)

**Zweryfikowane w sesji obejmującej kilka sklepów naraz. CLI 4.2.0.**

### Przełączanie kont
- `shopify auth logout` wylogowuje ze **WSZYSTKICH** kont (też tokeny `store auth`). Potem pierwsza komenda wymagająca auth otwiera logowanie (device code + przeglądarka).
- Logowanie jest **interaktywne** → user uruchamia je u siebie z prefiksem `!` (np. `! shopify theme list --store SKLEP.myshopify.com`). Agent NIE odpala tego sam (zawiesi się albo otworzy w złym kontekście).
- Workflow nowego sklepu: `! shopify theme list --store X` (login + lista motywów z ID) → user wkleja listę → wybiera motyw.

### Pull / push
- `shopify theme pull --store X --theme <ID> --path "<katalog-projektu>/<sklep>"`: **folder docelowy musi już istnieć** (`mkdir -p` najpierw), inaczej „A path was explicitly provided but doesn't exist”.
- `theme pull` na czystym folderze daje pełną strukturę motywu (assets/blocks/config/layout/locales/sections/snippets/templates).
- `theme push --only <plik> --only <plik2>`: wgrywaj TYLKO zmienione pliki (push bez `--only` nadpisuje `settings_data.json`/templates).
- **Push na motyw LIVE wymaga `--allow-live`** (inaczej „Failed to prompt” w trybie nieinteraktywnym). Push na unpublished bez tej flagi.
- Po każdej edycji waliduj `mcp__shopify-dev__validate_theme` (Shopify Dev MCP, Theme Check) PRZED push: łapie błędy Liquid/JSON schema.

### `shopify store execute` = Admin GraphQL z CLI (bez budowania aplikacji)
CLI 4.x ma `shopify store auth` / `store execute` / `store info`:
- Auth per sklep z zakresami: `shopify store auth --store X --scopes write_shipping,read_shipping,read_locations` (interaktywne → przez `!`). Trzyma osobny online-token per sklep (niezależny od loginu „motywowego”).
- Zapytania: `shopify store execute --store X --query-file q.graphql --json --output-file out.json`. Mutacje: dodaj **`--allow-mutations`** (domyślnie zablokowane).
- **GOTCHA odpowiedzi:** `store execute` zwraca JSON **BEZ koperty `data`**, czyli od razu `{ "deliveryProfileUpdate": {...} }`. Parsuj `d.get('data', d)`.
- **GOTCHA `/tmp` (mingw vs Windows Python):** plik zapisany do `/tmp` przez CLI/bash jest widoczny dla `ls`/`cat` (mingw), ale **python.exe (Windows) go nie widzi** (`FileNotFoundError`). Zapisuj `--output-file` do ścieżki w projekcie (np. `./_out.json`), nie do `/tmp`, gdy parsujesz Pythonem.
- **Przed mutacją na produkcji:** (1) introspekcja nazw pól input: `__type(name:"XInput"){inputFields{name}}` przez `store execute`; (2) walidacja kształtu mutacji przez `mcp__shopify-dev__validate_graphql_codeblocks` (api: admin, wersja z `learn_shopify_api`). To eliminuje halucynacje schematu.

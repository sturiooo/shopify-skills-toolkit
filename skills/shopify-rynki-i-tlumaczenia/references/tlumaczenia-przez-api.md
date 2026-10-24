# Tłumaczenia przez Admin API

Zapytania zwalidowane narzędziem shopify-dev (Shopify Dev MCP) na wersji 2026-07 (12.10.2026). Uruchamianie:
`shopify store execute` (skill `shopify-cli-i-api`).

## Kiedy API zamiast apki

Sklep z pluszakami (03-04.09.2026): klient wyczerpał limit języków w apce tłumaczeń, a API takiego limitu
nie ma. Cały sklep EN→PL (238 produktów) poszedł przez `translationsRegister`. Workflow da się w całości
oskryptować (eksport `translatableResources` → plik do tłumaczenia → rejestracja partiami), warto zbudować
go raz i reużywać.

## Scope'y

`read_translations`, `write_translations`, `read_locales` (do `shopLocales`), do rynków `read_markets`
i `write_markets`, do języków `write_locales`.
**`shopify store auth` zastępuje token, nie dokłada scope'ów** (sklep z obuwiem skórzanym, 09.10.2026): po auth
z innym zestawem `translatableResources` odbija „Access denied … Required access: read_translations”.
Przy każdym auth podawaj pełną listę na całą sesję.

## Układ sklepu

```graphql
query {
  shopLocales { locale primary published }
  markets(first: 20) { nodes { name status
    webPresences(first: 5) { nodes { id domain { host } subfolderSuffix
      defaultLocale { locale } alternateLocales { locale } rootUrls { locale url } } } } }
}
```

`Market.webPresence`, `Shop.domains` i `MarketWebPresence.market` są deprecated (walidator 2026-07),
działają, ale w nowych skryptach używaj `webPresences` i `domainsPaginated`.

## Eksport: treść, klucz, digest

```graphql
query {
  translatableResources(first: 50, resourceType: PRODUCT) {
    pageInfo { hasNextPage endCursor }
    nodes { resourceId
      translatableContent { key value digest locale }
      translations(locale: "de") { key value outdated market { handle } } }
  }
}
```

`translations` przyjmuje też `marketId` (tłumaczenie per rynek) i `outdated: true`.
`translatableResourcesByIds(resourceIds: [...])` pobiera digesty wybranych zasobów naraz.

## Zapis

```graphql
mutation Reg($id: ID!, $t: [TranslationInput!]!) {
  translationsRegister(resourceId: $id, translations: $t) {
    translations { key locale outdated }
    userErrors { field message code }
  }
}
```

`TranslationInput`: `key`, `locale`, `value`, `translatableContentDigest` (digest bieżącego źródła),
opcjonalnie `marketId`. Usuwanie: `translationsRemove(resourceId, translationKeys, locales, marketIds)`.

Pułapki ze sklepu z pluszakami (03-04.09.2026) i sklepu z obuwiem:
- **Emoji jako surowe UTF-8** (`ensure_ascii=False`). Ucieczki `\ud83e…` odbijają całą partię `PARSE_ERROR`.
- **Ustawienie motywu jest tłumaczalne dopiero, gdy ma wartość w `settings_data.json`.**
- **Po zmianie źródła digest się zmienia**: tłumaczenie robi się `outdated`, dalej się serwuje i myli.
  Eksportuj ponownie i przerejestruj (sklep z obuwiem, 01.09.2026, maile; sklep z obuwiem skórzanym, `color_swatch_config`).
- **Stare tłumaczenia trzymają stare dane** (sklep z obuwiem 24.08.2026: dawna firma nadal na `/en/` i `/de/`).
  Przy zmianie danych firmy, adresów i URL przejdź `translations(locale:)` dla WSZYSTKICH języków.
  Gdy źródło jest już w docelowym języku, przeterminowane rekordy usuń `translationsRemove` (ten sam sklep, 03.09.2026).
- Na Windows skrypt zapisuj do pliku i odpalaj z `PYTHONUTF8=1`; heredoc do `python -` psuje polskie
  znaki i `\n` (09.10.2026).
- 20 partii produktów tłumaczonych równolegle agentami z jedną instrukcją działa; kontrola: walidacja
  JSON, komplet kluczy per ID, limity długości meta, brak `"` w wartościach.

## Klucze per typ zasobu (docs, `TranslatableResourceType`)

| Typ | Klucze / uwagi |
|---|---|
| `PRODUCT`, `COLLECTION`, `PAGE`, `ARTICLE`, `BLOG` | `title`, `body_html`, `handle`, `meta_title`, `meta_description` (ARTICLE także `summary_html`). Tagi artykułów nietłumaczalne. |
| `SHOP_POLICY` | tylko `body`: tytuł polityki jest systemowy, więc tytuł dokumentu wstaw jako `<h2>` w body. |
| `LINK` / `MENU` | pozycje menu to `LINK` (`title`), nie `MenuItem`: `translatableResourcesByIds` z gid MenuItem daje `RESOURCE_NOT_FOUND`. |
| `EMAIL_TEMPLATE` | `title`, `body_html`. Źródło tylko z panelu, tłumaczenie przez API. Odczyt wszystkich 60 szablonów pozwala udowodnić brak danych na sztywno. |
| `DELIVERY_METHOD_DEFINITION` | `name`, `description`. Kontrahent B2B widzi je w języku z `companyLocation.locale`. |
| `FILTER` | `label`. |
| `METAFIELD` | `value`. Do wycofania na rzecz `Metafield.translatable` (API 2026-10). |
| `METAOBJECT` | pola wg typu, gdy definicja ma `capabilities.translatable.enabled`. |
| `ONLINE_STORE_THEME_LOCALE_CONTENT` | klucze z pliku locale języka PRIMARY. |
| `ONLINE_STORE_THEME_JSON_TEMPLATE`, `..._SECTION_GROUP` | teksty z `templates/*.json` i grup sekcji (np. `menu_title` mega menu w `header-group.json`). |
| `ONLINE_STORE_THEME`, `..._SETTINGS_CATEGORY` | ustawienia motywu (`general.swatch_config`, adresy, etykiety). |

## Audyt pokrycia

Dwie ścieżki, obie potrzebne (sklep z pluszakami, 2026-09):
1. **Skan plików motywu z live**: wytnij `{% schema %}`, `{% comment %}`, `{% doc %}` i komentarze JS,
   potem szukaj `[ąćęłńóśźż]` (562 trafienia przed filtrem, 44 po, realnych 6). Teksty zaszyte w pliku
   są niewidoczne dla panelu Tłumaczenia.
2. **`translatableResources` dla ~20 typów × każde locale** z aliasami `de: translations(locale:"de")`.
   W tym sklepie wyszło, że 4 z 5 polityk nie mają DE i FR.

Czego nie brać za błąd: brak tłumaczenia `handle`, nazwy własne bez tłumaczenia (Shopify pokaże oryginał),
słowa wspólne dla języków („Produkt” po niemiecku). **Sprawdź `templateSuffix`, zanim uznasz demo za
problem**: w sklepie na motywie Sleek 96 ze 128 angielskich trafień siedziało w nieprzypisanych szablonach (31.08.2026).
Po `translationsRegister` na metapolu filtr S&D pokazuje stare wartości ok. 1,5 min: nie poprawiaj drugi raz.

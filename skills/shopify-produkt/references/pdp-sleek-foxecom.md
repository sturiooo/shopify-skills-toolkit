# Karta produktu w motywie Sleek (FoxEcom): bloki, metapola, CSS i scope per-produkt

**Wdrożone:** sklep z suplementami dla psów (2026-06, motyw **Sleek 2.0.0 / FoxEcom**, sklep PL). Rodzina FoxEcom (jak Foxify): `cart.js` z `innerHTML` swap + event `cart:updated`, custom elementy.

#### Mapa karty produktu (gdzie co żyje, oszczędza grepowania)

- `sections/main-product.liquid`: wrapper sekcji + `{% schema %}` (blocks + section settings). Renderuje media i info przez snippety.
- `snippets/product-information-blocks.liquid`: **wszystkie bloki kolumny info** (`{%- case block.type -%}`): `price`, `title`, `description`, `sku`, `inventory`, `variant_picker`, `buy_buttons`→`render 'buy-buttons'`, `icon-with-text` itd. **Tu dodajesz nowy `when` + settingi w schemacie main-product.**
- `snippets/buy-buttons.liquid`: ATC + dynamiczny checkout. ATC: `class="product-form__submit btn btn--secondary"` (przy dynamicznym) / `btn--primary`. Dynamiczny: `{{ form | payment_button }}` → `.shopify-payment-button`.
- `snippets/product-media-gallery.liquid` → per-medium `snippets/product-thumbnail.liquid`. Kontener każdego medium: **`.product__media-container`** (`media-type-{image|video|model}`, ma `overflow:hidden`). To cel pod ramkę/radius mediów.
- `snippets/price.liquid`: sama cena (`.f-price`). Tekst „Z wliczonym podatkiem. Wysyłka…" jest w **product-information-blocks**, blok `price` (`.product__tax`), NIE w price.liquid.
- `layout/theme.liquid`: `<body class="{{ request.page_type }}-template {{ template.suffix }} …">`. Inline `<style>` w `<head>` = dom dla **globalnych** customów (w tym sklepie już były tam `@font-face` fontu marki + `.btn{font-family:'Brand Heading';uppercase}`).

#### Podpięcie metapola pod cenę (i ogólnie do bloku) + RICH TEXT gotcha

Zamiana `.product__tax` na pole konfigurowalne + fallback do metapola. **Typ metapola decyduje o renderze:**

| Typ metapola | Jak renderować w Liquid |
|---|---|
| Text (single/multi-line) | `{{ product.metafields.custom.klucz.value }}` |
| **Rich text** (sformatowany) | `{{ product.metafields.custom.klucz \| metafield_tag }}` |

**Gotcha (kosztowała 2 rundy):** dla rich text `{{ ...klucz }}` (drop) i `{{ ...klucz.value }}` wypisują **surowy JSON** `{"type":"root",...}`. Tylko `| metafield_tag` zamienia rich text na HTML. Pole edytora connect-owalne pod metapole = `inline_richtext` (łapie text metafieldy przez „Połącz źródło dynamiczne").

Wzorzec „edytor nadpisuje, inaczej metapole na stałe":
```liquid
{%- if block.settings.custom_note != blank -%}
  <div class="rte">{{ block.settings.custom_note }}</div>
{%- elsif product.metafields.custom.cena_za_sztuke != blank -%}
  <div class="rte">{{ product.metafields.custom.cena_za_sztuke | metafield_tag }}</div>
{%- endif -%}
```

#### Rozmiar tekstu desktop/mobile w rem: przez CSS variable + media query

Range w schemacie z `"unit": "rem"`, **`0` = „domyślne z motywu"** (sentinel, nie wymusza nic). Render: inline CSS var tylko gdy >0. CSS: `font-size: var(--x, fallback)`. Mobile fallback do desktopu: `var(--mob, var(--desk, fallback))`. `.rte p` w tym motywie **nie ma** sztywnego `font-size` → ustawienie na kontenerze kaskaduje na akapity.

#### PUŁAPKA, która zżarła rundę: twardy `!important` gdzieś w pliku

`section-main-product.css` miał **customowe `.product__block--description {font-size:22px!important}`** (sekcja hacków na dole pliku): nasze ustawienie bez `!important` przegrywało, „nic się nie zmieniało". **Reguła:** zanim uznasz, że Twój CSS nie działa, **zgrepuj plik(i) sekcji pod `font-size`/`!important` celujące w ten sam selektor**: w sklepach klientów na dole CSS sekcji jest zwykle blok ręcznych override'ów z `!important`. Fix: Twoja reguła `!important` + **fallback równy dotychczasowej twardej wartości** (żeby „0/auto" nie zmieniło obecnego wyglądu).

#### Dynamiczny przycisk `.shopify-payment-button`: co się da, a co nie

`{{ form | payment_button }}` renderuje markup zarządzany przez Shopify:
- **`.shopify-payment-button__button--unbranded`** = zwykłe „Kup teraz" (desktop / fallback): **w pełni stylowalne** (odwzoruj `.btn--secondary`: kolory `--color-secondary-button*`, `height: var(--buttons-height)`, font, radius, uppercase).
- **Wallety Apple/Google/Shop Pay** (mobile) = renderowane przez Apple/Google: **wnętrza NIE do przestylowania** (wytyczne marek). Można tylko `min-height` + `border-radius` kontenera, żeby pasowały rozmiarem.

Komunikuj klientowi: desktop „Kup teraz" = 1:1 jak ATC; mobile wallet = ten sam rozmiar/kształt, ale marka walleta zostaje.

#### Architektura CSS: 3 reguły, które ratują przed bałaganem

1. **Scope trap:** `section-main-product.css` ładuje się **tylko na stronie produktu**. Globalny selektor (`.btn--secondary`, `.quantity__input`, `a`, breadcrumby) wrzucony tam działa **tylko na produkcie**. Reguły globalne → inline `<style>` w `theme.liquid` (każda strona). Reguły produktowe → CSS sekcji.
2. **Scope per-JEDEN-produkt:** `<body>` ma klasę `{{ template.suffix }}`. Produkt z własnym szablonem `product.<suffix>.json` → scope `.<suffix> .selektor { … }`. Gdy produkt używa domyślnego szablonu (brak suffixu), dodaj do body `product-{{ product.handle }}` jedną linijką w theme.liquid i scope'uj `.product-<handle>`.
3. **Konsolidacja sprzecznych `!important`:** typowy bałagan klienta to ten sam radius ustawiany 2-3× różnie (np. `border-radius:0` w CSS sekcji vs `14px` w global Custom CSS) + **kruchy selektor po ID sekcji** (`#ProductSubmitButton-template--XXXX__main`, pada po przebudowie sekcji). Wygrywa specyficzność/kolejność, efekt nieprzewidywalny (ATC kwadratowy, reszta zaokrąglona). Fix: jeden punkt prawdy, usuń hardcoded-ID, klasowe selektory.

#### Czerwone flagi w „custom CSS" klienta

- **`a { color: … }` globalnie** = wszystkie linki w sklepie. Prawie zawsze miało być per-strona/breadcrumb/opis. **Zawężaj** (`.<suffix> .section--breadcrumb a`, `.<suffix> .product__block--description a`), nie przenoś globalnie.
- **Selektor po hardcoded ID sekcji** (`template--<id>__main`): kruche, zamień na klasę.
- Przy „przenieś mój custom CSS do plików": **najpierw zapytaj, które reguły są globalne, a które per-konkretna-karta**: klienci wrzucają per-stronowe rzeczy do globalnego Custom CSS (stąd globalny `a{}`). Po przeniesieniu **przypomnij o usunięciu ich ze starego Custom CSS** (inaczej duplikat/powrót buga).

#### Border/radius mediów + konfigurowalność przez Theme Editor

Ramka mediów = section settings (`media_border_enabled/color/width/radius`) + scoped `<style>` w sekcji na `.section-{{ section.id }} .product__media-container`. Obejmuje obrazy + wideo + modele (wspólny kontener). Wzorzec: każda wartość, którą klient może chcieć zmienić → setting, nie hardcode.

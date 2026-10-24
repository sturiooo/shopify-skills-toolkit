# Pigułki kategorii na karcie produktu: link „within", aktywny marker, GOTCHA z przycinaniem strzałki

**Wdrożone:** sklep z pluszakami (2026-06, `sections/category-pills.liquid`: pasek wszystkich kategorii z markerem aktywnej; odwzorowanie referencji w nowoczesnym designie).

Pełnoszerokościowy pasek z wieloma pigułkami (kategoriami) na stronie produktu, marker pod aktywną kategorią. **Pełna szerokość + dużo pozycji = sekcja**, nie blok w wąskiej kolumnie info.

#### Link do PIERWSZEGO produktu kategorii w kontekście kolekcji (filtr `within`)

Wymóg: klik w pigułkę → karta pierwszego produktu z tej kategorii (nie strona kolekcji), a na docelowej karcie pasek od razu zaznacza tę kategorię.

```liquid
{%- assign first_prod = col.products.first -%}
{%- if first_prod != blank -%}
  {%- assign target_url = first_prod.url | within: col -%}  {# /collections/handle/products/produkt #}
{%- else -%}
  {%- assign target_url = col.url -%}  {# fallback: pusta kolekcja → strona kolekcji #}
{%- endif -%}
```

`url | within: collection` buduje URL produktu w kontekście kolekcji → Shopify ustawia globalny `collection` na docelowej stronie → wykrywanie aktywnej działa samo. **Gotcha wydajność:** `col.products.first` dla każdej z ~19 kolekcji = tyle zapytań przy renderze. Akceptowalne (cache'owane), ale daj setting `click_target` (pierwszy produkt / strona kolekcji) jako wyjście awaryjne.

#### Wykrywanie aktywnej kategorii na stronie produktu

Na `/collections/x/products/y` globalny `collection` jest ustawiony. Aktywna, gdy: `link.current or link.active` **lub** `link.object.handle == collection.handle` (handle match to najpewniejszy backup; `link.active` łapie też ścieżkę-rodzica). Wejście bezpośrednio na `/products/y` → `collection` blank → nic nie jest aktywne (nie da się zgadnąć, zgodne z oczekiwaniem).

#### GOTCHA (krytyczny): `overflow-x: auto` przycina marker pod pigułką

Strzałka/notch pod aktywną pigułką (`::after` z `bottom: -Npx`) **znika / pokazuje się jako cienki pasek**, bo kontener pigułek ma `overflow-x: auto` do przewijania. Per spec CSS: gdy jedna oś ma `auto/scroll`, druga oś **nie może być `visible`** (komputuje się do `auto`) → pionowe przycinanie na krawędzi padding-boxu. Wszystko poniżej pigułki jest obcinane.

**Fix:** zarezerwuj miejsce w `padding-bottom` kontenera scrolla i trzymaj marker w jego granicach (obszar paddingu NIE jest przycinany: scrollport klipuje na zewnętrznej krawędzi paddingu):
```css
.cp-scroll { overflow-x: auto; padding-bottom: 16px; }       /* rezerwa na marker */
.cp-pill--active::after { bottom: -8px; border-top: 7px solid …; }  /* 8+7=15 < 16 → widoczne */
```
Reszta: `scrollbar-width: none` + `::-webkit-scrollbar{display:none}` (ukryty scrollbar), `pointer-events: none` na markerze. Mały JS scrolluje aktywną pigułkę do środka na wejściu (`active.offsetLeft - clientWidth/2 + active.offsetWidth/2`).

#### Pełna szerokość vs zawężona z zaokrąglonymi rogami (wzorzec dwóch trybów kontenera)

Setting `container_style: full | contained`:
- **full:** tło `.cp-bar` na 100%, wewnętrzny scroll trzyma `max-width` + `margin:auto`.
- **contained:** `.cp-bar` dostaje `max-width` + `margin:auto` + `border-radius` + `width: calc(100% - 2*side_margin)` (gutter od krawędzi), scroll `max-width:100%`. **Nie dawaj `overflow:hidden`** na bar dla zaokrąglenia: `border-radius` na tle wystarcza, a `overflow:hidden` ryzykuje ponowne przycięcie markera (children nie sięgają rogów dzięki paddingowi scrolla).

#### Stany hover (kolory przed/po) i border góra/dół sekcji

Osobne settingi `pill_bg/text/border` (przed) i `pill_bg/text/border_hover` (po) → płynna animacja przez `var(--animation-fast)` motywu. Border sekcji: `border_width` (range 0 do 10, **0 = brak**, render warunkowy `{%- if s.border_width > 0 %}`) + `border_color`, na `border-top`/`border-bottom` `.cp-bar`.

#### Łączenie dwóch źródeł danych jedną pętlą renderującą

Źródła „menu (link_list)" i „kolekcje produktu" mają różne obiekty. Zamiast dwóch bloków markupu: w fazie liquid spłaszcz oba do **stringa z separatorami** (`url|||label|||handle|||active|||highlight###...`), potem `split` i jedna pętla renderująca. Mniej duplikacji, spójny markup. (Separator wieloznakowy `|||`/`###` minimalizuje kolizję z treścią; dla treści dowolnej rozważ mniej prawdopodobny separator.)

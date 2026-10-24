# Pakiet customowych sekcji landingu (2026-06, Sleek/FoxEcom, sklep z suplementami dla psów)

**Wdrożone:** cztery nowe samodzielne sekcje + tweaki karty produktu. Wszystkie: self-contained (1 plik: `{% style %}` scoped `.section-{{ section.id }}` + markup + inline `<script>` + `{% schema %}`), pełna konfiguracja (kolory, rozmiary px desktop/mobile, odstępy), animacja wejścia przez IntersectionObserver (klasa `*-anim` dodawana JS-em + `is-in`; bez JS / `prefers-reduced-motion` → treść od razu widoczna), szerokość = motywowy **`<div class="page-width">`**.

#### Nowe sekcje (pliki)
- `sections/customer-stories.liquid`: „Case studies klientów": **slider** kart pionowych (zdjęcie psa 1:1 u góry + etykieta + H3 + treść + opiekun/„opiekun Burka, lat 13" + link do produktu). Silnik = `FoxTheme.Carousel` (jak `featured-reviews`). `slidesPerGroup: 1` (strzałki/autoplay o 1 slajd).
- `sections/ingredients-health.liquid`: „Składniki zdrowia psa": 2 kolumny (lewa = H3+opis+akordeon składników, prawa = zdjęcie + badge na dolnej krawędzi). Akordeon = **natywny `<details>/<summary>`** + `icon-plus-toggle` PO PRAWEJ + maks 1 otwarta (`<details name=...>` + JS fallback). Zdjęcie **sticky** przy scrollu na desktopie (opcja).
- `sections/dosage-steps.liquid`: „Jak dawkować (kroki)": **pozioma oś** numerowanych kółek (desktop) / **pionowy timeline** (mobile). Animacja: kółka wypełniają się empty→full + linia rysuje się (scaleX, desktop), stagger.
- `sections/bundle-offer.liquid`: „Pakiet produktów": 3 kafelki produktów z „+" + zielony box CTA. Auto-oszczędność (suma cen kafelków vs cena bundla → przekreślona cena). Przycisk dodaje bundle i **przechodzi do koszyka**.
- `sections/science-backed.liquid`: „Oparte na nauce": kwadratowe kafelki składników (3 kol), nazwa+sprostowanie+opis+link do źródła (animowane podkreślenie) + zdjęcie jako **dolny panel** kafelka + podpis sekcji.

#### GOTCHA #1 (krytyczny): custom element jest `display: inline` → padding/tło/szerokość NIE działają
`<customer-stories-slider>` (i każdy nieznany tag) domyślnie `display: inline`. Skutki: `padding-bottom` na mobile **nie rezerwuje miejsca** (strzałki `bottom:0` nachodzą na kartę), `background`/szerokość się nie malują. **Fix: `display: block`** na elemencie (jak `featured-reviews` ma `.fr-slider { display:block }`). Ten sam objaw dla sekcji-wrappera będącego custom elementem (tło z ustawienia „nie działa").

#### GOTCHA #2: parytet szerokości na mobile = używaj motywowego `.page-width`, nie własnego wrappera
Własny `.x-wrap { max-width: var(--page-width); padding-inline: var(--page-padding,1.5rem) }` wyglądał WĘŻEJ niż reszta sklepu. Motyw nie stosuje `max-width` na `.page-width`, centruje przez **ogromny `--page-padding`** (`max(13.5rem, 50vw - --page-width/2)` na dużych ekranach; `1.5rem` na mobile; def. w `theme.css` ~l.164/178/217). Wzorzec porównawczy: `sections/product-purpose.liquid` używa `<div class="page-width">`. **Fix: wszystkie sekcje → `<div class="page-width">`** (usunąć własne max-width/padding wrappery).

#### GOTCHA #3: płynny akordeon: co działa, a co nie
Próby (w kolejności): (a) natywne `<details>` + `@keyframes` fade na treści: działa, prosty fade, instant height; (b) WAAPI `element.animate` na `height` → **„mini zacięcie/lag"** (layout co klatkę + `scrollHeight` reflow + jednoklatkowy błysk); (c) `grid-template-rows: 0fr↔1fr`, płynne, ale **wymaga aby treść była zawsze w layoucie**, a natywny `<details>` chowa treść gdy zamknięty (UA) → **bug: treść widoczna przy zwiniętej zakładce**. **Wniosek/finał: natywne `<details>/<summary>` + prosty fade** (niezawodne, zwija się przez przeglądarkę, działa bez JS). Grid-rows wymagałoby porzucenia `<details>` (div+button+`role`), niewarte.

#### GOTCHA #4: selektor „ten sam element" vs „potomek"
Bug 50/50 w ingredients: klasa `ing--media-right` była NA tym samym `<div>` co `ing-grid`, a selektor `.ing--media-right .ing-grid` (ze spacją = potomek) nigdy nie trafiał → `grid-template-columns` się nie aplikował (został 1 kolumna). **Fix: `.ing-grid.ing--media-right`** (bez spacji = ten sam element). Reguły `order` na DZIECIACH (`.ing--media-left .ing-content`) były OK, bo dziecko faktycznie jest potomkiem.

#### Wzorce wielokrotnego użytku z tej sesji
- **Przycisk „jak w motywie":** `class="btn btn--primary|secondary|underline"` (ATC w `buy-buttons.liquid` = `product-form__submit btn btn--primary`). Własny override bez `!important` dla `font-size`/`border-radius` przez `.section-{{id}} .moja-klasa` (specyficzność 0,2,0 bije `.btn` 0,1,0); kolory wymagają `!important`. Pełne opcjonalne nadpisanie koloru: `{% if s.x != blank %}…!important{% endif %}` (puste = styl motywu).
- **Dodaj-do-koszyka „idź do koszyka" bez AJAX:** zwykły `<form action="{{ routes.cart_add_url }}" method="post">` z `<input name="id">` + `<input name="return_to" value="{{ routes.cart_url }}">`. Natywny POST → Shopify dodaje i przekierowuje do koszyka. Działa mimo `cartType=page` (to NIE jest `is='product-form'`, więc theme JS nie przejmuje). Wariant AJAX (cichy, bez nawigacji) = wzorzec z bloku komplementarnego (`fetch routes.cart_add_url` + `cart:grouped-sections` + `FoxTheme.pubsub` `cartUpdate` + `cart-drawer.show()`).
- **Stagger animacji:** `style="--i: {{ forloop.index0 }}"` na elemencie + `transition-delay: calc(var(--i, 0) * 0.1s)` (czytelniejsze niż `:nth-child` delays).
- **Oś czasu: linia łącząca przez gap siatki:** `::before` linii rozciągnięty o `calc(var(--gap) / -2)` z każdej strony (sąsiednie segmenty spotykają się w środku przerwy = ciągła linia), `:first-child{left:50%}` / `:last-child{right:50%}` przycina na środku kółka. Pozycja na środku kółka = `calc(var(--num-size)/2)` (działa dla każdej wielkości).
- **Kółko wypełnia się empty→full:** stan spoczynkowy = pełny (`background: fill; color: on-fill`); `.anim` ustawia `background: transparent; color: border-color`; `.is-in` wraca do pełnego (transition `background-color`/`color`).
- **Tytuł „małe litery, pierwsza wielka":** CSS `text-transform: lowercase` + `::first-letter { text-transform: uppercase }` (nie psuje danych, w przeciwieństwie do Liquid `capitalize`).
- **Kwadratowy kafelek tekstowy + dolny panel zdjęcia (bleed):** karta `aspect-ratio: 1/1; overflow: hidden; padding: var(--pad)`; zdjęcie `margin-top:auto; margin-inline/bottom: calc(var(--pad)*-1); width: calc(100% + var(--pad)*2); aspect-ratio: <panel>` → zdjęcie wypełnia dół do krawędzi, rogi przycięte do radiusu karty.
- **`<details name="...">` = natywny „exclusive accordion"** (jedna otwarta) w nowych przeglądarkach + JS fallback (`toggle` → zamknij pozostałe) dla starszych.

#### Tweaki karty produktu (przy okazji)
- `sections/main-product.liquid`: grupa „Obramowanie przycisków i ilości", 3 kolory (puste=bez zmian) scoped `<style>` z `!important` na `.product-form__submit` (ATC), `.shopify-payment-button__button` (Kup teraz), `.quantity` (selektor ilości).
- `snippets/product-information-blocks.liquid` (blok `complementary`): usunięta ikona koszyka z przycisku (`cmp_btn_inner` = sam tekst).
- Blok `collapsible_tab` (składany rząd) **już** ma w schemacie `tab_title_size_desktop/mobile` + `tab_content_size_desktop/mobile` (rem, 0=domyślne), renderowane scoped `#CollapsibleTab-{{block.id}}` z `!important`.

# Motyw Horizon: tło sekcji i efekt grain (sklep z biżuterią)

Motyw **Horizon** (Online Store 2.0,
web components, `content_for 'blocks'`, color schemes, `render 'media'`).

## Architektura sekcji w Horizon (wzorzec tła)
- Tło sekcji to `<img>` (klasa `image-background` / `image-background-fixed`
  lub własna) wewnątrz wrappera tła:
  - `.content-box__background-media` (często z `.with-overlay`)
  - albo bare `.with-overlay` (np. dynamic-grid)
- **Treść (teksty/przyciski) to OSOBNE rodzeństwo** wrappera tła
  (np. `.placement-grid`, `.dynamic-grid`, `.prose`). Dlatego cokolwiek
  włożysz do wrappera tła jest zawsze POD treścią.
- `render 'media'` **przyjmuje `class:`** i przekłada ją na `<img>`
  (potwierdzone: `class: 'image-background'` itp.). Można tak dokleić klasę.
- Sekcje mają w schemacie `"class": "shopify-section--<nazwa>"`, używaj tego do scope'owania CSS.
- **Media bloków (slajdy slidera, kafelki gridu) są w plikach bloków**, nie w
  pliku sekcji. Do nich trzeba edytować `blocks/*.liquid`, nie `sections/*.liquid`.

## Efekt „grain" (ziarno): dwa mechanizmy, NIE mylić ich
Snippet `snippets/premium-grain.liquid`, renderowany w `layout/theme.liquid`.

1. **Prostokątna warstwa** `.premium-grain-layer`: dla PEŁNYCH zdjęć tła
   (banery, slider, karty kolekcji). Wstawiamy `<div class="premium-grain-layer">`
   jako dziecko wrappera tła. Pseudo-niezależna (osobny element).
2. **Filtr przycięty do alfa** `#premium-grain-cutout` (`filter: url(...)`,
   `feComposite operator="in"`), dla produktów na PRZEZROCZYSTYM tle PNG
   (kafelki). Ziarno tylko na nieprzezroczystych pikselach; wycięte tło czyste.
   To ta sama receptura co istniejący `product-grain.liquid` (ziarno na produkcie).

Receptura szumu wspólna: `feTurbulence type=fractalNoise numOctaves=2`,
`feColorMatrix saturate 0`, `seed=7`.

## Najważniejsze pułapki (każda kosztowała czas)

1. **SVG jako `background-image` MUSI mieć `width`/`height`.**
   `<svg>` bez wymiarów + `<rect width='100%'>` = render 0×0 = **ziarno
   niewidoczne**. To był główny bug. Daj `<svg width='200' height='200'>`,
   a kafelkowanie steruj przez `background-size`.

2. **`.with-overlay` ma już własny pseudo-element** (overlay przez `--overlay`).
   NIE dawaj tam grainu przez `::after`/`::before` (kolizja). Użyj
   **dedykowanego elementu** `.premium-grain-layer`.

3. **Warstwa `position:absolute` potrzebuje pozycjonowanego przodka.**
   Nie każdy wrapper tła ma `position:relative` (np. karty kolekcji → ziarno
   „uciekało", było niewidoczne). Rozwiązanie bez ruszania motywu:
   ```css
   .content-box__background-media:has(> .premium-grain-layer),
   .with-overlay:has(> .premium-grain-layer) { position: relative; isolation: isolate; }
   ```
   `:has()` celuje tylko tam, gdzie faktycznie jest nasza warstwa.

4. **Shopify `range` musi mieć ≥3 kroki.** `(max-min)/step >= 3`.
   Np. min:1 max:2 step:1 → BŁĄD przy zapisie. Dla 1-2 użyj **`select`**.

5. **`config/settings_schema.json` to TABLICA grup.** Nowe grupy wklejasz
   JAKO ELEMENTY tablicy: po poprzedniej grupie `},` (przecinek!), a przed
   zamykającym `]` ostatnia grupa BEZ przecinka. Zła pozycja (po `]`) = niepoprawny JSON.

6. **Bramkuj grain na realny obraz.** Warstwę wstawiaj tylko w gałęzi Liquid
   z prawdziwym plikiem graficznym, nie placeholder, nie wideo, nie jednolity
   kolor z palety. (np. `if section.settings.image != blank` i `background_video == blank`.)

7. **Strefy zero-tolerancji** (NIE grain): zdjęcia produktów na listingach,
   galeria produktu, „Inspiracje", logo/ikony/SVG menu. Karty KOLEKCJI
   (okładki) to co innego niż karty PRODUKTÓW, okładkom grain wolno.

## Wzorce, które działają dobrze
- **Warstwa jako dziecko wrappera tła, rodzeństwo treści** → zawsze pod treścią,
  `z-index` lokalny nie przebija treści. `pointer-events:none` na warstwie.
- **Sterowanie zmiennymi CSS**: `--grain-opacity`, `--grain-size`, `--grain-blend`,
  z defaultami nadpisywanymi z Theme settings; override per sekcja w Custom CSS.
- **Dwa poziomy włączania**:
  - globalny master w Theme settings (CSS kill-switch `display:none`/`filter:none`),
  - **per sekcja/blok** checkbox (`section_grain`) bramkujący render warstwy.
- **Mix-blend `overlay`** dla ziarna nie szarzy obrazu (50% szarości = neutralne),
  daje teksturę. `soft-light` = łagodniej, `normal` = mocniej.
- Animacje hover: własny CSS (np. `scale(1.05)`, podkreślenie `scaleX(0→1)`)
  zamiast polegać na globalnych flagach motywu (`image_hover_animation`);
  daje przewidywalny efekt niezależny od ustawień. Dodaj `prefers-reduced-motion`.
- Podkreślenie tekstu o szerokości TEKSTU (nie całego kafla): owiń napis w
  `inline-block` span i `::after` na nim.

## Sprawdzanie schematu (rób to po każdej edycji `{% schema %}`)
```bash
python3 -c "import re,json,sys; s=open('plik.liquid',encoding='utf-8').read(); \
d=json.loads(re.search(r'{% schema %}(.*?){% endschema %}', s, re.S).group(1)); \
print('OK'); [print('range',x['id'],int((x['max']-x['min'])/x['step']),'kroków') \
for x in d['settings'] if x.get('type')=='range']"
```

## Pliki efektu grain (stan po wdrożeniu)
- `snippets/premium-grain.liquid`: warstwa + filtr alfa + utility `.premium-grain` + zmienne + master switch
- `snippets/product-grain.liquid`: osobny istniejący feature (ziarno na produkcie), NIE ruszać
- `layout/theme.liquid`: `{%- render 'premium-grain' -%}` w `<head>`
- Sekcje z grainem: slideshow (blok `_slideshow-image-slide`), `text-with-fixed-background`,
  `dynamic-grid` (tło) + `image-with-caption` (kafelki, filtr alfa), `products-with-image`
  (strona ze zdjęciem), `image-with-text-overlay`, `hot-spots`, `collection-card`,
  nowa sekcja własna (lista salonów).
- `config/settings_schema.json`: grupy „Efekt ziarna” i „(Premium grain)”.

## Nowe sekcje (np. lista salonów)
- Buduj w konwencji motywu: `.color-scheme`, `.container`/`.section-spacing`,
  `content-box` + `content-box__background-media with-overlay`, `render 'heading'`/`'subheading'`,
  bloki lokalne w schemacie (`for block in section.blocks`).
- Subheading mniejszy od heading: `render 'subheading'` (osobny snippet, mniejszy font).
- Daj preset z gotowymi blokami, opcje koloru tła, odstępów, efektów hover, grain toggle.

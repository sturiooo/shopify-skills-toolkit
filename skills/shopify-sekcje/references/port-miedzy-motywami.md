# Przenoszenie sekcji 1:1 między motywami: pełny playbook (2026-08-19/20, Release → Stretch)

Zadanie: przenieść `sections/testimonials.liquid` ze sklepu klienta A (motyw **Release**, Clean Canvas)
do sklepu B (motyw **Stretch**, Maestrooo), zachowując wygląd i dokładając kolorystykę docelową.
Sekcja „nie renderowała się" **z czterech niezależnych powodów naraz**, każdy dawał identyczny objaw.
To jest kolejność diagnozy, od najbardziej milczącego.

### Warstwa 1: globalne obiekty JS motywu ŹRÓDŁOWEGO

Przeniesiony `card-slider.js` wołał `DeviceDetector.isMobile()` (globalny obiekt motywu Release). W Stretchu nie
istnieje → **`ReferenceError` w konstruktorze custom elementu** → element nigdy nie zostaje
„upgrade'owany", karuzela pusta. **Zero błędów w Liquid, zero w Theme Check.**

Fix: shim w `assets/` odtwarzający **tylko realnie używane** metody (u nas 1 metoda, próg 750 px
skopiowany 1:1 ze źródła). Kolejność `defer` ma znaczenie: `swiper-bundle` → shim → `card-slider`.

**Reguła:** przed portem zgrepuj przenoszony JS pod kątem identyfikatorów pisanych wielką literą
(`/\b[A-Z][A-Za-z]+\./`) i sprawdź, które z nich istnieją w motywie docelowym.

### Warstwa 2: `"class"` w schemacie

Cały przeniesiony arkusz był scope'owany pod `.section-testimonials`. Bez
`"class": "section-testimonials"` w `{% schema %}` **żadna reguła nie wchodzi**, markup jest,
CSS jest, a wygląda jak goły HTML.

### Warstwa 3: KOLIZJE NAZW KLAS z motywem docelowym (najczęstsza przy portach)

Oba motywy miały sekcję opinii i **te same nazwy klas**:

| Klasa | Co robi motyw docelowy | Skutek |
|---|---|---|
| `.testimonials__content` | `:not(.is-selected){opacity:0;visibility:hidden}` + `grid-area:1/-1` | element **ukryty** (mój nigdy nie dostaje `.is-selected`), szerokość 15001 px |
| `.container` | Stretch centruje `margin-inline: max(...)`; Release `padding + max-width` | inny layout niż w źródle |
| `.icon` | `width: var(--icon-max-width, auto)` | kasuje `width="1em"` na przeniesionych SVG (gwiazdki) |

**Fix: przemianuj kolidujące klasy na własny prefiks** (`.prt-*`), w markupie ORAZ w przeniesionym
CSS, jednym skryptem. Utility, które w B nie istnieje (`.text-current`, `.small-down-hide`),
dopisz w `{% style %}` sekcji.

**Automatyczny skan kolizji** (rób ZAWSZE przy porcie):
```python
# klasy z markupu sekcji (przed {% schema %}) vs assets/*.css motywu docelowego
used = {tok for m in re.finditer(r'class="([^"]*)"', src) for tok in m.group(1).split()
        if re.fullmatch(r'[a-zA-Z][\w-]*', tok)}
for p in glob.glob('assets/*.css'):          # z WYŁĄCZENIEM plików portu
    css = re.sub(r'/\*.*?\*/', '', open(p).read(), flags=re.S)
    for c in used:
        if re.search(r'\.' + re.escape(c) + r'(?![\w-])', css): print('KOLIZJA', c, p)
```

### Warstwa 4: INNA BAZA `rem`: nic się nie „psuje", tylko wszystko jest za duże

**To jest pułapka, której nie widać w kodzie.** Release ma
`html { font-size: calc(var(--font-body-scale) * 62.5%) }` → **1rem = 10px**.
Stretch nie ma override'u → **1rem = 16px**. Każda wartość rem renderuje się **1,6×**:
padding karty 24 → 86 px, `min-height` 194 → 310 px. Sekcja jest widoczna, więc łatwo uznać, że
„działa", a jest rozdęta.

**Fix bez ręcznego przeliczania**, odtwórz bazę źródła lokalnie:
```liquid
#shopify-section-{{ section.id }} { --prt-rem: 0.625rem; }   /* = 10px */
```
i zamień w przeniesionym CSS każde `Nrem` → `calc(N * var(--prt-rem))`:
```python
re.sub(r'(?<![\w.])(-?\d*\.?\d+)rem(?![\w-])', lambda m: f'calc({m.group(1)} * var(--prt-rem))', css)
```
**Trzy warunki, żeby to było bezpieczne:**
1. **Breakpointy `@media` ZOSTAJĄ w px**, media query nie widzi custom properties. Sprawdź przed
   konwersją (`@media` z `rem` = trzeba je pominąć; u nas wszystkie były w px).
2. **Zmienne emitowane z ustawień sekcji licz przez tę samą bazę** (`calc({{ x }} * var(--prt-rem))`),
   inaczej CSS i schema pracują w dwóch skalach.
3. Po konwersji asercja `css.count('(') == css.count(')')`.

**Zawsze sprawdzaj `html { font-size }` w OBU motywach przed portem**, to jedna linia grepa,
a decyduje o skali całej sekcji.

### Warstwa 5 (osobna): wartości opcji schematu vs selektory przeniesionego CSS

Wpisałem `image_position` jako `left`/`right`, a CSS oczekiwał `image-start`/`image-end` →
`position--left` nie trafiał w nic, więc **w obu układach ze zdjęciem pozycja obrazu nie działała
w ogóle**, bez żadnego błędu. Weryfikacja: `grep -oE '\.position--[a-z-]+'` w CSS vs `options[].value`.

**Domyślne wartości bierz z REALNYCH ustawień sekcji w szablonie źródłowym** (`templates/*.json`),
nie z `default` w schemacie, klient prawie zawsze je nadpisał. U nas różnica: `spacing_inner`
default 2, a w szablonie 2; ale `spacing_top/bottom` schema 2 vs szablon 6.

### Weryfikacja portu musi być POMIAREM, nie oglądaniem

„Widzę sekcję" nie wyklucza skali 1,6×. Porównuj konkretne piksele z wartościami wyliczonymi ze źródła:
```js
const b = getComputedStyle(document.querySelector('.testimonial__body'));
({padding: b.padding, minHeight: b.minHeight})   // musi = padding/min-height ze źródła w px
```
Do tego: `swiper-initialized` na kontenerze, liczba slajdów, `overflow` przodków,
`document.documentElement.scrollWidth > clientWidth` (brak poziomego scrolla strony).

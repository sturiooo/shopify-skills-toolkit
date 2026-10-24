# Globalny design kart produktów: rewrite `snippets/card-product.liquid`

**Wdrożone:** sklep z obuwiem (2026-05, motyw FoxEcom/Foxify, standalone rewrite).

---

#### Strategia: rewrite snippetu zamiast override CSS

`snippets/card-product.liquid` jest renderowany wszędzie: collection grid, related products, search, featured collections. Jeden plik = zmiana globalna. Zamiast nadpisywać style motywu, piszemy od zera nową strukturę HTML z klasami `cst-card`.

**Co usunęliśmy z oryginalnego snippetu:**
- Quick Add / Quick View (motyw ma własną infrastrukturę, ale klient nie chciał)
- `{% render 'price' %}` → inline Liquid z `| money`
- `{% render 'pcard-color-swatch' %}` → własna implementacja z `variant.featured_image`
- `{% render 'motion-element' %}`, `{% render 'loading-spinner' %}`, `{% render 'icon-cart' %}`: wszystkie theme snippets

**Co zachowaliśmy:**
- Parametry wejściowe: `product`, `image_sizes`, `image_ratio`, `section_index`, `index`, `custom_class`
- Logikę `loading: 'eager'` dla pierwszych kart (performance)
- Judge.me ratings z fallbackiem na Shopify Reviews

---

#### CSS i JS w snippecie bez duplikacji: wzorzec guard + injection

Snippet renderuje się N razy na stronie (np. 8 kart). `<style>` i `<script>` wewnątrz snippetu duplikowałyby się 8×. Rozwiązanie:

**CSS: inject raz przez `document.createElement`:**
```js
if (!document.getElementById('cst-card-styles')) {
  var _cstStyle = document.createElement('style');
  _cstStyle.id = 'cst-card-styles';
  _cstStyle.textContent = '/* wszystkie style */';
  document.head.appendChild(_cstStyle);
}
```
Guard przez `id`: niezależnie ile razy snippet się wyrenderuje, styl trafia do `<head>` tylko raz. Brak FOUC, bo `<script>` jest PRZED HTML karty: style są wstrzyknięte, zanim przeglądarka przetworzy `.cst-card`.

**JS: event delegation + `window._cstCardInited`:**
```js
if (!window._cstCardInited) {
  window._cstCardInited = true;
  document.addEventListener('click', function(e) {
    var swatch = e.target.closest && e.target.closest('.cst-swatch');
    if (!swatch) return;
    // ... obsługa kliknięcia swatcha
  });
  document.addEventListener('mouseover', function(e) { /* hover second image */ });
  document.addEventListener('mouseout',  function(e) { /* przywróć image */ });
}
```
Jeden listener na `document` zamiast N listenerów per karta. Działa też dla kart dodanych dynamicznie (np. przez `<product-recommendations>` AJAX swap).

**Dlaczego `mouseover`/`mouseout` zamiast `mouseenter`/`mouseleave`:**
`mouseenter`/`mouseleave` nie bubblują → nie działają z event delegacją. `mouseover`/`mouseout` bubblują, ale strzelają przy wejściu w każdy child element. Fix: `link.contains(e.relatedTarget)` jako guard: ignoruje przejścia między elementami wewnątrz linka.

```js
document.addEventListener('mouseover', function(e) {
  var link = e.target.closest('.cst-card__img-link');
  if (!link || link.contains(e.relatedTarget)) return; // guard
  // tylko przy wejściu z zewnątrz
});
```

---

#### Obsługa `image_ratio`: modifier class + CSS variable

Sekcje przekazują `image_ratio` (`1/1`, `3/4`, `4/3`, `adapt`). Bez obsługi karty na collection grid mają `height: 280px` i małe zdjęcia.

**Liquid: obsługa `adapt`:**
```liquid
assign img_ratio = image_ratio | default: ''
if img_ratio == 'adapt'
  if featured != blank
    assign img_ratio = featured.aspect_ratio  {# float, np. 0.75, valid CSS aspect-ratio #}
  else
    assign img_ratio = '1'
  endif
endif
```

**HTML: modifier class + inline CSS variable:**
```html
<div
  class="cst-card__img-wrap{% if img_ratio != blank %} cst-card__img-wrap--ratio{% endif %}"
  {% if img_ratio != blank %}style="--cst-ratio: {{ img_ratio }};"{% endif %}
>
```

**CSS: dwa tryby wrappera:**
```css
/* Domyślny (brak image_ratio z sekcji) */
.cst-card__img-wrap { height: 280px; }

/* Z podanym ratio */
.cst-card__img-wrap--ratio { height: auto; aspect-ratio: var(--cst-ratio, 1); }

/* Mobile bez ratio: kwadrat; z ratio: zachowaj podany */
@media (max-width: 767px) {
  .cst-card__img-wrap:not(.cst-card__img-wrap--ratio) { height: auto; aspect-ratio: 1/1; }
}
```

**Gotcha:** `featured_media.aspect_ratio` zwraca float (np. `0.75`), nie stringa `"3/4"`. CSS akceptuje `aspect-ratio: 0.75`: to jest poprawna składnia, równoważna `3/4`.

---

#### Struktura `cst-card`: kolejność elementów w body

```
cst-card
├── cst-card__img-wrap
│   ├── a.cst-card__img-link → img.cst-card__img  (data-current-src, data-second-src)
│   └── span.cst-badge (Sale / Sold out)
└── cst-card__body
    ├── div.cst-swatches → button.cst-swatch × max 5
    ├── a.cst-card__title
    ├── div.cst-rating (tylko gdy rv != blank)
    └── div.cst-price  (margin-top: auto → zawsze na dole)
```

**Gotcha: sold out badge ma inny kolor:** `.cst-badge--soldout { background: #555 }` zamiast pomarańczowego. Priorytet: sold out > sale (warunek `if product.available == false` przed `elsif on_sale`).

# Karty produktów z wariantami kolorystycznymi, hover second image i ratingsami (sekcja product-tabs)

**Wdrożone:** sklep z obuwiem (2026-05, standalone sekcja bez zależności od motywu).

---

#### Wariant → zdjęcie: `variant.featured_image` wymaga konfiguracji w Shopify Admin

`variant.featured_image` (alias: `variant.image`) zwraca `nil`, jeśli zdjęcia nie są formalnie przypisane do wariantów. Samo wgranie zdjęć do produktu NIE wystarczy.

**Wymagana konfiguracja jednorazowa w Shopify Admin:**
1. Products → [produkt] → sekcja Media
2. Kliknij na zdjęcie → "Add to Variants"
3. Zaznacz warianty koloru, które to zdjęcie reprezentuje
4. Powtórz dla każdego zdjęcia

Po tym `variant.featured_image` zwraca właściwy obiekt i można go używać jako thumbnail swatcha i src głównego zdjęcia.

**Liquid pattern dla swatcha z obrazkiem:**
```liquid
{%- assign sw_img = variant.featured_image -%}
<button
  class="cst-swatch"
  {% if sw_img %}
  data-image-url="{{ sw_img | image_url: width: 700 }}"
  data-image-srcset="{{ sw_img | image_url: width: 300 }} 300w, {{ sw_img | image_url: width: 500 }} 500w, {{ sw_img | image_url: width: 700 }} 700w"
  {% endif %}
>
  {%- if sw_img -%}
    <img src="{{ sw_img | image_url: width: 68 }}" width="34" height="34" loading="lazy">
  {%- else -%}
    <span class="cst-swatch__dot"></span>
  {%- endif -%}
</button>
```

**Gotcha:** NIE ustawiaj fallbacku `{% elsif %}` na `product.featured_image`, gdy wariant nie ma zdjęcia: kliknięcie każdego swatcha zmieniałoby główne zdjęcie na ten sam obraz, co jest mylące.

---

#### Second image on hover: wzorzec z data-current-src

Hover pokazuje drugie zdjęcie produktu (`product.images[1]`). Po kliknięciu swatcha hover jest wyłączony, wraca po kliknięciu pierwszego (domyślnego) swatcha.

**Liquid: atrybuty na img:**
```liquid
{%- assign second_image = nil -%}
{%- if product.images.size > 1 -%}
  {%- assign second_image = product.images[1] -%}
{%- endif -%}

{%- assign default_src = featured | image_url: width: 500 -%}
<img
  class="cst-card__img"
  src="{{ default_src }}"
  srcset="{{ featured | image_url: width: 300 }} 300w, {{ featured | image_url: width: 500 }} 500w, {{ featured | image_url: width: 700 }} 700w"
  data-current-src="{{ default_src }}"
  {% if second_image %}data-second-src="{{ second_image | image_url: width: 500 }}"{% endif %}
>
```

**Liquid: marker na domyślnym swatchu:**
```liquid
{% if sw_count == 0 %}data-default-swatch="1"{% endif %}
```

**JS: hover listeners + swatch handler:**
```js
// Hover (w connectedCallback)
this.querySelectorAll('.cst-card__img-link').forEach(link => {
  const card = link.closest('.cst-card');
  const img  = link.querySelector('.cst-card__img');
  if (!img || !img.dataset.secondSrc) return;
  img.dataset.currentSrcset = img.getAttribute('srcset') || '';
  link.addEventListener('mouseenter', () => {
    if (card && card.dataset.swatchChanged) return; // swatch aktywny → brak hover
    img.src = img.dataset.secondSrc;
    img.removeAttribute('srcset');
  });
  link.addEventListener('mouseleave', () => {
    if (card && card.dataset.swatchChanged) return;
    img.src = img.dataset.currentSrc;
    if (img.dataset.currentSrcset) img.setAttribute('srcset', img.dataset.currentSrcset);
  });
});

// Swatch click
_onSwatch(swatch) {
  const card = swatch.closest('.cst-card');
  if (!card) return;
  card.querySelectorAll('.cst-swatch').forEach(s => s.classList.remove('is-active'));
  swatch.classList.add('is-active');

  // Domyślny swatch → przywróć hover; inny → zablokuj hover
  if (swatch.dataset.defaultSwatch) {
    delete card.dataset.swatchChanged;
  } else {
    card.dataset.swatchChanged = '1';
  }

  const imgUrl = swatch.dataset.imageUrl;
  if (imgUrl) {
    const img = card.querySelector('.cst-card__img');
    if (img && img.tagName === 'IMG') {
      img.src = imgUrl;
      const newSrcset = swatch.dataset.imageSrcset || '';
      newSrcset ? img.setAttribute('srcset', newSrcset) : img.removeAttribute('srcset');
      // KLUCZOWE: zaktualizuj data-current-src, żeby mouseleave wracał do wariantu, nie do oryginału
      img.dataset.currentSrc    = imgUrl;
      img.dataset.currentSrcset = newSrcset;
    }
  }
}
```

**Gotcha: kolejność operacji:** `img.dataset.currentSrcset` musi być ustawione w `connectedCallback` PRZED pierwszym `mouseenter`, nie przy okazji hover. Inaczej przy szybkim najechaniu pierwsze `mouseleave` nie znajdzie srcset.

---

#### Judge.me ratings: integracja z fallbackiem na natywne reviews

Judge.me zapisuje oceny w metapolach pod namespace `judgeme`. Natywna apka Shopify Product Reviews używa namespace `reviews`.

**Liquid: odczyt z fallbackiem:**
```liquid
{%- assign rv = product.metafields.judgeme.rating -%}
{%- assign rc = product.metafields.judgeme.reviews_count -%}
{%- if rv == blank -%}
  {%- assign rv = product.metafields.reviews.rating.value -%}
  {%- assign rc = product.metafields.reviews.rating_count.value -%}
{%- endif -%}

{%- if rv != blank -%}
  {%- assign rv_int = rv | round -%}
{%- elsif show_empty_stars -%}
  {%- assign rv_int = 0 -%}
{%- endif -%}

{%- if rv != blank or show_empty_stars -%}
  <div class="cst-rating">
    {%- for i in (1..5) -%}
      <span class="cst-star{% if i <= rv_int %} is-filled{% endif %}">★</span>
    {%- endfor -%}
    {%- if rc != blank and rc != '0' -%}
      <span class="cst-rating__count">({{ rc }})</span>
    {%- endif -%}
  </div>
{%- endif -%}
```

**Schemat settings:**
```json
{ "type": "checkbox", "id": "show_ratings", "label": "Pokaż oceny", "default": true,
  "info": "Obsługuje Judge.me oraz Shopify Product Reviews." },
{ "type": "checkbox", "id": "show_empty_stars", "label": "Pokaż puste gwiazdki gdy brak opinii", "default": false,
  "info": "5 pustych gwiazdek zamiast nic gdy produkt nie ma recenzji." }
```

**Gotcha:** `rc != '0'` (string comparison) zamiast `rc != 0`: Judge.me może zwracać liczbę jako string. Ukryj `(0)` przy pustych gwiazdkach.

---

#### Mobile 2-kolumnowy grid z inline controls

Układ z referencji: pill switcher + "Shop all →" w jednej linii, siatka 2×N kart.

**Kluczowe CSS mobile:**
```css
@media (max-width: 767px) {
  .cst-section .cst-controls {
    flex-wrap: nowrap;   /* NIE zawijaj: switcher i shop-all w jednej linii */
    align-items: center;
    gap: 12px;
  }
  .cst-section .cst-switcher  { flex-shrink: 0; }
  .cst-section .cst-shop-all  {
    display: block;      /* pokazuj na mobile, nie chowaj */
    flex-shrink: 0;
    font-size: 13px;
    white-space: nowrap;
  }
  .cst-section .cst-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  .cst-section .cst-card__img-wrap {
    height: auto;
    aspect-ratio: 1 / 1; /* kwadrat zamiast fixed height, responsywne */
    padding: 12px;
  }
  .cst-section .cst-swatch   { width: 26px; height: 26px; } /* mniejsze na mobile */
  .cst-section .cst-swatches { gap: 4px; }
  .cst-section .cst-card__body { padding: 8px 10px 14px; gap: 6px; }
}
```

**Gotcha: `display: none` na shop-all:** Nie dodawaj `display: none` do `.cst-shop-all` w mobile styles, jeśli referencja pokazuje go widocznego. Typowy błąd: desktop schował go, bo był zbędny → mobile też go chował przez kaskadę.

**Gotcha: `aspect-ratio` vs fixed height:** `height: 180px` przy 2 kolumnach daje inne proporcje na różnych ekranach. `aspect-ratio: 1/1` zawsze daje kwadrat niezależnie od szerokości: lepiej dla spójności UI.

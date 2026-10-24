# Blok produktów komplementarnych: redesign + render z metafielda (Sleek/FoxEcom)

**Wdrożone:** sklep z suplementami dla psów (2026-06). Blok `complementary` w `snippets/product-information-blocks.liquid` (`when 'complementary'`) + settingi w `sections/main-product.liquid`. Przeprojektowany na pionowe karty (zdjęcie w ramce → nazwa h3 → cena → przycisk „KUP TERAZ: {cena}") z konfigurowalnością wszystkiego.

#### GOTCHA #1 (krytyczny): `product-recommendations.js` KASUJE cały blok, gdy brak `.product-card`

`assets/product-recommendations.js` po AJAX-owym fetchu rekomendacji robi:
```js
if (recommendations.querySelector('.product-card')) { /* ok */ }
else { this.closest('.product__block').remove(); }  // ← usuwa CAŁY blok z DOM
```
Custom karta rekomendacji **MUSI** mieć klasę `product-card`, inaczej blok znika. Symptom: „dodałem swój design i blok w ogóle się nie pokazuje".

#### GOTCHA #2: rekomendacje przez API filtrują produkty z koszyka → produkt znika po dodaniu

`/recommendations/products?intent=complementary` (AJAX) **wyklucza produkty już w koszyku**. Symptom: klient dodaje komplementarny do koszyka, wraca na produkt → produkt zniknął z bloku. **Fix: renderuj server-side z metafielda Search & Discovery** zamiast API:
```liquid
{%- assign cmp_products = product.metafields["shopify--discovery--product_recommendation"]["complementary_products"].value -%}
{%- for product in cmp_products limit: cmp_limit -%} … {%- endfor -%}
```
`.value` to lista `product_reference` → iteracja daje obiekty produktów. Zawsze widoczne, bez AJAX, bez `product-recommendations.js`. Zachowaj wrapper `<div class="complementary-products">` (CSS celuje w `.complementary-products .f-price` itd.). Wymaga skonfigurowanych Complementary products w aplikacji Search & Discovery.

#### GOTCHA #3: `cartType === 'page'` łamie AJAX add-to-cart (FoxEcom)

Natywny `ProductForm` w `theme.js` (~linia 2487): `if (... FoxTheme.settings.cartType === 'page') return;` PRZED `event.preventDefault()` → przy cartType=page formularz robi **pełny POST na /cart** (nawigacja, nie AJAX). Dla custom przycisku „dodaj do koszyka bez przenoszenia":
- **NIE używaj `is: 'product-form'`** (odpaliłby natywny handler).
- Własny `submit` listener (capture) → `fetch(FoxTheme.routes.cart_add_url)`. Replikuj natywny flow: zbierz sekcje `document.documentElement.dispatchEvent(new CustomEvent('cart:grouped-sections', {bubbles:true, detail:{sections:[]}}))`, dołącz `sections` + `sections_url` do FormData, po dodaniu `cartJson.sections = added.sections`, `FoxTheme.pubsub.publish(FoxTheme.pubsub.PUB_SUB_EVENTS.cartUpdate, {cart: cartJson})` → header/koszyk odświeża się bez reload. Fallback: gdy JS padnie, formularz robi zwykły POST (degradacja).

#### Slider: jeden produkt = jeden slide + `slidesPerView` przez breakpoint (desktop/mobile osobno)

`complementary-product-slider.js` (FoxTheme.Carousel/Swiper). Zamiast grupować po N w siatce, **każdy produkt to osobny `.swiper-slide`**, a liczba widocznych = `slidesPerView`/`slidesPerGroup` z `data-per-desktop`/`data-per-mobile` + `breakpoints: { 768: {...} }`. Mobile default 1, desktop 2. To daje prawdziwy swipe-per-1 na mobile.

#### Strzałki nawigacji na mobile = overlay po bokach na środku zdjęcia (pozycja z JS)

Nagłówek bloku ma zmienną wysokość (tytuł + opis), więc czysty CSS nie trafi w środek zdjęcia. JS liczy środek pierwszego `.cmp-card__media` względem slidera i zapisuje do `--cmp-nav-top`; CSS na mobile: `.cmp-nav { position:absolute; top: var(--cmp-nav-top); left:0; right:0; justify-content:space-between }`. Przeliczane na `resize` + `ResizeObserver`. Kontener `pointer-events:none`, przyciski `auto` (swipe między strzałkami działa). Desktop bez zmian (media query tylko <768, JS usuwa zmienną na desktopie).

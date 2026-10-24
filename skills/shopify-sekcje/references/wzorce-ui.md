# Wzorce UI z tej sesji: reużywalne (2026-06)

### Motyw Airwave (Shopify, blokowy): szerokość i tło zdjęć (sklep z herbatą)
- **Szerokość sekcji „Normal"** = klasa `.wrapper { max-width: var(--content-max) }`. `--content-max` zdefiniowany TYLKO w `assets/theme.css` (1100px do 1399px / `80vw` od 1400px). Zmiana globalnej szerokości (np. na 1660px) = override `--content-max` w `<head>` `theme.liquid` (po `theme.css`, więc wygrywa), `:root{--content-max:1660px}` + ten sam w `@media(min-width:1400px)`. `.wrapper` to też baza `.grid-container.wrapper` (kolekcje dziedziczą).
- Opcje width sekcji (np. „Multi column"/Text columns with images): `wrapper`=Normal (max 1660), `wrapper--narrow`=670, **`wrapper--full-padded`=brak max-width + `padding:0 var(--outer)`** (pełna szerokość z marginesem), `wrapper--full`=pełna bez paddingu. Wzorzec dodania przełącznika do innej sekcji: setting `select width` z tymi wartościami + `class="… {{ section.settings.width }}"`.
- **Tło zdjęć produktów (PNG bez tła) = jednolity kolor:** CSS nie wykrywa przezroczystości: ustaw tło pod zdjęciem (widać tylko gdzie obraz transparentny). W Airwave: `.product-item__image:not(.image--empty){background:var(--bg)}` ORAZ warstwa hover `.product-item__bg__under{background:var(--bg)}`, **trzeba nadpisać OBIE** (+ galeria PDP `.product__photo`) z `!important` (specyficzność `:not()` = 0,2,0). Dodaj ustawienie motywu (`settings.product_image_bg`, grupa Product grid) i steruj z panelu.
- **Wyłączenie globalnego efektu w JEDNEJ sekcji:** scoped reset `#Section--{{ section.id }} .x { … !important }` (wyższa specyficzność + `!important` bije globalny override z `theme.liquid`). Plus checkbox per sekcja.
- **Zwężenie pojedynczej sekcji (np. Testimonials do 560px):** suwak `range` + scoped `[data-section-id="{{ section.id }}"] .wrapper--full-padded { max-width: Npx; margin-inline:auto }`.

### Przypięty „wyróżniony" pierwszy kafelek + slider reszty (customer-stories)
Wymóg: na desktopie nadal N widocznych, ale PIERWSZY zawsze widoczny (nie przewija się), z odrębnym stylem.
- Wyjmij pierwszy blok z karuzeli: `{%- for block in section.blocks limit: 1 -%}` → osobny `<article class="cs-card cs-featured">` (poza Swiperem). Reszta: `{%- for block in section.blocks offset: 1 -%}` w Swiperze.
- Slider dostaje `data-per-desktop = per_d - 1` (featured + reszta = per_d widocznych). Layout: `.cs-layout{display:flex;gap}` → `.cs-featured{flex:0 0 calc((100% - (per_d-1)*gap)/per_d)}` + `.cs-slider-col{flex:1 1 0;min-width:0}`. Mobile: `flex-direction:column`.
- Odrębny styl: modyfikator `.cs-featured` (własne tło/ramka przez osobne vars + fallback do zwykłych) + badge `position:absolute`.
- **GOTCHA strzałek nawigacji:** strzałki muszą zostać WEWNĄTRZ custom-elementu slidera (JS robi `this.querySelector('.swiper-button-prev')`). Jeśli kotwiczą się do slidera (`position:relative` na nim), po dodaniu featured ustawiają się względem prawej kolumny („przesunięte przez kafelek"). Fix: zdejmij `position` ze slidera, daj `position:relative` na `.cs-layout` (pełna szerokość) → strzałki `top:-Xrem; right:0` wracają nad całą sekcję. Animację wejścia (transform) przepnij też na `.cs-layout` (transform tworzy containing block → inaczej miganie kotwicy strzałek).

### Slider mobilny z kropkami + autoplay BEZ Swipera (science-backed)
Gdy desktop ma złożony layout (grid/sticky/flip) i nie chcesz konfliktu ze Swiperem, zrób mobilny slider na **CSS scroll-snap + własny JS**:
- CSS mobile: kontener `display:flex; overflow-x:auto; scroll-snap-type:x mandatory; scrollbar ukryty`; kafelek `flex:0 0 82%; scroll-snap-align:center`.
- Markup: pusty `<div class="x-dots">` (renderowany, widoczny tylko mobile + gdy włączone).
- JS: zbuduj kropki (1/kafelek), `IntersectionObserver`/scroll→aktywna kropka, klik→`scrollIntoView`/`scrollTo`, autoplay `setInterval` (pauza na `pointerdown`/`mouseenter`, respektuj `prefers-reduced-motion`), `matchMedia('(max-width:767.98px)')` włącza/wyłącza. Kolory kropek = ustawienia (`--x-dot`/`--x-dot-active`).

### FAQ: kategorie jako swipe-slider na mobile
Jeśli już jest `overflow-x:auto; flex-wrap:nowrap` → dołóż tylko `scroll-snap-type:x proximity` na kontenerze + `scroll-snap-align:start` na pigułkach (bez JS).

### Opinie / case studies: NIE dodawaj fake schema.org Review
Ręcznie wpisywane „opinie"/„case studies" w panelu (nie zweryfikowane), **nie oznaczaj `schema.org/Review`/`AggregateRating`** (self-serving → łamie wytyczne Google, ryzyko kary). FAQ z kategoriami, `FAQPage` JSON-LD jest OK, bo treść jest realna i widoczna server-side.

# Nowa sekcja slidera opinii od zera (samodzielna, FoxEcom/Sleek)

**Wdrożone:** sklep z suplementami dla psów (2026-06, `sections/featured-reviews.liquid`, „Wyróżnione opinie": nadtytuł + H2 + podtytuł + ręczny slider kart opinii, bloki dodawane ręcznie). Wzorzec na **dowolną nową sekcję ze sliderem** budowaną od zera w jednym pliku do wklejenia w Theme Editor.

#### GOTCHA #1 (kosztował 2 rundy „nie działa rozmiar"): rich text renderuje `<p>` → font-size z wrappera bywa zjadany

Pole `richtext` (i `inline_richtext`) wypisuje treść w `<p>`. Gdy ustawisz `font-size` tylko na **diviu-wrapperze** (`.fr-card__text { font-size: var(--x) }`), `<p>` powinien dziedziczyć, ale w praktyce **nie zmienia się** (motyw/`.rte` gdzieś zjada dziedziczenie lub jest twardszy selektor). **Fix: celuj też w `<p>` i daj `!important`:**
```css
.scope .fr-card__text,
.scope .fr-card__text p { font-size: var(--fr-text-size) !important; }
```
Dotyczy KAŻDEGO pola richtext, na którym dajesz konfigurowalny rozmiar (treść, podtytuł, opis). Objaw: „suwak rozmiaru X nie działa". Sprawdź najpierw czy X to richtext → jeśli tak, dołóż regułę na `p`.

#### GOTCHA #2: zmienna CSS z `{{ s.xxx }}` bez odpowiadającego settingu = cicha awaria

`--fr-card-radius: {{ s.card_radius }}px;` gdy w `{% schema %}` **nie ma** `card_radius` → renderuje `px` (pusta wartość) → `border-radius` nie działa, **bez błędu**. Reguła: **każdy `{{ section.settings.x }}` / `{{ s.x }}` w `{% style %}` MUSI mieć setting w schema.** Szybka walidacja przed wysłaniem: wyciągnij wszystkie `s.\w+` z `<style>` i sprawdź, że każdy `id` jest w schema (objaw u klienta: „zaokrąglenie/kolor/odstęp nie działa" mimo że suwak jest).

#### Slider = `FoxTheme.Carousel` (Swiper) przez custom element: self-contained

Cała sekcja w JEDNYM pliku: `{% style %}` scoped do `.section-{{ section.id }}` + markup `.swiper > .swiper-wrapper > .swiper-slide` + **inline `<script>` definiujący custom element pod guardem** `if (!customElements.get('...'))` + `{% schema %}`. Custom element w `connectedCallback`: czyta config z `data-*`, `new window.FoxTheme.Carousel(this.querySelector('.swiper'), options); .init()`. Opcje per-view przez `breakpoints: { 768: { slidesPerView, slidesPerGroup } }`, na mobile bazowy `slidesPerView`. Per-view 2/3 (nie `range`, 2 kroki łamią walidację, tylko `select` „2"/„3"). Strzałki/paginacja: `.swiper-button-prev/next` + `.swiper-pagination` przekazane przez `navigation.prevEl`/`pagination.el` (querySelector w elemencie). **Fallback gdy `window.FoxTheme.Carousel` niezaładowany** (sekcja na szablonie bez Swipera): `this.classList.add('fr-fallback')` → CSS `.fr-fallback .swiper{overflow-x:auto}` + `.swiper-wrapper{display:flex;gap}` + slide `flex-basis` → poziomy scroll zamiast zepsutego layoutu. Inline `<script>` przy wielu instancjach: define guardowany, każdy `<element>` ma własny `connectedCallback` (instancja z `data-*`).

#### Przełącznik układu 50/50 (zdjęcie obok treści): wrapper `__body` + flex modifier

Aby dać setting „pionowy / podział 50/50": owiń treść (wszystko poza zdjęciem) w `.fr-card__body` (flex column, `flex:1 1 auto`, `min-width:0`). Karta domyślnie `flex-direction: column` (zdjęcie u góry, body pod). Modifier `--split` → `flex-direction: row` (zdjęcie i body obok, `flex: 0 0 46%` na zdjęciu); `--media-right` → `row-reverse`. **Na mobile zawsze stackuj**: w `@media (max-width:767.98px)` nadpisz `.fr-card--split, .fr-card--split.fr-card--media-right { flex-direction: column }` (inaczej `row-reverse` daje odwróconą kolejność / ścisk). `margin-top:auto` na stopce autora działa, bo `__body` jest flex column o pełnej wysokości. Setting strony zdjęcia widoczny tylko w trybie split: `"visible_if": "{{ section.settings.card_layout == 'split' }}"`.

#### „Nudna" sekcja → eye-catch (tania robota, duży efekt)

Wyróżnione tło karty (panel `card_bg` ≠ tło sekcji) + `box-shadow` + hover `translateY(-0.4rem)` + większy cień; ozdobny cudzysłów `&ldquo;` (Georgia, duży, kolor akcentu, `line-height:0` + `height` żeby nie rozpychał); stopka autora oddzielona `border-top`; zdjęcie (tu: psa) jako zaokrąglony „bohater" karty z podpisem (np. `Imię, wiek` składane z dwóch pól przez `capture` + `strip`, render gdy `!= blank`). Rozmiary px osobno desktop/mobile przez nadpisanie zmiennych CSS w media query. Wszystko konfigurowalne (kolory, rozmiary, radius, cień on/off, cudzysłów on/off), pełna schema jak w innych customach. `{% style %}` z `padding:0.4rem; margin:-0.4rem` na `.swiper` żeby hover-shadow/translate nie był przycinany przez `overflow:hidden` Swipera.

#### GOTCHA #3 (KRYTYCZNY: autoplay „nie działa", suwak scroll „czasem wyskakuje"): moduły Carousela + race z theme.js

Druga runda na `featured-reviews` ujawniła dwie rzeczy o `FoxTheme.Carousel` (motyw Sleek/FoxEcom, `assets/theme.js`):

1. **Konstruktor: `new FoxTheme.Carousel(container, options, modules = null)`.** Domyślne moduły to TYLKO `Navigation, Pagination, Keyboard, Mousewheel`. **`Autoplay` (oraz `EffectFade`, `Thumbs`) NIE są domyślne: trzeba je podać jako 3. argument**, inaczej `autoplay: {...}` jest **po cichu ignorowane**:
   ```js
   var Swiper = window.FoxTheme && window.FoxTheme.Swiper;
   var modules = (autoplay && Swiper && Swiper.Autoplay) ? [Swiper.Autoplay] : null;
   this.instance = new Carousel(slider, options, modules);
   // wzór z assets/collections-slider.js: new Carousel(el, opts, [FoxTheme.Swiper.Autoplay, FoxTheme.Swiper.EffectFade])
   ```
   `loop: true` to natywny Swiper (bez modułu), ale włączaj go **warunkowo gdy `liczba slajdów > slidesPerView`** (inaczej loop się psuje / ostrzega). `autoplay` daj z `pauseOnMouseEnter: true`.

2. **Inline `<script>` sekcji wykonuje się PRZED `theme.js` (defer)** → `window.FoxTheme.Carousel` bywa `undefined` przy `connectedCallback` → kod od razu wpadał w fallback ze scrollbarem („czasem", zależnie od wyścigu). **Fix: czekaj na gotowość Carousela (poll ~50ms do ~3s) zanim sięgniesz po fallback**:
   ```js
   _initWhenReady(){ var C = window.FoxTheme && window.FoxTheme.Carousel;
     if (C) return this._build(C);
     if (this._tries++ > 60) return this.classList.add('fr-fallback');
     this._timer = setTimeout(this._initWhenReady.bind(this), 50); }
   ```
   Dodatkowo: fallback chowa scrollbar (`scrollbar-width:none` + `::-webkit-scrollbar{display:none}` + scroll-snap), a **na sekcji `overflow-x: clip`** kasuje ewentualne poziome wystawanie poza stronę (`clip` nie tworzy scroll-kontenera i nie wymusza `overflow-y:auto`, więc cień/hover w pionie nie jest przycinany). `disconnectedCallback` niszczy instancję (`this.instance.slider.destroy(true,true)`), czysty re-init w edytorze.

#### Strzałki pod sliderem na mobile (nie nachodzą na karty) + osobne kolory strzałki

Na mobile `.fr-nav { top:auto; bottom:0 }` nachodziło na kartę. Fix: zarezerwuj `padding-bottom` na kontenerze slidera (warunkowo `{% if show_arrows %}`) i ustaw strzałki absolutnie na dole, wyśrodkowane: `.fr-nav--prev{left:calc(50% - 4.8rem)} .fr-nav--next{left:calc(50% + 0.8rem)}` (paginacja zostaje statycznie nad nimi). Osobne kolory strzałki = 6 zmiennych zamiast jednej: tło / tło-hover / ikona / ikona-hover / ramka (puste→`transparent`) / kropki. Paddingi sekcji osobno mobile/desktop przez `--pt/--pb` nadpisywane w `@media`.

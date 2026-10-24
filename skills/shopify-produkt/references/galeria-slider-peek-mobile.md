# Galeria produktu: slider „peek" na mobile (centeredSlides + ułamkowy slidesPerView)

**Wdrożone:** sklep z suplementami dla psów (2026-06, Sleek/FoxEcom, `assets/media-gallery.js` + `snippets/product-media-gallery.liquid`).

Efekt „jedno zdjęcie centralne, po bokach kawałki sąsiednich, zapętlone". Wzorzec Swiper: `centeredSlides: true` + ułamkowy `slidesPerView` (np. 1.25 → środek 80%, po 10% z każdej strony). Przelicz w Liquid z procentu podglądu: `slidesPerView = 1 / (1 - 2*peek/100)`. Pass przez `data-mobile-peek-view`. W JS aplikuj tylko gdy włączone, z **breakpointem 768 przywracającym oryginalne desktopowe `slidesPerView`** (zapamiętaj wartość PRZED nadpisaniem, żeby freemode 'auto' / carousel '1' na desktopie zostały):
```js
if (this.mobilePeek && this.mobilePeekView > 1) {
  const desktopSpv = this.sliderOptions.slidesPerView;
  this.sliderOptions = Object.assign({}, this.sliderOptions, {
    slidesPerView: this.mobilePeekView, centeredSlides: true,
    breakpoints: Object.assign({}, this.sliderOptions.breakpoints, {
      768: { slidesPerView: desktopSpv, centeredSlides: false },
    }),
  });
}
```
`.product__media-item { width:100% }` w CSS: Swiper i tak nadpisuje inline width przy ułamkowym slidesPerView, więc działa. Galeria na mobile i tak jest zawsze sliderem (loop:true), peek tylko dokłada centrowanie.

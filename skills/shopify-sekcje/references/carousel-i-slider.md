# Carousel/slider sekcji: przesuwanie transformacją zamiast hide/show

**Wdrożone:** sklep z pluszakami (2026-06, motyw na bazie Nook, `sections/category-navigation.liquid`, rząd kółek kategorii z paginacją cyfry/kropki/stretch).

Wzorzec na każdy poziomy slider/karuzelę gdzie strony mają płynnie przejeżdżać (nie przeskakiwać). Działa dla dowolnych kafelków, nie tylko kółek.

#### Architektura: jeden tor + viewport, przesuwany `translateX`

NIE rób paginacji przez `display:none` na kafelkach spoza strony, to daje skok i psuje płynność. Zamiast tego: wszystkie elementy w jednym torze (`.row`), tor w `.viewport` z `overflow:hidden`, przesuwasz tor transformacją z CSS `transition`.

```
.viewport { overflow: hidden; width: 100%; }
.row.is-carousel { display:flex; flex-wrap:nowrap; transition: transform var(--slide) cubic-bezier(0.4,0,0.2,1); }
.row.is-carousel .item { flex: 0 0 calc((100% - (var(--per) - 1) * var(--gap)) / var(--per)); }
```

`--per` (ile na stronę) ustaw przez Liquid w CSS, desktop w bazowej regule, mobile w `@media`, wtedy szerokość kafelka przełącza się bez JS.

#### GOTCHA #1 (krytyczny): `translateX(%)` jest względem WŁASNEJ szerokości elementu, nie rodzica

Naturalny odruch „przesuń tor o `-100% * (strona-1)`" **nie działa**, procent w `translateX` liczy się od szerokości transformowanego elementu (toru, który jest szerszy niż viewport), nie od viewportu. Trzeba liczyć w px z JS:

```js
// strona 1-based; vpw = viewport.clientWidth; gap = computed gap toru
var x = -(currentPage - 1) * (vpw + gap);
row.style.transform = 'translateX(' + x + 'px)';
```

Dlaczego `vpw + gap`: przy `flex-basis = (100% - (per-1)gap)/per` szerokość kafelka+gap = `(vpw + gap)/per`, więc przesunięcie o jedną stronę (`per` kafelków) = dokładnie `vpw + gap`. Matematycznie zgadza się co do piksela, bez mierzenia obrazków/kafelków. Na `resize` przelicz `x` od nowa (zmienił się `vpw`).

#### GOTCHA #2: drag-follow palcem/myszą = toggle `transition`

Płynne śledzenie palca 1:1 i jednocześnie animowany snap po puszczeniu, przez przełączanie `transition`:

```js
function begin(x){ base = -(page-1)*(vpw+gap); row.style.transition='none'; }   // śledzenie 1:1
function move(x){ var dx=x-startX; row.style.transform='translateX('+(base+dx)+'px)'; }
function finish(x){ row.style.transition=''; /* snap */ goTo(page + dir) lub applyShift(); }
```

- Próg przerzutu: `Math.min(40, vpw*0.2)`, krótki gest na wąskim ekranie też zadziała.
- Rubber-band na krańcach: `if ((page===1 && dx>0) || (page===last && dx<0)) dx *= 0.35;`
- Guard `moved` + `click` w capture: `if (moved) e.preventDefault()`, przeciągnięcie nie odpala kliku w kafelek.
- Mysz: listeners `mousemove`/`mouseup` na `window` (nie na torze), żeby drag działał poza obszarem. `mousedown` → `e.preventDefault()` blokuje natywny drag obrazka.
- Touch: `touchstart`/`touchmove` jako `{passive:true}` (tylko czytasz clientX, nie blokujesz scrolla).
- Pierwszy paint: `transition='none'` → ustaw stronę z URL/aktywną → `requestAnimationFrame(() => transition='')`. Bez tego strona „dojeżdża" animacją przy wejściu.

#### GOTCHA #3: dostępność w sliderze bez `display:none`

Skoro kafelki spoza strony zostają w DOM (inaczej tor się rozjedzie), trzeba je wyjąć z nawigacji ręcznie, inaczej Tab skacze do niewidocznych:

```js
items.forEach(function(el,i){
  var onPage = i >= start && i < end;
  el.setAttribute('aria-hidden', onPage ? 'false' : 'true');
  el.tabIndex = onPage ? 0 : -1;
});
```

#### Tryb „stretch" (bez paginacji) na tym samym markupie

Ten sam tor, ale viewport dostaje `overflow-x:auto` (scrollbar ukryty: `scrollbar-width:none` + `::-webkit-scrollbar{display:none}`), kafelki wracają do `flex:0 0 auto`. Swipe palcem = natywny scroll (nic nie kodujesz). Drag myszą = `viewport.scrollLeft = startScroll - dx`.

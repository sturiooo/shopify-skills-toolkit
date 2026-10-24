# Gotchy CSS/Liquid z sesji 2026-08 (Maestrooo Impact/Airwave/Stretch, RoarTheme Concept)

### `margin-block-start: auto` na przycisku zjada margines motywu: NIE kompensuj paddingiem
Wyrównanie przycisków do dołu kolumny (`.prose` jako flex column + `margin-block-start: auto`)
nadpisuje `margin-block-start: var(--prose-button-spacing)`, który motyw daje przyciskom.
Kompensowanie tego **paddingiem na samym przycisku rozdyma jego wysokość**, przycisk wygląda
na „rozciągnięty w górę", bo napis ląduje przy dolnej krawędzi. Poprawnie: odstęp dokłada
**element poprzedzający** przycisk:
```css
.prose > *:has(+ :where(a.button, button, .button, .button-group)) { margin-block-end: var(--prose-button-spacing); }
```

### Sekcja, której wysokość dyktuje wideo
Na szerokich ekranach kolumna z wideo rośnie proporcjonalnie i ciągnie całą sekcję. Rozwiązanie:
ustawienie `range` w vh (**0 = zachowanie domyślne motywu**) + na desktopie `height: Xvh` na kolumnie
z mediami, `height: 100%` na wewnętrznym kontenerze i `object-fit: cover` na `img/video/iframe`.
Nigdy nie rozciągaj mediów, kadruj.

### Sticky „dodaj do koszyka" (Maestrooo)
`.product-sticky-add-to-cart` jest `position: fixed` z `width: min(100%, 40rem)` i `inset-inline-end`,
a **osobna reguła w `@media (max-width: 699px)` ustawia go inaczej**, nadpisując, trzeba pokryć
**oba warianty**. Scope przez `#shopify-section-{{ section.id }}` (specyficzność 1,1,0) wygrywa
z regułami motywu także wewnątrz ich media query.

### Kolejność pozycji w koszyku: Shopify nie ma na to API
Kolejność linii = kolejność dodania i **nie da się jej zmienić przez API**. Ale motywy często mają
własny mechanizm przenoszenia pozycji na koniec (RoarTheme/Concept: `{% capture cart_item %}` +
worek `cart_gift_wrap_items` renderowany po pętli). **Rozszerz ten mechanizm** (drugi worek na dodatki),
zamiast pisać własne sortowanie. Bezpieczne, bo motyw identyfikuje linie po `item.key`
(`data-index`, `/cart/change.js {id: key}`), a nie po pozycji; pozycyjne `updates[]` zostaje tylko
w `<noscript>`. To sortowanie działa **wyłącznie na warstwie wyświetlania**, w checkoucie kolejność zostaje.

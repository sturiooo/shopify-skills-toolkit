# Ziarno (grain/noise) na zdjęciach produktów: wybór techniki zależy OD TŁA zdjęcia

**Wdrożone:** sklep z biżuterią (2026-06, motyw Maestrooo Impact). Lekcja z ~8 iteracji, większości dało się uniknąć jednym pytaniem na starcie.

**Kontekst:** klient chce widoczne ziarno filmowe „grain/noise" na zdjęciach produktów, nakładane globalnie z kodu (CSS/SVG), żeby uploadować lekkie, gładkie, mocno skompresowane zdjęcia, a charakter dokładał motyw.

#### PYTANIE #1 NA STARCIE (determinuje całą architekturę): czy tło zdjęć jest przezroczyste (PNG) czy wtopione w plik?

To jedyny czynnik, który decyduje o technice. Zapytaj o to ZANIM napiszesz linijkę kodu, inaczej zrobisz kilka rund w złą stronę (tak było tu). Dodatkowo **poproś o realny przykład zdjęcia produktu**, jeden rzut oka rozstrzyga architekturę w 10 sekund.

| Tło zdjęcia | Czego chce klient | Jedyna poprawna technika |
|---|---|---|
| **Przezroczyste (PNG)** | ziarno **tylko na produkcie**, tło czyste | **Filtr SVG na `<img>` przycięty do alfa** (`feComposite operator="in"`) |
| Wtopione w plik (jednolite tło część JPG) | ziarno na całym kadrze | nakładka `::after` z szumem + `mix-blend-mode` na kontenerze |
| Dowolne, „tylko na półtonach produktu" | ziarno na produkcie, słabnie na płaskim jasnym tle | `::after` + `mix-blend-mode: overlay`/`soft-light` |

#### Dlaczego `::after` overlay NIE działa dla przezroczystych PNG

Nakładka `::after` (inset:0) wypełnia **cały prostokąt kontenera**, nie wie, gdzie jest produkt, a gdzie przezroczystość. Efekt: **ziarno na tle/letterboxie, produkt czysty** (dokładnie odwrotnie niż się chce). Żaden blend tego nie naprawi, bo problem jest geometryczny, nie tonalny.

#### Poprawna technika dla PNG: filtr SVG na img, przycięty do kanału alfa

Ziarno pojawia się **wyłącznie na nieprzezroczystych pikselach = na produkcie**; przezroczyste tło zostaje czyste. Kluczowy jest ostatni `feComposite operator="in"` (clip do `SourceGraphic`):

```liquid
<svg width="0" height="0" style="position:absolute;width:0;height:0;overflow:hidden;">
  <filter id="product-grain" x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="{{ base_freq }}" numOctaves="2" stitchTiles="stitch" seed="7" result="noise"/>
    <feColorMatrix in="noise" type="saturate" values="0" result="mono"/>
    <feComponentTransfer in="mono" result="grain">
      <feFuncA type="linear" slope="{{ grain_alpha }}" intercept="0"/>   {# slope = siła 0..1 #}
    </feComponentTransfer>
    <feComposite in="grain" in2="SourceGraphic" operator="over" result="grained"/>
    <feComposite in="grained" in2="SourceGraphic" operator="in"/>        {# ← przycięcie do sylwetki produktu #}
  </filter>
</svg>
<style>.product-gallery__media img { filter: url(#product-grain); }</style>
```
`base_freq = 60.0 | divided_by: grain_size` (size px → częstotliwość; mniejszy size = drobniejsze ziarno).

#### Gotchy, każdy kosztował iterację

1. **Filtr SVG MUSI być w `<body>`, nie `<head>`**, Safari nie zawsze rozwiązuje `filter: url(#id)`, gdy `<svg>` jest w head. Render snippetu po `{%- render 'shadow-dom-templates' -%}`.
2. **Data-URI szumu NIE wkładaj do stringa Liquida z escapowanymi cudzysłowami** (`"url(\"data:...\")"`). Shopify Liquid **nie obsługuje `\"`**, string urywa się, a reszta data-URI trafia do parsera → `Liquid syntax error: Unknown tag 'stitchTiles'`. Data-URI trzymaj w **surowym CSS**, a wybór źródła rób przez `{%- if -%}` wokół linii CSS, nie w `assign`.
3. **`overlay`/`soft-light` znikają na płaskim, bardzo jasnym/ciemnym tle** (blend dąży do zera przy bieli/czerni). Katalog na jednolitym jasnym tle = ziarno gaśnie tam, gdzie jest 80% kadru → „nic nie widać". `normal` widać wszędzie, ale ziarni cały prostokąt jak tło.
4. **Filtr na `<img>` bywa zbyt subtelny** przy małej sile: łatwo uznać „nie działa". Zanim ocenisz efekt, **potwierdź trafienie selektora drastycznym testem**: tymczasowo `filter: invert(1)` na img (produkt zmieni się w negatyw) albo `outline:3px solid red` na kontenerze. „Totalnie nic przy DWÓCH różnych technikach" = snippet się **nie renderuje** (zły render w theme.liquid / nie zapisany), nie wina techniki.
5. **Zapisane ustawienia z Customize biją domyślne z kodu**, zmiana `default` w schemacie nic nie da, jeśli klient już zapisał wartość. Po zmianie domyślnych trzeba przestawić ręcznie w Customize.

#### Mapa motywu Maestrooo Impact (przyda się następnym razem)

- Wszystkie zdjęcia idą przez `snippets/media.liquid` (filtr `image_tag`) → goły `<img>`.
- Galeria produktu: `.product-gallery__media img` (kontener ma `data-media-type="image|video|model"`, można wykluczyć wideo/modele). Miniatury to osobne `.scroll-marker img`.
- Karty produktu (kolekcje, wyszukiwarka, related, featured): `.product-card__image` (+ `--secondary` dla hover). Wrapper `.product-card__media` ma już `position:relative; isolation:isolate; overflow:hidden`.
- Layout: `layout/theme.liquid`, render w head: `social-meta-tags`, `microdata-schema`, `css-variables`, `js-variables`; `<body>` zaczyna `{%- render 'shadow-dom-templates' -%}`.

#### Przełączniki „gdzie pokazywać" w schemacie

Klient zwykle chce wybór miejsc. Daj checkboxy mapowane na selektory i buduj CSS warunkowo (osobne reguły, bez sklejania stringów selektorów):
```liquid
{%- if on_product -%}.product-gallery__media img { filter: url(#product-grain); }{%- endif -%}
{%- if on_collection -%}.product-card__image { filter: url(#product-grain); }{%- endif -%}
```
Konteksty wyświetlania zdjęć produktu w Impact = realnie dwa: **galeria (strona produktu)** i **karty (wszystkie listy)**. Sekcje „featured product" też używają `product-gallery` → łapią się pod galerię.

#### `config/settings_schema.json`: błędy, które rzucają „Nieprawidłowy JSON" (powtarzały się tu wielokrotnie)

Plik to **jedna tablica `[ ... ]`** grup. Przy wklejaniu nowej grupy waliduj:
- **Przecinek MIĘDZY grupami, NIGDY przed `]`.** Ostatnia grupa bez przecinka po `}`.
- **Dokładnie jeden `]` na końcu**, przy iteracjach łatwo zostawić stary `]` w środku (grupa ląduje wtedy „poza tablicą").
- **Żadnych surowych enterów wewnątrz wartości `"..."`**, każdy `content`/`label`/`info` w jednej linii. Edytor Shopify zawija wizualnie, ale realny `\n` w stringu = błąd zapisu.
- Czysty JSON: brak komentarzy, brak trailing comma.

Gdy klient zgłasza „Nieprawidłowy JSON", najszybciej **poproś o ostatnie ~30 linii pliku** zamiast zgadywać; przyczyną prawie zawsze jest przecinek przy ostatniej grupie albo zdublowany `]`.

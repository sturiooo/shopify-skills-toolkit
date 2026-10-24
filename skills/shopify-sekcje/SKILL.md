---
name: shopify-sekcje
description: "Budowa nowej sekcji albo bloku motywu Shopify (OS 2.0, Horizon, Sleek/FoxEcom, Maestrooo, RoarTheme) oraz przeróbka istniejącej: schemat, preset, style, tłumaczenia, slidery, ikony, fonty, grain. Uruchamiaj, gdy zadanie brzmi: dodaj sekcję, zrób baner, slider, karuzelę, zakładki, pasek korzyści, kafelki, przenieś sekcję z makiety Figma albo z innego motywu, dołóż blok do istniejącej sekcji."
---

# Sekcje i bloki motywu

Zanim napiszesz sekcję od zera, przejdź kolejność decyzji:
**1)** czy motyw docelowy ma to natywnie (grep + schematy sekcji),
**2)** czy biblioteka gotowych sekcji zespołu (jeśli ją prowadzicie) ma gotowca do przeniesienia,
**3)** dopiero potem piszemy od zera, a gotowa sekcja wraca do biblioteki z README.

Start: `references/budowa-od-zera.md`.

## Co tu jest

Wczytuj pojedynczy plik referencyjny, nie cały katalog.

| Plik | Temat |
|---|---|
| `references/as-seen-in-press-bar.md` | Sekcja As Seen In (press bar). |
| `references/blok-sku-z-prefiksem.md` | Blok SKU z konfigurowalnym przedrostkiem (label + bold + guard + padding). |
| `references/budowa-od-zera.md` | Budowa nowej sekcji albo bloku motywu Shopify (OS 2.0, Horizon i pochodne) od zera, ze schematem, presetem, stylami i kluczami tłumaczeń. |
| `references/carousel-i-slider.md` | Carousel/slider sekcji: przesuwanie transformacją zamiast hide/show. |
| `references/dopasowanie-koloru.md` | Dopasowanie koloru z cudzego projektu do palety klienta (2026-08-20). |
| `references/edycja-istniejacej-sekcji.md` | Dostosowywanie ISTNIEJĄCEJ sekcji motywu bez psucia reszty sklepu (`recently-viewed-products`, Sleek/FoxEcom). |
| `references/fonty-i-easingi-z-motywu.md` | Fonty i easingi z motywu: zmienne CSS zamiast `font_picker`/hardkodu. |
| `references/fonty-sleek-foxecom.md` | Architektura fontów motywu Sleek/FoxEcom: nagłówki HARDKODOWANE, globalny override w theme.liquid. |
| `references/gotchy-css-liquid.md` | Gotchy CSS/Liquid z sesji 2026-08 (Maestrooo Impact/Airwave/Stretch, RoarTheme Concept). |
| `references/ikony-w-bloku.md` | Ikony w bloku: zestaw motywu (`render 'icon'`) vs samodzielny + własna grafika. |
| `references/js-przy-wielokrotnym-renderze.md` | Sekcja renderowana wielokrotnie: JS pod jednym globalnym guardem + registry. |
| `references/linklist-zamiast-blokow.md` | Menu (`link_list`) jako szybkie źródło wielu pozycji - zamiast bloków po kolei. |
| `references/migracja-px-na-rem.md` | Migracja rozmiarów z px na rem, globalne pokrętło skali i dwie pułapki migracji: przeliczenie wartości w szablonach oraz wyścig sekcja/szablon w jednym push (2026-09-22, motyw Nook). |
| `references/pakiet-sekcji-landingu.md` | Pakiet customowych sekcji landingu (2026-06, Sleek/FoxEcom). |
| `references/port-miedzy-motywami.md` | Przenoszenie sekcji 1:1 między motywami: pełny playbook (2026-08-19/20, Release → Stretch). |
| `references/selektor-jezyka-w-header.md` | Selektor języka w header na mobile (zamiast na dole hamburger menu). |
| `references/slider-opinii.md` | Nowa sekcja slidera opinii od zera (samodzielna, FoxEcom/Sleek). |
| `references/stretch-wyroznianie-slowa.md` | Stretch (Maestrooo): wyróżnianie słowa w nagłówku jest NATYWNE (2026-08-20). |
| `references/wlasny-blok-w-main-product.md` | Dodawanie własnego bloku do istniejącej sekcji `main-product` (zamiast nowej sekcji). |
| `references/wzorce-ui.md` | Wzorce UI z tej sesji: reużywalne (2026-06). |
| `references/z-makiety-figma.md` | Budowa sekcji z Figmy „element po elemencie”: lekcje z PDP (2026-07-31/08-01, Local 3.2.1 KrownThemes). |
| `references/ziarno-grain.md` | Ziarno (grain/noise) na zdjęciach produktów: wybór techniki zależy OD TŁA zdjęcia. |
| `references/grain-horizon.md` | Horizon (sklep z biżuterią): tło sekcji jako osobne rodzeństwo treści, efekt grain (warstwa vs filtr alfa), SVG bez wymiarów = 0×0, `.with-overlay` ma własny pseudo-element, `range` ≥3 kroki. |
| `references/wymiary-banerow-slideshow.md` | Wymiary banerów dla slideshow o stałej wysokości: proporcja zależna od szerokości ekranu, kadr + strefa bezpieczna, osobny plik mobile (2026-10-12, motyw z rodziny Horizon). |
| `references/tekst-na-cala-szerokosc.md` | Tekst (np. imię, logo) na całą szerokość: `container-type` + `cqw` zamiast skryptu (CLS 0,114 → 0,012), jak zmierzyć stałą, obcinanie polskich znaków nad literą (2026-10-18). |


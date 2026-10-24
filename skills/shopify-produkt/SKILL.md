---
name: shopify-produkt
description: "Strona produktu (PDP) i karty produktów na listingach: bloki PDP, metapola w karcie, galeria i media per wariant, swatche kolorów, hover drugiego zdjęcia, produkty komplementarne, upsell, pigułki kategorii, H1 i SEO na produkcie. Uruchamiaj przy przebudowie PDP, zmianie wyglądu kart produktów, problemach z galerią wariantu albo rekomendacjami."
---

# Karta i strona produktu

Najpierw ustal, **który plik faktycznie renderuje** to, co poprawiasz: ten sam komponent bywa zduplikowany (snippet karty vs sekcja PDP vs blok apki), a rekomendacje często dociągane są AJAX-em po załadowaniu strony.

Przy galerii per wariant: **policz pokrycie danych** (ile wariantów faktycznie ma przypisane media), zanim orzekniesz, że kod jest zepsuty.

## Co tu jest

Wczytuj pojedynczy plik referencyjny, nie cały katalog.

| Plik | Temat |
|---|---|
| `references/blok-upsell.md` | Redesign bloku upsell: slider → statyczna lista poziomych wierszy (Sleek/FoxEcom). |
| `references/galeria-slider-peek-mobile.md` | Galeria produktu: slider "peek" na mobile (centeredSlides + ułamkowy slidesPerView). |
| `references/globalny-design-kart.md` | Globalny design kart produktów: rewrite snippets/card-product.liquid (FoxEcom). |
| `references/karty-z-wariantami-koloru.md` | Karty produktów z wariantami kolorystycznymi, hover second image i ocenami Judge.me (sekcja product-tabs). |
| `references/media-i-galeria-per-wariant.md` | Media i galeria PER WARIANT (zdjęcia + wideo): pełny playbook (2026-07-30/31, Concept/RoarTheme). |
| `references/pdp-sleek-foxecom.md` | Karta produktu w motywie Sleek (FoxEcom): bloki, metapola, CSS i scope per-produkt. |
| `references/pigulki-kategorii.md` | Pigułki kategorii na karcie produktu: link "within", aktywny marker, GOTCHA z przycinaniem strzałki. |
| `references/produkty-komplementarne.md` | Blok produktów komplementarnych: redesign + render z metafielda (Sleek/FoxEcom). |
| `references/przebudowa-pdp-sleek.md` | Lekcje: przebudowa PDP + koszyka + SEO (2026-06, Sleek/FoxEcom; Concept/RoarTheme). |
| `references/seo-na-produkcie-h1.md` | SEO na produkcie Shopify: jeden H1 + H1 niosący frazę z metapola. |
| `references/podmiana-zdjec-hd-fileupdate.md` | Podmiana zdjęć na wersje HD bez ruszania galerii (`fileUpdate` z `originalSource`), dopasowanie folderu klienta z Drive po hashu obrazu (2026-10-19). |

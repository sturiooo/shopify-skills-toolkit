# Diagnostyka „przestały się liczyć konwersje”: GTM i Google Ads (2026-08-19, sklep niemiecki)

Zgłoszenie: konwersje „purchase” w Google Ads przestały spływać. Rozstrzygnięcie **bez dostępu
do konta Ads**, na samym kontenerze GTM.

**Kontener GTM jest publiczny**: `https://www.googletagmanager.com/gtm.js?id=GTM-XXXXXXX` pobiera
się zwykłym `curl`, bez logowania. Jest w nim pełna lista tagów, triggerów i zmiennych. To najszybsza
droga do faktów, gdy klient mówi „coś się popsuło”, a nikt nie wie kiedy.

**W eksporcie kontenera `fingerprint` to timestamp ostatniej modyfikacji w milisekundach**
(`datetime.fromtimestamp(int(fp)/1000)`). Pozwala **datować zmiany** i zestawić je z momentem,
w którym konwersje spadły, bez historii wersji z panelu.

**Metoda, która rozstrzygnęła:** porównaj **payload tagu konwersji** z tym, czego oczekuje odbiorca.
U nas payload nie zawierał pól, które sypie warstwa danych sklepu, a jedno pole było ustawiane
zawsze. Z tego wynikało, że **tag nigdy nie odpalał** od konkretnej daty, a konwersje w Ads
pochodziły wyłącznie z **bezkodowej reguły URL** (Ads potrafi liczyć konwersje z samego adresu
strony podziękowania, niezależnie od GTM). Objaw „konwersje spadły” = reguła URL przestała łapać,
a tagu GTM nie było za czym stanąć.

**Wnioski ogólne:**
- **Konwersja w Ads może mieć dwa niezależne źródła** (tag GTM + reguła bezkodowa). Zanim
  zaczniesz naprawiać tag, ustal, **które źródło faktycznie liczyło**, inaczej „naprawisz” coś,
  co nigdy nie działało, i policzysz konwersje podwójnie.
- **Nie diagnozuj z opisu.** Klient/kolega opisuje objaw z panelu Ads; przyczyna jest w kontenerze,
  który możesz przeczytać w minutę.
- Przy odpowiedzi dla osoby nietechnicznej: podaj **jeden najbardziej prawdopodobny scenariusz
  i konkretny krok do sprawdzenia**, nie listę hipotez.

---

## Dodatkowo: wzorce z tej samej sesji

### Judge.me: widget produktowy z fallbackiem na opinie o sklepie (sklep z herbatą, 2026-08)

**Wdrożone:** sklep z herbatą (motyw rodziny Maestrooo, widget wstawiony kodowo, blok apki wyłączony).

Problem: produkt bez ani jednej opinii = pusty widget i „dziura” na karcie produktu.
Rozwiązanie bez apki i bez API: **Judge.me trzyma cache gotowego HTML w metapolach sklepu**.

```liquid
{%- assign jm_count = product.metafields.reviews.rating_count.value | default: 0 | plus: 0 -%}
{%- if jm_count == 0 and shop.metafields.judgeme.all_reviews_0 != blank -%}
  <div class="jdgm-widget jdgm-all-reviews-widget" data-widget="all-reviews">
    {{ shop.metafields.judgeme.all_reviews_header }}
    <div class="jdgm-rev-widg__reviews">{{ shop.metafields.judgeme.all_reviews_0 }}</div>
  </div>
{%- else -%}
  {%- render 'judgeme-review-widget' -%}
{%- endif -%}
```

- `all_reviews_header` = podsumowanie (średnia, histogram), `all_reviews_0` = pierwsza porcja
  opinii (u nas ~46 kB, 25 recenzji). Renderują się **statycznie**, bez ich JS.
- **NIE używać `judgeme.featured_carousel` jako fallbacku**: jego cache ma w środku
  `<style>.jdgm-carousel{display:none}` i bez skryptu apki zostaje niewidoczny.
- Liczba opinii: `product.metafields.reviews.rating_count.value`; średnia:
  `product.metafields.reviews.rating.value.rating` (uwaga na `.value.rating`).

### FAQ per produkt z metapól, w istniejącej sekcji motywu (sklep z herbatą, 2026-08)

Sekcja `faq` motywu jest blokowa → treść wspólna dla całego szablonu. Zamiast pisać nową sekcję,
**rozszerz istniejącą o drugie źródło danych**:

- metapola `custom.faq_1..5_pytanie` (`single_line_text_field`) + `_odpowiedz` (`rich_text_field`),
  definicje tworzone `metafieldDefinitionCreate` z `pin: true` (widoczne od razu na karcie produktu),
- w sekcji: pętla `for i in (1..5)` + bracket access `product.metafields.custom[klucz]`,
  odpowiedź przez `| metafield_tag` (rich text!), render tym samym snippetem `accordion` co bloki,
- **gate `section.blocks.size > 0` zmienić na `... or pf_count > 0`**,
- dane strukturalne `FAQPage` przełączyć razem z treścią (`| metafield_tag | strip_html`).

Efekt: produkt z własnym FAQ pokazuje swoje pytania, produkt bez FAQ ogólne z bloków.
Zero duplikacji sekcji w szablonie.

### Mapa punktów sprzedaży bez apki i bez klucza API

Skrót decyzyjny:

| Ile punktów | Rozwiązanie |
|---|---|
| do ~50, klient edytuje sam | bloki sekcji |
| więcej / dane z zewnątrz | snippet z danymi (`~~R~~` / `~~F~~` + `split`): **`for` po `split` nie ma limitu 50** |
| klient już ma Google My Maps | import KML: `google.com/maps/d/kml?mid=<MID>&forcekml=1` (bez klucza) |

Leaflet wgrywać **do `assets/` motywu**, nie z CDN. Pinezki jako `L.divIcon` z CSS, bez
zależności od obrazków markerów. Kafelki: CARTO Positron wygląda dużo lepiej pod minimalistyczne
sklepy niż domyślny OpenStreetMap; oba bezpłatne, wymagają atrybucji.

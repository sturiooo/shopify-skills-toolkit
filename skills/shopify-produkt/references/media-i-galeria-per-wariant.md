# Media i galeria PER WARIANT (zdjęcia + wideo): pełny playbook (2026-07-30/31, sklep z pluszakami, Concept/RoarTheme)

Sesja: „po wejściu na produkt zaznacz najmniejszy rozmiar", „packshot tylko na kartach kolekcji",
„w kafelkach TYLKO zdjęcia tego wariantu", „jak wrzucać wideo per wariant". Wzorzec jest ogólny:
motywy RoarTheme/Krown/Dawn-podobne mają te same dwa mechanizmy grupowania mediów.

### Dwa mechanizmy grupowania mediów po wariancie i ich realne ograniczenia

| | Metapole wariantu (lista plików) | Konwencja ALT (`#opcja_wartość`) |
|---|---|---|
| Ile mediów na wariant | **wiele** (zdjęcia + wideo) | wiele |
| Precyzja | **dokładny wariant** (kolor+rozmiar) | **tylko JEDNA opcja** (np. wszystkie czerwone) |
| Praca w panelu | wpis przy każdym wariancie | jeden alt na plik |
| Wideo Shopify | tak | tak |
| YouTube/Vimeo | nie (patrz niżej) | tak (jest w `product.media`) |

- **Konwencja ALT grupuje po JEDNEJ opcji.** Kod (`snippets/product-media.liquid`) leci po liście
  connectów po `#`, ale **`break`-uje na pierwszym, którego prefiks pasuje do nazwy opcji produktu**
  → `#color_red,size_220-cm` liczy tylko `color_red`. „Czerwony **i** 220 cm" jednym altem = niemożliwe.
- **Konwencja ALT jest zbramkowana `hide_variants == false`** (`if media.alt contains '#' and hide_variants == false`).
  Włączona w sekcji opcja „Hide other variants' media" **wyłącza alty**. Sprawdź `templates/product.json`,
  zanim obiecasz klientowi, że alty zadziałają.
- Wartości są handleizowane: `Color`→`color`, `220 cm`→`220-cm`, prefiks `iso:` dla wielojęzyczności.

### GOTCHA #1: motyw renderuje TYLKO `product.media`

Plik wybrany w metapolu wariantu, którego **nie ma w sekcji Media produktu**, nie wyrenderuje się
NIGDY (galeria iteruje `product.media`). Najczęstszy błąd osoby obsługującej sklep, objaw „wgrałem
5 zdjęć, widać 2". Diagnoza: porównaj `references` metapola z `product.media` po `id`.
W kodzie filtruj listę metapola przez obecność w `product.media` (inaczej licznik mediów kłamie).

### GOTCHA #2: wbudowane „ukryj media innych wariantów" bywa martwe, nie polegać

Mechanizm motywu = klasa `.product__media--variant` (dawana, gdy `variant_images contains media.src`)
+ CSS `.product__media--variant:not(:first-child){display:none}`. Dwa problemy:
`variant_images` to `product.images | where 'attached_to_variant?' | map 'src'`, a **`media.src` na
obiekcie `media` jest niepewne** (dla media udokumentowane jest `preview_image`, nie `src`) → klasa
może nigdy nie wejść; a `:not(:first-child)` ukrywa też media, które własny filtr przepuścił.
**Wzorzec:** filtruj w Liquid po `id`, a klasę motywu w swoim trybie świadomie pomiń
(`if hide_variants and moja_lista == blank and …`).

### Wzorzec: lista dozwolonych `id` przekazywana do snippetów

```liquid
{%- comment -%} w snippecie galerii: zbuduj ',12,34,' + licznik {%- endcomment -%}
assign cv_variant_media = ''            # ',id,id,'
assign cv_variant_media_count = 0
# 1) metapole listy plików -> tylko pozycje obecne w product.media
# 2) elsif natywne product_variant.featured_media -> 1 plik
# 3) nic -> filtr OFF (cała galeria, żeby nie była pusta)
```
W `product-media.liquid` / `product-thumbnail.liquid`:
```liquid
assign cv_media_key = media.id | prepend: ',' | append: ','
if cv_variant_media contains cv_media_key   # przecinki po OBU stronach: 12 nie trafi w 123
```
- **`media_count` przelicz z tej listy**: bramkuje pasek miniatur (`media_count > 1`) i klasę `with-only1`.
  Bez tego kafelki/kropki są niespójne z tym, co się faktycznie renderuje.
- Starą logikę grupowania owiń `if moja_lista == blank`: zostaje dla featured-product / quick view
  i sklepów jadących na konwencji ALT.
- **Natywnie Shopify daje 1 obraz na wariant** → wariant z samym natywnym zdjęciem = galeria z 1 pozycją
  i BEZ kafelków. Wiele mediów na wariant = tylko metapole. Powiedz to klientowi wprost, zanim uzna to za bug.

### WIDEO per wariant: fakty zweryfikowane na żywym sklepie (2026-07-31)

- **`Video` (hostowane w Shopify) przechodzi do `list.file_reference`**: zapis `metafieldsSet` OK,
  lista mieszana (wideo + zdjęcia) OK.
- **`ExternalVideo` (YouTube/Vimeo) jest ODRZUCANY**: „Value musi być ciągiem znaków odniesienia do pliku",
  bo osadzenie nie jest plikiem. Wideo z YT per wariant = tylko konwencją ALT.
- **Wideo w Media produktu = TEN SAM obiekt co plik w bibliotece** (to samo `gid://shopify/Video/…`,
  potwierdzone `files(query:"media_type:VIDEO")`) → picker metapola je pokaże, a porównanie `id` w motywie
  trafi. Analogicznie zdjęcia produktu to `MediaImage` w bibliotece.
- **Definicja metapola bez `validations` = brak ograniczenia typu plików** (`file_type_options` puste)
  → przyjmie wideo. Jeśli ktoś ustawił `file_type_options: ["Image"]`, wideo odpadnie: sprawdź definicję.
- **`productCreateMedia` NIE przyjmie URL-a wideo** (nawet własnego `cdn.shopify.com`): „Invalid video url".
  Wideo wymaga `stagedUploadsCreate` (`resource: VIDEO`, `httpMethod: POST`, `fileSize` jako string) →
  multipart POST na `url` ze wszystkimi `parameters` + `file=@plik.mp4` (HTTP 204) → `productCreateMedia`
  z `originalSource: resourceUrl`. Obrazy przez zwykły URL działają.
- **`metafieldsSet` jest atomowy dla całej paczki**: jeden zły element wywala WSZYSTKIE i potrafi wskazać
  **mylący `elementIndex`** (błąd pokazał indeks 0, a winny był ExternalVideo w indeksie 1).
  Wysyłaj małymi porcjami i izoluj przypadki przy diagnozie.
- **`fileDelete` wymaga scope `write_files`** (nie ma go w `write_products`) → nie usuniesz pliku sesją
  „produktową". Ale **usunięcie produktu usuwa też jego media z biblioteki**: wystarczy do sprzątnięcia testu.
- `ProductVariant.image` to obraz: natywnego „wideo wariantu" w API nie ma.
- Motyw renderuje wideo w galerii przez `snippets/media.liquid` (`video_tag` / `external_video_tag`),
  miniatura dostaje ikonę „play"; autoplay/loop to osobne checkboxy sekcji (domyślnie OFF).
- Kolejność: główny element galerii = pierwszy z `product.media` należący do listy wariantu → wideo
  wskakuje na górę, jeśli leży w Media przed zdjęciem. Przełącznik kolejności (`gallery_variant_order`)
  zmienia tylko sortowanie, nie filtrowanie.

### Auto-wybór wariantu na wejściu (server-side) i pułapka, która to zabija

Wymóg „po wejściu zaznaczony najmniejszy rozmiar" robi się w Liquid: policz `current_variant` na górze
sekcji i podmień WSZYSTKIE `product.selected_or_first_available_variant` (w tym motywie było ich 64
w sekcji + 57 w `buy-buttons.liquid`), przekaż do pickerów/galerii/buy-buttons/inventory/pickup,
a `product-price`/`product-badges` przez `variant:`.

- **PUŁAPKA (kosztowałaby cofanie kliknięć):** motyw re-renderuje sekcję po kliknięciu opcji przez
  **`?option_values=…&section_id=…`**, a wtedy **`product.selected_variant` jest PUSTE** → własna logika
  „na wejściu wybierz X" nie odróżni kliknięcia od wejścia na stronę i **nadpisze wybór użytkownika**.
  Ryzyko realne, gdy kolejność wartości opcji nie jest rosnąca (tu: 80 produktów, np. 120/90/70).
  **Fix: dołóż `&variant=<id>` do re-renderu** (`ProductInfo.buildRequestUrlWithParams`), biorąc id
  z `variant-picker.currentVariant`, a gdy blok nie ma dynamicznych wariantów, policz je z `[data-variants]`
  (`syncCurrentOptions()` + `findAndSetCurrentVariant()` działają bez argumentu).
  Dowód, że `variant=`+`section_id=` to legalna para: motyw sam tak fetchuje w innym miejscu.
- `<script data-selected-variant>` to **źródło prawdy dla JS po re-renderze** (z niego lecą URL,
  `input[name=id]`, cena) → musi zawierać ten sam wariant, który wyliczył Liquid.
- W pickerach stan `checked`/`selected` bierz z `current_variant['option' + option.position]`,
  **nie z `option.selected_value`** (to drugie po wejściu pokazuje wariant motywu). Porównanie wartości
  przez `capture` (drop vs string).
- Parsowanie rozmiaru: `downcase | replace: 'cm','' | replace: 'mm','' | replace: ' ','' | plus: 0`
  (0 = nienumeryczny → pomiń, zostaje kolejność motywu). Rozpoznanie opcji: nazwa zawiera
  `size`/`rozmiar`/locale-trigger, tak samo jak istniejący `snippets/size-value-order.liquid`.
- Bracket access na wariancie (`cv_variant['option2']`) działa: motyw sam tego używa.

### Testowanie nowych mechanizmów na żywym sklepie

- **Nie testuj na danych klienta.** Zrób **tymczasowy produkt DRAFT** (`productSet`, `status: DRAFT`,
  nazwa „ZZZ TEST … (do usunięcia)"), przeprowadź pełny łańcuch (upload → media → metapole → odczyt
  referencji), a potem `productDelete`. Draft nie jest nigdzie widoczny, a usunięcie zabiera też jego media.
- **Weryfikuj odczytem tą samą ścieżką, którą czyta motyw**: `metafield.references` → `id` vs `product.media` → `id`.
- Skrypty patchujące Liquid: **`grep -c` liczy LINIE, nie wystąpienia**: asercje licz `re.findall`
  (tu 59 linii vs 64 wystąpienia). Lookbehind `(?<![\w.])` chroni przed złapaniem
  `variant.product.selected_or_first_available_variant` w pętli po innych produktach. I podmieniaj
  PRZED dopisaniem własnego nagłówka, żeby nie podmienić go samemu sobie.

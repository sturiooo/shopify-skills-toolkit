---
name: shopify-rynki-i-tlumaczenia
description: "Sklep wielojęzyczny na Shopify Markets: języki i rynki, domeny i podkatalogi, Translate & Adapt, tłumaczenia przez Admin API (translationsRegister, translatableResources, digest), pliki locales/*.json i *.schema.json, tłumaczenie metapól i metaobiektów, hreflang i canonical, selektor kraju i języka, przekierowania geo. Uruchamiaj, gdy dodajesz język albo rynek, gdy „na /en/ jest polski tekst” (albo odwrotnie), gdy tłumaczysz sklep bez apki, gdy domena przekierowuje nie tam, gdzie trzeba, i przed każdym warunkiem w kodzie zależnym od języka."
---

# Rynki i tłumaczenia

Trzy rzeczy, które wracają najczęściej:
- **tekst na storefroncie ma trzy źródła naraz**, a wygrywa warstwa tłumaczeń, nie plik w motywie,
- **zmiana treści źródłowej nie aktualizuje tłumaczeń**: stare wartości dalej się serwują,
- **język główny zmienia się wyłącznie w panelu**, API tego nie umie.

Ceny, cenniki i waluty rynków: skill `shopify-b2b-i-dostawa`. Tłumaczenie metapola, które
się nie wyświetla: `shopify-diagnostyka`. Audyt SEO wersji językowych: osobne narzędzie spoza tego pakietu.

Sklepy w przykładach opisane są neutralnie: „sklep z pluszakami” (motyw Concept), „siostrzany sklep z pluszakami”
(ten sam motyw), „sklep z obuwiem” (rodzina FoxEcom), „sklep z herbatą”, „sklep z basenami” (rodzina XO),
„sklep z obuwiem skórzanym” (Prestige), „sklep z jednym produktem” (Wonder), „sklep na motywie Sleek”.

## Co tu jest

| Plik | Temat |
|---|---|
| `references/tlumaczenia-przez-api.md` | Workflow `translatableResources` → `translationsRegister`, gotowe zapytania (zwalidowane na 2026-07), klucze per typ zasobu, audyt pokrycia, scope'y. |

## 1. Zanim cokolwiek przetłumaczysz: ustal układ

Jedno zapytanie, zanim padnie choć jedno zdanie o tłumaczeniach (zapytanie w references):
`shopLocales` (który język jest `primary`, które `published`) i `markets` z `webPresences`
(domena albo `subfolderSuffix`, `defaultLocale`, `alternateLocales`, `rootUrls`).

Układy spotkane w praktyce, każdy wymaga innej roboty:
- **Jeden język** (sklep na motywie Sleek i sklep z suplementami na motywie Stretch, 31.08.2026): warstwa
  tłumaczeń jest pusta, „tłumaczenie” to polonizacja źródła. `translatableResources` i tak zwraca treść
  ŹRÓDŁOWĄ, więc nadaje się do skanu.
- **Primary `pl`, a treść źródłowa po angielsku** (sklep z obuwiem, 01.09.2026, po anglicyzacji): warunek
  `request.locale.iso_code == 'pl'` jest prawdziwy na całym głównym sklepie i fałszywy na `/en/`, czyli
  działa odwrotnie do intencji. Przed każdym warunkiem językowym porównaj źródło z `translations(locale:)`.
- **Primary `en`, polska treść wpisana w slot `en`** (siostrzany sklep z pluszakami, do 02.10.2026): `locales/pl.json` miał
  komplet 460 kluczy, a klient widział „Your cart is currently empty”, bo motyw serwował `en.default.json`.
  Obejście na już: treść `pl.json` do `en.default.json` (z backupem). Docelowo zmiana primary w panelu.

**Zmiany języka domyślnego nie zrobisz przez API** (siostrzany sklep z pluszakami 21.09.2026, sklep z herbatą 03.09.2026):
`ShopLocaleInput` ma tylko `published` i `marketWebPresenceIds`. Języka głównego nie da się też
odpublikować. Decyzję „zostajemy przy układzie czy przestawiamy primary” podejmij PRZED tłumaczeniem
szablonów, inaczej robisz to dwa razy.

## 2. Języki, rynki, domeny

- **Dodanie języka to trzy kroki** (sklep z pluszakami, 02.09.2026): `shopLocaleEnable(locale: "pl")`,
  `shopLocaleUpdate` z `published: true`, i dopisanie do `alternateLocales` obecności webowej rynku.
  Opublikowany język bez obecności webowej nie jest dostępny na żadnym rynku (siostrzany sklep 2026-09: rynek
  `pl` bez `webPresences`; sklep z herbatą 03.09.2026: `/pl/` 404).
- **Jeden kraj należy do jednego rynku.** Rynku z krajem, który siedzi w innym rynku, nie utworzysz;
  rynku nadrzędnego nie usuniesz, więc łatwiej przerobić istniejący przez `marketUpdate` (sklep z pluszakami, 13.08.2026).
- **Wydzielenie kraju do własnego rynku ZMIENIA ADRESY**: podkatalog powstaje jako `/<język>-<sufiks>/`.
  W sklepie z pluszakami `/pl/` zaczęło zwracać 404, a sklep dostał `/pl-pl/`. Szczegóły i alternatywy:
  `shopify-b2b-i-dostawa`.
- **Obecność webowa ma albo `domainId`, albo `subfolderSuffix`, nigdy oba** (potwierdzone w docs:
  `MarketWebPresenceUpdateInput`).
- **Domenę rynku przestawia WYŁĄCZNIE wycofywany `marketWebPresenceUpdate`.** Następca
  `webPresenceUpdate` (`WebPresenceUpdateInput`) ma tylko `defaultLocale`, `alternateLocales`
  i `subfolderSuffix`, bez `domainId` (sklep z pluszakami, 16.09.2026; potwierdzone w docs 2026-07).
- **Domena sklepu przekierowuje 302 na `.myshopify.com`, choć `primaryDomain` jest poprawny**
  (ten sam sklep, 16.09.2026): rynek podstawowy miał w obecności webowej domenę myshopify. Objaw
  dodatkowy: `<link rel="canonical">` wskazuje myshopify, czyli Google indeksuje zły adres.
  Diagnoza: `rootUrls` rynku. Po naprawie CDN jeszcze chwilę serwuje stare 302: testuj z `?cb=123`.
- **Zmiana nazwy rynku nie zmienia `handle`** (ten sam sklep, 16.09.2026). Przez API szukaj po nazwie albo ID.
- Rynek z walutą lokalną bez ustawionej waluty pokazuje „Austria (PLN zł)” w selektorze
  (sklep z herbatą, 11.09.2026). Waluty rynku nie zmienisz tokenem bez `write_markets`, wtedy panel.

## 3. Skąd naprawdę bierze się tekst

Kolejność pierwszeństwa (sklep z pluszakami, 15.09.2026, polski uparcie pokazywał starą etykietę):

1. **warstwa tłumaczeń Shopify** (`translatableResources`, typy `ONLINE_STORE_THEME*`), wygrywa,
2. **pliki `locales/*.json`** w motywie,
3. **tekst zaszyty w kodzie** sekcji.

Gdy plik locale „nie działa”, najpierw sprawdź, czy ktoś nie zapisał tłumaczenia ustawienia motywu.
Dopiero `translationsRemove` na tym kluczu odblokował plik (`general.easify_button_label`).

**Źródłem `ONLINE_STORE_THEME_LOCALE_CONTENT` jest plik locale języka PRIMARY** (`pl.json`, gdy
primary to `pl`), nie `en.default.json` (sklep z obuwiem, 10.08.2026). Tłumaczenia z Translate & Adapt
materializują się w plikach pozostałych języków, dlatego te pliki na live różnią się od pulla.
Nowy klucz z tekstem zaszytym w Liquid: (1) dopisz do pliku primary i pozostałych, (2) `{{ 'klucz' | t }}`,
(3) wgraj, (4) zarejestruj tłumaczenia przez API, inaczej regeneracja plików przez T&A zje wartości.

## 4. Pliki locale motywu

- **Nagłówek `/* */` i wiszące przecinki** w `locales/*.json` (sklep z pluszakami, 15.09.2026; 17.08.2026).
  `json.load` się na nich wywala. Wytnij, sparsuj, **porównaj liczbę kluczy przed i po**, przy zapisie
  dołóż nagłówek z powrotem.
- **Nowy klucz wystarczy dopisać do pliku primary i `en.default.json`**: pozostałe języki spadają na plik
  domyślny (17.08.2026). Brak klucza w ogóle daje „translation missing: …”, a to string truthy, więc
  `| default:` się nie odpali (szczegóły: `shopify-koszyk`, pakowanie na prezent).
- **Klucz z HTML musi kończyć się `_html`**, inaczej `t` escapuje znaczniki. Link przez interpolację
  `| t: url: …` (sklep z obuwiem, 10.08.2026).
- **Limity z docs**: maks. 3400 tłumaczeń w jednym pliku locale, wartość maks. 1000 znaków.
- **`*.schema.json` tłumaczą tylko etykiety edytora motywu**, klient sklepu ich nie widzi. Brak `pl.schema.json`
  = panel po angielsku (sklep z kawą funkcjonalną, 2026-09). Nie licz ich w audycie storefrontu.
- **Pole tekstowe z `default` w schemacie nigdy nie jest puste**, więc `{{ settings.x | default: t }}`
  nie sięgnie po locale i `/en/` dostaje polski tekst (sklep z jednym produktem, 03.09.2026: trzy rundy sprawdzania uploadu,
  winny był schemat). Teksty dla klienta trzymaj w locale, pola w schemacie bez `default`. Gdy pole ma już
  wartość w `settings_data.json`, wyczyść też ją (sklep z pluszakami, 15.09.2026).
- **Wartość w `settings_data.json` może siedzieć w presecie, nie w `current`** (sklep na motywie Sleek, 23.09.2026:
  `cart_empty_message` tylko w presecie motywu, motyw brał angielski default ze schematu).
- **Gotowe `pl.json` z motywu bywa tłumaczeniem maszynowym**: „Wymeldować się” na przycisku kasy,
  „Twój wózek”, „Dom”, „Jasne” (= Clear), „Sprzedaż” (= Sale). Sklep na motywie Sleek 23.09.2026: 157 poprawek,
  sklep z obuwiem 2026-08 to samo. Przy każdym nowym sklepie przejrzyj widoczne klucze koszyka i kasy.
- **Przy synchronizacji motywu między sklepami nie kopiuj `pl.json` 1:1**, scalaj: siostrzany sklep ma 12 własnych
  poprawek względem sklepu, z którego skopiowano motyw (02.10.2026).

## 5. Translate & Adapt i to, czego nie tłumaczy

- Auto-translate wypełnia brakujące i nieaktualne tłumaczenia, **ręcznych nie nadpisuje** (help.shopify.com).
  Limit automatycznego tłumaczenia do 2 języków podają tylko wątki społeczności, nie oficjalne docs:
  sprawdź w panelu, zanim obiecasz klientowi.
- **Tłumaczenie maszynowe niszczy nazwy własne** (sklep z pluszakami, 2026-09, 29 poprawek): nazwy modeli
  i postaci przetłumaczone jak zwykłe słowa (np. model „Brave” jako „Mutig”), a formularz odstąpienia
  po niemiecku jako „wniosek o wypłatę”. Po każdym auto-translate przegląd nazw produktów, kolekcji i dokumentów prawnych.
- **Ustawienie bloku podpięte do dynamicznego źródła** (`{{ product.description }}` jako string w JSON)
  nie respektowało locale dla DE (sklep z basenami, 2026-06). Renderuj `product.description` i metapola wprost w Liquid.
- **Statyczne ustawienia sekcji T&A złapał dla EN, a dla DE nie** (ten sam sklep, 2026-06): po tłumaczeniu
  sprawdź render w każdym języku osobno, nie w jednym.
- **Blok Custom Liquid nie ma tłumaczeń**: wtedy warunek na `request.locale.iso_code` w bloku (sklep z jednym produktem, 2026-09).
- **`image_picker` nie jest tłumaczony**, tagi artykułów też nie: wzorce obejścia w `shopify-diagnostyka`
  (sklep wielojęzyczny, sklep z obuwiem skórzanym 05 i 09.10.2026).
- **Szablony powiadomień: źródło tylko ręcznie w panelu, tłumaczenie przez `translationsRegister`**
  (`EMAIL_TEMPLATE`, sklep z obuwiem 01.09.2026). Po wklejeniu źródła digest się zmienia: przerejestruj tłumaczenie.
- **Widgety apek tłumaczy apka**, nie motyw: Judge.me (język w panelu), Klaviyo (osobny formularz EN
  z targetowaniem „URL contains /en/”, sklep z jednym produktem), kreatory zestawów. Awaryjnie słownik
  w motywie (podmiana tekstów widgetu skryptem); to temat spoza tego pakietu.

## 6. Metapola i metaobiekty

- **Tłumaczalne są typy tekstowe**: `single_line_text_field` i `multi_line_text_field` tak, `date` nie
  (docs, przykład `Metafield.translatable`); `rich_text_field` tłumaczy się w praktyce (sklep z basenami, sklep z obuwiem).
  Pełnej listy docs nie podają: zanim obiecasz, sprawdź pole `translatable` na konkretnym metapolu. W sklepie z pluszakami z 955 metapól
  tylko 186 było tekstowych, reszta to listy gid mediów: pomijaj je w eksporcie (04.09.2026).
- **Od API 2026-10 jest pole `Metafield.translatable`**, a wartość `METAFIELD` w `TranslatableResourceType`
  jest oznaczona do wycofania (nadal działa na każdej wersji). Nowy kod: metapola z zasobu właściciela,
  filtr `translatable: true`, digesty przez `translatableResourcesByIds`.
- **Metaobiekt tłumaczy się tylko, gdy definicja ma `capabilities.translatable.enabled`**; tłumaczalne
  pola wynikają z typu metaobiektu (docs: `MetaobjectCapabilitiesTranslatable`). Dobór metapole kontra
  metaobiekt: `shopify-metapola`.
- **Rich text renderuj przez `| metafield_tag`**, nie `.value` (sklep z basenami, 2026-06).
- **Wartości filtra S&D z metapola to przetłumaczone wartości per produkt**: niespójne tłumaczenia
  dają osobne pozycje („Gray” i „Grey”, sklep z obuwiem skórzanym 09.10.2026). Tłumacz słownikiem, nie produkt po produkcie.

## 7. Dane katalogu, które psują się po tłumaczeniu

Zanim przetłumaczysz nazwy lub wartości opcji, zrób grep motywu po tych wartościach.
- **Próbki kolorów dobierane po nazwie wartości** gasną po tłumaczeniu (sklep z pluszakami 04.09.2026, Concept
  `swatch_config`; sklep z obuwiem skórzanym 09.10.2026, `color_swatch_config`). Fix bez kodu: tłumaczenie tego
  ustawienia motywu z kluczami w nowym języku. Nowy kolor dopisuj w obu wersjach.
- **„Default” przetłumaczone na „Domyślny”** zepsuło kod koszyka, który ukrywa wariant warunkiem
  `contains 'Default'` (starszy sklep z pluszakami, 01.10.2026, 131 opcji do odkręcenia).
- **Mega menu włączane zgodnością `menu_title` z tytułem pozycji menu**: tłumacz parami, inaczej w nowym
  języku menu spada do zwykłego dropdownu (sklep z obuwiem, 10.08.2026).
- **Etykiety filtrów biorą się z nazw opcji, typu produktu i producenta**, nie z motywu (siostrzany sklep z pluszakami, 21.09.2026:
  `Size`, `Color` i producent z nazwą marki na 252 produktach).
- **Uchwytów (`handle`) zwykle nie tłumacz**; brak tłumaczenia handle to nie błąd w audycie (sklep z pluszakami).

## 8. Linki, hreflang, canonical

- **hreflang dokłada Shopify sam** przez `content_for_header`, gdy sklep używa Markets; tagi idą za
  językami i domenami rynków i za canonical (docs: themes/seo/hreflang). Własnych tagów nie dokładaj,
  bo powstają duplikaty. Wyłącznik: Sklep online → Preferencje → „Automatic hreflang tags”; własne tagi
  tylko przy kilku osobnych sklepach na różnych domenach i tylko budowane z obiektu `localization`.
- **Canonical bierze się z `rootUrls` rynku**: zła domena rynku = zły canonical (sekcja 2).
- **Zaszyte ścieżki gubią język i rynek.** `/pages/bundle-builder` w ustawieniu motywu wyrzucało klienta
  z `/pl/` na wersję domyślną, a koszyk przeskakiwał z PLN na EUR (sklep z pluszakami, 18.09.2026). W kodzie
  `routes.root_url` i `routes.*`, linki do dokumentów przez `shop.terms_of_service.url`,
  `shop.privacy_policy.url` (sklep z obuwiem i starszy sklep z pluszakami, 08 i 09.2026: zaszyte `/policies/...` dawały angielski
  regulamin w każdym języku).
- **Tłumaczenie ustawienia z adresem potrafi przetrwać zmianę wartości źródłowej** (sklep z pluszakami, 18.09.2026:
  DE i FR wskazywały stary adres apki na domenie myshopify). Po zmianie każdego URL w ustawieniach motywu
  przejrzyj jego tłumaczenia.
- Audyt hreflang i canonical rób na żywym HTML (crawler albo `curl` + grep), nie na kodzie motywu.

## 9. Selektor kraju i języka, przekierowania geo

- **Automatyczne przekierowanie ma dwa osobne przełączniki** (Sklep online → Preferencje): kraj po IP
  (rynek i waluta) i język po ustawieniach przeglądarki. Niemiec z angielską przeglądarką dostaje angielski.
  Żeby język zależał sztywno od kraju, potrzebny osobny rynek z własnym `defaultLocale` (sklep z pluszakami, 2026-09).
- **W UE rozporządzenie 2018/302 (geoblocking)** ogranicza wymuszone przekierowanie kraju; Shopify wewnątrz
  UE pokazuje rekomendację zamiast przekierowania. Przekierowanie języka tego nie narusza.
- Test bez panelu: `curl -s -o /dev/null -D - -H "Accept-Language: de-DE,de;q=0.9" https://domena/`.
  200 bez `location` = przekierowanie języka wyłączone, 302 na `/de` = włączone.
- **Jedna lista „język = kraj”** (sklep z herbatą, 11.09.2026): osobny `{% form 'localization' %}` na każdą pozycję,
  bo jeden submit wysyła tylko własną parę nazwa/wartość; każda pozycja wysyła `locale_code` i `country_code`.
- **Warunek na usługę krajową stawiaj po kraju, nie po języku** (`localization.country.iso_code`;
  sklep z obuwiem, 01.09.2026, Wygodne Zwroty).
- **Apki geo potrafią działać tylko na języku głównym** (sklep z basenami, 2026-06: Addify blokował koszyk po IP
  na `/`, a na `/en` i `/de` już nie). Po wdrożeniu apki kraju sprawdź każdy prefiks języka.

## 10. Kolejność przy przestawianiu sklepu na inny język

Sprawdzone na sklepie z obuwiem (01.09.2026) i siostrzanym sklepie z pluszakami (10.09.2026):
1. **Najpierw szukaj oryginału klienta**, nie tłumacz wstecz: stary sklep, Store API WooCommerce
   (`/wp-json/wc/store/products`), tagi klienta jako słownik nazw.
2. produkty → kolekcje → strony → menu → locale motywu → szablony JSON → nazwy i wartości opcji,
   typ produktu, producent.
3. **Skanuj pliki pobrane ze sklepu, nie kopię lokalną** (sklep z obuwiem: 194 trafienia lokalnie, 166 na live).
4. Dokumentów prawnych nie tłumacz sam, poproś klienta o pliki. Nazwy własne (spółka, ulica, sąd) zostają.
5. Weryfikuj odczytem i curlem renderu `/<lang>/products/<handle>`, nie komunikatem zapisu.

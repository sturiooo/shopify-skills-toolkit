# Shopify: wiedza z wdrożeń (skille Claude Code)

Zestaw dziesięciu skilli dla Claude Code z praktyczną wiedzą o Shopify: motywy (Liquid, sekcje,
PDP, koszyk), Admin API i CLI, B2B, dostawa, rynki i tłumaczenia, tokeny dla integratorów.
Treść powstała w realnych wdrożeniach sklepów, głównie polskich, i opisuje rzeczy, których nie ma
w dokumentacji albo które w niej łatwo przeoczyć: co zawiodło, jak to rozpoznać i jak naprawić.

- **Autor:** Igor Pieczyński. Skille autorskie, z trzema wyjątkami opisanymi niżej (adaptacje na licencji MIT).
- **Dla kogo:** zespół, który buduje i utrzymuje sklepy na Shopify z pomocą Claude Code.
- **Język:** polski. Nazwy API, plików motywu i komunikaty Shopify zostają w oryginale.
- **Dane klientów:** usunięte. Sklepy opisane są rodzajem i motywem („sklep z pluszakami, motyw Concept”),
  bez nazw, domen, osób, produktów i identyfikatorów.

Do użytku wewnętrznego zespołu.

## Instalacja

### Przez marketplace pluginów (zalecane)

Repozytorium jest jednocześnie pluginem i marketplace’em. W Claude Code:

```
/plugin marketplace add Sturiooo/shopify-skills-toolkit
/plugin install shopify-skills@igor-shopify
```

Albo z terminala:

```bash
claude plugin marketplace add Sturiooo/shopify-skills-toolkit
claude plugin install shopify-skills@igor-shopify
```

Repozytorium jest prywatne, więc Claude Code musi mieć dostęp do GitHuba bez pytania o hasło:
klucz SSH w `ssh-agent` albo `gh auth login` i `gh auth setup-git` (helper poświadczeń dla HTTPS).
Sama zmienna `GITHUB_TOKEN` nie wystarczy do automatycznych aktualizacji.

Aktualizacja:

```
/plugin marketplace update igor-shopify
```

albo `claude plugin update shopify-skills@igor-shopify`. Automatyczne aktualizacje włączysz w
`/plugin` → Marketplaces → `igor-shopify` → Enable auto-update. Wersja jest przypięta w
`.claude-plugin/plugin.json`, więc nowa treść dociera po podniesieniu wersji (patrz `CHANGELOG.md`).

Skille z pluginu mają prefiks: `/shopify-skills:shopify-koszyk` itd. Claude uruchamia je sam,
gdy temat rozmowy pasuje do opisu, więc zwykle nie trzeba ich wywoływać ręcznie.

### Ręcznie (bez marketplace)

Skopiuj katalogi z `skills/` do:

- `~/.claude/skills/` (dostępne we wszystkich projektach), albo
- `.claude/skills/` w repozytorium projektu (dostępne tylko tam, wspólne dla zespołu przez git).

```bash
git clone git@github.com:Sturiooo/shopify-skills-toolkit.git
cp -r shopify-skills-toolkit/skills/* ~/.claude/skills/
```

Przy instalacji ręcznej skille nie mają prefiksu i nie aktualizują się same.

## Skille

| Skill | Do czego | Kiedy się uruchamia (przykładowe prompty) | Co zawiera |
|---|---|---|---|
| `shopify-diagnostyka` | Potwierdzanie faktów, zanim ogłosisz przyczynę: pomiar zamiast założeń, cache storefrontu, DNS, stany magazynowe, konwersje GTM | „po wgraniu nic się nie zmieniło”, „ustawienie z panelu nie działa”, „domena pokazuje parking”, „w magazynie 0, a da się kupić”, „konwersje przestały się liczyć” | 15 plików referencyjnych, lista niżej |
| `shopify-audyt-liquid` | Przegląd kodu Liquid napisanego przez AI przed `theme push` | „sprawdź ten plik przed wgraniem”, „zrób review sekcji”, każdy push nowego `.liquid` | jeden `SKILL.md` z listą kontrolną |
| `shopify-koszyk` | Cart API, pasek darmowej dostawy i gratisu, dopłaty, pola własne, zgody i blokada kasy | „dodaj checkbox regulaminu w koszyku”, „gratis od 200 zł”, „pakowanie na prezent za 9 zł”, „prezent nie zeruje się z kodem rabatowym” | 10 plików referencyjnych |
| `shopify-produkt` | PDP i karty produktów: galeria per wariant, swatche, komplementarne, upsell, H1 | „galeria pokazuje zdjęcia innych wariantów”, „przebuduj kartę produktu”, „blok produktów komplementarnych znika”, „dwa H1 na produkcie” | 11 plików referencyjnych |
| `shopify-metapola` | Metapola kontra metaobiekty, definicje, typy, filtry, odczyt w Liquid | „dodaj tabelę rozmiarów per produkt”, „metapole się nie wyświetla”, „filtr po metapolu nie działa” | jeden `SKILL.md` |
| `shopify-sekcje` | Budowa i przeróbka sekcji i bloków motywu, slidery, fonty, port między motywami, sekcje z Figmy | „dodaj sekcję z opiniami”, „zrób slider”, „przenieś tę sekcję z innego motywu”, „zbuduj to z makiety Figma” | 25 plików referencyjnych |
| `shopify-cli-i-api` | Shopify CLI przy wielu kontach, `store execute`, zaskakujące pola Admin API, praca na motywie live | „pobierz motyw nowego sklepu”, „CLI nie widzi sklepu”, „wgraj na live”, „mutacja zwraca success, a nic się nie zmieniło” | 3 pliki referencyjne |
| `shopify-b2b-i-dostawa` | Natywne B2B (firmy, katalogi, cenniki, limity planów), strefy i stawki dostawy, punkty odbioru | „ceny hurtowe dla firm”, „katalog B2B nie działa na Grow”, „stawka wagowa do 5 kg”, „ukryj paczkomat dla gabarytów” | 6 plików referencyjnych |
| `shopify-rynki-i-tlumaczenia` | Języki, rynki, domeny, Translate & Adapt, tłumaczenia przez Admin API, hreflang | „dodaj język niemiecki”, „na /en/ jest polski tekst”, „przetłumacz sklep bez apki”, „domena przekierowuje na myshopify” | `SKILL.md` z 10 sekcjami + 1 plik referencyjny |
| `shopify-token-api` | Stały token Admin API dla integratora (Dev Dashboard, custom distribution) | „integrator prosi o klucz API”, „token do sklepu dla systemu ofert”, „shop_not_permitted”, „link instalacyjny jest nieprawidłowy” | 4 pliki referencyjne + `token.sh` |

### Zawartość skilli

### `shopify-diagnostyka` (16 pl.)

- `references/cache-storefrontu.md`: Cache storefrontu potrafi serwować KILKA różnych wersji naraz (2026-08-20, sklep z kawą funkcjonalną, Stretch).
- `references/curl-first.md`: Diagnostyka „curl-first”: jak potwierdzać fakty bez przeglądarki (2026-08); fałszywe „0 wyników” przez zsh.
- `references/kolor-wypalony-w-pliku.md`: Kolor nie znika mimo poprawnego CSS, bo siedzi w pikselach pliku (2026-09-22); odczyt piksela, przemalowanie bez obwódki, podmiana zdjęcia kolekcji przez API.
- `references/kolekcja-automatyczna-opoznienie.md`: Kolekcja automatyczna po zmianie tagów przelicza się ok. minutę: liczność i storefront kłamią, tagi na produkcie nie (2026-10-02).
- `references/konwersje-gtm.md`: Diagnostyka „przestały się liczyć konwersje”: GTM i Google Ads (2026-08-19); dodatkowo fallback widgetu Judge.me, FAQ per produkt z metapól, mapa punktów sprzedaży bez apki.
- `references/przekierowanie-na-wersje-robocza.md`: Przekierowanie 301 jest, a adres daje 404, bo cel to produkt w wersji roboczej; audyt reguł po statusie celu. Ta sama przyczyna w linkach menu `HTTP` i status `UNLISTED` chowający produkty z kolekcji (2026-09-24, 29).
- `references/przekierowania-trafnosc-po-migracji.md`: Przekierowania po migracji: 99% pokrycia, a 29% produktów trafia w inny typ (soft 404); pomiar z web.archive.org + `urlRedirects`, brak daty utworzenia reguły (2026-10-06).
- `references/sklep-wielojezyczny-czego-nie-tlumaczy-tlumaczenie.md`: Drugi język: puste próbki kolorów (osobne tłumaczenie `color_swatch_config`), duplikaty i opóźnienie filtra S&D z metapola, nieprzetłumaczalne tagi artykułów (etykieta z locale), obraz per język w sekcji; curl nie widzi paska tagów bloga (2026-10-09, Prestige).
- `references/tlumaczenie-metapola.md`: Playbook: „tłumaczenie metapola się nie wyświetla w danym języku”.
- `references/ustawienie-nie-dziala.md`: Diagnostyka „ustawienie z panelu NIE działa” w blokach FoxEcom/Sleek (2026-06).
- `references/zmierz-efekt-nie-znacznik.md`: Weryfikacja na efekcie, nie na śladzie zmiany: niejawna kolumna siatki, SEO strony głównej poza Admin API, rozrzut PageSpeed przez hCaptchę Shopify Forms (2026-09-25).
- `references/domena-dns-nazwa-pl.md`: Domena pokazuje parking zamiast sklepu: pytaj serwer autorytatywny, cache routera, format rekordów nazwa.pl (pełne nazwy, CAA z cudzysłowem, CNAME www odrzucany → A), CAA wymagane przez Shopify, MX zależny od A, poczta u innego dostawcy (2026-10-12/20).
- `references/domena-w-cudzym-koncie-cloudflare.md`: Domena delegowana do Cloudflare, ale nie ma jej na koncie klienta: para NS = konto, ślepa strefa w LH.pl, Connect zamiast Transfer, odtwarzanie strefy bez eksportu (wildcard fałszuje odczyt), NS osobno od przepięcia na Shopify (2026-10-13).
- `references/stany-zewnetrzny-magazyn.md`: „W magazynie 0, a w sklepie da się kupić”: śledzenie na dzień zamówienia, integracja (SellAsist) zapisuje tylko przy zmianie u siebie, fantom po zwrocie z restockiem, pełne porównanie z listy ofert SellAsist, naprawa (2026-10-16).
- `references/render-headless-mobile.md`: Render mobile w headless Chrome: `--window-size` to nie viewport (fałszywe „wychodzi poza ekran”), emulacja przez CDP, ukryte elementy na liście wystających, zrzuty po kolei, usuwanie banerów cookies (2026-10-18).

### `shopify-audyt-liquid` (1 pl.)

- `SKILL.md`: cała treść w jednym pliku (walidacja maszynowa, lista osądu, pułapki schematu, dostępność, format wyniku).

### `shopify-koszyk` (11 pl.)

- `references/blokada-checkoutu-zgoda.md`: Blokada checkoutu + reset zgody (Checkout Consent Checkbox), adaptacje do motywów Nook, FoxEcom i Ignite.
- `references/cart-api-podstawy.md`: Cart API: twarda wiedza dla każdego projektu.
- `references/checkbox-regulaminu.md`: Checkbox zgody (regulamin) w koszyku: gdzie go wstawić, żeby był widoczny (2026-08, motyw Wonder).
- `references/pakowanie-na-prezent.md`: Checkbox "pakowanie na prezent" w koszyku (dopłata): produkt-linia, nie opłata.
- `references/pasek-postepu-i-gratis.md`: Free-gift cart progress bar (Buy X Get Y hybryda).
- `references/pola-wlasne-i-klaviyo.md`: Pola własne w koszyku + integracja Klaviyo + checkbox zgody (2026-06, Sleek/FoxEcom).
- `references/zgoda-marketingowa-newsletter.md`: Checkbox zgody na marketing: newsletter form (RODO).
- `references/obowiazkowy-krok-przed-kasa.md`: Obowiązkowy krok (kreator dodatków) przed kasą: zapis stanu koszyka przy wejściu w krok, furtki do zamknięcia, test curlem (2026-09-28, Concept).
- `references/kreator-dodatkow-w-motywie.md`: Kreator dodatków w motywie zamiast apki bundle: czego nie da się bez Plus, właściwości `_` w panelu zamówienia, wiązanie po variant_id, pomiar sprzedaży przez metapole analyticsQueryable i ShopifyQL (2026-09-29, Concept).
- `references/prezent-bxgy-subskrypcje-i-laczenie.md`: Prezent od progu (Kup X, odbierz Y): subskrypcje nie liczą się do progu (`customerBuys.isSubscription`), łączenie z rabatem apki zestawów, ochrona przed dublem z kodem −100%, test trzech koszyków, prezent bez stanu albo tylko-B2B (2026-10-13); kod z `productDiscounts: false` czyni prezent płatnym, tani gratis zestawu przegrywa z kodem, test kodu bez kasy, blokada prezentu na sesję (2026-10-22).

### `shopify-produkt` (12 pl.)

- `references/blok-upsell.md`: Redesign bloku upsell: slider → statyczna lista poziomych wierszy (Sleek/FoxEcom).
- `references/galeria-slider-peek-mobile.md`: Galeria produktu: slider "peek" na mobile (centeredSlides + ułamkowy slidesPerView).
- `references/globalny-design-kart.md`: Globalny design kart produktów: rewrite snippets/card-product.liquid (FoxEcom).
- `references/karty-z-wariantami-koloru.md`: Karty produktów z wariantami kolorystycznymi, hover second image i ocenami Judge.me (sekcja product-tabs).
- `references/media-i-galeria-per-wariant.md`: Media i galeria PER WARIANT (zdjęcia + wideo): pełny playbook (2026-07-30/31, Concept/RoarTheme).
- `references/pdp-sleek-foxecom.md`: Karta produktu w motywie Sleek (FoxEcom): bloki, metapola, CSS i scope per-produkt.
- `references/pigulki-kategorii.md`: Pigułki kategorii na karcie produktu: link "within", aktywny marker, GOTCHA z przycinaniem strzałki.
- `references/produkty-komplementarne.md`: Blok produktów komplementarnych: redesign + render z metafielda (Sleek/FoxEcom).
- `references/przebudowa-pdp-sleek.md`: Lekcje: przebudowa PDP + koszyka + SEO (2026-06, Sleek/FoxEcom; Concept/RoarTheme).
- `references/seo-na-produkcie-h1.md`: SEO na produkcie Shopify: jeden H1 + H1 niosący frazę z metapola.
- `references/podmiana-zdjec-hd-fileupdate.md`: Podmiana zdjęć na wersje HD bez ruszania galerii (`fileUpdate` z `originalSource`), dopasowanie folderu klienta z Drive po hashu obrazu (2026-10-19).

### `shopify-metapola` (1 pl.)

- `SKILL.md`: cała treść w jednym pliku (metapole kontra metaobiekt, definicje, typy, limity filtrów, odczyt w Liquid, diagnoza).

### `shopify-sekcje` (26 pl.)

- `references/as-seen-in-press-bar.md`: Sekcja As Seen In (press bar).
- `references/blok-sku-z-prefiksem.md`: Blok SKU z konfigurowalnym przedrostkiem (label + bold + guard + padding).
- `references/budowa-od-zera.md`: Budowa nowej sekcji albo bloku motywu Shopify (OS 2.0, Horizon i pochodne) od zera, ze schematem, presetem, stylami i kluczami tłumaczeń.
- `references/carousel-i-slider.md`: Carousel/slider sekcji: przesuwanie transformacją zamiast hide/show.
- `references/dopasowanie-koloru.md`: Dopasowanie koloru z cudzego projektu do palety klienta (2026-08-20).
- `references/edycja-istniejacej-sekcji.md`: Dostosowywanie ISTNIEJĄCEJ sekcji motywu bez psucia reszty sklepu (`recently-viewed-products`, Sleek/FoxEcom).
- `references/fonty-i-easingi-z-motywu.md`: Fonty i easingi z motywu: zmienne CSS zamiast `font_picker`/hardkodu.
- `references/fonty-sleek-foxecom.md`: Architektura fontów motywu Sleek/FoxEcom: nagłówki HARDKODOWANE, globalny override w theme.liquid.
- `references/gotchy-css-liquid.md`: Gotchy CSS/Liquid z sesji 2026-08 (Maestrooo Impact/Airwave/Stretch, RoarTheme Concept).
- `references/ikony-w-bloku.md`: Ikony w bloku: zestaw motywu (`render 'icon'`) vs samodzielny + własna grafika.
- `references/js-przy-wielokrotnym-renderze.md`: Sekcja renderowana wielokrotnie: JS pod jednym globalnym guardem + registry.
- `references/linklist-zamiast-blokow.md`: Menu (`link_list`) jako szybkie źródło wielu pozycji - zamiast bloków po kolei.
- `references/migracja-px-na-rem.md`: Migracja rozmiarów z px na rem, globalne pokrętło skali i dwie pułapki migracji: przeliczenie wartości w szablonach oraz wyścig sekcja/szablon w jednym push (2026-09-22, motyw Nook).
- `references/pakiet-sekcji-landingu.md`: Pakiet customowych sekcji landingu (2026-06, Sleek/FoxEcom).
- `references/port-miedzy-motywami.md`: Przenoszenie sekcji 1:1 między motywami: pełny playbook (2026-08-19/20, Release → Stretch).
- `references/selektor-jezyka-w-header.md`: Selektor języka w header na mobile (zamiast na dole hamburger menu).
- `references/slider-opinii.md`: Nowa sekcja slidera opinii od zera (samodzielna, FoxEcom/Sleek).
- `references/stretch-wyroznianie-slowa.md`: Stretch (Maestrooo): wyróżnianie słowa w nagłówku jest NATYWNE (2026-08-20).
- `references/wlasny-blok-w-main-product.md`: Dodawanie własnego bloku do istniejącej sekcji `main-product` (zamiast nowej sekcji).
- `references/wzorce-ui.md`: Wzorce UI z tej sesji: reużywalne (2026-06).
- `references/z-makiety-figma.md`: Budowa sekcji z Figmy „element po elemencie”: lekcje z PDP (2026-07-31/08-01, Local 3.2.1 KrownThemes).
- `references/ziarno-grain.md`: Ziarno (grain/noise) na zdjęciach produktów: wybór techniki zależy OD TŁA zdjęcia.
- `references/grain-horizon.md`: Horizon (sklep z biżuterią): tło sekcji jako osobne rodzeństwo treści, efekt grain (warstwa vs filtr alfa), SVG bez wymiarów = 0×0, `.with-overlay` ma własny pseudo-element, `range` ≥3 kroki.
- `references/wymiary-banerow-slideshow.md`: Wymiary banerów dla slideshow o stałej wysokości: proporcja zależna od szerokości ekranu, kadr + strefa bezpieczna, osobny plik mobile (2026-10-12, motyw z rodziny Horizon).
- `references/tekst-na-cala-szerokosc.md`: Tekst (np. imię, logo) na całą szerokość: `container-type` + `cqw` zamiast skryptu (CLS 0,114 → 0,012), jak zmierzyć stałą, obcinanie polskich znaków nad literą (2026-10-18).

### `shopify-cli-i-api` (4 pl.)

- `references/admin-api-scopey-i-pola.md`: Admin API: scope'y i pola, które zaskakują (2026-08); scalanie duplikatów produktów w warianty; składnia atrybucji ShopifyQL dla kanału AI.
- `references/cli-workflow-wielu-kont.md`: Shopify CLI: workflow wielu kont, pull/push, Admin GraphQL bez aplikacji (2026-06).
- `references/praca-na-motywie-live.md`: Praca na motywie LIVE i konflikty z edytorem: reguły potwierdzone w praktyce (2026-08); zmiana uchwytu przepisuje szablony.

### `shopify-b2b-i-dostawa` (7 pl.)

- `references/b2b-i-dostawa-gotchy.md`: Shopify CLI, B2B i dostawa: gotchy z 2026-08-13/17 (limit tokenów `store auth`, katalog B2B przez rynek, strefy, przekierowania, Rollouts i SimGym, FAQ w szablonie, `themeFilesUpsert`).
- `references/b2b-jak-dziala.md`: Shopify B2B: jak to naprawdę działa i ile z tego jest natywne (2026-08, plan Grow), limit 3 katalogów, kolejność wdrożenia, checklista danych od klienta.
- `references/cenniki-detal-kontra-b2b.md`: Który cennik wygrywa: detal kontra B2B; pole `market` lokalizacji firmy nie rozstrzyga ceny, pułapka `RELATIVE`, bezpieczna kolejność zmiany cen (2026-09-23).
- `references/delivery-api-strefy-i-stawki.md`: Delivery API: strefy wysyłki i stawki przez `deliveryProfileUpdate` (2026-06), `zonesToUpdate.countries` zastępuje listę, zmiana progu wagi (`criteriaUnit: "kg"`) i wyłączanie stawki (2026-10-01).
- `references/punkty-odbioru-i-ukrywanie-metod.md`: Octolize (cena wg planu Shopify, ORLEN Paczka) i Payflow (zestawy warunków, wykluczenia przewoźników zamiast listy dozwolonych) (2026-09-30); COD w Payflow dopasowuj po „COD”, Globe Pickup Points i bliźniacze stawki paczkomatu (2026-10-12).
- `references/produkty-tylko-dla-b2b.md`: Produkty tylko dla firm: wymagany kanał Sklep online + katalog detaliczny bez nich, `/products.json` ignoruje katalog rynku (2026-10-09).

### `shopify-rynki-i-tlumaczenia` (2 pl.)

- `references/tlumaczenia-przez-api.md`: Workflow `translatableResources` → `translationsRegister`, gotowe zapytania (zwalidowane na 2026-07), klucze per typ zasobu, audyt pokrycia, scope'y.

### `shopify-token-api` (6 pl.)

- `references/staly-token-krok-po-kroku.md`: **Główna procedura.** Kroki człowieka i Claude, kolejność linków, wymiana kodu, weryfikacja.
- `references/pulapki-i-bledy.md`: Komunikat błędu albo coś „nie działa”: tabela błąd → przyczyna → naprawa, blokady auto mode.
- `references/client-credentials.md`: Sklep w organizacji agencji i integrator umie odnawiać token co dobę.
- `references/wiadomosc-dla-integratora.md`: Gotowy tekst do wysłania programiście (bez tabelek, do wklejenia).
- `token.sh`: Skrypt: `url` buduje link autoryzacyjny, `exchange` wymienia kod na token, `verify` sprawdza token.

## Jak to działa

- Claude Code na starcie widzi tylko `name` i `description` każdego skilla. Pełny `SKILL.md` wczytuje
  dopiero wtedy, gdy temat rozmowy pasuje do opisu (albo gdy wywołasz skill ręcznie).
- `SKILL.md` jest krótki: najważniejsze zasady i tabela „Co tu jest”. Szczegóły leżą w `references/`,
  a Claude czyta **pojedynczy plik**, który pasuje do problemu, a nie cały katalog. Dzięki temu skill
  z 25 plikami nie zjada kontekstu.
- Pliki referencyjne mają daty. Shopify zmienia API i panel co kwartał, więc data mówi, kiedy dana
  obserwacja była prawdziwa. Przy rozbieżności z dokumentacją wygrywa świeży pomiar.
- Część wskazówek zakłada narzędzia: Shopify CLI (`theme`, `store auth`, `store execute`) i serwer
  Shopify Dev MCP (`validate_theme`, `validate_graphql_codeblocks`). Bez nich skille dalej działają
  jako wiedza, tylko walidację robisz inaczej.

## Zasady pracy, które skille zakładają

- **Najpierw sprawdź przesłankę, potem stawiaj diagnozę.** Najczęstszy błąd to pomiar czegoś innego,
  niż się myśli (podgląd innego motywu, cache CDN, dane, które nie mogą uruchomić funkcji).
- **Nie ufaj komunikatowi „success”.** Po każdym wgraniu pobierz plik z powrotem i sprawdź konkretne klucze
  albo realny render.
- **Na motywie live: `pull` tuż przed pushem**, nowa wersja budowana z tego stanu, po pushu znowu `pull`.
  Zapis w edytorze motywu nadpisuje cały szablon kopią z przeglądarki.
- **Najpierw sekcja (schemat), potem szablon JSON**, osobnymi pushami.
- **Kotwicz się po typie sekcji, nie po jej ID.** Klient, który doda sekcję w edytorze, nadaje jej nowe ID.
- **Policz skalę na danych** (Admin API), zanim napiszesz klientowi „naprawione”.
- **Nowy mechanizm testuj na tymczasowym produkcie w wersji roboczej**, nie na danych klienta. Potem go usuń.
- **Backup przed każdą operacją destrukcyjną**, z opisem, jak przywrócić stan.
- **Rozszerzaj to, co motyw już ma**, zamiast pisać równoległy mechanizm. Kolejność: natywne w motywie,
  gotowa sekcja z biblioteki zespołu, dopiero potem kod od zera.
- **Gdy wymagania klienta mogą się odwrócić, daj przełącznik w ustawieniach motywu**, nie hardkod.

## Polecane do doinstalowania (cudze, nie są częścią tego repo)

- [Shopify AI Toolkit](https://github.com/Shopify/shopify-ai-toolkit): oficjalny plugin Shopify
  (dokumentacja, walidacja GraphQL i Liquid). Instalacja: `/plugin marketplace add Shopify/shopify-ai-toolkit`.
- [baslefeber/shopify-skills](https://github.com/baslefeber/shopify-skills) (MIT, Bas Lefeber):
  oryginały, z których zaadaptowano `shopify-audyt-liquid`, `shopify-metapola` i `references/budowa-od-zera.md`
  w `shopify-sekcje`.
- [henkisdabro/wookstar-claude-plugins](https://github.com/henkisdabro/wookstar-claude-plugins) (MIT):
  skille Google Analytics 4 i Google Tag Manager.
- Skill „pagespeed-insights” (autor: Ender Puentes, licencja „free use”): audyt wydajności według
  wytycznych PageSpeed Insights i Core Web Vitals. Link do źródła do uzupełnienia.
- Playwright CLI: automatyzacja przeglądarki do pomiaru renderu, gdy weryfikacja plikowa nie wystarcza.

## Wkład

Zasady dodawania i poprawiania skilli, format frontmattera i obowiązkowy check anonimizacji
opisuje [CONTRIBUTING.md](CONTRIBUTING.md). Każdy PR przechodzi:

```bash
python scripts/check-anonymization.py /sciezka/poza/repo/czarna-lista.txt
claude plugin validate .
```

## Licencja

Do użytku wewnętrznego zespołu. Repozytorium nie ma pliku licencji. Fragmenty zaadaptowane
z baslefeber/shopify-skills pozostają na licencji MIT ich autora (informacja w odpowiednich plikach).

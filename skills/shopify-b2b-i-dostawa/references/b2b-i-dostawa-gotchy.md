# Shopify CLI, B2B i dostawa: gotchy z 2026-08-13/17 (sklep z pluszakami, motyw Concept)

### CLI trzyma tylko **5 tokenów `store auth`** naraz

Podłączenie szóstego sklepu **po cichu wypycha najstarszy token**. Objaw: sklep, z którym pracowałeś
tydzień temu, znika z `shopify store auth list` i `store execute` przestaje działać, mimo że nikt się
nie wylogowywał. Naprawa to zwykłe ponowne `store auth`, ale **nigdy `shopify auth logout`**, bo ten
kasuje sesje do wszystkich sklepów naraz.

### Katalog B2B: na planach poza Plus MUSI iść przez rynek

`catalogCreate` z `context.companyLocationIds` odbija się błędem
**`UNPERMITTED_ENTITLEMENTS_DIRECT_CATALOG_ASSIGNMENT`** („Katalogów przypisanych do lokalizacji firmy
nie można aktywować w Twoim planie"). Poprawna kolejność: **rynek typu COMPANY_LOCATION → katalog
z `context.marketIds` → cennik z `catalogId`**.

- `MarketConditionsCompanyLocationsInput` przyjmuje **dokładnie jeden** argument: albo `applicationLevel`,
  albo `companyLocationIds`. Podanie obu = „requires exactly one argument, but 2 were provided".
- `applicationLevel: ALL` = wszystkie istniejące i przyszłe lokalizacje firm. Wygodne, ale **dwa aktywne
  rynki tego typu to konflikt**: sprawdź, czy w sklepie nie wisi stary testowy rynek z absurdalnym rabatem.
- Cennik **zawsze wymaga bazowej korekty** (`parent.adjustment`), nie da się zrobić „samych cen sztywnych".
- **`priceList.prices` BEZ `originType` zwraca też ceny RELATIVE** (wyliczone z procentu) dla całego
  katalogu. Pytając „co ma cenę wpisaną ręcznie", filtruj **`originType: FIXED`**, inaczej dostaniesz
  wszystkie produkty sklepu i opublikujesz w katalogu rzeczy, których tam nie chcesz.
- **`publicationUpdate` ze 100 pozycjami wywala „Przekroczono limit jednoczesnych aktualizacji publikacji"**,
  a partie po 20 z krótkim `sleep` przechodzą.
- `companies`, `companyLocationsCondition` i zakładanie firm wymagają **`read_customers` / `write_customers`**;
  `write_products` nie wystarcza.

### Strefy dostawy

- **Każdemu krajowi dawaj `includeAllProvinces: true`.** Bez tego kraje z prowincjami odbijają zapis
  („Kraj: »Ireland« musi mieć powiązaną co najmniej jedną prowincję"). Wcześniej znane dla GB, dotyczy też IE.
- **Kolejność przy wymianie profilu:** najpierw skonfiguruj profil **domyślny**, dopiero potem
  `deliveryProfileRemove` na własnym. Warianty wracają do domyślnego, więc odwrotna kolejność
  zostawia cały katalog bez dostawy.
- Profil domyślny bez stref = w kasie „brak dostępnych metod dostawy" dla wszystkiego, co nie jest
  przypisane do profilu własnego. Warto to sprawdzać jako pierwsze przy zgłoszeniu „nie da się kupić".

### Przekierowania: ścieżka i ograniczenia (Centrum Pomocy, 2026-08)

`Treść → Menu → Wyświetl przekierowania adresów URL` *(Content → Menus → View URL Redirects)*,
**nie** w sekcji Sklep online, gdzie większość ich szuka.

- **Nie da się przekierować adresu, który działa**, tylko taki, który zwraca 404.
- **Brak łańcuchów**; ścieżki zarezerwowane (`/products`, `/collections`, `/cart`) wyłączone.
- Import masowy z CSV jest dostępny (przycisk **Importuj** + szablon).
- Limit 100 000 przekierowań (20 mln na Plus).
- Przy sprzedaży wielorynkowej **nie przenoszą się automatycznie na podfoldery językowe**.
- W panelu zmiana uchwytu proponuje utworzenie przekierowania (pole wyboru), ale **przez API i przy
  zmianach masowych NIE powstaje ono samo**. Potwierdzone: 172 zmienione uchwyty, zero przekierowań.

### Rollouts i SimGym (Winter '26 Edition)

**Rollouts**: `Rynki → Rollouts`. Opakowanie na zmianę: zaplanowane uruchomienie, stopniowe wdrożenie
na % ruchu, eksperyment A/B. Typy zmian: motyw główny (edycja albo podmiana) oraz kasa i konta klienta.
`Launch immediately` **wymaga 100% ruchu**. `Add end date` → `Will roll back to 0%` (domyślne) albo
`Will be applied permanently`; kampania sezonowa zawsze z rollbackiem.
**Rollouts od planu Basic, ale eksperymenty A/B i analityka rolloutów wymagają Grow lub wyżej.**
Metryki: uruchomienia: Gross sales, AOV, Orders, Conversion rate; eksperymenty: Conversion rate,
Bounce rate, Reached checkout rate. **Dokumentacja NIE podaje progu istotności ani minimalnego czasu testu.**

**SimGym**: aplikacja z App Store, „AI Research Preview". Wymaga motywu **Liquid** (nie headless),
włączonego **Shopify Network Intelligence**, sklepu **bez hasła** i ≥1 produktu. Tryby: porównanie
motywu aktywnego z roboczym albo analiza jednego motywu; obszar skupienia: strona główna, produkty,
kolekcje, koszyk, wyszukiwarka. Rozliczenie: 1 symulacja = 1 kredyt. Shopify zastrzega, że **wyniki
mogą różnić się od zachowania prawdziwych kupujących**.
Reguła robocza: **SimGym generuje hipotezy, Rollouts je rozstrzyga.**

### FAQ wspólne dla wszystkich produktów = sekcja w szablonie, NIE metapola

Sekcja umieszczona w `templates/product.json` jest wspólna dla **każdego produktu** korzystającego
z tego szablonu. Metapola są do treści różnej per produkt, a przy FAQ chcesz odwrotnie.
Motywy RoarTheme/Concept mają gotową sekcję `faq` z blokami `question` (`inline_richtext title`
+ `richtext text`), często **już wstawioną w szablon z trzema blokami demo Shopify**
(„Frequently asked question" / „Use this text to answer questions…"). Warto to sprawdzić i podmienić,
zanim sklep wyjdzie zza hasła.

**Uwaga:** ta sama sekcja na stronie głównej i na produkcie to **dwa niezależne zestawy bloków**.
Shopify nie ma jednego źródła treści dla sekcji w dwóch szablonach. Przy większej liczbie miejsc
lepsza jest osobna strona FAQ i linkowanie do niej.

### Zapis pliku motywu przez Admin API (gdy `theme push` niedostępny)

`themeFilesUpsert(themeId, files: [{filename, body: {type: TEXT, value}}])`.
Sprawdzony wzorzec bezpieczny dla motywu LIVE:
**świeży odczyt pliku → modyfikacja w pamięci → zapis kopii sprzed zmiany do lokalnego katalogu z backupami → upsert →
ponowny odczyt i weryfikacja konkretnych kluczy.** `templates/*.json` mają na początku komentarz
`/* … */`: trzeba go odciąć przed `json.loads` i **dokleić z powrotem** przy zapisie.

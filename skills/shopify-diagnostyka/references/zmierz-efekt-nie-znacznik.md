# Zmierz efekt, nie znacznik (2026-09-25, sklep na motywie Sleek i sklep z figurkami kolekcjonerskimi)

Trzy razy w jednej sesji „weryfikacja” sprawdzała ślad zmiany (klasę w HTML, odpowiedź mutacji,
jeden przebieg pomiaru), a nie efekt, który miał zobaczyć klient. Za każdym razem wynik był fałszywie pozytywny.

| Teza | Co było naprawdę | Czego nie sprawdziłem |
|---|---|---|
| „Formularz ma pola jedno pod drugim, bo kontener ma `f-grid-1-cols`” | e-mail stał obok imienia | pozycji pól (`getBoundingClientRect`) |
| „Tytuł strony głównej ustawiony, `metafieldsSet` bez userErrors” | storefront dalej pokazywał samą nazwę sklepu | `<title>` na stronie po zapisie |
| „hCaptcha w PSI to Shopify blokujący bota” | ładuje ją Shopify Forms każdemu odwiedzającemu | zwykłej wizyty w przeglądarce |

## Siatka z 1 kolumną i `grid-column: 1 / 3` dobudowuje drugą kolumnę

- **`grid-column-end: 3` w siatce z jedną kolumną tworzy niejawną 2. kolumnę** (szerokość `auto`),
  a kolejne pole wskakuje do niej obok poprzedniego, z inną szerokością. Motyw Sleek, `assets/section-contact-form.css`,
  reguła `.contact__fields .form-field--full`. Recepta: `grid-column: 1 / -1` (do końca siatki jawnej),
  działa i przy 1, i przy 2 kolumnach. Przy każdym przełączniku liczby kolumn grepuj CSS pod kątem
  `grid-column-end` / `span` na dzieciach.

## Tytułu i opisu strony głównej nie ustawisz przez Admin API

- **Metapola sklepu `global.title_tag` / `global.description_tag` zapisują się, ale storefront ich nie czyta.**
  Preferencje sklepu (tytuł i opis strony głównej) nie są wystawione w Admin API. Recepta: zapas w motywie
  (ustawienie tekstowe używane, gdy `request.page_type == 'index' and page_title == shop.name`), a martwe metapola
  usunąć `metafieldsDelete`. Weryfikacja zawsze na `<title>` pobranym ze sklepu.

## Rozrzut PageSpeed: najpierw diff żądań, potem wniosek

- **Wynik tej samej strony skakał od 38 do 75 (telefon).** Różnica między przebiegami: +130 żądań i +920 KB z `hcaptcha.com`.
  Inicjator: `cdn.shopify.com/extensions/.../forms-*/` (app embed Shopify Forms, popup newslettera). Średnio: 73 bez, 51 z hCaptchą.
  Recepta: porównaj żądania per domena między najlepszym i najgorszym przebiegiem, znajdź inicjator
  (CDP `Network.requestWillBeSent` → `initiator.stack`) i potwierdź w zwykłej wizycie z normalnym User-Agentem,
  zanim uznasz coś za artefakt testu. Mediana z min. 5 przebiegów, bez odrzucania „dziwnych”.

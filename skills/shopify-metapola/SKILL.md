---
name: shopify-metapola
description: "Modelowanie danych własnych w Shopify: metapole kontra metaobiekt, definicje, typy, odczyt w Liquid i filtrowanie. Uruchamiaj, gdy trzeba dołożyć produktowi albo kolekcji własne pole (tabela rozmiarów, skład, opis per wariant, dane do zakładek), gdy planujesz metaobiekty, albo gdy metapole nie wyświetla się mimo poprawnego kodu."
---

# Metapola i metaobiekty

Adaptacja `shopify-metafields-architect` z [baslefeber/shopify-skills](https://github.com/baslefeber/shopify-skills)
(MIT, Bas Lefeber / learnshopify.dev), scalona z lekcjami z realnych wdrożeń.

## Co tu jest

Ten skill nie ma katalogu `references/`: cała treść jest w tym pliku.

| Sekcja | Temat |
|---|---|
| Wybór: metapole czy metaobiekt | kiedy które, koszt metaobiektów |
| Zanim cokolwiek odczytasz: definicja | definicje, kontrola dostępu przy tworzeniu przez API |
| Typy, które zaskakują | rich text bez tabel, co filtruje, limit 128 elementów listy, `variant_reference` w panelu |
| Limity filtrów przy dużym katalogu | 5 000 produktów, 100 wartości, 25 filtrów |
| Odczyt w Liquid | `.value`, listy referencji powyżej 50 pozycji |
| Gdy metapole się nie wyświetla | kolejność sprawdzania |
| Uwaga przy zapisie przez API | `productUpdate` z `seo` kasuje `description` |

## Wybór: metapole czy metaobiekt

- **Metapole** to pole doklejone do istniejącego zasobu (produkt, wariant, klient, kolekcja, sklep).
  Domyślny wybór dla danych jednego zasobu, np. „instrukcja pielęgnacji tego produktu".
- **Metaobiekt** to osobny typ rekordu, do którego odwołuje się wiele zasobów. Wybierz go,
  gdy dana jest **bytem samym w sobie**, np. wspólna tabela rozmiarów albo profil producenta.

**Zanim sięgniesz po metaobiekty, policz koszt.** W sklepie na motywie Local (KrownThemes) zejście
z metaobiektów na 84 zwykłe metapola rozwiązało problem „nie da się tego edytować", bo podpięte
metapole kasowało render bloków, a wpisy metaobiektu były współdzielone między produktami.

## Zanim cokolwiek odczytasz: definicja

Metapole **bez definicji nie istnieje dla storefrontu**. To najczęstsza przyczyna
„metapole nie działa". Definicja ustala właściciela, typ, przestrzeń nazw i klucz
(zwykle `custom.nazwa`).

Tworzenie przez API, pułapka: **w przestrzeni `custom` NIE podawaj `access.admin`**.
Serwer odbija komunikatem, że musi to być `public_read_write`, a enum przyjmuje tylko
`MERCHANT_*`. Wysyłaj sam `access: { storefront: PUBLIC_READ }`.

W przestrzeni `shopify` (definicje standardowe) **nie podawaj kontroli dostępu w ogóle**,
inaczej dostaniesz „Ustawianie kontroli dostępu dla definicji w tej przestrzeni nazw
jest niedozwolone".

## Typy, które zaskakują

- **`rich_text_field` NIE MA WĘZŁA TABELI.** Zna root, akapit, nagłówek, listę, element listy,
  tekst i link. Tabelę trzymaj w `multi_line_text_field` i składaj Liquidem.
- **Filtrują: `single_line_text_field`, `list.single_line_text_field`, `number_integer`, `number_decimal`,
  `boolean`, `metaobject_reference`, `list.metaobject_reference`** (shopify.dev, storefront filtering).
  Listy tekstów FILTRUJĄ, każda wartość osobno (potwierdzone 24.09.2026 w sklepie z figurkami
  kolekcjonerskimi; wcześniejszy zapis „listy nie filtrują” był błędny). Definicja musi mieć włączone
  filtrowanie, a sam filtr włącza się **wyłącznie w aplikacji Search & Discovery**. Liczby renderują się
  jako zakres, więc motyw, który pomija filtry zakresowe (np. quick-filter w Ignite), ich nie pokaże:
  wtedy tekst ze słownikiem.
- `metaobject_reference` może wskazywać definicję, która nie istnieje. Sierota po testach,
  nie przenoś jej przy migracji.
- **Lista w metapolu (`list.*`) mieści maksymalnie 128 elementów.** 129 odbija `INVALID_VALUE`
  „Value ma więcej niż 128 elementów.” (test w sklepie z pluszakami, 04.10.2026). Model „lista dozwolonych”
  przy rosnącym katalogu szybko w to uderza: wyłącz z listy kategorie zawsze dostępne albo trzymaj
  listę wyjątków (krótszą stronę). Licz zapas przy każdej dostawie nowych pozycji.
- **Opis definicji: maks. 255 znaków** (`TOO_LONG`). `metafieldsSet` z jawnym `type` działa też BEZ
  definicji, a utworzona później definicja przejmuje istniejące wartości (`metafieldsCount` od razu pełny),
  więc nieudane utworzenie definicji przed migracją nie unieważnia zapisanych danych.
- **Pole `variant_reference` / `list.variant_reference` w panelu pokazuje miniaturę TYLKO zdjęcia przypiętego do wariantu.**
  Zdjęcie produktu się nie liczy, więc warianty „Default / Default” bez przypiętego medium wyglądają jak puste wiersze
  z samą nazwą (sklep z pluszakami, 13.10.2026: 90 dodatków). Naprawa: `productVariantAppendMedia` z `featuredMedia` produktu,
  najpierw sprawdź, czy warianty różnią się tylko rozmiarem (inaczej przypniesz zdjęcie w złym kolorze). Storefront się nie zmienia,
  jeśli motyw i tak robi `variant.image || product.image`.

## Limity filtrów przy dużym katalogu (sklep z częściami samochodowymi, 25.09.2026)

Sprawdzone w help.shopify.com (Search & Discovery filters). Przy katalogu rzędu dziesiątek tysięcy
produktów te trzy limity decydują o architekturze, zanim zaprojektujesz choć jedno pole:

- **Kolekcja z ponad 5 000 produktów NIE WYŚWIETLA filtrów.** `all` przy 76 tys. produktów nie ma
  filtrów wcale. Każda wyszukiwarka „wybierz auto / rozmiar” oparta na `collection.filters` z `/collections/all`
  (np. `sections/quick-filter.liquid` w Ignite, pobiera `/collections/all?view=filters`) będzie miała puste
  listy. Recepta: podkolekcje po rodzaju produktu poniżej 5 000 szt., a listy wyszukiwarki z własnego JSON-a
  lub katalogu, nie z filtrów.
- **Filtr pokazuje najwyżej 100 wartości.** Model auta, kod lakieru, numer katalogowy to nie są filtry
  panelu bocznego. Wartości przeliczają się po zawężeniu, więc kaskada marka → model może się zmieścić:
  sprawdź na realnych danych.
- **25 filtrów na cały sklep**, łącznie z ceną i dostępnością. Filtr pokazuje się tylko w kolekcji, w której
  ma wartości, więc filtry branżowe (felgi, lampy) nie przeszkadzają w innych kategoriach.

Wyszukiwarka w nagłówku nie przeszukuje metapól `custom.*`: numery katalogowe trzeba dopisać do tytułu,
opisu albo tagów, jeśli mają być wyszukiwalne.

## Odczyt w Liquid

Metapola typowane wymagają `.value`, żeby zwrócić obiekt zamiast stringa:

```liquid
{{ product.metafields.custom.material.value }}
```

Dla referencji do metaobiektu `.value` zwraca sam obiekt, więc można schodzić w pola.

**Lista referencji powyżej 50 pozycji (15.10.2026).** `m.value.size` zwraca pełną liczbę (58),
ale `m.value | map: 'id'` i `{% for x in m.value %}` dają **maksymalnie 50**. `m | json` odpada
(„json not allowed for this object”). Gdy potrzebujesz samych ID, czytaj surową wartość pola:

```liquid
{%- assign ids = m | append: '' | remove: 'gid://shopify/ProductVariant/' | remove: '[' | remove: ']' | remove: '"' | remove: ' ' -%}
```

Wynik `123,456,...` ma komplet. Logikę list > 50 testuj na realnym renderze, nie na danych z Admin API.

## Wzorzec zalecany: najpierw edytor, metapole jako nadpisanie

Daj ustawienia sekcji jako wartości domyślne, a metapole jako opcjonalne nadpisanie
per produkt. Mniej tarcia dla klienta, a zaawansowane przypadki nadal działają.

**Zanim dołożysz nową powierzchnię, sprawdź, czy motyw już nie czyta tego metapola.**
W sklepie z obuwiem sekcja zakładek czytała `custom.size_chart` od początku, o mało nie powstał
drugi, równoległy mechanizm obok istniejącego.

## Czego nie robić

- parsowanie tytułów, uchwytów albo tagów zamiast pola
- JSON wciśnięty w pole tekstowe bez typu
- obejścia przez `localStorage`
- odczyt metapola bez definicji

## Gdy metapole się nie wyświetla

Sprawdzaj w tej kolejności:

1. czy **definicja istnieje** i ma `storefront: PUBLIC_READ`
2. czy **dane w ogóle są**: policz pokrycie, ile obiektów faktycznie ma to pole.
   W sklepie z pluszakami galeria per wariant „działała losowo", bo filtrowała po metapolu,
   a 95 z 96 wariantów miało zdjęcia przypisane natywnie
3. czy czytasz **właściwy plik**, ten sam komponent bywa zduplikowany w motywie
4. czy wersja językowa ma tłumaczenie, jeśli sklep jest wielojęzyczny (skill `shopify-rynki-i-tlumaczenia`)

## Uwaga przy zapisie przez API

`productUpdate` z `seo: { title }` **kasuje `description`**, a `userErrors` jest puste.
Zawsze wysyłaj oba pola i porównaj stan przed i po. Ta sama ostrożność dotyczy
każdego wejścia, które nadpisuje cały obiekt zagnieżdżony.

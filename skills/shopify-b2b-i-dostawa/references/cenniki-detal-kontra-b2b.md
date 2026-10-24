# Który cennik wygrywa: detal kontra B2B, i jak to sprawdzić przed zmianą

Ustalone pomiarem na sklepie z pluszakami (motyw Concept, 22-23.09.2026), ale mechanika jest niezależna od sklepu.

## Cennik katalogu przebija cenę wpisaną w produkcie

Cena stała z cennika podpiętego do rynku **przykrywa cenę z produktu** dla tego rynku.
To jest sposób na sprzedaż w innej walucie niż waluta sklepu, gdy waluty sklepu nie można
zmienić (może to zrobić wyłącznie właściciel konta). Ceny w produktach zostają, ale przestają
mieć znaczenie dla klienta z tego rynku.

## Pole `market` na lokalizacji firmy NIE mówi, z którego cennika liczy się cena B2B

To najgroźniejsza pułapka tej konstrukcji. W tym sklepie wszystkie lokalizacje firm miały
`companyLocation.market` ustawiony na rynek REGION niosący cennik DETALICZNY, co sugerowało,
że kontrahenci kupują po detalu i że każda zmiana detalu popsuje im ceny.

**Pomiar pokazał co innego.** `productVariant.contextualPricing(context: {companyLocationId})`
na jednym wariancie: lokalizacje PLN dostały cenę z cennika hurtowego PLN, lokalizacje EUR cenę
z cennika hurtowego EUR. Żadna nie dostała ceny detalicznej.

**Wniosek: katalogi typu COMPANY_LOCATION wygrywają, a `market` na lokalizacji dotyczy obecności
webowej, nie rozstrzygania cennika.** Nigdy nie wnioskuj o cenie B2B ze struktury rynków.
Zmierz `contextualPricing` przed zmianą i po niej, na tym samym wariancie.

**Gotcha pomiaru:** dla lokalizacji w walucie innej niż waluta sklepu `contextualPricing` zwraca
kwotę przeliczoną po kursie dnia, więc dwa odczyty tego samego wariantu różnią się o grosz
(35,37 kontra 35,39 kontra 35,40). To dryf kursu, nie zmiana ceny. Rozstrzyga odczyt ceny stałej
z cennika, nie `contextualPricing`.

## Warunek krytyczny: pokrycie cennika musi być pełne

Cennik z regułą bazową `PERCENTAGE_DECREASE 0` nadaje wariantowi **bez ceny stałej** typ
`RELATIVE`, co znaczy **ta sama liczba w innej walucie**. Cena 219,99 zł staje się 219,99 EUR,
czyli około czterokrotnie za drogo.

Po każdym wgraniu policz rozkład `originType` w CAŁYM cenniku (ma być zero `RELATIVE`).
`fixedPricesCount` nic nie mówi o pokryciu, trzeba porównać z
`productVariantsCount(query: "product_status:active")`.

**Realny przykład takiej dziury:** cenniki hurtowe tego sklepu mają po 75 pozycji `RELATIVE`,
bo dodatki świadomie usunięto z hurtu. W cenniku PLN to tylko brak rabatu, ale w cenniku EUR
kontrahent widzi liczbę ze złotówek jako euro, czyli 9,99 EUR zamiast około 2,40 EUR.
**Usunięcie ceny z cennika nie wyłącza pozycji, tylko przełącza ją na regułę bazową.**

## Waluty lokalne rynku a „dokładnie te ceny"

`currencySettings.localCurrencies` działa na CAŁY rynek, nie na wybrany kraj.
Przy `false` każdy kraj rynku widzi walutę bazową (np. wszyscy EUR).
Przy `true` kraje spoza tej waluty widzą swoją, przeliczoną z ceny z cennika po kursie dnia,
zaokrągloną do okrągłej wartości (`roundingEnabled`).

Tych dwóch rzeczy nie da się mieć naraz: „każdy kraj ma dokładnie kwotę z pliku"
wyklucza „kraje spoza strefy euro mają swoją walutę". Wyłóż to klientowi wprost, bo
przy takim zgłoszeniu łatwo przełączać tam i z powrotem (u nas trzy razy w jednej dobie).

## Kolejność bezpiecznej zmiany cen

1. Zrzuć obecny cennik do pliku (backup z sumą kontrolną cen).
2. Ustal walutę pliku wejściowego **porównaniem** z istniejącymi cennikami, nie z nazwy kolumny:
   ile pozycji już pasuje co do grosza. U nas 467 z 895 pasowało, co przesądziło, że to EUR
   i że plik jest aktualizacją, a nie nowym cennikiem.
3. Zmierz `contextualPricing` dla każdej lokalizacji firmy PRZED.
4. Wgraj `priceListFixedPricesAdd` partiami po 50 (mutacja działa jak nadpisanie po wariancie,
   więc jest idempotentna i można wznawiać).
5. Odczyt zwrotny, porównanie 1:1 z plikiem, kontrola zera `RELATIVE`.
6. Zmierz `contextualPricing` PO i porównaj z punktem 3.
7. Pomiar na storefroncie `?country=XX` na kilku krajach, bo tylko to pokazuje, co widzi klient.

# Migracja rozmiarów z px na rem i skalowalna typografia

Wdrożone 22.09.2026 w sklepie z figurkami kolekcjonerskimi (motyw Nook), ale schemat jest niezależny od motywu.

## Najpierw zmierz, ile motyw już ma w rem

Zanim zaczniesz przepisywać arkusze, policz proporcje. W tym sklepie `main.css` miał
**74 wartości w rem wobec 23 w px**, `critical.css` 11 do 3, plus **86 odwołań do
`var(--font-*-size)`**. Nagłówki `h1` do `h3` były już w rem, łącznie z `clamp()`.
Największą dźwignią było przełączenie kilkunastu ZMIENNYCH, a nie przepisywanie reguł.

## Baza rem: sprawdź, nie zakładaj

Wiele motywów ustawia `html { font-size: 62.5% }`, czyli **1rem = 10px** i `1.8rem = 18px`.
Sprawdź to we WSZYSTKICH serwowanych arkuszach (może być nadpisane w media query),
a nie tylko w jednym pliku.

## Zmienne motywu: piksele w panelu, rem na wyjściu

```liquid
--font-base-size: {{ settings.type_body_font_size | default: 16 | divided_by: 10.0 }}rem;
```

Ustawienia zostają w pikselach, więc klient widzi znajome suwaki, ale wyjście jest skalowalne.
Zero migracji danych i zero zmian w schemacie motywu. `| default:` jest konieczny, bo brakujące
ustawienie da `0rem`.

**Sprawdź przy okazji, czy któraś zmienna nie jest zepsuta.** W tym sklepie
`--font-price-size: {{ settings.type_price_font_size }}px` dawało samo `px`, bo tego ustawienia
**nie ma w `settings_schema.json`**. Deklaracja nieprawidłowa, więc `var()` w cenie na karcie
i w koszyku nie miało czym się rozwinąć i cena dziedziczyła rozmiar skądinąd.

## Globalne pokrętło skali

Skoro wszystko jest w rem, zmiana `html { font-size }` skaluje całą stronę proporcjonalnie.
Wystaw to jako ustawienie (np. 90 do 110%) i licz `62.5 * skala / 100`.

**Pokrętło MUSI być renderowane inline w `<head>`, nie w skompilowanym arkuszu.** Motywy,
które przekompilowują `settings.css` dopiero przy zapisie pliku `.liquid`, a nie przy zmianie
ustawienia, sprawią, że suwak nic nie zrobi. Wepnij snippet po arkuszach, żeby nadpisywał
regułę bazową przy równej specyficzności.

**Wymiary układu też przełącz na rem** (`--gap`, `--grid-gap`, wysokość nagłówka), inaczej
pokrętło powiększy tekst, a odstępy zostaną i układ się rozjedzie. Skoro skaluje całe UI,
nazwij ustawienie „Skala interfejsu", nie „Skala typografii".

## Dwie pułapki migracji, obie kosztują rundę

**1. Zapisane wartości trzeba przeliczyć w szablonach, nie tylko w schemacie.** Ustawienie zmienia
jednostkę, ale w `templates/*.json` dalej siedzi `18`, co po zmianie odczyta się jako `18rem`.
Podziel przez 10 we WSZYSTKICH szablonach, gdzie sekcja występuje: łatwo przeoczyć drugi,
np. `page.o-nas-main.json` obok `index.json`.

**2. Sekcja i szablon NIE MOGĄ iść w jednym `themeFilesUpsert`.** Szablon jest walidowany
przeciwko schematowi sprzed operacji, więc `1.3` przy starym zakresie `0 do 40 krok 1` odbija się jako
`FILE_VALIDATION_ERROR: Setting 'x' must be a step in the range`. Sekcje przechodzą, szablony nie.
**Kolejność: najpierw sekcje, potem osobnym pushem szablony.**

## Co konwertować, a czego nie

Tylko rozmiary CZCIONEK. `strzalki_rozmiar`, `rozmiar_ikony` i podobne to geometria, zostają w px,
inaczej suwak „wielkość strzałki" zacząłby zależeć od skali tekstu.

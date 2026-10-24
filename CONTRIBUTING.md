# Jak dodać albo poprawić skill

## Struktura

```
skills/<nazwa-skilla>/
  SKILL.md            # frontmatter + krótki wstęp + tabela „Co tu jest”
  references/*.md     # wiedza, jeden temat na plik
  *.sh / *.py         # opcjonalnie skrypty używane przez skill
```

- Nazwa katalogu = `name` we frontmatterze, małe litery i łączniki, prefiks `shopify-`.
- `SKILL.md` ma być krótki: po co jest skill, dwie, trzy zasady, które wracają najczęściej, i tabela
  wszystkich plików z `references/` (każdy plik jednym zdaniem). Szczegóły idą do `references/`.
- Jeden plik referencyjny to jeden temat. Claude wczytuje pojedynczy plik, więc długi plik
  „o wszystkim” kosztuje kontekst przy każdym użyciu.

## Frontmatter

```yaml
---
name: shopify-nazwa
description: "Co skill robi i KIEDY go uruchamiać. Najważniejszy przypadek na początku. Wymień słowa, którymi ktoś opisze problem („nie działa”, „klient zgłasza”), nazwy API i plików motywu."
---
```

- `description` decyduje o tym, czy skill się w ogóle uruchomi. Pisz po polsku, konkretnie,
  z typowymi sformułowaniami zgłoszeń. Opis i `when_to_use` razem są ucinane na 1536 znakach.
- Nie dokładaj innych pól, jeśli nie są potrzebne (część z nich nie działa poza Claude Code).

## Treść

- Każdy wpis z datą i z kontekstem bez nazwy klienta: „sklep z pluszakami (motyw Concept), 2026-09”.
  Motywy i aplikacje nazywaj wprost, to wiedza. Sklepów, osób, domen i produktów nie.
- Pisz, co było objawem, co było przyczyną i jak to sprawdzić. Sama recepta bez objawu się nie przyda.
- Gdy wpis okazał się błędny, popraw go i dopisz korektę z datą, zamiast cicho usuwać.
- Bez długich myślników (pauza U+2014 i półpauza U+2013): przecinek, dwukropek albo kropka.
- Kod w blokach ma być poprawny składniowo (Liquid, GraphQL, JSON). Po zmianie bloku JSON zwaliduj go.

## Obowiązkowy check anonimizacji przed PR

Czarną listę (nazwy sklepów, domeny, osoby, ID) każdy trzyma u siebie, **poza repozytorium**.
Sama lista zawiera dane klientów, więc nigdy jej nie commituj.

```bash
python scripts/check-anonymization.py /sciezka/poza/repo/czarna-lista.txt
```

Skrypt sprawdza pliki i całą historię git (`git log -p --all`): frazy z listy (także bez spacji
i łączników) oraz wzorce generyczne: `*.myshopify.com`, `gid://shopify/...` z prawdziwym ID, długie
liczby, adresy e-mail, tokeny `shpat_`/`shpca_`/`shpss_`, ścieżki prywatnego workspace i linki do notatek w podwójnych nawiasach kwadratowych.
Wynik ma być `WYNIK: 0 trafień`. Jeśli coś trafiło do commita, przepisz historię przed pushem.

Dodatkowo:

```bash
python -c "import pathlib,sys; b=[str(p) for p in pathlib.Path('skills').rglob('*') if p.is_file() and any(c in p.read_text(encoding='utf-8') for c in '\u2014\u2013')]; print(b or 'OK'); sys.exit(bool(b))"
claude plugin validate .             # ma być „Validation passed”
```

## Wersje

`version` w `.claude-plugin/plugin.json` przypina wersję: użytkownicy dostaną zmiany dopiero po jej
podniesieniu. Każdy merge do `main` z nową treścią podnosi wersję (poprawka wiedzy: patch, nowy plik
albo skill: minor) i ma wpis w `CHANGELOG.md`.

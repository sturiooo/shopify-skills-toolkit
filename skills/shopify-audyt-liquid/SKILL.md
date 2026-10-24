---
name: shopify-audyt-liquid
description: "Audyt kodu Liquid napisanego przez AI, PRZED wgraniem na sklep. Uruchamiaj, zanim wykonasz theme push albo themeFilesUpsert z nowym lub mocno zmienionym plikiem .liquid, oraz gdy użytkownik prosi o sprawdzenie albo review kodu motywu. Łapie zmyślone filtry, logikę wariantów przepisaną w JS, pominięte Section Rendering API, zahardkodowane ścieżki, surowe ceny, brakujące tłumaczenia i pułapki schematu."
---

# Audyt kodu Liquid przed wgraniem

Adaptacja `review-ai-shopify-liquid` z [baslefeber/shopify-skills](https://github.com/baslefeber/shopify-skills)
(MIT, Bas Lefeber / learnshopify.dev), scalona z lekcjami z realnych wdrożeń.

Przechodź listę w kolejności. Najpierw maszyna, potem osąd.

## Krok 1: walidacja maszynowa

Odpal `mcp__shopify-dev__validate_theme` (Shopify Dev MCP) na zmienionych plikach. Wymaga `conversationId`,
`absoluteThemePath` i `filesCreatedOrUpdated` jako listy **obiektów** `{path: ...}`, nie stringów.
Na katalogu z jednym plikiem zgłosi brakujące pliki sąsiednie i klucze locale, to **nie są**
błędy Twojej zmiany.

Do tego `node --check` na każdym osadzonym `<script>` wyciągniętym do pliku tymczasowego
oraz walidacja `{% schema %}`:

```bash
python3 -c "import re,json,sys; s=open('plik.liquid',encoding='utf-8').read(); \
d=json.loads(re.search(r'{% schema %}(.*?){% endschema %}', s, re.S).group(1)); \
print('OK'); [print('range',x['id'],int((x['max']-x['min'])/x['step']),'krokow') \
for x in d['settings'] if x.get('type')=='range']"
```

## Krok 2: osąd, czego walidator nie złapie

### Zmyślone filtry i ścieżki obiektów
Każdy filtr sprawdź w dokumentacji. `titleize` istnieje w Rails, nie w Shopify.
Uważaj na property, które wyglądają sensownie, a są nieudokumentowane dla danego typu
(np. `media.src`), bo mogą nigdy nie zadziałać.

### Logika wariantów przepisana w JS
Odrzuć ręczny JavaScript odtwarzający wybór wariantu albo dostępność. Natywny mechanizm
obsługuje przypadki brzegowe (wyprzedany wariant, zmiana ceny), których własna implementacja
nie łapie.

### Koszyk i kolekcje z pominięciem Section Rendering API
Odrzuć `fetch('/cart/add.js')` z ręcznym przebudowywaniem DOM. Section Rendering API zwraca
gotowy HTML jednej sekcji.

### Zahardkodowane ścieżki
Nigdy `/cart`, `/collections/all`, `/account`. Używaj `routes.cart_url`,
`routes.all_products_collection_url`, `routes.account_url`, bo tylko one dokładają prefiks
języka i rynku.

### Surowe ceny
Każda cena przez `money`, `money_with_currency` albo `money_without_trailing_zeros`.
Samo `{{ product.price }}` wypisuje grosze, a ręczne dzielenie psuje waluty bezgroszowe.

### Filtry wyciekające z argumentu nazwanego
`{{ img | image_url | image_tag: alt: x | default: y | strip_html }}` nie działa tak,
jak wygląda. `default` i `strip_html` łapią się na CAŁY wynik `image_tag`, więc `strip_html`
kasuje `<img>` i **zdjęcie znika**. Policz wartość wcześniej do zmiennej.

### Tłumaczenia
Wszystkie napisy przez `{{ 'klucz' | t }}`. **Nie dawaj `default:` w polu, które ma `default`
w schemacie**, bo `settings.x | default: t` nigdy nie sięgnie po locale.

## Krok 3: pułapki schematu

- `"default": ""` na polu wymaganym wywala zapis, lepiej pominąć klucz
- `range` musi mieć **co najmniej 3 kroki**: `(max - min) / step >= 3`. Dla zakresu 1 do 2 użyj `select`
- `range` przyjmuje **maksymalnie jedną cyfrę po przecinku** w `step`, `default`, `min`, `max`
- filtr wewnątrz porównania (`{% if i == n | plus: 1 %}`) jest niepoprawny, policz wcześniej
- `{% doc %}` działa tylko w snippetach, nie w sekcjach
- `"type"` bloku musi wskazywać istniejący plik
- wrapper bloku potrzebuje `{{ block.shopify_attributes }}`
- duże pętle wymagają `{% paginate %}`
- pole `richtext` nie przepuści `<table>`, użyj `liquid` albo strony przez `page`
- `config/settings_schema.json` to TABLICA grup, nowa grupa wchodzi jako element tablicy

## Krok 4: dostępność i obrazy

`<button>` zamiast `<div onclick>`. Zamiast `outline: none` widoczny stan fokusu.
`image_tag` z wymiarami, żeby nie było przeskoku układu. `prefers-reduced-motion` przy animacjach.

## Krok 5: styl pracy w tym pakiecie

- **Style w pliku sekcji**, w bloku `<style>`, nie w polu Custom CSS sekcji (limit 500 znaków,
  niewidoczne w repo, nie działa dla drawerów przenoszonych do `<body>`)
- **Sekcja musi mieć `"class"` w schemacie**, inaczej scope'owanie CSS nie zadziała
- Osobne rozmiary mobile i desktop przez zmienne CSS nadpisywane w `@media`, nie przez duplikowanie reguł

## Wynik

Podziel znaleziska na trzy grupy i podaj poprawiony kod dla każdego blokera:

1. **Blokery**, kod nie zadziała albo coś zepsuje
2. **Do poprawy**, zadziała, ale podejście jest złe
3. **Kosmetyka**

Jeśli nic nie znalazłeś, napisz to jednym zdaniem. Nie wymyślaj znalezisk na siłę.

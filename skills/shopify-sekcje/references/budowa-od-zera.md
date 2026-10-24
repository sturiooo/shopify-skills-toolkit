# Budowa sekcji od zera

Adaptacja `shopify-section-builder` z [baslefeber/shopify-skills](https://github.com/baslefeber/shopify-skills)
(MIT, Bas Lefeber / learnshopify.dev), scalona ze standardem schematu z tego pakietu.

## Krok 0, obowiązkowy: nie buduj, jeśli nie musisz

Kolejność decyzji jest zawsze taka sama:

1. **Czy motyw docelowy ma to natywnie?** Grep po `sections/` i po schematach.
2. **Czy biblioteka gotowych sekcji zespołu ma gotowca?** Jeśli ją prowadzicie, jej README
   to spis komponentów i zależności.
3. **Dopiero potem piszemy od zera**, a gotowa sekcja **wraca do biblioteki** razem z README
   (zależności, pułapki, gdzie wdrożona).

Napisz wprost, którą ścieżkę wybrałeś i dlaczego.

## Cztery części każdej sekcji

1. **Markup** z klasą-zaczepem i `{{ block.shopify_attributes }}` na wrapperze bloku
2. **Style scope'owane** przez `#shopify-section-{{ section.id }}` albo klasę z `"class"` w schemacie
3. **Schemat** z ustawieniami, blokami i tablicą `presets`, bez presetu sekcja nie pojawi się
   w menu dodawania
4. **Teksty przez klucze tłumaczeń**, nie zaszyte w kodzie

## Standard schematu obowiązujący w tym pakiecie

Każda nowa sekcja i każdy nowy blok dostaje komplet:

- **fonty osobno dla desktop i mobile**, wartość 0 znaczy „domyślny z motywu"
- **kolory wszystkich elementów**, nie tylko tła
- **padding góra i dół, osobno desktop i mobile**
- **radius i ramka**
- **szerokość treści zgodna z page-width motywu**
- **przełączniki** do ukrywania elementów
- `!important` na nagłówkach i `.rte`, bo motywy lubią je nadpisywać

Osobne rozmiary mobile i desktop rób przez zmienne CSS nadpisywane w `@media`,
nie przez duplikowanie reguł.

## Pułapki schematu, które wywalają zapis

- `range` musi mieć **co najmniej 3 kroki**: `(max - min) / step >= 3`. Dla zakresu 1 do 2 użyj `select`
- `range` przyjmuje **maksymalnie jedną cyfrę po przecinku**, więc `0.1` tak, `0.05` nie
- `"default": ""` na polu wymaganym wywala zapis, lepiej pominąć klucz
- pole tekstowe, które ma być tłumaczone, **nie może mieć `default`** w schemacie,
  bo wtedy `settings.x | default: t` nigdy nie sięgnie po locale
- `"type"` bloku musi wskazywać istniejący plik
- filtr wewnątrz porównania jest niepoprawny, policz wcześniej do zmiennej
- pole `richtext` nie przepuści `<table>`

Po każdej edycji `{% schema %}` odpal walidację:

```bash
python3 -c "import re,json; s=open('plik.liquid',encoding='utf-8').read(); \
d=json.loads(re.search(r'{% schema %}(.*?){% endschema %}', s, re.S).group(1)); \
print('OK'); [print('range',x['id'],int((x['max']-x['min'])/x['step']),'krokow') \
for x in d['settings'] if x.get('type')=='range']"
```

## Style: gdzie je pisać

W bloku `<style>` **w pliku sekcji**. Nigdy w polu Custom CSS sekcji, bo ma limit 500 znaków,
nie widać go w repo i nie działa dla drawerów przenoszonych do `<body>`.

Sekcja musi mieć `"class": "shopify-section--<nazwa>"` w schemacie, inaczej nie ma po czym
scope'ować.

## Tło w Horizon

`base.css` wymusza przezroczystość na `.section`, więc zrób dedykowane dziecko
`.section-background` i nałóż klasę schematu kolorów na oba: na sekcję, żeby dziedziczyła,
i na div tła, żeby się wyrenderowało.

Warstwa `position: absolute` potrzebuje pozycjonowanego przodka. Nie każdy wrapper tła
ma `position: relative`, użyj `:has()`, żeby celować tylko tam, gdzie faktycznie jest Twoja warstwa.

## Bloki zagnieżdżone

Bloki potomne w osobnych plikach `blocks/_dziecko.liquid` z podkreśleniem na początku nazwy,
renderowane przez `content_for`.

## Przenoszenie sekcji między motywami

Cztery warstwy awarii, sprawdź wszystkie: brakujący globalny JS motywu, brak `"class"`
w schemacie, kolizje nazw klas, inna baza rem (62,5% daje 10px zamiast 16px).
Wartości opcji schematu muszą pasować do selektorów CSS.

## Gdy sekcja renderuje się wielokrotnie

Jeden globalny guard plus rejestr instancji, inaczej `resize` i `shopify:section:load`
dostaną duplikaty listenerów.

## Na koniec

1. Walidacja schematu i `node --check` na JS
2. Sekcja wraca do biblioteki gotowych sekcji (jeśli ją prowadzicie) z wpisem w README
3. Powiedz klientowi, co dokładnie kliknąć, żeby ją zobaczyć

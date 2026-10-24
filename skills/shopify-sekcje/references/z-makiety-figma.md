# Budowa sekcji z Figmy „element po elemencie": lekcje z PDP (2026-07-31/08-01, Local 3.2.1 KrownThemes)

Pięć własnych sekcji (opinie/karuzela, „dla kogo", „dlaczego" z tłem-grafiką, „liczby" z animowanym
licznikiem, „sample box" z działającym CTA) na motywie roboczym. Poniżej rzeczy, które realnie
kosztowały czas albo wywaliły układ.

### 1. Edytor motywu i CLI walczą o ten sam `templates/*.json`: w OBIE strony

Znaliśmy już „push sekcji kasuje jej ustawienia z template JSON". Druga strona tej samej monety
(potwierdzona dwa razy w jednej sesji): **zapis w edytorze nadpisuje CAŁY szablon kopią z pamięci
przeglądarki**. Skutki: sekcja dodana przez CLI **znika**, a z sekcji, których schemat kopia
edytora znała w starszej wersji, **wylatują nowe klucze** (u nas `carousel_full_width`, `peek`,
`autoplay_mode`, `card_ratio` → wróciły wartości domyślne i układ się rozjechał).

Workflow, który to zamyka:
1. **`theme pull` szablonu TUŻ przed każdym pushem**, i buduj nową wersję z tego pobranego stanu,
   nigdy z lokalnej kopii sprzed godziny (inaczej cofniesz zmiany klienta z edytora).
2. Push sekcji → **osobno** push szablonu → **pull-back i sprawdzenie konkretnych kluczy**
   (`grep`/parse, nie „success" z CLI).
3. Powiedz klientowi wprost: **zamknij/odśwież edytor przed pushem**, a jeśli pracuje równolegle:
   niech zgłasza każdą swoją zmianę, bo inaczej jego zapis wygrywa.

### 2. NIE kotwicz kolejności po własnym ID sekcji

Gdy klient sam doda tę samą sekcję w edytorze, dostaje ona **nowe id** (`custom_audience_rCt4Dt`,
`custom_stats_XMQKD9`), a Twoja instancja znika. Skrypt wstawiający kolejną sekcję po
`d['order'].index('custom_stats_1')` po cichu trafia w fallback i sekcja ląduje w złym miejscu.
**Szukaj kotwicy po `type`**, nie po id:
```python
stats = [k for k,v in d['sections'].items() if v.get('type')=='custom-stats']
anchor = stats[0] if stats else 'fallback_id'
```

### 3. `line-height`: jedna pomyłka w dzielniku rozwala całą sekcję

Największy bug sesji: schemat trzymał interlinię w **procentach** (150 = 1,5), a CSS dzielił przez
**10** (konwencja z innej sekcji, gdzie ustawienie było w dziesiątych) → `line-height: 15`, czyli
**15 × rozmiar fontu** (210 px na linię przy 14 px). Karty urosły na pół ekranu, a tytuł „pływał"
w pustce, objaw wyglądał jak zepsuty layout, nie jak literówka w dzielniku.
**Reguła:** jedna konwencja na projekt, zapisana w `info` ustawienia; procenty → `divided_by: 100.0`,
dziesiąte → `divided_by: 10.0`. **Sprawdzaj wynik w wyrenderowanym HTML** (`line-height: 1.5`),
nie w kodzie Liquida.

### 4. `| default:` przy KAŻDEJ wartości liczbowej w CSS (to nie kosmetyka)

Gdy ustawienie zniknie z szablonu (patrz punkt 1), `{{ s.content_width }}px` renderuje się jako
`max-width: px`, **niepoprawna deklaracja, przeglądarka ją ignoruje**, więc sekcja idzie na pełną
szerokość i wygląda jak zepsuta. Analogicznie `line-height: 0`, `gap: px`,
`grid-template-columns: repeat(, minmax(0,1fr))`. Po tej wpadce każda wartość ma `| default:`
z wartością z projektu, sekcja rysuje się poprawnie nawet po wycięciu ustawień.

### 5. Zrzut od klienta bywa… projektem z Figmy, nie sklepem

„Totalnie się rozjechało" przyszło z dwoma zrzutami: jeden był **renderem z Figmy** (identyczny
z tym, co zwraca `get_design_context`), drugi: realnym sklepem. Zanim zaczniesz diagnozować,
ustal, **co przedstawia zrzut**: charakterystyczne są ciemne tło kanwy Figmy, karty wychodzące poza
ramkę i brak elementów motywu (header/footer). Inaczej „naprawiasz" wygląd, który jest celem.

### 6. Skala z artboardu ≠ skala sklepu

Figma miała kolumnę 666 px i nagłówek 22 px, a sekcje na sklepie stały na 1200 px z nagłówkiem 32
(klient sam je podniósł). Kopiowanie px z Figmy dałoby mikroskopijny tekst.
**Sprawdź realne ustawienia wdrożonych instancji** (`templates/*.json`), wylicz mnożnik
(22→32 ≈ 1,45×) i przeskaluj resztę proporcjonalnie. Z projektu bierz wtedy **układ, kolory,
zaokrąglenia i proporcje**, nie wartości bezwzględne.

### 7. Wyrównanie własnych sekcji do siatki motywu: zmiennymi, nie pikselami

„Marginesy równe z sekcją produktu" rób **zmiennymi motywu**, nie przepisaną liczbą:
```css
max-width: var(--theme-max-width);
padding-inline: var(--gutter-container);   /* 40/30/20/15 px na kolejnych breakpointach */
```
(w Local/KrownThemes to klasa `.container--large`, której używa `main-product`). Dzięki temu
wyrównanie trzyma się na każdej szerokości ekranu i przeżywa zmianę `theme_max_width` w ustawieniach.
Daj przełącznik „Jak sekcja produktu / Własna szerokość" i tak dobierz warunek, żeby **brak
ustawienia = tryb wyrównany**.

### 8. Karuzela „N pełnych kart + równo pół karty przy krawędziach"

`slidesPerView = N + 2 × peek`; **peek 50% = dokładnie połowa karty** z każdej strony
(3 pełne → `slidesPerView: 4.0`). Warunek: karuzela musi **wyjść poza kolumnę treści**
(`max-width: none; padding-inline: 0` na jej wrapperze), a nagłówek i elementy dodatkowe zostają
w kolumnie. Autoplay „co kilka sekund o jedną kartę" = `autoplay.delay` + krótkie `speed`
+ `slidesPerGroup: 1` i **bez** `transition-timing-function: linear` (to jest do trybu ciągłego).

### 9. Karta w karuzeli o płynnej szerokości: proporcja, nie stała wysokość

Stała `min-height` + szerokość zależna od viewportu = karta robi się kwadratem na dużych ekranach.
`aspect-ratio: 100 / <procent>` (z Figmy: 188×223 → 119%) trzyma prostokąt na każdym ekranie,
a `min-height` zostaje jako podłoga; w kolumnie flex treść i tak może kartę wydłużyć.

### 10. Dodawanie do koszyka w customowej sekcji: reużyj komponentów motywu

Nie pisz własnego `fetch`. W Local/KrownThemes wystarczy **łańcuch elementów motywu**:
```liquid
<quick-add-to-cart>                                  <!-- otwiera szufladę -->
  <product-form data-ajax-cart data-product-url="{{ p.url }}">
    {%- form 'product', p -%}
      <input type="hidden" name="id" value="{{ v.id }}">
      <button type="submit" name="add">…</button>
    {%- endform -%}
  </product-form>
</quick-add-to-cart>
```
Podział ról, który trzeba znać: **`product-form`** robi AJAX (`/cart/add`), podmienia
`#AjaxCartForm` i licznik w nagłówku, po czym emituje zdarzenie `add-to-cart`; **`<quick-add-to-cart>`**
dopiero na to zdarzenie woła `#site-cart-sidebar.show()`. Bez tego opakowania produkt ląduje
w koszyku, ale **szuflada się nie otwiera**, łatwo to wziąć za bug. Oba skrypty
(`component-product-form.js`, `component-quick-buy.js`) są w tym motywie ładowane globalnie.
W innym motywie: znajdź, jak robi to „quick buy" na kartach produktów, i skopiuj ten sam łańcuch.
Motyw dokłada klasę `working` na `[type="submit"]`, warto ostylować stan ładowania.

### 11. Animowany licznik „startuje po wejściu w kadr": bez pustych wartości

Wzorzec: **wartość DOCELOWA renderuje się w HTML**, a JS podmienia ją na startową dopiero w
momencie, gdy faktycznie zaczyna animować. Dzięki temu bez JS, przy `prefers-reduced-motion`
i dla robotów widać poprawną liczbę, nigdy zera. Do tego `IntersectionObserver` z progiem
(np. 0.35) + `unobserve` po odpaleniu (animacja raz na wejście), `easeOutCubic` na `rAF`
i **`font-variant-numeric: tabular-nums`**, bo proporcjonalne cyfry mają różne szerokości
i licznik „skacze". Prefiks/sufiks (`~`, `%`, `x`) trzymaj POZA animowanym `<span>`.

### 12. Assety z Figma MCP wygasają (~7 dni): nigdy do commitu

Grafiki wracają jako `https://www.figma.com/api/mcp/asset/...`. Nie wstawiaj ich jako `default`
w schemacie ani na sztywno w kodzie. Zamiast tego `image_picker` (+ ewentualnie fallback do
`product.featured_image`) i informacja dla klienta, żeby wgrał plik.

### 13. Bramka walidacyjna przed KAŻDYM pushem (ta lista złapała realne błędy)

- `range`: 3-101 kroków, `default` na siatce `min + n*step`, **`max` < 10000**
  (`card_ratio` 0-180 step 1 = 181 kroków → push odrzucony; Theme Check tego nie widzi).
- Każdy `{{ s.x }}` w CSS **ma ustawienie w schemacie ORAZ `| default:`**.
- Dzielnik interlinii zgodny z jednostką w `info`.
- Inline JS: wyciąć do pliku i `node --check`.
- `name`/`presets[].name`/`blocks[].name` ≤ 25 znaków.
- Theme Check **filtrowany do zmienianych plików**, ten motyw ma 119 błędów
  `MatchingTranslations` (brakujące `general.newsletter.consent_*` w ~31 locales), które są szumem
  sprzed naszej pracy i zagłuszają realne zgłoszenia.

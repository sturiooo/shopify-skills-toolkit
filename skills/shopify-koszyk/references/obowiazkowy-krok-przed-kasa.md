# Obowiązkowy krok (np. kreator dodatków) przed kasą

Wdrożone w sklepie z pluszakami (28.09.2026, Concept/RoarTheme, kreator EB Easy Bundle Builder).

## Warunek „zaliczenia” kroku nie może być „w koszyku jest już X”

- **Samo „w koszyku jest zestaw z kreatora” to za słaby warunek.** Klient wybrał dodatki, wszedł do kasy,
  cofnął się, dołożył drugi produkt główny i dostał zwykłą kasę, bo zestaw z pierwszego przejścia wciąż był w koszyku.
- **Recepta: zapamiętaj, CO było w koszyku w chwili wejścia w krok.** Na stronie kroku zapisz atrybut koszyka
  (`/cart/update.js`, `attributes: { _dodatki_krok: ",wariant:ilość,..." }`), a w Liquid przepuść kasę tylko wtedy, gdy
  jest efekt kroku (zestaw/dodatek) **i** każdy produkt główny mieści się w tej liście (ten sam wariant, ilość <= zapisanej).
  Pozycje dodane przez sam krok (u EB: właściwości `_easyBundle*`) pomijaj w porównaniu.
- **Listę licz przez Section Rendering API, nie w HTML strony kroku.** Techniczna sekcja bez wyglądu
  (`/?section_id=...`) zawsze widzi świeży koszyk; strona produktu mogłaby przyjść z cache.
- **Wtedy klasyfikacja produktów jest w jednym miejscu** (Liquid), a JS tylko przepisuje wynik do atrybutu.

## Furtki, które trzeba zamknąć razem z przyciskiem kasy

- „Kup teraz” / dynamiczne przyciski płatności na karcie produktu (omijają koszyk).
- Szybkie płatności (`content_for_additional_checkout_buttons`) na stronie koszyka.
- Karty podarunkowe wyłączyć z wymogu (`item.product.gift_card?`).
- Motyw nie zamknie ręcznie wpisanego `/checkout`; to zrobi tylko walidacja kasy (Shopify Functions, apka).

## Szuflada przerysowuje się przez innerHTML

`<script>` wstawiony razem z przyciskiem nie wykona się po dodaniu pierwszego produktu (pusty koszyk przy
ładowaniu = brak przycisku i skryptu). Obsługę kliknięcia renderuj ZAWSZE, poza warunkami koszyka, z globalnym guardem.

## Test bez przeglądarki

Sesja `curl -c/-b` na `/cart/add.js`, `/cart/update.js`, `/?sections=cart-drawer` i sprawdzanie atrybutu przycisku
(np. `data-addons-step-url="`, z cudzysłowem, bo ta sama nazwa bywa w selektorze skryptu i daje fałszywe „jest”).

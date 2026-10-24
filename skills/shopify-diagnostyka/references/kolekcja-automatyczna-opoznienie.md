# Kolekcja automatyczna przelicza się z opóźnieniem po zmianie tagów (2026-10-02, sklep z pluszakami, motyw Concept)

- **Po `tagsAdd` / `tagsRemove` kolekcja automatyczna (reguła TAG = …) nie jest od razu aktualna.** Mutacje wracają
  bez `userErrors`, tagi na produkcie są już nowe, ale `collection.productsCount` i `/collections/<uchwyt>/products.json`
  przez ok. minutę pokazują stan pośredni. Zmierzone przy przeniesieniu 20 toreb z `sacks` do nowej `gift-bags`:
  od razu po zmianie `gift-bags` = 12 (sklep 14), `sacks` = 17 z torbami w środku; po 60 s `gift-bags` = 20, `sacks` = 3.
- **Ten stan pośredni wygląda jak błąd skryptu** („część produktów się nie przeniosła”) i kusi, żeby puścić zmianę drugi raz.
- **Recepta:** najpierw sprawdź źródło prawdy, czyli tagi na samych produktach (`nodes(ids:) { tags }`), a liczność
  kolekcji i storefront dopiero po odczekaniu ok. 60 s. Kolekcję docelową twórz PRZED przetagowaniem, wtedy produkt
  nigdy nie wisi bez kategorii dłużej niż samo przeliczenie.
- **To samo dotyczy kreatora i każdej sekcji, która bierze produkty z kolekcji automatycznej:** zaraz po zmianie tagów
  może pokazać stary albo niepełny zestaw.

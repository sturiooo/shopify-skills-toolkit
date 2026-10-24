# Przekierowanie 301 istnieje, a adres i tak daje 404 (2026-09-24, sklep z suplementami, motyw Stretch)

- **Reguła 301 prowadząca na produkt w wersji roboczej (status DRAFT, w panelu „Wersja robocza”) kończy się na 404.** Shopify wykonuje
  przekierowanie, ale cel nie jest opublikowany na kanale Sklep online. W GSC wygląda to jak
  „brak przekierowania”, a w panelu reguła jest. Przykład: `/produkt/produkt-a/` →
  `/products/produkt-a-1000-mg` = `404 https://example.com/products/produkt-a-1000-mg`
  (88 kliknięć w 3 miesiące, druga strona organiczna sklepu).
- **Karty przechodzą do wersji roboczej PO zrobieniu przekierowań.** 31.08 Produkt B i Produkt C były aktywne,
  a 24.09 były w wersji roboczej. Nikt nie ruszał reguł, a one po cichu zaczęły prowadzić donikąd.
- **Lista z GSC nie pokazuje wszystkich takich reguł.** Z listy wynikało 5, a audyt po celu
  znalazł 6 (`/produkty/produkt-c` nie miał wyświetleń w tym okresie).

**Recepta:** audytuj reguły po **statusie celu**, nie po liście 404 z GSC.
1. `urlRedirects(first:250)` z paginacją (`pageInfo.endCursor`) → wszystkie `path`/`target`.
2. `products { handle status }` → zbiór `/products/<handle>` ze statusem ≠ ACTIVE.
3. Reguły, których `target.split('?')[0]` jest w tym zbiorze, to ukryte 404.

Nie aktywuj produktu sam (decyzja klienta: stan, cena). Przepnij regułę `urlRedirectUpdate(id, urlRedirect:{target})`
na najbliższy aktywny odpowiednik albo kolekcję. Uważaj: kolekcja, w której jedynym produktem jest ta wersja robocza,
wyświetli się pusta, więc wtedy lepsza jest strona główna. Stare cele zapisz, żeby wrócić po ponownej aktywacji.

Po drodze: `shopify store execute` potrafi dokleić do wyniku komunikat npm (`changed 49 packages…`)
po zamykającym `}`. `json.load` rzuca wtedy `Extra data`, więc parsuj przez `json.JSONDecoder().raw_decode`.


## Ta sama przyczyna, inne miejsca: menu i status UNLISTED (2026-09-29)

- **Linki w menu to zwykłe adresy (`type: HTTP`), więc psują się po cichu razem z produktem.**
  Audyt z 24.09 poprawił reguły 301 na wersje robocze, ale pominął menu: „Produkt A” i „Produkt C” w `main-menu`
  i `main-menu-kopia` prowadziły na te same wersje robocze i były głównym źródłem 44 odsłon 404 w 12 dni.
  Link typu `PRODUCT` (z `resourceId`) Shopify pilnuje sam, link `HTTP` z wpisanym `/products/...` nie.
  **Recepta:** przy każdym audycie „cel w wersji roboczej” przejdź też `menus { items { type url resourceId items {...} } }`
  i sprawdź `curl -o /dev/null -w '%{http_code}'` każdy adres `/products/` i `/collections/`.
- **Status `UNLISTED` chowa produkt z kolekcji w Liquid.** W sklepie z pluszakami (motyw Concept) 62 z 69 dodatków miało `UNLISTED`,
  a kreator dodatków czyta `collection.products`, więc byłby pusty, choć produkty są opublikowane
  (`publishedOnPublication = true`). Kolekcje dodatków też nie były opublikowane w Sklepie online
  (`resourcePublications` puste). Zanim uznasz, że sekcja z kolekcją „nie działa”, sprawdź status produktów
  i publikację kolekcji, nie kod.

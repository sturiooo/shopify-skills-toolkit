# Przekierowania po migracji: pokrycie to nie wszystko, sprawdź trafność

Źródło: sklep z artykułami kuchennymi (migracja IdoSell → Shopify, maj 2026), audyt 06.10.2026.

## Teza

**99% starych adresów z przekierowaniem nie znaczy, że migracja jest naprawiona.** W tym sklepie 15 044 reguły pokrywały 4 280 z 4 322 zarchiwizowanych adresów, a mimo to ok. 29% przekierowań produktowych prowadziło do produktu **innego typu** (cedzak → deska do krojenia, wentylator → toster, tarka → patelnia, pościel → ręczniki). Google traktuje przekierowanie na niepowiązaną stronę jak soft 404, więc sygnały starej strony przepadają, a pokrycie wygląda wzorowo.

## Jak to zmierzyć (bez przeglądarki)

1. **Stare adresy:** archiwum web.archive.org, tylko HTML sprzed daty migracji:
   `https://web.archive.org/cdx/search/cdx?url=<domena>/*&to=<RRRRMMDD>&output=txt&fl=timestamp,original&filter=statuscode:200&filter=mimetype:text/html&collapse=urlkey&limit=5000`
   Przy okazji rozpoznasz starą platformę po strukturze (IdoSell: `/pl/products/<nazwa>-<id>.html`, zasoby `/hpeciai/`).
2. **Reguły:** `urlRedirects(first:250, after:$c){ path target }` w pętli (`urlRedirectsCount` zwraca tylko „AT_LEAST 10000”, więc licz sam).
3. **Pokrycie:** stare ścieżki ∩ `path` (porównuj lowercase).
4. **Trafność:** dla `/pl/products/…` porównaj pierwszy wyraz sluga źródła i celu (typ produktu: patelnia, garnek, cedzak…) oraz czy cel jest aktywnym produktem. Niezgodny typ = do ręcznego przemapowania.

## Czego nie da się ustalić

**Shopify nie trzyma daty utworzenia przekierowania.** Jeśli spadek ruchu był wcześniej niż reguły, z API tego nie udowodnisz; potrzebny wykres z Search Console (w tym sklepie: 5.06 do 28.07.2026 prawie zero kliknięć).

## Recepta

Mapowanie 1:1 do odpowiednika; gdy go nie ma, do **kategorii** tego samego typu, nie do „najbliższego” produktu z dopasowania tekstowego. Storefront łatwo zrobić 429 przy masowym curlu: listę reguł bierz z Admin API, curlem sprawdzaj tylko próbkę.

# „W magazynie 0, a w sklepie da się kupić”: integracja stanów (SellAsist i pokrewne)

Zmierzone 16.10.2026 w sklepie z pluszakami (motyw Concept, stany z SellAsist). Kolejność sprawdzania, zanim ogłosisz przyczynę.

## 1. Czy Shopify w ogóle sprawdzał stan w chwili zamówienia

- **`inventoryItem.tracked = false` znaczy: sprzedawaj zawsze.** Sprawdź stan śledzenia NA DZIEŃ ZAMÓWIENIA, nie dziś.
  Dziś może być włączone, a zamówienia z przeszłości weszły przy wyłączonym (tu: 23.09 do 13.10 wyłączone, w dniu audytu 100% włączone).
- Źródła historii: zrzuty z własnych skryptów (pole `tracked`, jeśli zapisujesz backupy przed zmianami), `inventoryItem.updatedAt`
  (masowa zmiana = setki pozycji w kilka minut), a w panelu **Produkty > Zapasy > Historia korekt**
  (`/products/inventory/<inventoryItemId>/inventory_history?location_id=…`): zamówienie przy „Dostępne” 0 → -1 przy polityce DENY
  oznacza, że śledzenie było wtedy wyłączone.
- Pułapka: `productVariant.updatedAt` nie mówi nic o śledzeniu, zmienia się przy każdej synchronizacji cen.

## 2. Jak integracja zapisuje stan

- **SellAsist ustawia „Dostępne” = swój stan, ale tylko gdy stan zmieni się U NIEGO.** W historii widać to jako
  „Korekta zapasów / SellAsist integracja” o różnicę, nie jako pełny zapis. Nie ma okresowej pełnej synchronizacji.
- Skutek: każda zmiana zrobiona tylko w Shopify żyje do następnej zmiany w SellAsist.
  Typowa: **zwrot pieniędzy z „Zwróć produkty do magazynu” po anulowaniu**. SellAsist już oddał sztukę (+1), Shopify dodaje drugą (+1)
  i powstaje fantom, na który wpada kolejne zamówienie (u nas dwa przypadki: Produkt A, wariant 150 cm, i Produkt B, wariant 160 cm).
- Recepta dla klienta: przy anulowaniu za brak towaru NIE zaznaczać „Zwróć do magazynu”.

## 3. Pełne porównanie stanów (bez eksportu CSV)

- SellAsist: **Integracje > Shopify > Oferty** (`/admin/externalshops_offers/edit?engine=shopify&page=N`, 50 na stronę)
  ma kolumny „Stan Shopify” i „Stan Sellasist” oraz `Nr oferty` = `<productId>-<variantId>`. Czytaj stronami przez `fetch` + DOMParser.
- **Kolumna „Stan Shopify” to to, co SellAsist wysłał, nie stan w Shopify.** U nas była zgodna w 100% także dla fantomów.
  Porównuj z realnym `inventoryQuantity` z Admin API (mapę wariant → stan wstrzyknij do strony i licz tam).
- Zakładka „Braki powiązań” i wyszukiwarka `/admin/searchsplit?type=products&word=<EAN>` pokazują warianty bez produktu w SellAsist:
  tych integracja nigdy nie zaktualizuje.
- Stan w SellAsist bywa wspólny dla kilku kanałów („Główny stan magazynowy asortymentu”): ujemne stany to sprzedaż ponad stan w innym kanale.

## 4. Naprawa

- Wyrównanie: `inventorySetQuantities` z `changeFromQuantity` (nie ruszy, jeśli stan się zmienił) + `@idempotent(key:)`.
- Śledzenie: `productVariantsBulkUpdate` per produkt z `inventoryItem.tracked: true` i `inventoryPolicy: DENY`.
- Kontrola po: świeży odczyt OBU stron, nie wynik skryptu. Przed naprawą zapisz backup stanów (wariant, `tracked`, ilość) do pliku.

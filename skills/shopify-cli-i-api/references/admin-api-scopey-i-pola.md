# Admin API: scope'y i pola, które zaskakują (2026-08, sklep z pluszakami, motyw Concept)

| Operacja | Wymaga / gotcha |
|---|---|
| `urlRedirectCreate` (301) | **`write_online_store_navigation`**: NIE ma tego w `write_content` |
| `onlineStoreUrl`, `publishedOnCurrentPublication` | `read_publications` / `read_product_listings`; `null` = produkt **nieopublikowany** na kanale |
| `productVariantsBulkCreate` z `mediaSrc` | **pole jest po cichu ignorowane** → `productCreateMedia`, potem `productVariantsBulkUpdate {id, mediaId}` |
| `productVariantsBulkReorder` | `ProductVariantPositionInput` ma **`position`**, nie `newPosition` |
| `collection.products` | zwraca też produkty **ARCHIVED**: licząc realny stan, filtruj `status: ACTIVE` |
| `metafieldsSet` | atomowy dla całej paczki; `elementIndex` w błędzie potrafi wskazać zły element |
| `productOptionsReorder` | trzeba podać **wszystkie** opcje produktu z nazwami (`{name, values:[{name}]}`); sam `Size` odbija „Brak nazwy opcji „Color”.” (2026-10-04) |
| `resourcePublicationsV2` | domyślnie `onlyPublished: true`: produkt DRAFT przypisany do kanałów pokazuje pustą listę; sprawdzaj z `onlyPublished: false` (2026-10-03) |
| `metafieldDefinitionCreate` | `description` maks. 255 znaków; lista `list.*` maks. 128 elementów (szczegóły: skill `shopify-metapola`) |

### Scalanie duplikatów produktów w warianty (playbook)
Objaw: „ten sam produkt widnieje 3 razy z różną ceną”, bo każdy rozmiar był osobnym produktem,
a rozmiar siedział tylko w **uchwycie** (`-wielki`, `-duzy`, `-sredni`, `-male`).
1. Master = produkt o **najniższej cenie** (jego wariant zostaje pierwszy, „od…” w listingach).
2. Warianty dla pozostałych: cena + SKU + **zdjęcie przeniesione** (`productCreateMedia` → `mediaId`).
3. Duplikaty → `status: ARCHIVED` (odwracalne), **nie delete**.
4. Usuń martwą opcję (np. `Color` z jedyną wartością „Default”): `productOptionsDelete` ze strategią
   `NON_DESTRUCTIVE`; tytuły wariantów robią się „Small” zamiast „Default / Small”.
5. Kolejność wariantów rosnąco po cenie (`productVariantsBulkReorder`).
6. **Zrób backup do pliku w repo przed startem** (id, handle, ceny, SKU) i pamiętaj o przekierowaniach
   301 ze starych uchwytów, oraz o tym, że apki (np. kreatory boxów) trzymają **ID produktów**
   i po scaleniu trzeba je przemapować w panelu apki.

---

## ShopifyQL: kanał AI (`agentic_referring_channel`) i składnia atrybucji (2026-10-06)

- Wymiar `agentic_referring_channel` wymaga modelu atrybucji, ale **słowo kluczowe jest jedno, sklejone**: `WITH LAST_NON_DIRECT_CLICK_ATTRIBUTION` (inne: `ANY_CLICK_ATTRIBUTION`, `FIRST_CLICK_ATTRIBUTION`, `LAST_CLICK_ATTRIBUTION`, `LINEAR_ATTRIBUTION`). Zapis `WITH ATTRIBUTION MODEL last_non_direct_click` daje `mismatched input 'ATTRIBUTION'`.
- Przykład: `FROM sales SHOW total_sales, orders GROUP BY agentic_referring_channel, month WITH LAST_NON_DIRECT_CLICK_ATTRIBUTION SINCE 2026-05-01 UNTIL today`. Kolumny wracają z sufiksem `__last_non_direct_click`. Wartości kanału: `ChatGPT`, `Google AI Mode and Gemini`, `None`.

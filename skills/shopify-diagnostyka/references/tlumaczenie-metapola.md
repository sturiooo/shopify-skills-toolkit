# Diagnostyka: „tłumaczenie metapola się nie wyświetla w danym języku” (playbook)

**Kiedy:** klient zgłasza, że metapole (opis/specyfikacja/lista) NIE tłumaczy się w jakimś języku, choć w innych działa. Częste przy i18n z apkami (T-Lab, Langify, Weglot) lub Translate & Adapt. Zweryfikowane w sklepie z basenami (motyw z rodziny XO, 2026-06: `parametry_v2`/ES nie serwowane mimo poprawnej rejestracji).

**Diagnozuj W TEJ KOLEJNOŚCI, od najtańszego, NIE zakładaj, że to bug:**

**1. Czy to dynamiczne źródło w ustawieniu sekcji? (NAJCZĘSTSZE, naprawialne w kodzie).**
Jeśli pole sekcji/bloku ma podpięte „dynamiczne źródło” (w `templates/*.json` widać string typu `"{{ product.metafields.custom.x | metafield_tag }}"` jako WARTOŚĆ ustawienia), to **nie respektuje aktywnego locale** (zwykle EN łapie, DE/inne wracają do języka bazowego lub pusto). **Fix: renderuj metapole BEZPOŚREDNIO w Liquid** (`product.metafields[ns][key] | metafield_tag`), nie przez binding ustawienia. Wzorzec: dodaj select `*_source` (custom/metafield) + pole ścieżki `namespace.key`, w snippecie `split: '.'` → bracket access (w tamtym sklepie: rozwijane bloki sekcji main-product i sekcja `product-specification`). To rozwiązuje większość przypadków.

**2. Rich text: użyj `| metafield_tag`, nie `.value`.** Dla `rich_text_field` surowe `{{ ...key.value }}` wypisuje JSON; tłumaczy i renderuje dopiero `| metafield_tag`. (Dla text/multiline `.value` OK.)

**3. Jeśli kod renderuje poprawnie (działa dla 3 z 4 pól tym samym torem) → problem jest w DANYCH/SERWOWANIU tłumaczenia po stronie Shopify. Weryfikuj przez Admin API** (`shopify store auth --scopes read_products,read_translations,read_locales,read_markets,write_translations`; potem `store execute`):
   - `translatableResource(resourceId:"gid://shopify/Metafield/<ID>"){ translatableContent{ key digest } translations(locale:"xx"){ value outdated market{handle} } }`
   - Sprawdź: czy tłumaczenie ISTNIEJE, `outdated` (false=digest zgodny), poprawny JSON, **brak pustego market-override** (wymaga `read_markets`).
   - Porównaj pole ZEPSUTE z DZIAŁAJĄCYM (ten sam język): jeśli oba mają identyczną strukturę, outdated=false, brak market, to **bug serwowania/cache tłumaczeń Shopify**.

**4. Próby naprawy (eskalacja):**
   - Re-save w apce / Translate & Adapt (kanoniczna kolejność kluczy rich-text: `{"type":"list","listType":"unordered",...}`, czyli `type` PRZED `listType`; tak wygląda natywny edytor).
   - Czysty `translationsRegister` przez Admin API (`--allow-mutations`, `write_translations`) z `translatableContentDigest` = aktualny digest bazy. **UWAGA: w tamtym sklepie ani re-save, ani czysty API-register + 5 min NIE pomogły** → potwierdzony bug po stronie Shopify. Wtedy: zgłoszenie do **Shopify Support** (główny kanał; nawet ich API nie wymusza serwowania), apka tłumaczeń pobocznie.
   - Trop dla supportu: różnica musi być w niewidocznym przez publiczne API stanie rekordu; poproś o porównanie internal state pola zepsutego vs działającego (ten sam język) i o clear/rebuild translation cache. Historyczna poszlaka: które języki robione natywnie (Translate & Adapt) vs apką; często działają te natywne.

**5. Skan skali (reużywalny, ground-truth):** fetch storefront per locale i sprawdź realny render, nie ufaj, że „działa”. Wzorzec: `GET {primary-domain}/{locale}/products/{handle-bazowy}?cb={random}` (locale-prefix + handle z języka bazowego → Shopify przekieruje na zlokalizowany; `?cb` omija full-page cache). Parsuj kontener renderujący metapole i sprawdź, czy ma treść. Dla motywów XO/`product-specification` cel = `<xo-transform-list-content>` w `product-specification-N__grid` (puste = metapole nie serwuje). Zbuduj macierz produkt × locale → lista „pustych komórek”. `metafield_tag` zwracający CAŁKOWITĄ pustkę (bez wrappera `<div class="metafield-rich_text_field">`) = wartość rozwiązuje się do pustej w warstwie serwowania, nie w Liquid.

**Gotcha:** kolejność kluczy w JSON jest semantycznie nieistotna dla parsera: `listType` przed `type` vs odwrotnie to NIE jest przyczyna braku renderu (potwierdzone: bazowy PL z `listType`-first renderuje się normalnie). To bywa mylący trop; nie trać na to czasu.

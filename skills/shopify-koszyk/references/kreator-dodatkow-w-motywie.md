# Kreator dodatków zbudowany w motywie (bez apki bundle)

Źródło: sklep z pluszakami, 29.09.2026 (Concept 5.3.3, plan „Shopify”, nie Plus). Kod: `sections/addons-builder.liquid`,
`snippets/cart-addon-parent.liquid`, `snippets/cart-bundle-children.liquid`, `snippets/cart-addons-only-check.liquid`.

## Czego nie da się zrobić bez Plus

- **Zagnieżdżenia zestawu w kasie Shopify** („Hide 3 items” pod rodzicem) nie zrobi motyw: to Cart Transform
  (`linesMerge`), a **custom app z funkcjami działa tylko na Plus** (docs „About Shopify Functions”). Apki publiczne
  (EB) mogą. Motyw zagnieżdża dodatki tylko w szufladzie i na `/cart`; w kasie są płaską listą.
- **Blokady adresu `/checkout`** też nie ma bez Plus (Checkout Validation = funkcja). Motyw chowa przyciski kasy.

## Właściwości linii koszyka

- **Panel zamówienia pokazuje ZAWSZE właściwości zaczynające się od `_`**, ukryte są tylko przed klientem
  (koszyk, kasa, mail). Technicznych właściwości daj minimum i krótkie (tu jedna: `_dla` = variant_id produktu głównego),
  resztę licz w Liquid.
- **Wiązanie dodatku z produktem po variant_id, nie po `key` linii**: `key` zmienia się przy każdej zmianie
  właściwości linii (np. pakowanie na prezent), zmiana ilości go nie zmienia.
- **Etykiety widoczne (np. „For toy: Produkt A (brown, 120 cm)”) trzymaj w Ustawieniach motywu**, nie w locales:
  klient chce je w jednym języku niezależnie od języka kupującego, i zmienia zdanie.
- Nazwy wariantów w etykiecie zapisują się w języku, w którym klient przegląda sklep (motyw nie widzi innych).

## Lista produktów do przypisania

- Aktualny koszyk czytaj przez Section Rendering API (`/?section_id=...`), nie z Liquid strony (cache).
  Parsuj odpowiedź `DOMParser`, nie regexem z literałem `<script>` w inline JS (Theme Check: LiquidHTMLSyntaxError).

## Pomiar sprzedaży dodatków bez apki

- **Metapole produktu z `capabilities: {analyticsQueryable: {enabled: true}}`** (od API 2026-04; PRODUCT,
  PRODUCTVARIANT, ORDER, CUSTOMER) staje się wymiarem w Analityce i ShopifyQL:
  `WHERE product.metafields.custom.addon_category IS NOT NULL GROUP BY product.metafields.custom.addon_category`.
- `shopifyqlQuery` wymaga scope `read_reports` (bez niego: „Access denied for shopifyqlQuery field”).
- Jedno zapytanie ze wszystkim: `WITH PERCENT_CHANGE ... COMPARE TO previous_period` (12 kolumn);
  `WITH TOTALS, GROUP_TOTALS` rozdmuchuje do 29 kolumn, nieczytelne.
- Odsetek zamówień z dodatkami = `SHOW orders WHERE <pole> IS NOT NULL` podzielone przez `SHOW orders`
  (dwa zapytania). Zamówienia z net_sales 0 w wynikach to anulowane/zwrócone (testy).

# Produkty widoczne tylko dla firm B2B (2026-10-09, sklep z herbatą)

- **Produkt musi być w kanale Sklep online ORAZ w katalogu B2B.** Zdjęcie produktu ze wszystkich kanałów (żeby ukryć go przed detalem)
  sprawia, że firma też go nie widzi, mimo że jest w publikacji katalogu B2B i ma cenę w cenniku. Objaw zgłoszony przez klienta jako
  „nie widać produktów bez zdjęć”: zdjęcia i stan 0 były fałszywym tropem (karta bez zdjęcia ma placeholder, produkt ze stanem 0 był widoczny).
- **Jak ukryć przed detalem poprawnie:** katalog dla rynków detalicznych (REGION) z publikacją `defaultState: ALL_PRODUCTS`, `autoPublish: true`
  i usuniętymi produktami tylko-B2B (`publicationUpdate.publishablesToRemove`); dopiero potem `publishablePublish` do Sklepu online.
  Bezpieczna kolejność: publikacja bez B2B, `catalogCreate` z `publicationId` i `context.marketIds`, pomiar gościa (te same handle w kolekcjach), publikacja B2B.
  Rynek bez katalogu = gość widzi wszystko ze Sklepu online.
- **Weryfikacja gościa:** 404 na `/products/<handle>`, `.js` i `/en/...`, brak w kolekcjach, wyszukiwarce i sitemap.
  **`/products.json` ignoruje katalog rynku** i nadal listuje produkty tylko-B2B (nazwa i cena bazowa), nie traktuj go jako miary.
  `publishedInContext(context:{country})` też jest niewiarygodne dla gościa.
- Koszt: każdy kolejny produkt tylko-B2B trzeba ręcznie wyłączyć z katalogu detalicznego (autoPublish go doda).

---
name: shopify-b2b-i-dostawa
description: "Natywne B2B w Shopify (firmy, lokalizacje, katalogi, cenniki, limity planów), rynki i waluty oraz strefy i stawki dostawy przez Delivery API. Uruchamiaj przy konfiguracji cen hurtowych, katalogów B2B, kontrahentów, stawek wysyłki, wag i gabarytów, VAT per rynek."
---

# B2B, cenniki i dostawa

Dwie pułapki, które wracają najczęściej:
- **cennik rynku przelicza wszystkie waluty rynku**, łącznie z walutą sklepu,
- **cena stała nie zadziała, jeśli produktu nie ma w publikacji katalogu** (potrzebny `publicationCreate`).

**BaseLinker, faktury i etykiety kurierów:** poza tym pakietem.

## Co tu jest

Wczytuj pojedynczy plik referencyjny, nie cały katalog.

| Plik | Temat |
|---|---|
| `references/b2b-i-dostawa-gotchy.md` | Shopify CLI, B2B i dostawa: gotchy z 2026-08-13/17 (limit tokenów `store auth`, katalog B2B przez rynek, strefy, przekierowania, Rollouts i SimGym, FAQ w szablonie, `themeFilesUpsert`). |
| `references/b2b-jak-dziala.md` | Shopify B2B: jak to naprawdę działa i ile z tego jest natywne (2026-08, plan Grow), limit 3 katalogów, kolejność wdrożenia, checklista danych od klienta. |
| `references/cenniki-detal-kontra-b2b.md` | Który cennik wygrywa: detal kontra B2B; pole `market` lokalizacji firmy nie rozstrzyga ceny, pułapka `RELATIVE`, bezpieczna kolejność zmiany cen (2026-09-23). |
| `references/delivery-api-strefy-i-stawki.md` | Delivery API: strefy wysyłki i stawki przez `deliveryProfileUpdate` (2026-06), `zonesToUpdate.countries` zastępuje listę, zmiana progu wagi (`criteriaUnit: "kg"`) i wyłączanie stawki (2026-10-01). |
| `references/punkty-odbioru-i-ukrywanie-metod.md` | Octolize (cena wg planu Shopify, ORLEN Paczka) i Payflow (zestawy warunków, wykluczenia przewoźników zamiast listy dozwolonych) (2026-09-30); COD w Payflow dopasowuj po „COD”, Globe Pickup Points i bliźniacze stawki paczkomatu (2026-10-12). |
| `references/produkty-tylko-dla-b2b.md` | Produkty tylko dla firm: wymagany kanał Sklep online + katalog detaliczny bez nich, `/products.json` ignoruje katalog rynku (2026-10-09). |

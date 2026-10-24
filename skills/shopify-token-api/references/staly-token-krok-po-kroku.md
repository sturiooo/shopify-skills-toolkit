# Stały token Admin API (custom distribution + authorization code grant)

Potwierdzone 01.10.2026 na dwóch sklepach spoza organizacji agencji.
Wynik: token `shpca_…` bez `expires_in`, działa do odinstalowania apki albo rotacji secretu.
Dokumentacja Shopify: nakaz tokenów wygasających dotyczy aplikacji PUBLICZNYCH, nie custom.

## Dane do zebrania przed startem

1. Domena `*.myshopify.com` sklepu.
2. Lista zakresów od integratora (patrz niżej, gdy jej nie ma).
3. Adres, na który ma wrócić przekierowanie. Wystarczy dowolna działająca domena klienta
   (np. `https://example.com/`): kod czyta się z paska adresu, nic tam nie musi działać.
   Blokada Cloudflare czy stary WooCommerce na tej domenie NIE przeszkadza.

## Komplet zakresów „wszystko o produktach” (sprawdzone w docs + działający token)

```
read_products,write_products,read_inventory,write_inventory,read_locations,read_product_listings,write_product_listings,read_publications,write_publications,read_files,write_files,read_translations,write_translations,read_metaobjects,write_metaobjects,read_metaobject_definitions
```

Pokrywa: produkty, warianty, kolekcje, ceny, metapola produktów, stany i magazyny, widoczność w kanałach,
pliki i zdjęcia, tłumaczenia, metaobiekty. „Oferta” w rozumieniu zamówienia/wyceny wymaga dodatkowo
`read_draft_orders,write_draft_orders` i `read_customers` (zapytaj integratora).
Token zwraca 9 pozycji zamiast 16, bo `write_X` zawiera `read_X`. To poprawne; `access_scopes.json` pokazuje komplet 16.

## Krok 1. Formularz aplikacji (Claude w Chrome)

`https://dev.shopify.com/dashboard/<id-organizacji>/apps/new` (organizacja agencji), opcja „Utwórz aplikację ręcznie”.
NIE `npm init @shopify/app`: szablon dokłada metaobiekt FAQ, metapole i panel w adminie, których integracja nie potrzebuje.

| Pole | Wartość |
|---|---|
| Nazwa aplikacji | `<Sklep> <cel>` np. „<Sklep> system ofert” |
| Nazwa wersji | `v1-produkty` (**bez spacji**: dozwolone litery, cyfry, `. - _ /`) |
| Adres URL aplikacji | `https://<domena-klienta>` |
| Osadź aplikację w panelu | **wyłączone** |
| Dozwolone adresy przekierowania | `https://<domena-klienta>/` (dokładnie ten sam string co `redirect_uri` w linku) |
| Użyj starszego przepływu instalacji | **włączone** |

Pola wypełniaj przez `find` → `ref` (klik/`type`). Komunikat walidacji pod polem przesuwa układ, więc klikanie po
współrzędnych trafia obok. Po wypełnieniu odczytaj wszystkie wartości skryptem.

## Krok 2. Zakresy i utworzenie (CZŁOWIEK)

Auto mode blokuje Claude wpisanie zakresów. Daj userowi listę do wklejenia w pole „Zakresy” → **Utwórz aplikację**.
Jeśli wersja nie wyda się sama: Wersje → Wydaj.

## Krok 3. Dystrybucja (CZŁOWIEK albo Claude)

Aplikacja → Dystrybucja → **Niestandardowa** → domena `*.myshopify.com` → wygeneruj link.
Nieodwracalne. Strona otwiera się w Partners (`partners.shopify.com/<id>/apps/<app-id>/distribution`).
User wkleja: **Client ID** (z Ustawień) i **link instalacyjny** (`.../oauth/install_custom_app?client_id=…&signature=…`).

## Krok 4. Link instalacyjny NAJPIERW (CZŁOWIEK)

Otworzyć link z dystrybucji. Przy legacy flow **nie ma ekranu zgody**: przeglądarka idzie na app URL
(sklep klienta „jakbym miał coś kupić”). To poprawne. Ten krok dopuszcza sklep do instalacji.
Bez niego krok 5 kończy się „Link instalacyjny dla tej aplikacji jest nieprawidłowy” (01.10.2026).

## Krok 5. Link autoryzacyjny (CZŁOWIEK zatwierdza)

Skrypt `token.sh` z katalogu tego skilla:
`bash "${CLAUDE_PLUGIN_ROOT:-.}/skills/shopify-token-api/token.sh" url <sklep>.myshopify.com <client_id> <redirect> "<zakresy>"`
albo ręcznie:

```
https://<sklep>.myshopify.com/admin/oauth/authorize?client_id=<ID>&scope=<zakresy po przecinku>&redirect_uri=https://<domena>/&state=<dowolne>
```

Ekran zgody → **Zainstaluj** → przekierowanie na `https://<domena>/?code=…&hmac=…&host=…&shop=…&state=…&timestamp=…`.
User wkleja cały adres. **Kod żyje kilka minut i działa raz.**

## Krok 6. Wymiana kodu na token (Claude albo człowiek)

Dwie opcje, zapytaj usera, którą woli:
- **user wkleja kod i secret** → Claude robi `token.sh exchange` od razu (secret ląduje w czacie);
- **user wkleja sam kod** → Claude daje komendę, user uruchamia u siebie, NIE przez `!` (secret zostaje u niego).

```
curl -s -X POST https://<sklep>.myshopify.com/admin/oauth/access_token -d client_id=<ID> -d client_secret=<SECRET> -d code=<KOD>
```

**BEZ `expiring=1`** (z nim token wygasa po godzinie i przychodzi refresh token).
Gdy user wkleja komendę z placeholderami: pilnuj, żeby nie zostało dosłowne `CLIENT_SECRET` (pierwsze wdrożenie: secret
dokleił się do kodu → `Missing or invalid client secret`). Najbezpieczniej podać komendę z wstawionymi wartościami
albo przez zmienne w osobnych liniach (`SECRET='…'`, `KOD='…'`, potem `"client_secret=$SECRET"`).

## Krok 7. Weryfikacja (Claude, tylko odczyt)

`bash "${CLAUDE_PLUGIN_ROOT:-.}/skills/shopify-token-api/token.sh" verify <sklep>.myshopify.com <token>`:
nazwa sklepu, liczba produktów, liczba zakresów. Oczekiwane: właściwy sklep, >0 produktów, komplet zakresów.

## Krok 8. Domknięcie

- Tekst dla integratora: `references/wiadomosc-dla-integratora.md`.
- Notatka bez sekretów (Client ID, app id, zakresy, data, jak odebrać dostęp) w dokumentacji projektu.
- Zamknij swoje karty w Chrome.

## Rozszerzenie zakresów później

Nowa wersja z większą listą → Wydaj → ponownie krok 5 (instalacja już jest, od razu wraca `code`) → krok 6.
Powstaje NOWY token; integrator musi go podmienić.

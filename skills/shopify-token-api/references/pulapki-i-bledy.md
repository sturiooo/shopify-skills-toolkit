# Błędy i pułapki przy wydawaniu tokenu (stan 01.10.2026)

| Objaw | Przyczyna | Naprawa |
|---|---|---|
| Panel sklepu nie ma „Projektuj aplikacje” / integrator odsyła tam | ścieżka martwa dla nowych apek od 2026 | Dev Dashboard, ta procedura |
| `shop_not_permitted` (400) przy client credentials | apka w innej organizacji niż sklep | stały token przez custom distribution (`staly-token-krok-po-kroku.md`) |
| `app_not_installed` (400) przy client credentials | organizacja OK, brak instalacji | zainstalować apkę w sklepie |
| „Link instalacyjny dla tej aplikacji jest nieprawidłowy” na ekranie instalacji | link autoryzacyjny otwarty PRZED linkiem z dystrybucji | najpierw link `install_custom_app` z Partners, potem authorize |
| Link z dystrybucji prowadzi do sklepu „jakbym miał coś kupić” | legacy flow: przekierowanie na app URL, bez ekranu zgody | to poprawne; teraz otworzyć link authorize |
| „Nazwa wersji: Może zawierać tylko litery, cyfry i znaki . - _ /” | spacja w nazwie wersji | `v1-produkty` |
| `Oauth error invalid_request: Missing or invalid client secret` | w komendzie zostało dosłowne `CLIENT_SECRET`, secret dokleił się do kodu | podać komendę z wstawionymi wartościami; kod zwykle nadal ważny, jeśli minęło mało czasu |
| `invalid_request` dotyczący kodu | kod wygasł albo użyty | ponownie link authorize (apka zainstalowana → od razu nowy `code`) |
| Token przyszedł z `expires_in` i `refresh_token` | w wymianie było `expiring=1` | powtórzyć wymianę bez tego parametru |
| Token zwraca mniej zakresów niż wpisano | `write_X` zawiera `read_X` | poprawne; sprawdź `access_scopes.json` (pełna lista) |
| Prefiks `shpca_` zamiast `shpat_` | token apki z custom distribution | normalne, działa identycznie |

## Blokady auto mode (Claude Code)

- **Wpisanie zakresów w formularzu apki** → odmowa „Permission Grant”. Nie obchodzić; zakresy wkleja człowiek.
- **Zatwierdzenie instalacji / ekran zgody** → ta sama kategoria; klika człowiek.
- **Wymiana kodu na token i weryfikacja curl-em** → przechodzą (to nie nadawanie uprawnień).
- Odczyt linku z `signature=` przez `javascript_tool` bywa blokowany filtrem („Cookie/query string data”) → poproś usera o wklejenie.

## Sesja przeglądarki

- Wejście na `dev.shopify.com` potrafi przekierować przez `accounts.shopify.com` do panelu INNEGO sklepu
  („Konto … nie ma uprawnień do wyświetlenia tej strony”). Po prostu nawiguj ponownie na adres Dev Dashboard.
- Dev Dashboard agencji: `https://dev.shopify.com/dashboard/<id-organizacji>/apps`. Do organizacji klienta
  zwykle nie masz loginu i tej drogi nie potrzebujesz.

## Bezpieczeństwo

- Secret wklejony w czat = wyciek do historii rozmowy. Zaproponuj rotację **przed** wydaniem tokenu
  (rotacja po wydaniu unieważni token u integratora). Decyzja należy do usera.
- Token daje zapis w katalogu: integrator trzyma go tylko po stronie serwera.

---
name: shopify-token-api
description: "Wydanie klucza / tokenu Admin API dla zewnętrznego systemu (integrator, system ofert, ERP, magazyn, hurtownia) na sklepie klienta: aplikacja w Dev Dashboard, custom distribution, stały token shpca_ przez authorization code grant albo token 24 h przez client credentials. Uruchamiaj, gdy ktoś prosi o „klucz API”, „token do sklepu”, „połączenie systemu ze sklepem”, „npm init @shopify/app dla klienta”, gdy integracja każe iść w Aplikacje → Projektuj aplikacje (martwa ścieżka), oraz przy błędach shop_not_permitted, app_not_installed, „Link instalacyjny dla tej aplikacji jest nieprawidłowy”, invalid_request przy access_token."
---

# Token Admin API dla zewnętrznego systemu

**Najważniejsze:** od 2026 nie ma „aplikacji niestandardowej w panelu sklepu” i nie ma tokena do skopiowania.
Token powstaje z aplikacji w **Dev Dashboard**. Która droga, zależy od jednego pytania:
**czy sklep jest w organizacji agencji (Twojej organizacji w Dev Dashboard)?** (`shopify store list`).

| Sytuacja | Droga | Token |
|---|---|---|
| Sklep spoza organizacji agencji (typowy klient, pracujesz jako współpracownik) | **custom distribution + authorization code grant** | `shpca_…`, **nie wygasa** |
| Sklep w organizacji agencji | client credentials grant | `shpat_…`, **24 h**, integrator musi odnawiać |
| Integrator ma apkę w App Store | zainstalować jego apkę | nie robimy nic |
| **SellAsist** (nowy moduł) | ZAWSZE apka w organizacji właściciela sklepu + client credentials | gotowego `shpca_` NIE przyjmie (01.10.2026: „Nie udało się wygenerować access_token”, test = `shop_not_permitted`) |

Integratorzy prawie zawsze chcą **stałego tokenu**. Domyślnie idź pierwszą drogą, ona działa też dla sklepów w organizacji.

## Co tu jest

Wczytuj pojedynczy plik referencyjny, nie cały katalog.

| Plik | Kiedy |
|---|---|
| `references/staly-token-krok-po-kroku.md` | **Główna procedura.** Kroki człowieka i Claude, kolejność linków, wymiana kodu, weryfikacja. |
| `references/pulapki-i-bledy.md` | Komunikat błędu albo coś „nie działa”: tabela błąd → przyczyna → naprawa, blokady auto mode. |
| `references/client-credentials.md` | Sklep w organizacji agencji i integrator umie odnawiać token co dobę. |
| `references/wiadomosc-dla-integratora.md` | Gotowy tekst do wysłania programiście (bez tabelek, do wklejenia). |
| `token.sh` | Skrypt: `url` buduje link autoryzacyjny, `exchange` wymienia kod na token, `verify` sprawdza token. |

## Zasady stałe

- **Najpierw zakresy od integratora.** Nie „poprawiaj” jego listy z pamięci (SellAsist 08.2026: usunięty `write_locations`
  istniał, klient przechodził instalację drugi raz). Gdy integrator nie wie: komplet produktowy z referencji, `write_`.
- **Osobna aplikacja na integrację i sklep**, nie dopisywanie zakresów do innej apki. Da się ją wyłączyć bez ruszania reszty.
- **Custom distribution jest NIEODWRACALNE** i przypina apkę do jednego sklepu. To pożądane.
- **Wpisanie zakresów i zatwierdzenie instalacji robi człowiek.** Auto mode blokuje to w przeglądarce („Permission Grant”).
  Claude wypełnia resztę formularza, buduje linki, wymienia kod, weryfikuje.
- **Rotacja Client secret unieważnia stały token.** Jeśli secret wyciekł (np. wklejony w czat), rotuj PRZED wydaniem tokenu.
- **Sekretów nie zapisujemy w plikach repo.** Notatka po wdrożeniu (Client ID, zakresy, data, jak odebrać dostęp) bez secretu i tokenu.
- **Aplikacja w organizacji agencji = własność agencji.** Powiedz o tym klientowi; przy końcu współpracy trzeba ją przenieść.

## Wdrożenia referencyjne

Procedura przeszła na dwóch sklepach spoza organizacji 01.10.2026: pierwsze przejście z błędami (opisane w `pulapki-i-bledy.md`),
drugie czysto, w około 10 minut.

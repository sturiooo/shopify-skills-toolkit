---
name: shopify-diagnostyka
description: "Metodyka potwierdzania faktów zanim postawisz diagnozę: weryfikacja curl-first, cache storefrontu serwujący kilka wersji naraz, ustawienie z panelu które nie dochodzi do bloku, tłumaczenie metapola które się nie wyświetla, konwersje GTM które przestały się liczyć. Uruchamiaj, gdy coś nie działa mimo poprawnego kodu, gdy zmiana nie weszła po wgraniu, i zanim napiszesz klientowi, co jest przyczyną."
---

# Diagnostyka: zanim ogłosisz przyczynę

Najczęstszy błąd w pracy nad sklepami nie jest błędem kodu, tylko **błędem pomiaru**: mierzysz co innego, niż myślisz. Zanim postawisz diagnozę, sprawdź przesłankę, na której się opiera.

Po każdym wgraniu na sklep: **nie ufaj komunikatowi "success"**, ściągnij plik z powrotem i zgrepuj markery.

## Co tu jest

Wczytuj pojedynczy plik referencyjny, nie cały katalog.

| Plik | Temat |
|---|---|
| `references/cache-storefrontu.md` | Cache storefrontu potrafi serwować KILKA różnych wersji naraz (2026-08-20, sklep z kawą funkcjonalną, Stretch). |
| `references/curl-first.md` | Diagnostyka „curl-first”: jak potwierdzać fakty bez przeglądarki (2026-08); fałszywe „0 wyników” przez zsh. |
| `references/kolor-wypalony-w-pliku.md` | Kolor nie znika mimo poprawnego CSS, bo siedzi w pikselach pliku (2026-09-22); odczyt piksela, przemalowanie bez obwódki, podmiana zdjęcia kolekcji przez API. |
| `references/kolekcja-automatyczna-opoznienie.md` | Kolekcja automatyczna po zmianie tagów przelicza się ok. minutę: liczność i storefront kłamią, tagi na produkcie nie (2026-10-02). |
| `references/konwersje-gtm.md` | Diagnostyka „przestały się liczyć konwersje”: GTM i Google Ads (2026-08-19); dodatkowo fallback widgetu Judge.me, FAQ per produkt z metapól, mapa punktów sprzedaży bez apki. |
| `references/przekierowanie-na-wersje-robocza.md` | Przekierowanie 301 jest, a adres daje 404, bo cel to produkt w wersji roboczej; audyt reguł po statusie celu. Ta sama przyczyna w linkach menu `HTTP` i status `UNLISTED` chowający produkty z kolekcji (2026-09-24, 29). |
| `references/przekierowania-trafnosc-po-migracji.md` | Przekierowania po migracji: 99% pokrycia, a 29% produktów trafia w inny typ (soft 404); pomiar z web.archive.org + `urlRedirects`, brak daty utworzenia reguły (2026-10-06). |
| `references/sklep-wielojezyczny-czego-nie-tlumaczy-tlumaczenie.md` | Drugi język: puste próbki kolorów (osobne tłumaczenie `color_swatch_config`), duplikaty i opóźnienie filtra S&D z metapola, nieprzetłumaczalne tagi artykułów (etykieta z locale), obraz per język w sekcji; curl nie widzi paska tagów bloga (2026-10-09, Prestige). |
| `references/tlumaczenie-metapola.md` | Playbook: „tłumaczenie metapola się nie wyświetla w danym języku”. |
| `references/ustawienie-nie-dziala.md` | Diagnostyka „ustawienie z panelu NIE działa” w blokach FoxEcom/Sleek (2026-06). |
| `references/zmierz-efekt-nie-znacznik.md` | Weryfikacja na efekcie, nie na śladzie zmiany: niejawna kolumna siatki, SEO strony głównej poza Admin API, rozrzut PageSpeed przez hCaptchę Shopify Forms (2026-09-25). |
| `references/domena-dns-nazwa-pl.md` | Domena pokazuje parking zamiast sklepu: pytaj serwer autorytatywny, cache routera, format rekordów nazwa.pl (pełne nazwy, CAA z cudzysłowem, CNAME www odrzucany → A), CAA wymagane przez Shopify, MX zależny od A, poczta u innego dostawcy (2026-10-12/20). |
| `references/domena-w-cudzym-koncie-cloudflare.md` | Domena delegowana do Cloudflare, ale nie ma jej na koncie klienta: para NS = konto, ślepa strefa w LH.pl, Connect zamiast Transfer, odtwarzanie strefy bez eksportu (wildcard fałszuje odczyt), NS osobno od przepięcia na Shopify (2026-10-13). |
| `references/stany-zewnetrzny-magazyn.md` | „W magazynie 0, a w sklepie da się kupić”: śledzenie na dzień zamówienia, integracja (SellAsist) zapisuje tylko przy zmianie u siebie, fantom po zwrocie z restockiem, pełne porównanie z listy ofert SellAsist, naprawa (2026-10-16). |
| `references/render-headless-mobile.md` | Render mobile w headless Chrome: `--window-size` to nie viewport (fałszywe „wychodzi poza ekran”), emulacja przez CDP, ukryte elementy na liście wystających, zrzuty po kolei, usuwanie banerów cookies (2026-10-18). |

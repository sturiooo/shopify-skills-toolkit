# Diagnostyka „curl-first”: jak potwierdzać fakty bez przeglądarki (2026-08)

| Potrzeba | Sposób |
|---|---|
| Uchwyty i tytuły produktów bez Admin API | `curl -s "https://<sklep>/products.json?limit=250"` |
| Czy sekcja/snippet faktycznie się renderuje | `curl` strony + `grep` po markerach z markupu (nie po klasach z CSS, te są w `<style>` i dają fałszywe trafienia!) |
| Konfiguracja apki na storefroncie | `grep -oE 'window\.<nazwa>Settings.{0,200}'`: apki wypychają ustawienia do HTML |
| Platforma sklepu (migracja) | `grep -oiE "woocommerce\|wp-content\|cdn.shopify\|idosell"` |
| Fakty o domenie i poczcie | `dig +short NS/A/MX/TXT <domena>` |
| Kolory z zrzutu ekranu (bez PIL) | dekompresja PNG: `zlib` + defiltering scanlinii (Paeth/Sub/Up/Average) + histogram obszaru |

**Cloudflare challenge (`cf-mitigated: challenge`, 403 na `/`, `/sitemap.xml`, `/products.json`)
kończy temat**: nie obchodzimy bot-detekcji. Wtedy dane pobiera klient z przeglądarki
(sitemapy XML, eksport produktów, eksport z Search Console).

**Uwaga na fałszywe potwierdzenia:** `grep` po nazwie klasy trafi też w blok `{% style %}` sekcji.
Sprawdzaj po **tekstach lub ID, które istnieją wyłącznie w markupie** (np. `JdgmPlaceholder-`,
treść dopisku), inaczej „widzę klasę, więc się renderuje” jest błędem.

---

## Fałszywe „0 wyników” przez zsh (2026-10-03)

- **zsh nie dzieli niecytowanej zmiennej na słowa** (w przeciwieństwie do bash): `python3 - $EANS` dostaje JEDEN argument
  z 10 kodami, zapytanie `barcode:<wszystkie naraz>` zwraca 0 i wygląda jak „nie ma w sklepie”.
- Recepta: listy trzymaj w pliku (`eans.txt`, `read().split()`), a każde „nie ma” potwierdź kontrolą pozytywną
  (to samo zapytanie na kodzie, który na pewno istnieje). Przy 10 i 8 kodach dopiero kontrola wykazała błąd.

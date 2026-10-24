# Ikony w bloku: zestaw motywu (`render 'icon'`) vs samodzielny + własna grafika

**Wdrożone:** sklep z pluszakami (2026-06, motyw na bazie Nook).

**Kolejność decyzji:**

1. **Sprawdź czy motyw ma `snippets/icon.liquid`** (`grep -rl "render 'icon'"`). Nook/Horizon mają bogaty zestaw, wylistuj dostępne nazwy: `grep -oE "when '[^']+'" snippets/icon.liquid`. Wtedy select z **prawdziwymi nazwami ikon motywu** + `{%- render 'icon', icon: block.settings.x -%}`.
2. **Jeśli snippetu NIE ma w eksporcie** (częste: klient wkleja pojedyncze pliki), **nie zgaduj nazw**. Zaszyj samodzielny zestaw SVG w sekcji (`case` z inline `<svg stroke="currentColor">`), bo `render 'icon'` z nieistniejącą nazwą = pusta ikona. Self-contained renderuje się niezależnie od motywu.

**ZAWSZE waliduj nazwy ikon przed wysłaniem**, gdy używasz `render 'icon'`:
```bash
for ic in package return lock star; do grep -q "when '$ic'" icon.liquid && echo "OK $ic" || echo "MISSING $ic"; done
```

**Rozmiar i kolor ikony z `render 'icon'`:** snippet zwykle dodaje klasy (`icon icon-md`). Pełną kontrolę px daj własnym CSS targetując `.twoj-wrap .icon { width: var(--x); height: var(--x); }` (specyficzność `.wrap .icon` > `.icon-md`). Kolor: `color` na wrapperze → ikony na `currentColor` (fill/stroke) podążają.

**Opcja „własna ikona" (image_picker nadpisuje listę):** dodaj `image_picker` obok selecta. W renderze priorytet: wgrana grafika → ikona z listy → nic.
```liquid
{%- if ts_image != blank -%}
  {{ ts_image | image_url: width: 128 | image_tag: loading: 'lazy', widths: '32,64,96,128', class: 'ts-custom-icon', alt: ts_alt }}
{%- elsif ts_icon != 'none' -%}
  {%- render 'icon', icon: ts_icon -%}
{%- endif -%}
```
CSS: `.ts-custom-icon { width: var(--icon); height: var(--icon); object-fit: contain; }`, kwadratowy box, brak deformacji niekwadratowych. **Gotcha do zakomunikowania klientowi:** „Kolor ikon" NIE działa na wgrane grafiki (rastrowe mają własny kolor; SVG wstawiony jako `<img>` też jest izolowany od `currentColor`).

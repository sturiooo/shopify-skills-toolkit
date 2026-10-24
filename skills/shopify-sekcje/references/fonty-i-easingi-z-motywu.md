# Fonty i easingi z motywu: zmienne CSS zamiast `font_picker`/hardkodu

**Wdrożone:** sklep z pluszakami (motyw na bazie Nook, 2026-06).

Gdy klient mówi „fonty z szablonu", nie dawaj `font_picker` (dubluje konfigurację motywu) ani nie hardkoduj. Ten motyw (i większość nowych OS 2.0) eksponuje rodziny, wagi i easingi jako globalne zmienne CSS, używaj ich bezpośrednio:

| Zmienna | Wartość |
|---|---|
| `--font-body-family`, `--font-heading-family`, `--font-navigation-family`, `--font-button-family`, `--font-product-family` | rodziny czcionek |
| `--font-normal` / `--font-medium` / `--font-bold` | wagi (400/500/700) |
| `--font-body-weight`, `--font-heading-weight` | wagi przypisane do roli |
| `--animation-fast` (0.3s), `--animation-primary` (0.5s), `--animation-smooth` (0.7s), `--animation-nav` (0.5s) | gotowe `transition`/easing cubic-bezier |

Pattern: select w schema (`body`/`heading`/`navigation`) → mapowanie przez `case` na `var(--font-*-family)` → wstaw do CSS custom property sekcji. Transition w komponencie: `var(--animation-fast, 0.3s ease)` (z fallbackiem, gdy motyw nie ma zmiennej). **Sprawdź `grep -i "font-.*-family\|--animation" theme.css` w nowym motywie**, nazwy bywają inne (Dawn: `--font-body-family` też, ale starsze mają `--font-body-scale`).

Procent z range na skalę CSS: `transform: scale({{ s.hover_scale | divided_by: 100.0 }})`, range `100..120 %` → `1.0..1.2`.

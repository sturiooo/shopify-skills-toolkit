# Architektura fontów motywu Sleek/FoxEcom: nagłówki HARDKODOWANE, globalny override w theme.liquid

**Wdrożone:** sklep z suplementami dla psów (2026-06). Kosztowało godzinę zgadywania „dlaczego nagłówek sekcji ma inny font niż reszta".

**Sedno (pułapka diagnostyczna):** motyw **nie używa własnej zmiennej** `--font-heading-family` do stylowania nagłówków. W `assets/theme.css` (~linia 1109) jest na sztywno:
```css
h1,.h1, h2,.h2, h3,.h3, h4,.h4, h5,.h5, h6,.h6 { font-family: "aktiv-grotesk-extended", sans-serif; font-weight:600; ... }
```
(plus ~10 dalszych hardkodów `aktiv-grotesk` dla `.hd1/.h0/.font-heading/.text-pcard-title`). Czyli **zmiana fontu nagłówków w Typografii NIE zmienia renderu**, `--font-heading-family` (= `settings.type_header_font.family`, def. w `snippets/css-variables.liquid:342`) jest ignorowana.

**Gdzie naprawdę żyją globalne fonty:** `layout/theme.liquid` ma inline `<style>` w `<head>` (po linku do `theme.css`, więc wygrywa kaskadą) z `@font-face` dla fontów marki (tu: **`'Brand Heading'`, `'Brand Heading Italic'`, `'Brand Sans'`**) + override `h2 { font-family:'Brand Heading Italic' !important; font-weight:600!important; font-style:italic!important }` (to ON nadaje nagłówkom sklepu kursywę fontu marki, nie zmienna motywu) oraz `.btn { 'Brand Heading' !important; uppercase }`.

**Reguły praktyczne:**
- „Zmień font wszystkich nagłówków" → **edytuj/rozszerz tę regułę w `theme.liquid`** (np. `h2` → `h1, h2, h3`), NIE Typografię i NIE `theme.css` (hardkod + ogromny plik do re-copy). `!important` konieczny, by pobić hardkod `theme.css`.
- „Jaki font ma nagłówek X?" → najpierw **sprawdź inline `<style>` w `theme.liquid`** (override `h2`/`.btn`), potem hardkody `aktiv-grotesk` w `theme.css`, dopiero na końcu zmienne. Nie zakładaj, że `--font-heading-family` cokolwiek robi.
- Globalny override tagów `h1/h2/h3` z `!important` **klobruje też klasowe fonty na tych tagach** (np. tytuł produktu `<h2 class="hd1">` w kursywie fontu marki, i tak był w foncie marki, więc spójnie; ale pamiętaj o efekcie ubocznym i zakomunikuj klientowi).
- Konsekwencja dla customów: w sekcji ustawienie „krój/grubość nagłówka" jest martwe, dopóki globalny `h2{...!important}` istnieje, nagłówek-`h2` zawsze dostanie kursywę fontu marki 600. Jeśli chcesz, by tytuły kafelków wyglądały „jak nagłówek", **renderuj je jako `h3`** i pozwól globalnej regule je złapać (nie ustawiaj im fontu lokalnie na `var(--font-heading-family)`, to inny font niż widoczny font marki).

# Sekcja "As Seen In" (press bar)

**Wdrożone:** sklep z obuwiem (2026-05, samodzielna sekcja).

Prosta belka z etykietą i nazwami mediów. Plik: `sections/as-seen-in.liquid`.

**Schema settings:**
- Etykieta: tekst, rozmiar (8-18px), kolor, pogrubienie (checkbox)
- Marki: rozmiar desktop (12-24px), rozmiar mobile (10-20px), kolor
- Tło + padding górny/dolny
- Bloki `brand`: nazwa + opcjonalny URL

**Animacja podkreślenia na hover:**
```css
.asi-brand { position: relative; }
.asi-brand::after {
  content: '';
  position: absolute;
  bottom: -3px; left: 0;
  width: 100%; height: 1px;
  background: currentColor;
  transform: scaleX(0);
  transform-origin: left center;
  transition: transform 0.3s ease;
}
.asi-brand:hover::after { transform: scaleX(1); }
```
`currentColor` śledzi kolor tekstu, jeden kolor picker wystarczy dla obu stanów.

**Gotcha: bold etykiety przez Liquid w CSS variable:**
```liquid
--asi-label-weight: {% if section.settings.label_bold %}700{% else %}var(--font-body-weight){% endif %};
```
Nie używaj `assign` + interpolacji do CSS, bezpośrednie `{% if %}` w bloku `<style>` lub CSS variable jest poprawne i czytelne.

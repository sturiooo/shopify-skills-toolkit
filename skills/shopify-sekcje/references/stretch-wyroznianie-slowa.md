# Stretch (Maestrooo): wyróżnianie słowa w nagłówku jest NATYWNE (2026-08-20, sklep z kawą funkcjonalną)

Zanim zbudujesz własny mechanizm „podświetl słowo w nagłówku", **Stretch ma to gotowe**:
`snippets/heading.liquid` + komponent `highlighted-heading` (w `theme.js`, ładowany globalnie).

**Jak działa:** klient zaznacza słowo **kursywą** w edytorze → snippet zamienia `<em>` na
`<highlighted-heading effect="...">` i nakłada efekt. Osiem efektów: `none`, `italic`, `circle`,
`circle_pencil`, `underline`, `underline_pencil`, `marker`, `tilted_marker`.

Podpięcie w customowej sekcji (zachowuje własne klasy przez `style:`):
```liquid
{%- assign heading_classes = 'section__heading ' | append: section.settings.heading_size -%}
{%- render 'heading',
  content: section.settings.heading, html_tag: 'h2', style: heading_classes,
  highlight_effect: section.settings.heading_highlight_effect,
  highlight_accent_color: section.settings.color_highlight_accent,
  highlight_text_color: section.settings.color_highlight_text -%}
```
Pole nagłówka musi być **`inline_richtext`** (żeby dało się wpisać kursywę). Gdy w treści nie ma
`<em>`, snippet zwraca zwykły `<h2 class="...">`, **zero regresji**, można podpiąć w ciemno.

### Krój wyróżnienia zmieniaj LOKALNIE, nie w ustawieniach motywu

Efekt `italic` czyta `--heading-italic-font-*`, ustawiane globalnie w `snippets/css-variables.liquid`
z `settings.heading_italic_font`. **Zanim to ruszysz: policz, ile `<em>` jest już w sklepie**
(`grep -c '<em>' templates/*.json sections/*-group.json`). U nas 8 wystąpień na samej stronie
głównej → zmiana globalna ruszyłaby wszystkie. Zamiast tego nadpisz zmienne w obrębie sekcji:
```liquid
{%- assign hf = section.settings.highlight_font -%}
{%- assign hf_italic = hf | font_modify: 'style', 'italic' -%}
{{ hf | font_face: font_display: 'swap' }}
{%- if hf_italic -%}{{ hf_italic | font_face: font_display: 'swap' }}{%- endif -%}
#shopify-section-{{ section.id }} .highlighted-heading {
  --heading-italic-font-family: {{ hf.family }}, {{ hf.fallback_families }};
  --heading-italic-font-weight: {{ hf.weight }};
  --heading-italic-font-size-multiplier: {{ section.settings.highlight_font_size_multiplier }}%;
}
```
**`font_modify: 'style', 'italic'` jest konieczne**, `font_picker` zwraca krój w stylu normalnym,
a CSS efektu wymusza `font-style: italic`; bez wgrania wariantu przeglądarka rysuje **sztuczną
kursywę** (pochylony regular), co w serifach widać od razu. `font_modify` zwraca `nil`, gdy krój
nie ma italika, dlatego guard `{%- if hf_italic -%}`.

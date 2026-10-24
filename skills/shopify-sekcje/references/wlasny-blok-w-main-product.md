# Dodawanie własnego bloku do istniejącej sekcji `main-product` (zamiast nowej sekcji)

**Wdrożone:** sklep z pluszakami (2026-06, motyw na bazie Nook: bloki produktu „Pasek zaufania", rozbudowa bloku „sku").

Gdy klient chce „element na karcie produktu" w kolumnie informacji (trust signals, SKU, custom badge), to **blok w sekcji `main-product`**, nie osobna sekcja. Standalone sekcja ląduje poza kolumną info i nie integruje się z układem produktu. Sygnał z praktyki: pierwsza wersja jako sekcja → klient poprawia „ma być jako blok do dodania w main product info".

**Jak motyw Nook/Dawn renderuje bloki produktu:** w sekcji jest pętla `{%- for block in section.blocks -%}` → `{%- case block.type -%}` z `when` per typ. Dodanie własnego bloku = **dwa miejsca**:

1. Nowy `{%- when 'twoj_typ' -%}` w pętli renderującej (z `{{ block.shopify_attributes }}` na elemencie).
2. Nowy obiekt w tablicy `"blocks": [...]` w `{% schema %}`.

Etykiety motywu są przez `t:...` (locale theme), ale Twój blok możesz opisać **zwykłymi stringami PL**, Shopify pozwala mieszać `t:` z literałami w jednym schemacie.

**Powtarzalne pozycje BEZ sub-bloków (bloki sekcji nie zagnieżdżają się):** gdy blok ma N stałych pozycji (np. 4 ikony), nie ma „bloków w bloku". Robisz N kompletów settingów (`icon_1..4`, `text_1..4`) i iterujesz z **dynamicznym dostępem do settingów**, to działa w Shopify Liquid:

```liquid
{%- for i in (1..4) -%}
  {%- assign icon_key = 'icon_' | append: i -%}
  {%- assign text_key = 'text_' | append: i -%}
  {%- assign ic = block.settings[icon_key] -%}
  {%- assign tx = block.settings[text_key] -%}
  {%- if ic != 'none' or tx != blank -%}  {# pusta pozycja → pomiń #}
    <li>…</li>
  {%- endif -%}
{%- endfor -%}
```

`block.settings[zmienna]` (bracket access ze zmienną) jest wspierane, pozwala uniknąć 4× copy-paste markupu.

**Gotchy:**

- **Scoped `<style>` w pętli bloków**: scope przez `#TwojBlok-{{ block.id }}` (nie `section.id`!), bo blok ma własne `block.id`. Kilka instancji bloku = kilka bloków `<style>`, każdy unikalny → brak kolizji. Wartości settingów → CSS custom properties.
- **Walidacja przed renderem pozycji**: `if ic != 'none' or tx != blank`: pusta ikona + puste hasło = pozycja ukryta. Klient steruje liczbą widocznych pozycji bez dotykania kodu.
- **Kontrola rozmiaru osobno mobile/desktop**: para range'ów + nadpisanie zmiennej CSS w `@media (max-width: 749px)`.

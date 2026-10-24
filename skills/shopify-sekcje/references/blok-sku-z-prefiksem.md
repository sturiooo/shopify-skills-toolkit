# Blok SKU z konfigurowalnym przedrostkiem (label + bold + guard + padding)

**Wdrożone:** sklep z pluszakami (2026-06, motyw na bazie Nook, blok `sku` w `main-product`).

Domyślny blok SKU motywu renderuje sam kod. Klient chce `SKU: <kod>`. Rozbudowa bloku (motyw renderuje info produktu server-side przy zmianie wariantu, więc prefiks w Liquid przetrwa, sprawdź najpierw `grep "Sku-\|\.sku"` czy jakiś JS nie nadpisuje `#Sku-...textContent`; jeśli nadpisuje → label przez CSS `::before`, nie Liquid).

```liquid
{%- when 'sku' -%}
  {%- assign current_sku = product.selected_or_first_available_variant.sku -%}
  {%- if current_sku != blank -%}   {# brak SKU → cały blok (z etykietą) ukryty #}
    <p class="product__sku" style="padding-top: {{ block.settings.padding_top }}px; padding-bottom: {{ block.settings.padding_bottom }}px;" {{ block.shopify_attributes }}>
      {%- if block.settings.label != blank -%}<span style="font-weight: 700;">{{ block.settings.label }}</span> {% endif -%}
      <span class="product__sku-value">{{ current_sku }}</span>
    </p>
  {%- endif -%}
```

**Kluczowe:** guard `current_sku != blank` opakowuje WSZYSTKO: gdy produkt nie ma SKU, przedrostek „SKU:" nie wisi sam. Etykieta renderuje się tylko gdy niepusta (brak zbędnej spacji gdy klient ją wyczyści). Wartość w osobnym `<span>` do ewentualnego stylowania.

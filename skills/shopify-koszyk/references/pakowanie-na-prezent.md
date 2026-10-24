# Checkbox „pakowanie na prezent" w koszyku (dopłata): produkt-linia, nie opłata

**Wdrożone:** sklep z kosmetykami (2026-06, motyw **Sahara 3.0.0 / DigiFist**, sklep PL). Mechanika koszyka jak Dawn/Sense: `assets/cart.js` = `fetch` + Section Rendering API + `document.dispatchEvent('cart:updated')`. Motyw ma już `assets/gift-tier.js` (free-gift): **idealny wzorzec do skopiowania `requestRefresh()`**.

#### Krytyczna wiedza: suma koszyka zmienia się WYŁĄCZNIE przez line item

Nie istnieje w theme/JS API „dorzuć X zł do total". Każda kwota = realna pozycja. Dowolne opłaty w koszyku to dopiero Shopify Functions/Scripts (Plus, i to w checkoutcie). Dlatego „pakowanie na prezent z dopłatą" = **ukryty produkt** „Pakowanie na prezent" (cena dopłaty, 1 wariant, inventory tracking OFF, bez kolekcji). Checkbox zaznaczony → `/cart/add.js` z `properties: { _gift_wrap: 'true' }`; odznaczony → usuń. Suma rośnie/maleje sama. To samo robią wszystkie apki „Gift Wrap".

#### Implementacja (pliki)

- `snippets/gift-wrap-checkbox.liquid`: checkbox + cena (`gw_variant.price | money`), renderowany w `sections/main-cart.liquid` (przy `cart-terms-checkbox`) i `snippets/cart-drawer.liquid`. Skrypt ładowany przez `<script src>` w snippecie (browser dedupuje).
- `assets/gift-wrap.js`: `setWrap(shouldHave)` + `requestRefresh()` (skopiowany 1:1 z `gift-tier.js`: odświeża `#CartDrawer-Body`, `#CartDrawer-Summary`, main `cart-items` przez `?sections=`).
- `config/settings_schema.json`: grupa Cart: `enable_gift_wrap` (checkbox), `gift_wrap_product` (product picker), `gift_wrap_border` (checkbox).

#### Gotchy

1. **Stan checkboxa synchronizuje się SAM przez Liquid server-side.** W snippecie `{%- for item in cart.items -%}` sprawdzasz `item.variant_id == gw_variant.id or item.properties['_gift_wrap'] == 'true'` → `gw_in_cart` → `{% if gw_in_cart %}checked{% endif %}`. Każdy Section Render (też przy zmianie ilości innego produktu) re-renderuje snippet z poprawnym stanem. JS `syncCheckbox()` (fetch `/cart.js` → ustaw `.checked`) tylko jako backup.
2. **Usuwanie wszystkich linii pakowania jednym callem:** `/cart/update.js` z `{ updates: { [variantId]: 0 } }` (zeruje wszystkie linie tego wariantu naraz, prościej niż line-by-line, gdzie indeksy się przesuwają).
3. **Identyfikacja przez property `_gift_wrap`**, nie tylko variant_id (settingi w main-cart i drawer mogą się rozjechać, patrz free-gift bar gotcha #5 w `pasek-postepu-i-gratis.md`).
4. **Mutex `inFlight` + `cb.disabled = true` na czas operacji** (blokuje double-toggle; po refreshu element i tak jest nowy z serwera).
5. **`| t` z `| default:` NIE działa dla brakującego klucza locale**: `'klucz' | t` zwraca string „translation missing: …" (truthy!), więc `| default: 'X'` się NIE odpala. Albo dodaj klucz do WSZYSTKICH `locales/*.json`, albo **hardkoduj** user-facing string (sklep PL). Tu: „Zapakuj na prezent" na sztywno w snippecie.

#### Wyrównanie checkboxa w ramce do innego flush-left checkboxa (full-bleed)

Element z ramką (`padding-inline: 1.4rem`) wcina checkbox względem sąsiada bez ramki (regulamin, x=0). Fix: **`margin-inline: -1.4rem` = `padding-inline: 1.4rem`** → content (checkbox) ląduje na x=0 (wyrównany), border „wystaje" w gutter. Toggle ramki = modifier class `--bordered` + cała geometria w warunkowym `{% if settings.x %}` w `{% style %}`. Odstęp tekstu jak w natywnym: NIE dawaj własnego `gap`, label dziedziczy `padding-inline-start: 0.8rem` z `.checkbox input + label`.

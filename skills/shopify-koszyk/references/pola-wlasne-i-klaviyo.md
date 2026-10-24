# Pola własne w koszyku + integracja Klaviyo + checkbox zgody (2026-06, sklep z suplementami dla psów, Sleek/FoxEcom)

### Własne pola w koszyku (imię/data ur. psa) = ATRYBUTY koszyka, nie notatka: audyt złej vs dobrej wersji
Reużywalne dla KAŻDEGO „własnego pola w koszyku" (imię, data, grawer, dedykacja).

**Anti-pattern (stara wersja):** pola z `name="attributes[...]"` WEWNĄTRZ `<cart-note>` + funkcja dopisująca wartości do **notatki** na **klik `button[name="checkout"]`**. Cztery błędy:
1. **`<cart-note>.onChange` łapie bąbelkujący `change`** z dowolnego pola w środku → `POST {note: event.target.value}` → wpisanie imienia **nadpisuje całą notatkę**.
2. `name="attributes[...]"` **bez `form="cart"`** (i poza `<form id="cart">`) = nigdy nie trafia do submitu → atrybuty martwe.
3. Zapis na klik checkout → **express checkout (Shop Pay/Apple Pay) omija przycisk** → dane przepadają; plus **race** z nawigacją.
4. Dane w notatce jako brudny string, wymagały konwersji przez Shopify Flow.

**Dobry wzorzec (wdrożony):** custom element `<cart-dog-fields>` (snippet `cart-dog-fields.liquid`):
- Pola **POZA `<cart-note>`**, **bez atrybutu `name`** (tylko `data-*`) → zero kolizji z notatką/formularzem.
- Zapis na `input`/`change` (**debounce 500 ms**) przez `POST /cart/update.js {attributes:{...}}` (`cache:'no-store'`) → atrybuty zamówienia (czytelne pary klucz-wartość w „Dodatkowych szczegółach"). Działa dla KAŻDEJ ścieżki kasy, bez race.
- **Pre-fill z `cart.attributes['Klucz']`** server-side → wartości przeżywają re-render drawera (FoxEcom podmienia innerHTML).
- Guard `customElements.get(...)` przy define. **NIE publikować `cartUpdate`** po zapisie (uniknięcie re-renderu i utraty focusu w trakcie pisania).
- Pełna data = natywne **`input type="date"`** (`value` ZAWSZE ISO `yyyy-mm-dd` niezależnie od locale, idealne dla date property w Klaviyo) + `max="{{ 'now' | date: '%Y-%m-%d' }}"`.

**Docs Shopify (zweryfikowane w Shopify Dev MCP, `search_docs_chunks`):** cart attribute = `<input name="attributes[Klucz]" form="cart" value="{{ cart.attributes['Klucz'] }}">` **lub** `POST /cart/update.js {attributes}`. Note = `<textarea name="note" form="cart">`. Line item property = `properties[Klucz]`. To atrybuty **zamówienia/koszyka**, NIE profilu klienta: storefront nie zapisze danych na profil (do tego Admin API / Flow po zamówieniu).

### Push danych z motywu do Klaviyo (onsite): wariant A
- Klaviyo ładowane oficjalną appką Shopify (onsite embed, `company_id` w `settings_data.json`). `window.klaviyo` istnieje **dopiero po zgodzie marketingowej** (CMP typu **Consentmo**) → push naturalnie gatowany RODO.
- W `commit()` po zapisie atrybutu: `window.klaviyo.push(['identify', {dog_name, dog_birthday}])` (właściwości profilu) + `window.klaviyo.push(['track', 'Set Dog Info', {...}])` (event). Forma `.push([...])` odporna na stan ładowania; owinąć w `try/catch`, guard `if (!window.klaviyo) return`.
- **`dog_birthday` w ISO `yyyy-mm-dd`** → Klaviyo auto-wykrywa jako **date property** → flow urodzinowy „around the anniversary of". Sam ROK nie wystarczy (potrzeba dzień+miesiąc).

### Onsite JS (A) vs Shopify Flow→Klaviyo API (B): wybór metody
| | A: onsite JS (motyw) | B: Flow → Klaviyo API (serwerowo) |
|---|---|---|
| Kiedy dane | przy wpisaniu (pre-purchase) | po złożeniu zamówienia |
| Abandoned cart | tak | nie (za późno) |
| Łapie niekupujących | tak (po e-mailu) | nie |
| Niezawodność | średnia (przeglądarka/zgoda/cookie) | wysoka (serwer, zna e-mail) |
- **KLUCZOWY FAKT: Shopify Flow NIE ma API do tworzenia workflow** (Admin API ma tylko `flowTriggerReceive` = odpalenie istniejącego triggera). **Nie da się zbudować Flow przez CLI/`store execute`**: to robota w UI aplikacji Flow.
- Serwerowa alternatywa, którą DA się zakodować: **Cloudflare Worker + webhook `orders/create`** (webhook tworzony przez CLI `webhookSubscriptionCreate`) → Worker woła Klaviyo `profile-import`. Niezależne od przeglądarki/zgody, z retry.
- Rekomendacja: **hybryda A+B (onsite + Worker)**: A pokrywa pre-purchase, Worker = serwerowy backstop; obie zapisują tę samą właściwość.

### Checkbox zgody (regulamin + polityka) blokujący kasę: Sleek/FoxEcom (potwierdzenie wzorca FoxTheme z `blokada-checkoutu-zgoda.md`)
Snippet `consent-checkout.liquid` (HTML+CSS+JS, guard `window.__consentCheckoutInited`) przez `{%- render 'consent-checkout', id: section.id -%}` w `cart-drawer.liquid` (przed `<form class="drawer__footer-buttons">`) i `main-cart.liquid` (blok `buttons`, przed `<button name="checkout">`).
- Blokada = **capture phase**: `click` na `button[name="checkout"], a[href*="/checkout"]` + `submit` (`e.submitter.name==='checkout'`). `preventDefault`+`stopImmediatePropagation`+komunikat.
- Wizualnie **`aria-disabled`+CSS** (NIE `disabled`: capture phase jest realną bramką, nieobchodzalną przez DevTools).
- Selektor JS = klasa `.consent-checkbox` (drawer i `/cart` nigdy razem w DOM), `id` unikalne tylko dla `<label for>`. Linki `shop.terms_of_service.url`/`shop.privacy_policy.url` (fallback `/policies/...`). Reset sam przy re-renderze + `applyState()` na `cart:updated`/`cart:refresh`.
- **LIMIT:** dynamiczne przyciski (Shop Pay/Apple Pay/`additional_checkout_buttons`) OMIJAJĄ guard.
- **Argument „po co, skoro jest baner cookies":** baner = zgoda na śledzenie/marketing (ePrivacy/RODO-tracking); checkbox = akceptacja **umowy sprzedaży** (dyrektywa konsumencka). Cookie consent NIE dowodzi akceptacji regulaminu: różne podstawy, potrzebne oba; checkbox powiązany z konkretnym zamówieniem = lepszy dowód w sporze.

### Footer cart-drawer FoxEcom: struktura i inline pole rabatu zamiast modala
- `#CartDrawerBody-{id}` = ciało (`cart-items` + `cart-drawer-products-recommendation` + `foxkit-incart-upsell`). `#CartDrawerFooter-{id}` = `drawer__footer-head` (gift-wrap, addony note/wysyłka/rabat **otwierające modale `cart-addon-modal`**) + `drawer__footer-body` (lista zastosowanych rabatów + `.totals`).
- **Rabat z modala → inline:** zreplikuj `<form is="cart-discount">` (input `name="discount"` + submit) bezpośrednio w footerze; **inny `id`** niż modal (np. `CartCouponInline-{id}`); zakomentuj przycisk otwierający modal. Element `is="cart-discount"` motywu obsłuży walidację/usuwanie.
- **Ukrycie „Z wliczonym podatkiem. Wysyłka…"** = klasa `.tax-note` (w `cart-drawer`, `main-cart` ORAZ `quick-order-list`): owiń blok w `{%- comment -%}` (czyściej niż CSS hide).
- **Przeniesienie bloku** w footerze/body = przenieś linię `{%- render 'cart-dog-fields' ... -%}` (np. na dół `CartDrawerBody`, po rekomendacjach, przed zamknięciem body).

### Rozmiar ikony bloku „Featured icon" (FoxEcom/Sleek main-product, też motyw Wonder)
- Rozmiar ikony (SVG z listy ORAZ wgrany obrazek) steruje **jedna zmienna CSS `--featured-icon-size`** na `.wt-keys__image-container` (kontener + `.wt-keys__image` + `svg` używają tej zmiennej). Wrapper bloku ma `data-block-id="{{ block.id }}"`.
- Suwak osobno desktop/mobile = scoped `<style>` per blok: `[data-block-id="{{ block.id }}"] .wt-keys__image-container { --featured-icon-size: Npx; }` (mobile w bazie, desktop w `@media (min-width:600px)`; motyw używa breakpointu 600 dla tego kontenera). Sentinel `0` = rozmiar z motywu (render `<style>` tylko gdy >0).

### Drobne referencje FoxEcom/Sleek z tej sesji
- Utility gap w `theme.css`: **`.gap-4 { gap: 1.6rem }`** (do liczenia „o X%": -35% z 1.6 = 1.04rem). Override gapu na elemencie z utility = wyższa specyficzność (`.wrapper .content` 0,2,0 bije `.gap-4`), bez `!important`.
- Przycisk inline (np. rabat): etykieta w `<span class="btn__text">`; rozmiar fontu celuj w `.scope .btn, .scope .btn__text` z `!important`; `border-radius` na `.scope .btn` z `!important`.
- Ustawienia rem desktop/mobile: wzór `{ "type":"range","min":0,"max":4,"step":0.1,"unit":"rem","default":0 }` (0 = domyślny), render przez `{% style %}` + `@media (max-width:767.98px)` dla mobile.

### Pomysł na przyszłość: upsell w „pustej" przestrzeni cart-drawer
Klient pytał o produkty upsell po lewej stronie otwartego drawera. **Haczyk:** „puste miejsce po lewej" to backdrop i istnieje TYLKO na desktopie (mobile drawer = pełnoekranowy). Najczystsze = **poszerzony drawer 2-kolumnowy** (lewa: grid upsell, prawa: koszyk; mobile → 1 kolumna/slider). Reużyć istniejące rekomendacje + AJAX add-to-cart FoxTheme. Trudność: średnia (layout + responsywność + re-render). Osobny panel poza `CartDrawerBody` = trudniejszy (sync open/close + brak auto-refreshu przy zmianie koszyka).

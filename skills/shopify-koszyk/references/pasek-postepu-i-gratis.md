# Free-gift cart progress bar (Buy X Get Y hybryda)

**Wdrożone:** sklep z kosmetykami (2026-05, motyw na bazie Sense, sklep PL, plan Basic).

---

#### WZORZEC WZORCOWY: pasek 100% server-side + Section Rendering (ten sam sklep, nowsza wersja szablonu, motyw Sahara/DigiFist)

> Inny dev zrobił ten sam mechanizm **dużo czyściej** niż moja pierwsza wersja „belt + suspenders" (3 kanały, polling, pub/sub, duplikat matematyki w JS, patrz niżej). **To jest wzorzec do naśladowania.** Sedno: **cała matematyka i stany w Liquid (single source of truth), JS tylko dodaje/usuwa gratis i wywołuje re-render sekcji.** Zero przeliczania progresu w JS.

**Pliki:** `snippets/shipping-bar.liquid` (cały pasek + logika), `assets/gift-tier.js` (~107 linii: reconcile + requestRefresh), `assets/component-cart.css` (style tierów), klucze `cart.shipping_bar.*` w `locales/*.json`, global settings (`enable_shipping_notification` + `shipping_notification_threshold`, `enable_gift_tier` + `gift_threshold` + `gift_product`, `show_currency_codes`). Render w `sections/main-cart.liquid` i `snippets/cart-drawer.liquid` przez `{%- render 'shipping-bar' -%}`.

**1. Jeden pasek, dwa progi (shipping + gift) liczone w Liquid:**
- `bar_total = gift_enabled ? gift_threshold : ship_threshold` (gratis to wyższy próg → wypełnia cały pasek).
- `progress_percentage = cart.total_price * 100 / bar_total` (clamp 0 do 100).
- `checkpoint_percentage = ship_threshold * 100 / gift_threshold` → pozycja **checkpointu dostawy** (ikona ciężarówki `theme-truck`) w połowie paska; ikona prezentu (`theme-gift`) na 100%.
- `ship_reached` / `gift_reached` (porównanie z `cart.total_price`) → klasa `.is-reached` przełącza wypełnienie ikon.
- Tekst: 3 stany przez i18n (`progress_html` → `gift_progress_html` po przekroczeniu dostawy → `gift_success` po progu gratisu). Kwota przez `| money` / `| money_with_currency` (gdy `show_currency_codes`).

**2. Walidacja w Liquid (boundary):** gift tier włącza się TYLKO gdy `enable_gift_tier` + `gift_threshold != blank` + `gift_product != blank` + wariant istnieje + **`gift_threshold > ship_threshold`** (gratis musi być wyższym progiem). Inaczej fallback do zwykłego paska dostawy.

**3. Config przez data-atrybuty na web komponencie** `<shipping-bar>`: `data-gift-variant`, `data-gift-threshold`, `data-cart-total`, `data-shipping-threshold`, `data-progress`. Klasa `progress-bar--two-tier` = marker trybu dwustopniowego.

**4. KLUCZOWY TRIK: natywny updater JS POMIJA pasek dwustopniowy.** W `global.js` `updateFreeShipping()` (native, optymistycznie aktualizuje tekst+szerokość paska po stronie klienta) ma na początku pętli:
```js
if (freeShipping.classList.contains('progress-bar--two-tier')) return;
```
Czyli: **pasek jednostopniowy** = szybki update client-side (JS przelicza); **pasek dwustopniowy** = JS go NIE rusza → aktualizuje się **wyłącznie przez Section Rendering** (świeży HTML z Liquid). Dzięki temu skomplikowana matematyka dwóch progów nigdy się nie rozjeżdża, bo jest tylko w jednym miejscu (Liquid).

**5. `gift-tier.js`: minimalistyczny reconcile (bez pollingu, bez pub/sub, jeden mutex):**
```js
let inFlight = false;
function getConfig() {                       // czyta config z DOM (data-atrybuty paska)
  const bar = document.querySelector('shipping-bar.progress-bar--two-tier[data-gift-variant]');
  if (!bar) return null;
  return { variantId: +bar.dataset.giftVariant, threshold: +bar.dataset.giftThreshold };
}
async function reconcile() {                  // idempotentny: dopasuj koszyk do progu
  if (inFlight) return; inFlight = true;
  try {
    const cart = await fetch('/cart.js').then(r => r.json());
    const giftLine = cart.items.find(i => i.variant_id === cfg.variantId);
    if (cart.total_price >= cfg.threshold) {
      if (!giftLine) { /* add.js qty 1 */ requestRefresh(); }
      else if (giftQty > 1) { /* change.js qty 1 (cap) */ requestRefresh(); }
    } else if (giftLine) { /* change.js qty 0 (remove) */ requestRefresh(); }
  } finally { inFlight = false; }
}
document.addEventListener('cart:updated', () => setTimeout(reconcile, 50));  // jedyny trigger
document.addEventListener('DOMContentLoaded', () => setTimeout(reconcile, 400)); // initial
```
`requestRefresh()` re-renderuje `#CartDrawer-Body`, `#CartDrawer-Summary` i main `cart-items` przez `?sections=` i podmienia `innerHTML` → pasek (i cały koszyk) odtwarza się z Liquid z poprawnymi stanami.

**Czym to bije moją pierwszą wersję (belt+suspenders niżej):** brak duplikatu progresu w JS (zasada „rozszerzaj, nie duplikuj"), brak pollingu/pub-sub (jeden event `cart:updated` wystarcza, bo motyw go dispatchuje), gratis identyfikowany po `variant_id` (OK, bo `gift_product` to **global setting**, jeden wariant wszędzie; per-section property `_gift_wrap` potrzebny dopiero, gdy config jest osobny per sekcja).

**Uwaga, kompromisy tej wersji:** `gift-tier.js` usuwa/capuje przez `{ id: giftLine.key }`, nie line-based (patrz gotcha #1 niżej: przy ochronie Buy X Get Y bezpieczniejsze jest `{ line }`); tu działa, ale gdyby gratis nie znikał mimo status 200, to pierwsze miejsce do zmiany. Brak własnej walidacji NaN w JS (`+dataset` → NaN, gdy brak atrybutu, ale `getConfig` guarduje przez `if (!variantId || !threshold)`).

**Styl tierów (component-cart.css):** `.progress-bar--two-tier .progress-bar__progress { overflow: visible }` (żeby ikony tierów wystające poza pasek nie były przycięte; analogia do gotchy „overflow przycina marker" z pigułek kategorii w skillu `shopify-produkt`). `.progress-bar__tier` absolutnie pozycjonowane (`left: checkpoint%` / `left: 100%`, `translate(-50%,-50%)`), `.is-reached` przełącza kolory.

---

**Krytyczna wiedza biznesowa: czytaj PRZED implementacją**

Shopify Automatic Discount **Buy X Get Y** wbrew nazwie **NIE dodaje fizycznie produktu Y do koszyka**. Tylko daje 100% rabat na Y, **jeśli klient sam go włożył**. Czyli:

- Bez theme JS: klient widzi „Gratulacje, masz darmowe lusterko!", ale gratisu w koszyku nie ma → nie kupuje
- Z theme JS: my dodajemy gratis fizycznie, Shopify go rabatuje do 0 zł → klient widzi w koszyku za 0 zł

Bez tej wiedzy będziesz tracić godziny, próbując samym Buy X Get Y. **Wszystkie płatne apki „Free Gift" robią dokładnie to samo**: dodają produkt JSem, polegają na Discount engine, że go zrabatuje. Różnią się tylko engineering quality i tym, że są maintained.

**Architektura „belt + suspenders": 3 niezależne kanały reakcji na cart change:**

```
┌─────────────────────────────────────────────────────────────┐
│  Kanał 1: native events                                      │
│    document.addEventListener('cart:change' / 'cart:refresh'  │
│      / 'cart:updated', handler)                              │
│    ↑ Dispatch z patcha CartItems.updateQuantity              │
├─────────────────────────────────────────────────────────────┤
│  Kanał 2: Dawn pub/sub (feature-detected)                    │
│    window.subscribe(PUB_SUB_EVENTS.cartUpdate, handler)      │
│    ↑ Działa, jeśli theme ma nowsze pubsub.js                 │
├─────────────────────────────────────────────────────────────┤
│  Kanał 3: polling                                            │
│    setInterval(() => fetchAndUpdate(), 2000)                 │
│    ↑ Safety net. Idempotentny przez mutex giftOp             │
└─────────────────────────────────────────────────────────────┘
```

Jeśli kanał 1 lub 2 zawodzi (typowo: event się gubi w przerwie disconnectedCallback/connectedCallback przy Section Render), **kanał 3 pokryje** maks. po 2 sekundach. Cart.js Shopify wytrzymuje polling bez issue.

**Gotchy, które poznaliśmy (każdy kosztował debug session):**

1. **`/cart/change.js` z `{id: key}` może NIE działać** dla items pod ochroną discount engine. ZAWSZE używaj `{line: lineIndex}`, pattern z natywnego CartItems.updateQuantity. To **#1 przyczyna** „server zwraca status=200, ale gratis nadal w koszyku".

2. **`section.settings.gift_product` z `type: "product"` zwraca OBIEKT produktu**, nie handle. NIE używaj `all_products[section.settings.gift_product]`: to redundant lookup, który działa „przez przypadek".

3. **`variants.first.id`** bierze pierwszy wariant **niezależnie od dostępności** (może być sold-out). Bezpieczniej: `selected_or_first_available_variant.id`. Lub w schema: `type: "product_variant"`.

4. **MutationObserver gubi eventy** między `disconnectedCallback` i `connectedCallback`, gdy Section Rendering API podmienia innerHTML zewnętrznej sekcji. NIE polegaj tylko na nim.

5. **Identyfikuj gratis przez `properties: { _gift: 'true' }`**, nie po `variant_id`. Dlaczego: settings `gift_product` w sekcjach `main-cart` i `cart-drawer` są **osobne**, mogą się rozjechać, klient może zmienić jedno bez drugiego. Property na linii koszyka jest niezawodne:
   ```js
   cart.items.filter(i => 
     (i.properties && i.properties._gift === 'true') ||
     i.variant_id === this.variantId  // fallback dla legacy sesji
   )
   ```

6. **`theme.liquid` ma globalny `section 'cart-drawer'`** w większości Dawn-based themes. Czyli na `/cart` istnieją DWIE instance `<cart-gift-bar>` (main-cart + drawer). Wybór:
   - **Mutex globalny** (`document.body.dataset.giftOp`): obie instance robią write, mutex chroni przed double-fire. JS single-threaded → atomic check+set przed pierwszym `await`. Plus fault-tolerance, gdy drawer settings nieskonfigurowane.
   - `data-display-only="true"` na jednej: czystsze, ale traci fault-tolerance.

7. **Patch `CartItems.prototype.updateQuantity` musi dispatchować `cart:change` PO `updateLiveRegions`**, nie przed. Wcześniejszy patch (setTimeout wrapper) tworzył race z error detection → fałszywy „Można dodać tylko N". Pełny rewrite metody z dispatch na końcu chain'a `.then`.

8. **Po manualnej DOM mutation (twoje `refreshCartSections`) re-kalibruj `CartItems.currentItemCount`**: patrz `cart-api-podstawy.md`.

9. **Drawer i main-cart MAJĄ OSOBNE schema settings** w Theme Editor (`gift_threshold`, `gift_product`). Klient musi zsynchronizować ręcznie. Albo wynieś do `config/settings_schema.json` jako global (większa zmiana).

10. **Shopify Discount Buy X Get Y musi być skonfigurowany jako Automatic, nie code-based.** „Customer buys: Minimum purchase amount" = próg PLN. „Customer gets: 1× [produkt] → Percentage 100%". Inaczej Shopify nie zrabatuje gratisu.

**Wzorzec `CartGiftBar` web component (kluczowe fragmenty):**

```js
if (!customElements.get('cart-gift-bar')) {
  class CartGiftBar extends HTMLElement {
    connectedCallback() {
      this.threshold  = parseInt(this.dataset.threshold, 10);
      this.variantId  = parseInt(this.dataset.variant, 10);
      this.messageEl  = this.querySelector('.cart-gift-bar__message');
      this.fillEl     = this.querySelector('[data-progress-line]');
      this.progressEl = this.querySelector('.progress-bar__progress');

      // Kanał 1: native events
      this._onCartEvent = this.onCartEvent.bind(this);
      document.addEventListener('cart:change',  this._onCartEvent);
      document.addEventListener('cart:refresh', this._onCartEvent);
      document.addEventListener('cart:updated', this._onCartEvent);

      // Kanał 2: Dawn pub/sub (feature-detected)
      if (typeof window.subscribe === 'function' &&
          window.PUB_SUB_EVENTS?.cartUpdate) {
        this._unsubscribe = window.subscribe(window.PUB_SUB_EVENTS.cartUpdate, (data) => {
          if (document.body.dataset.giftOp) return;
          if (data?.cartData) this.update(data.cartData);
          else this.fetchAndUpdate();
        });
      }

      // Kanał 3: polling
      this._pollInterval = setInterval(() => {
        if (!document.body.dataset.giftOp) this.fetchAndUpdate();
      }, 2000);
    }

    disconnectedCallback() {
      // ZAWSZE cleanup wszystkich trzech kanałów
      document.removeEventListener('cart:change',  this._onCartEvent);
      document.removeEventListener('cart:refresh', this._onCartEvent);
      document.removeEventListener('cart:updated', this._onCartEvent);
      this._unsubscribe?.();
      if (this._pollInterval) clearInterval(this._pollInterval);
    }

    findGiftItems(cart) {
      return cart.items.filter(i =>
        (i.properties && i.properties._gift === 'true') ||
        i.variant_id === this.variantId
      );
    }

    async removeGift(key) {
      if (document.body.dataset.giftOp) return;
      document.body.dataset.giftOp = '1';
      try {
        // KLUCZOWE: line index, nie {id: key}
        const preCart = await fetch('/cart.js').then(r => r.json());
        const lineIndex = preCart.items.findIndex(i => i.key === key) + 1;
        await fetch('/cart/change.js', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
          body: JSON.stringify(lineIndex > 0
            ? { line: lineIndex, quantity: 0 }
            : { id: key, quantity: 0 })
        });
        // Weryfikacja + fallback
        const postCart = await fetch('/cart.js').then(r => r.json());
        if (this.findGiftItems(postCart).length > 0) {
          // Fallback: /cart/update.js
          await fetch('/cart/update.js', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ updates: { [this.variantId]: 0 } })
          });
        }
        await this.refreshCartSections();
      } finally {
        delete document.body.dataset.giftOp;
      }
    }
  }
  customElements.define('cart-gift-bar', CartGiftBar);
}
```

**Checkout race fix (cap qty=1 przed submit):**

```js
document.addEventListener('click', async function (e) {
  const btn = e.target.closest('button[name="checkout"], [data-checkout]');
  if (!btn || btn.disabled) return;
  const bar = document.querySelector('cart-gift-bar[data-variant]');
  if (!bar || btn.dataset.giftChecked === '1') return;

  e.preventDefault();
  btn.disabled = true;
  btn.dataset.giftChecked = '1';   // flag chroni przed pętlą po btn.click()

  try {
    const cart = await fetch('/cart.js').then(r => r.json());
    const gifts = cart.items.filter(i => i.properties?._gift === 'true');
    const qty = gifts.reduce((s, i) => s + i.quantity, 0);
    if (qty > 1 && gifts[0]) {
      await fetch('/cart/change.js', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: gifts[0].key, quantity: 1 })
      });
    }
  } finally {
    btn.disabled = false;
    btn.click();   // re-fire, flag chroni przed re-cap
  }
}, true);   // capture phase!
```

**ARIA wymagana:**

```liquid
<div
  class="progress-bar__progress"
  role="progressbar"
  aria-valuemin="0"
  aria-valuemax="100"
  aria-valuenow="{{ gift_progress }}"
  aria-label="Postęp do darmowego gratisu"
>
  <span class="progress-bar__progress-inner" data-progress-line
        style="width: calc({{ gift_progress }}% + 2px);"></span>
</div>
<p class="cart-gift-bar__message" aria-live="polite">…</p>
```

W JS update'uj `progressEl.setAttribute('aria-valuenow', progress)` przy każdym update.

**Debug logging convention** (zostaw na produkcji, szybko diagnozuje issues):

```js
console.log('[gift-bar] addGift variant=' + this.variantId);
console.log('[gift-bar] removeGift key=' + key);
console.log('[gift-bar] removeGift via line=' + lineIndex);
console.log('[gift-bar] removeGift status=' + res.status);
console.log('[gift-bar] triggerRemove total=' + total + ' threshold=' + this.threshold);
console.log('[gift-bar] refreshCartSections done, currentItemCount synced');
```

Gdy klient zgłasza bug, prosisz: „otwórz DevTools Console, powtórz akcję, wklej wszystko `[gift-bar]`". Diagnoza w 5 minut zamiast godziny.

**Konfiguracja Shopify Admin (czek-lista):**

1. Discounts → Create discount → **Automatic** (NIE Discount code)
2. Buy X Get Y
3. Customer buys: **Minimum purchase amount** = próg (np. 500.00 PLN)
4. Customer gets: **1×** [produkt-gratis] → **Percentage** → **100%**
5. At a discounted value = Free / 100% off
6. Active dates: od dziś (uwaga strefa czasowa!)
7. Combinations (jeśli widoczne): włącz „Combine with other product/order/shipping discounts", jeśli masz inne aktywne

**Kiedy NIE robić tego ręcznie:**

- **Klient ma Shop Pay Express na product page** → klik kupuje wprost, omija `/cart` → gratis się nie dodaje. Bez fixa.
- **Klient ma plan Shopify Plus** → użyj Cart Transform Function (server-side, brak race conditions, działa wszędzie).
- **Klient chce „set and forget"** → płatna apka *Free Gifts BOGO by Secomapp* / *Monster Cart Upsell* / *BOGOS.io* (~$10-30/mc). Robi to samo plus marketing features.
- **Klient chce kilka różnych progów / kombinacji** (np. 300 zł = lusterko, 500 zł = lusterko+chusta) → płatna apka, własny kod się rozsypie.

**Pliki implementacji w drzewie themu:**

- `sections/main-cart.liquid`: sekcja koszyka. Liquid block `<cart-gift-bar>` z ARIA + schema settings (enable_gift_bar checkbox, gift_threshold number, gift_product picker)
- `sections/cart-drawer.liquid`: wrapper `{%- render 'cart-drawer' -%}` + identyczne schema settings
- `snippets/cart-drawer.liquid`: pełny drawer + Liquid block `<cart-gift-bar>` + inline `<style>` z `.cart-gift-bar` + inline `<script>` z całą logiką (CartGiftBar class + checkout guard + CartItems patch)
- `assets/cart.js`, `assets/cart-drawer.js`: bez zmian (theme native)

**Referencje:**
- [Josh: I Built 3 Shopify Cart Features Without a Single App](https://dev.to/joshmsn/i-built-3-shopify-cart-features-without-a-single-app-just-liquid-js-27k9): race conditions pattern
- [Dawn Theme: Subscribe to cart:update event](https://community.shopify.com/t/dawn-theme-subscribe-to-cart-update-event/388207): pub/sub usage
- [Coding with Jan: Shopify Pub/Sub Events Complete Guide](https://codingwithjan.com/blog/shopify-tutorials/shopify-pub-sub-events/): PUB_SUB_EVENTS reference
- [shopify.dev: cart Liquid object](https://shopify.dev/docs/api/liquid/objects/cart): autorytatywna definicja pól `total_price`, `items_subtotal_price` itd.

# Cart API: twarda wiedza dla każdego projektu

Zebrane z konkretnych debug sessions. Te rzeczy zawsze obowiązują, niezależnie od projektu.

### Pola cart object (zweryfikowane w shopify.dev)

| Pole | Co znaczy | Kiedy używać |
|------|-----------|--------------|
| `cart.total_price` | **Po wszystkich rabatach**, w subunit (cents/grosze), w presentment currency | „Ile klient faktycznie zapłaci za rzeczy": domyślnie dla progress baru free-shipping/gift |
| `cart.items_subtotal_price` | Po line-item discounts, **przed** cart-level discounts i shipping | „Ile kosztują rzeczy przed cart-level rabatami" |
| `cart.original_total_price` | **Przed** rabatami | „Ile by było bez rabatów" |
| `cart.total_discount` | Łączna kwota rabatów | Wyświetlanie „zaoszczędziłeś X zł" |

**Pułapka multi-currency:** `cart.total_price` jest w walucie kupującego (presentment). Jeśli próg w settings jest liczbą bez waluty (np. `gift_threshold: 500`), w Markets/EUR storefront porównujesz 500 EUR z presentment EUR: wartość liczbowa nie skaluje się. Sklep PL-only = OK, ale future-proof komentarzem.

### Endpointy Cart API i ich pułapki

| Endpoint | Body | Działa dla | Gotcha |
|----------|------|-----------|--------|
| `POST /cart/add.js` | `{items: [{id, quantity, properties}]}` | Dodawanie produktów | Zwraca dodane items, nie cały cart. Po add zawsze `fetch /cart.js`, żeby mieć aktualny stan |
| `POST /cart/change.js` | **Preferuj `{line: N, quantity}`** zamiast `{id: key, quantity}` | Zmiana / usunięcie | `{id: key}` **może być ignorowane** dla items pod ochroną discount engine (Buy X Get Y). Pattern z natywnego CartItems.updateQuantity to ZAWSZE line-based |
| `POST /cart/update.js` | `{updates: {variant_id: qty, ...}}` | Bulk update | Fallback, gdy `/cart/change.js` zawodzi (rzadko, ale się zdarza) |
| `GET /cart.js` | brak | Pobranie stanu | Generous rate limit: polling co 1-2s jest OK |
| `GET /?sections=section-id` | brak | Section Rendering API | Zwraca HTML pełnej sekcji w `{[section-id]: "<html>"}` |

**Convertowanie key → line index** (gdy masz tylko key z item):
```js
const cart = await fetch('/cart.js').then(r => r.json());
const lineIndex = cart.items.findIndex(i => i.key === key) + 1;  // 1-based
```

### Section Rendering API: co wiedzieć

- Selector w `getSectionsToRender()` to `#shopify-section-{id} cart-items` (np.): selektuje **wewnętrzny element** wewnątrz sekcji
- `getSectionInnerHTML(html, selector)` parsuje HTML i bierze `innerHTML` z querySelector(selector)
- `elementToReplace.innerHTML = ...` podmienia **dzieci** zewnętrznego elementu, ale sam element pozostaje (custom element instance jest preservowane)
- **Web components WEWNĄTRZ podmienianej sekcji** → `disconnectedCallback` na starych, `connectedCallback` na nowych (świeże instances)
- **Web components POZA podmienianą sekcją** (np. drawer instance, gdy aktualizujesz main-cart) → pozostają z OLD state: musisz je obudzić eventem lub poll'em

### Cache busting: KONIECZNY przy każdym manualnym fetch cart/sections

**Bug, który kosztował debug session w sklepie z kosmetykami (2026-05):** przeglądarki agresywnie cache'ują GET requesty, w tym `/cart.js` i `?sections=section-id`. Mimo że Shopify wysyła `Cache-Control: no-cache`, w praktyce Chrome/Safari potrafią serwować stale response, co skutkuje:

- Gift-bar widzi STARY cart i podejmuje decyzję na nieaktualnych danych (np. `addGift`, mimo że gratis już jest)
- Po manualnym section refresh podmieniasz `innerHTML` na STARY HTML (sprzed cart change) → gratis, który właśnie usunęliśmy server-side, nadal widoczny w UI

**Bezpieczny wzorzec**: używaj W KAŻDYM fetch state-changing'u:
```js
// Dla /cart.js: sam cache:'no-store' wystarcza
fetch('/cart.js', { cache: 'no-store' }).then(r => r.json())

// Dla ?sections=... w niektórych przeglądarkach (zwłaszcza Safari) cache:'no-store'
// NIE WYSTARCZA. Trzeba dodać unikalny query param, żeby URL był każdorazowo unikalny.
const cacheBust = '&_t=' + Date.now() + Math.random().toString(36).slice(2);
fetch(`${root}?sections=${id}${cacheBust}`, { cache: 'no-store' })
```

Reguła: każdy fetch, który czyta lub zmienia stan koszyka, MUSI być cache-busted.

### DOM/Server state mismatch: pattern bezpiecznego cleanup

Po manualnym section refresh (np. po `removeGift` → `refreshCartSections`) **DOM może być desync z server cart**. Naiwna logika typu „jeśli widzę gift line w DOM, usuń" jest **destrukcyjna**: usuwa też gratis, który właśnie został dodany (i którego DOM POWINIEN pokazywać).

**Bezpieczny wzorzec**: porównaj DOM ze server source of truth:

```js
// 1. Fetch server state (cache busted)
const serverCart = await fetch('/cart.js', { cache: 'no-store' }).then(r => r.json());
const serverHasGift = findGiftItems(serverCart).length > 0;

// 2. Sprawdź DOM
const allInputs = document.querySelectorAll('[name="updates[]"]');
const domHasGift = Array.from(allInputs).some(input => {
  const lineItem = input.closest('[id^="CartItem-"], [id^="CartDrawer-Item"]');
  return lineItem && lineItem.outerHTML.includes(String(this.variantId));
});

// 3. Cztery przypadki:
if (!serverHasGift && domHasGift) {
  // Server bez, DOM ma → stale cache. Wyczyść z DOM.
} else if (serverHasGift && !domHasGift) {
  // Server ma, DOM nie pokazuje → section render zwrócił stary HTML.
  // Log diagnostyczny: nie próbuj ręcznie dodać (zbyt theme-specific).
}
// Pozostałe dwa przypadki (oba true / oba false): NIC NIE RÓB.
```

**Anti-pattern:** `if (domHasGift) removeFromDom()` bez sprawdzenia server state: usuwa gratis, który DOPIERO został dodany. Symptom: user dodaje produkt powyżej progu, gratis pojawia się na milisekundę i znika.

### Pub/sub Dawn: kiedy używać

W `theme.liquid` szukaj `<script src="{{ 'pubsub.js' | asset_url }}"`. Jeśli jest:

```js
// Feature detect: starsze versions Dawn nie eksponują pub/sub globalnie
if (typeof window.subscribe === 'function' &&
    typeof window.PUB_SUB_EVENTS === 'object') {
  const unsubscribe = window.subscribe(window.PUB_SUB_EVENTS.cartUpdate, (data) => {
    // data.cartData = pełny cart object
    // data.source = który komponent wywołał update
  });
}
```

Eventy: `cartUpdate`, `quantityUpdate`, `cartError`, `variantChange`, `optionValueSelectionChange`.

**Pułapka:** starsze cart.js (jak w Sense i motywach na nim opartych) NIE publishują `cartUpdate` z `CartItems.updateQuantity`. W tym przypadku patch CartItems.prototype.updateQuantity, żeby sam publishował (lub używaj custom event jak `cart:change`).

### CartItems.updateLiveRegions: fałszywy „Można dodać tylko N element(ów)"

W cart.js: `if (this.currentItemCount === itemCount)` → wyświetla błąd z `[quantity]` placeholder. Założenie: jeśli liczba items po update jest TAKA SAMA jak przed (suma input values w konstruktorze), server odrzucił request.

**Bug:** `this.currentItemCount` jest liczony tylko **raz w konstruktorze**. Po każdej DOM mutation spoza CartItems flow (np. nasze `removeGift` przez raw fetch + section refresh) inputy zmieniają się, ale `currentItemCount` nie. Przy następnym user update wartości mogą się przypadkowo zbiec → fałszywy error.

**Fix po każdym manualnym section refresh:**
```js
document.querySelectorAll('cart-items, cart-drawer-items').forEach(el => {
  el.currentItemCount = Array.from(el.querySelectorAll('[name="updates[]"]'))
    .reduce((acc, input) => acc + (parseInt(input.value, 10) || 0), 0);
});
```

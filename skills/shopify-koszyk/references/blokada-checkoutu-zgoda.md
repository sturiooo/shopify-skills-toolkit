# Blokada checkoutu + reset zgody (Checkout Consent Checkbox)

**Status:** wzorzec ogólny, przygotowany pierwotnie dla sklepu z pluszakami (motyw dynamiczny z AJAX cart); adaptacje opisane niżej są wdrożone.

**Kontekst legislacyjny: DLACZEGO to jest wymagane**

Wymóg wynika z:
- **Dyrektywy UE 2011/83/UE** o prawach konsumentów: przed finalizacją zamówienia klient musi wyraźnie zaakceptować warunki
- **Polskiej ustawy o prawach konsumenta**: przycisk "Zamów i zapłać" musi być poprzedzony akceptacją T&C przez klienta
- **RODO/GDPR**: checkbox nie może być pre-zaznaczony; wymagane aktywne działanie użytkownika
- **Praktyczne**: reset zgody po każdej zmianie koszyka = każda nowa sesja zamówienia wymaga nowej zgody

**Wymagania funkcjonalne:**
1. Checkout **domyślnie zablokowany**
2. Odblokowuje się tylko po zaznaczeniu checkboxa
3. Każda zmiana koszyka (add/change/update przez AJAX) → odznacza checkbox + blokuje checkout ponownie
4. Odporna na re-render sekcji i podmianę DOM (dynamiczne motywy)
5. Odporna na ręczne usunięcie `disabled` w DevTools
6. Komunikat błędu pod checkboxem, nie `alert()`
7. Nie psuje natywnej logiki motywu

**Pliki do pobrania od klienta: ZAWSZE pytaj o te pliki PRZED implementacją**

| Plik | Lokalizacja w Theme Editor | Po co |
|------|--------------------------|-------|
| `cart-drawer.liquid` | `snippets/cart-drawer.liquid` | Przycisk checkout drawera + form `CartDrawer-Form` |
| `main-cart-footer.liquid` | `sections/main-cart-footer.liquid` | Przycisk checkout strony koszyka (Dawn-based) |
| `cart.liquid` / `cart.json` | `templates/` | Template strony koszyka |
| `theme.liquid` | `layout/theme.liquid` | Skrypty globalne, żeby wiedzieć gdzie wstrzyknąć JS |
| `cart.js` / `cart-drawer.js` | `assets/` | Czy motyw używa `fetch` czy `XMLHttpRequest` |

W motywach nie-Dawn (Nook, Sense, itp.) przycisk `name="checkout"` może być w różnych miejscach: poszukaj go przez grep lub zapytaj klienta. Nie zakładaj struktury.

**Metoda implementacyjna: KLUCZOWA, nie upraszczaj**

#### 1. Capture phase zamiast `disabled` jako primary guard

```js
document.addEventListener('click', function(e) {
  const btn = e.target.closest('button[name="checkout"], a[href*="/checkout"]');
  if (!btn) return;
  const checkbox = document.querySelector('#consent-checkbox'); // dynamiczny querySelector ZAWSZE
  if (!checkbox || !checkbox.checked) {
    e.preventDefault();
    e.stopImmediatePropagation();
    showConsentError();
  }
}, true); // true = capture phase, PRZED logiką motywu
```

**Dlaczego capture phase, nie `disabled`:**
- `disabled` można usunąć ręcznie w DevTools w 2 sekundy
- Button re-renderuje się po AJAX update → listener przypisany do elementu przestaje istnieć
- Capture phase działa niezależnie od stanu DOM, zawsze przed Shopify logiką

#### 2. Nadpisanie `window.fetch`: reset po każdej operacji koszyka

```js
(function() {
  const _origFetch = window.fetch;
  window.fetch = function(url) {
    const result = _origFetch.apply(this, arguments);
    const urlStr = typeof url === 'string' ? url : (url?.url || '');
    if (/\/cart\/(add|change|update)/.test(urlStr)) {
      result.then(function() {
        setTimeout(resetConsent, 300); // czekaj na re-render sekcji
      });
    }
    return result;
  };
})();
```

#### 3. Fallback na XMLHttpRequest (sprawdź w `assets/cart.js` czy motyw go używa)

```js
(function() {
  const _origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url) {
    if (/\/cart\/(add|change|update)/.test(url)) {
      this.addEventListener('load', function() {
        setTimeout(resetConsent, 300);
      });
    }
    return _origOpen.apply(this, arguments);
  };
})();
```

#### 4. Funkcja resetConsent

```js
function resetConsent() {
  const cb = document.querySelector('#consent-checkbox');
  if (cb) cb.checked = false;
  // NIE rób tutaj btn.disabled = true, button się re-renderował
  // Blokada jest w capture phase, działa automatycznie po odznaczeniu
  updateCheckoutVisualState();
  hideConsentError();
}
```

#### 5. Wizualna blokada (opcjonalna, ale dobry UX)

```js
function updateCheckoutVisualState() {
  const cb = document.querySelector('#consent-checkbox');
  const isChecked = cb && cb.checked;
  document.querySelectorAll('button[name="checkout"]').forEach(function(btn) {
    btn.style.opacity = isChecked ? '1' : '0.5';
    btn.style.cursor  = isChecked ? 'pointer' : 'not-allowed';
    // NIE używaj disabled, capture phase jest primary guard
  });
}
```

#### 6. MutationObserver: resync po re-renderze sekcji

```js
new MutationObserver(function() {
  updateCheckoutVisualState();
}).observe(document.body, { childList: true, subtree: true });
```

#### 7. HTML: checkbox + error div (wstaw w cart-drawer i/lub main-cart-footer)

```liquid
<div class="consent-wrap">
  <label>
    <input
      type="checkbox"
      id="consent-checkbox"
      aria-required="true"
    >
    {{ 'cart.consent.label' | t | default: 'Przeczytałem/am i akceptuję regulamin sklepu.' }}
  </label>
  <div
    id="consent-error"
    class="consent-error"
    aria-live="polite"
    style="display: none; color: red; font-size: 13px; margin-top: 4px;"
  >
    {{ 'cart.consent.error' | t | default: 'Musisz zaakceptować regulamin, aby przejść do kasy.' }}
  </div>
</div>
```

#### 8. Pełna struktura IIFE (obowiązkowe, nie zatruwaj scope globalnego)

```js
<script>
(function() {
  'use strict';

  var CHECKBOX_SEL = '#consent-checkbox';
  var ERROR_SEL    = '#consent-error';

  // 1. Capture phase: primary guard
  document.addEventListener('click', function(e) {
    var btn = e.target.closest && e.target.closest('button[name="checkout"], a[href*="/checkout"]');
    if (!btn) return;
    var cb = document.querySelector(CHECKBOX_SEL);
    if (!cb || !cb.checked) {
      e.preventDefault();
      e.stopImmediatePropagation();
      showConsentError();
      updateCheckoutVisualState();
    }
  }, true);

  // 2. Checkbox change: update visual state
  document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'consent-checkbox') {
      updateCheckoutVisualState();
      if (e.target.checked) hideConsentError();
    }
  });

  // 3. fetch override
  var _origFetch = window.fetch;
  window.fetch = function(url) {
    var result = _origFetch.apply(this, arguments);
    var urlStr = typeof url === 'string' ? url : (url && url.url ? url.url : '');
    if (/\/cart\/(add|change|update)/.test(urlStr)) {
      result.then(function() { setTimeout(resetConsent, 300); });
    }
    return result;
  };

  // 4. XHR fallback
  var _origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url) {
    if (/\/cart\/(add|change|update)/.test(url)) {
      this.addEventListener('load', function() { setTimeout(resetConsent, 300); });
    }
    return _origOpen.apply(this, arguments);
  };

  // 5. MutationObserver: resync po re-render
  new MutationObserver(function() {
    updateCheckoutVisualState();
  }).observe(document.body, { childList: true, subtree: true });

  // --- helpers ---
  function resetConsent() {
    var cb = document.querySelector(CHECKBOX_SEL);
    if (cb) cb.checked = false;
    updateCheckoutVisualState();
    hideConsentError();
  }

  function updateCheckoutVisualState() {
    var cb = document.querySelector(CHECKBOX_SEL);
    var ok = cb && cb.checked;
    document.querySelectorAll('button[name="checkout"]').forEach(function(btn) {
      btn.style.opacity = ok ? '1' : '0.5';
      btn.style.cursor  = ok ? 'pointer' : 'not-allowed';
    });
  }

  function showConsentError() {
    var el = document.querySelector(ERROR_SEL);
    if (el) el.style.display = 'block';
  }

  function hideConsentError() {
    var el = document.querySelector(ERROR_SEL);
    if (el) el.style.display = 'none';
  }

  // Init visual state on load
  document.addEventListener('DOMContentLoaded', updateCheckoutVisualState);
})();
</script>
```

**Gdzie umieścić kod:**
- Checkbox HTML + error div: w `snippets/cart-drawer.liquid` (drawer) **ORAZ** `sections/main-cart-footer.liquid` (cart page), oba miejsca, jeśli klient ma drawer + stronę koszyka
- JS: jeśli drawer jest renderowany globalnie przez `theme.liquid` → inline `<script>` w snippecie ładuje się raz automatycznie. Alternatywnie: plik `assets/consent-checkout.js` + `{{ 'consent-checkout.js' | asset_url | script_tag }}` w `theme.liquid`

**Gotche:**

- **`setTimeout(300ms)`** może być za krótki na wolnych połączeniach/urządzeniach. Jeśli reset nie działa: zwiększ do 500ms
- **Selektory checkout button różnią się między motywami**: sprawdź faktyczny HTML: `button[name="checkout"]`, `#CartDrawer-Checkout`, `a[href="/checkout"]`. Zawsze daj kilka selektorów w `closest()`
- **Dynamic Checkout Buttons** (Buy Now / Apple Pay / Shop Pay bezpośrednio na stronie produktu) **omijają koszyk całkowicie** → ta blokada ich nie obejmuje. Jeśli klient ma `{{ form | payment_button }}`, rozważ `display: none` na `.shopify-payment-button` lub wymagaj przejścia przez koszyk
- **ARIA**: checkbox musi mieć `<label for="consent-checkbox">` + `aria-required="true"`. Error div z `aria-live="polite"`: screen reader ogłosi zmianę bez skupienia
- **Dwie instancje** (drawer + cart page): oba mają `id="consent-checkbox"`, JS działa poprawnie, bo i tak robi `querySelector`, który znajdzie ten, który jest w DOM (tylko jeden jest widoczny w danej chwili)
- **Locales**: jeśli motyw ma tłumaczenia, dodaj klucze `cart.consent.label` i `cart.consent.error` do wszystkich `locales/*.json`

---

#### Adaptacja do konkretnego motywu: sklep z pluszakami, motyw na bazie Nook (2026-05)

**Zweryfikowane przy implementacji. Czytaj, zanim zaczniesz w podobnym motywie.**

##### Jak rozpoznać ten typ motywu

- `cart.js` ma `CartItems` class z `theme.pubsub.subscribe(PUB_SUB_EVENTS.cartUpdate, ...)`
- Po każdej zmianie koszyka: `miniCart.innerHTML = updatedElement.innerHTML`, cały drawer zastępowany
- Motyw dispatchuje `cart:updated` event PO zamianie DOM (na końcu `onCartUpdate`)
- Odświeżanie drawera przez `cart:refresh` event → async fetch + innerHTML replace

##### Kluczowa różnica: NIE używaj window.fetch override

W tym typie motywu fetch override jest **zbędny i ryzykowny**. Motyw sam dispatchuje `cart:updated` po każdym update koszyka: to jest niezawodny sygnał. Zamiast:

```js
// ŹLE dla tego motywu: nadpisuje fetch globalnie, może złamać inne requesty
window.fetch = function(...) { ... }
```

Użyj:
```js
// DOBRZE: natywny event motywu, odpala PO zamianie DOM
document.addEventListener('cart:updated', function() {
  updateVisual(false); // nowy checkbox jest już w DOM i jest odznaczony
  hideError();
});

// cart:refresh = otwieranie drawera przez kliknięcie ikony koszyka
// Jest async, potrzebuje małego setTimeout, żeby poczekać na innerHTML replace
document.addEventListener('cart:refresh', function() {
  setTimeout(function() { updateVisual(false); hideError(); }, 100);
});
```

##### Dlaczego checkbox resetuje się automatycznie

`miniCart.innerHTML = updatedElement.innerHTML` zastępuje **cały** kontent drawera nowym HTML z serwera. Nowy HTML ma checkbox odznaczony (tak jest w pliku Liquid). Nie trzeba go ręcznie odznaczać, wystarczy zaktualizować wygląd przycisku po zamianie.

##### Gdzie wstawić checkbox w tym motywie

W `snippets/cart-drawer.liquid`, PRZED blokiem `{%- if section.settings.show_checkout_button or section.settings.show_view_cart_button -%}`, wewnątrz `<div class="drawer__footer-bottom">`:

```liquid
{%- if section.settings.show_checkout_button -%}
  <div class="consent-wrap">
    <label class="consent-label flex items-start gap-2 text-sm leading-tight cursor-pointer">
      <input
        type="checkbox"
        id="consent-checkbox-drawer"
        class="consent-checkbox shrink-0"
        style="margin-top: 2px;"
        aria-required="true"
      >
      <span>Zapoznałem/am się z <a href="/policies/terms-of-service" class="link" target="_blank" rel="noopener">regulaminem sklepu</a> i akceptuję warunki zamówienia.</span>
    </label>
    <p id="consent-error-drawer" class="text-xs" aria-live="polite" role="alert" style="display: none; color: #c0392b; margin-top: 4px;">
      Zaakceptuj regulamin, aby przejść do kasy.
    </p>
  </div>
{%- endif -%}
```

Selector dla `updateVisual`: `.drawer__footer-buttons button[name="checkout"]`, węższy niż `button[name="checkout"]`, żeby nie łapać przycisków na cart page, gdy klient nawiguje.

Skrypt wstawić wewnątrz warunku `{%- if request.page_type != 'cart' -%}`, PO `</cart-drawer>`, PRZED `{%- endif -%}`.

---

#### Adaptacja do konkretnego motywu: sklep z obuwiem, FoxTheme (FoxKit/The4) (2026-06)

**Wdrożone.** Rozpoznanie motywu: metafieldy `shop.metafields.foxtheme.*` w `theme.liquid`, ładuje `vendor.js` + `theme.js`, custom elementy `cart-drawer`, `main-cart`, `cart-items`.

##### Mechanika koszyka (jak Nook: używaj eventów, NIE fetch override)

- `assets/cart.js` po każdej zmianie podmienia `#CartDrawerBody-{id}` / `#CartDrawerFooter-{id}` (drawer) oraz `#MainCart-{id}` (strona /cart) przez `innerHTML`, a na końcu emituje `document.dispatchEvent(new CustomEvent('cart:updated', …))`. To niezawodny sygnał → checkbox w footerze/main-cart **resetuje się sam** (świeży HTML z serwera jest odznaczony).
- Otwieranie/odświeżanie drawera = event `cart:refresh` (async) → reset wizualny z `setTimeout(~150ms)`.

##### Dwie OSOBNE sekcje (nie snippet drawer + footer jak w Dawn/Nook)

| Plik | Przycisk checkout | Gdzie wstawić checkbox |
|------|-------------------|------------------------|
| `sections/cart-drawer.liquid` | `<button name="checkout">` w `<form class="drawer__footer-buttons">`, wewnątrz `#CartDrawerFooter-{id}` | przed tym `<form>` |
| `sections/main-cart.liquid` | `<button name="checkout" form="cart">` w bloku `{%- when 'buttons' -%}` (`.cart__footer--buttons`), wewnątrz `<main-cart>` | przed przyciskiem checkout |

Drawer renderuje się tylko gdy `request.page_type != 'cart'` → **drawer i main-cart nigdy nie są w DOM jednocześnie** → globalny `document.querySelector('.consent-checkbox')` zawsze trafia w jedyną instancję. Dlatego: klasa `.consent-checkbox` jako selektor JS + unikalne `id` (`-drawer` / `-cart`) tylko dla `<label for>`.

##### JS w osobnym snippecie `snippets/consent-checkout.liquid`

Bo strona /cart NIE renderuje drawera: inline script w drawerze by się tam nie załadował. Snippet (`<style>` + IIFE z guardem `window.__consentCheckoutInited`) renderowany przez `{%- render 'consent-checkout' -%}` w OBU sekcjach. Primary guard = `click` w capture phase na `button[name="checkout"]`; druga warstwa = `submit` z `e.submitter.name === 'checkout'` (Enter). Blokada wizualna przez `aria-disabled` + CSS, NIE `disabled` (capture phase jest właściwą blokadą).

##### Newsletter w FoxTheme: `is="newsletter-form"` to PEŁNY POST, nie AJAX

`snippets/newsletter-form.liquid` używa `{%- form 'customer', is: 'newsletter-form' -%}` (custom element `extends HTMLFormElement`). Klasa `NewsletterForm` w `theme.js` **nie przechwytuje submitu**, tylko pokazuje modal po przeładowaniu (sprawdza `form_type=customer` w URL). Czyli statyczny POST → wystarczy `submit` guard w capture phase (jak w motywie na bazie Nook). Checkbox dajemy bez `name` (czysta bramka zgody; zapis przez form `customer` i tak opt-inuje do marketingu). Guard `window._newsletterConsentInited`: snippet renderuje się w sekcji + footerze + popupie.

---

#### Adaptacja do konkretnego motywu: sklep z częściami samochodowymi, Ignite 2.6.1 (Benchmark Themes) (2026-09-30)

**Wdrożone na motywie live.** Pliki: `snippets/consent-checkout-field.liquid`, `snippets/consent-newsletter-field.liquid`, `snippets/consent-scripts.liquid` (CSS + JS, render przed `</body>` w `layout/theme.liquid` i `layout/password.liquid`), przełączniki w grupie „Zgody (legislacja)” w `settings_schema.json`, teksty `consent.*` w `pl.json` + `en.default.json`.

- **Drawer renderuje się na KAŻDEJ stronie, także na /cart** (`theme.liquid`: `render 'cart-drawer'` przy `cart_drawer_enabled`). Na /cart są więc dwa checkboxy naraz, globalny `querySelector` trafi w zły. Checkbox wiązany z przyciskiem przez wspólny `.cart__ctas-container` (jest i w drawerze, i w `main-cart`).
- **Trzeci przycisk kasy: `snippets/cart-notification.liquid`** (okienko po ATC, `atc_action: notification`). Zamiast trzeciego checkboxa: klik w nim = `notification.close()` + `cart-drawer.open()` (motyw robi to samo dla „Zobacz koszyk”). Drawer i tak przerenderowuje się po ATC (`product-form.js` woła `cartDrawer.renderContents`).
- **Reset przez `PerformanceObserver` (type `resource`)** na `/cart/(add|change|update|clear)`, bez nadpisywania `fetch`. Powód: pubsub motywu przemianowuje `cartUpdate` na `cartAdd`/`cartRemove` zależnie od źródła, a `quick-order-list` i notatka koszyka strzelają fetchem bez publish. Observer łapie wszystko, także apki. Uwaga: notatka koszyka (`cart/update` z `note`) też zresetuje zgodę; w tym wdrożeniu notatka była wyłączona.
- **Natywny checkbox motywu `cart_terms`** (Ustawienia > Koszyk) zostaje pusty: tylko `required`, nie obejmuje okienka po ATC, brak resetu.
- **Wygląd blokady czystym CSS przez `:has()`**, bez MutationObservera: `.cart__ctas-container:has(.consent-checkout .consent-field__cb:not(:checked)) [name='checkout']` + ukrycie `.additional-checkout-buttons` (Shop Pay itp. w iframe nie da się zablokować klikiem).
- **Newsletter: jedno miejsce na cały motyw.** Sekcja newsletter, popup, email-signup-banner i blok `email-form` renderują `standard-blocks` → `when 'email_form'` (dwie gałęzie, `dont_render_customer_form`). Zgoda wstawiona w obie, ukryta przy `form.posted_successfully?`.

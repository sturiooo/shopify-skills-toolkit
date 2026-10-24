# Checkbox zgody na marketing: newsletter form (RODO)

**Wdrożone:** sklep z pluszakami (2026-05, motyw na bazie Nook, `snippets/newsletter-form.liquid`).

**Kontekst legislacyjny: różnica względem checkboxa checkout**

| | Checkout consent | Newsletter consent |
|---|---|---|
| Podstawa prawna | Dyrektywa 2011/83/UE, ustawa o prawach konsumenta | RODO Art. 6 ust. 1 lit. a: zgoda na marketing |
| Kiedy wymagany | Przed każdym zamówieniem | Przed zapisem do newslettera |
| Reset po zmianie | Tak, każda zmiana koszyka | Nie, statyczny form |
| Typ form | AJAX / dynamiczny | Statyczny POST |

**Pliki do pobrania od klienta:**

- `snippets/newsletter-form.liquid`: snippet renderowany wszędzie, gdzie jest formularz zapisu
- NIE potrzeba `cart.js` ani `cart-drawer.liquid`

**Metoda implementacji: prosta, bo statyczny POST**

Newsletter form to zwykły `<form>` z pełnym przeładowaniem strony. Nie ma re-renderu DOM, nie ma AJAX. Wystarczy `submit` event:

```js
document.addEventListener('submit', function(e) {
  var form = e.target;
  if (!form || !form.classList.contains('newsletter-form')) return;
  var cb = form.querySelector('.newsletter-consent-cb');
  if (!cb) return;
  if (!cb.checked) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var errEl = form.querySelector('.newsletter-consent-error');
    if (errEl) errEl.style.display = 'block';
  }
}, true);
```

**Kluczowe różnice implementacyjne względem checkout:**

1. **Klasa zamiast `id`**: snippet renderuje się w wielu miejscach (footer + popup). `id` musi być unikalne na stronie; klasa działa dla wielu instancji.
2. **Guard `window._newsletterConsentInited`**: JS dodawany inline w snippecie; bez guard'a każde wywołanie `{% render 'newsletter-form' %}` dodałoby duplicate listener.
3. **Brak `window.fetch` override**: form robi pełny POST, nie AJAX.
4. **Brak `cart:updated` / `MutationObserver`**: form nie jest re-renderowany dynamicznie.

**Gdzie wstawić checkbox w snippecie:**

WEWNĄTRZ `{%- form -%}...{%- endform -%}`, po `div.field` z inputem email (przed alertami błędów):

```liquid
{%- form 'customer', id: form_id, class: form_class -%}
  ...
  <div class="field relative">
    {# email input + inline submit button #}
  </div>

  <div class="newsletter-consent flex flex-col gap-1">
    <label class="consent-label flex items-start gap-2 text-sm leading-tight cursor-pointer">
      <input
        type="checkbox"
        class="newsletter-consent-cb shrink-0"
        style="margin-top: 2px;"
        aria-required="true"
      >
      <span>Wyrażam zgodę na otrzymywanie informacji marketingowych drogą elektroniczną zgodnie z <a href="/policies/privacy-policy" class="link" target="_blank" rel="noopener">polityką prywatności</a>.</span>
    </label>
    <p class="newsletter-consent-error text-xs" aria-live="polite" role="alert" style="display: none; color: #c0392b;">
      Wymagana zgoda na marketing, aby się zapisać.
    </p>
  </div>

  {%- liquid
    if form.errors ...  {# alerty błędów/sukcesu, zostawiamy po checkboxie #}
  -%}
{%- endform -%}

<script>
(function() {
  'use strict';
  if (window._newsletterConsentInited) return;
  window._newsletterConsentInited = true;
  // [submit listener + change listener]
})();
</script>
```

**Uwaga po przeładowaniu strony z błędem:** Shopify re-renderuje stronę, gdy `form.errors`: checkbox wraca odznaczony (świeży HTML). Użytkownik musi ponownie zaznaczyć. To jest poprawne zachowanie (nowa sesja = nowa zgoda).

**Gotche:**

- Sprawdź, czy motyw ma `context: 'footer'` vs `context: 'popup'` w `render 'newsletter-form'`: form w popupie ma inny `section_id`, ale ta sama klasa `.newsletter-form` = ten sam JS handler działa dla obu
- Jeśli sukces jest obsługiwany AJAXem (motyw podmienia HTML bez przeładowania), wtedy trzeba resetować widok checkboxa podobnie jak w cart-drawer. Sprawdź `form.posted_successfully?` pattern w snippecie.

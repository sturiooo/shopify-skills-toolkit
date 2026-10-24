# Checkbox zgody (regulamin) w koszyku: gdzie go wstawić, żeby był widoczny (2026-08, motyw Wonder)

Wymóg operatorów płatności (Przelewy24/PayU/Autopay): **aktywna akceptacja regulaminu
z klikalnym linkiem w procesie zakupowym** + telefon w stopce. Wdrożenie: snippet
`snippets/consent-checkout.liquid` renderowany w koszyku (strona) i w szufladzie.

### Pułapka nr 1: stopka koszyka bywa rozbita na gałęzie `{% if %}`
W Wonder `snippets/cart-footer.liquid` ma **trzy** gałęzie zależne od ustawień
(`show_view_cart` × `hide_checkout_button`) i w każdej własny przycisk kasy. Wstawka
trafiła do jednej z nich, a sklep używał innej, więc checkbox **w ogóle się nie renderował**
(objaw zgłoszony jako „nie widać go").

- **Zanim wstawisz cokolwiek do pliku z gałęziami, sprawdź, KTÓRA gałąź jest aktywna:**
  odczytaj klucze z `config/settings_data.json → current` (uwaga: brak klucza = wartość
  **domyślna ze schematu**, nie `false`; trzeba zajrzeć do `settings_schema.json`).
- **Lepiej: wstaw poza gałęziami**, w kontenerze, który renderuje się zawsze
  (tu: `snippets/cart-drawer.liquid`, `<div class="wt-cart__subtitle">` pod notatką
  do zamówienia). Jedno miejsce, zero zależności od konfiguracji przycisków.
- Uwaga na klucze-bliźniaki: `cart_drawer_show_order_note` z `presets` ≠
  `cart_show_order_note`, którego faktycznie używa Liquid.

### Pułapka nr 2: na stronie koszyka są DWIE instancje checkboxa
Szuflada koszyka siedzi w layoucie na każdej podstronie, na `/cart` w DOM są więc
dwa checkboxy naraz. Skrypt, który szukał „checkboxa w kontenerze przycisku"
z fallbackiem na `document.querySelector`, potrafił czytać **niewidoczną** instancję:
klient zaznacza swój, a kasa dalej zablokowana.

**Wzorzec:** zgoda jest JEDNA, nie per instancja.
```js
function granted() {              // zaznaczony którykolwiek = zgoda udzielona
  var all = boxes();
  return all.length === 0 || all.some(function (b) { return b.checked; });
}
document.addEventListener('change', function (e) {
  var box = e.target.closest && e.target.closest(CHECKBOX);
  if (box) { sync(box.checked); paintButtons(); }   // sync = kopiuj stan na resztę
});
```
Komunikat błędu pokazuj przy instancji **najbliższej klikniętemu przyciskowi**
(`closest('cart-drawer, .wt-cart, form, body')`), z fallbackiem na pierwszą, która
faktycznie ma `getClientRects().length > 0` (czyli jest widoczna).

### Pułapka nr 3: przyciski ekspresowe omijają blokadę
Shop Pay / Apple Pay / PayPal (`additional_checkout_buttons`) Shopify renderuje
w **iframe**: `click` w fazie capture ich nie złapie. Jedyny pewny hak to CSS:
```css
.wt-consent-blocked { pointer-events: none; opacity: 0.55; }
```
klasa zdejmowana w `paintButtons()` na kontenerach
`.additional-checkout-buttons, [data-shopify-buttoncontainer], shopify-accelerated-checkout`.
**Zawsze sprawdź, czy sklep ma włączone express checkout**: bez tego wdrożenie nie
spełnia wymogu, mimo że „checkbox działa".

### Reszta mechaniki (potwierdzona wcześniej w trzech innych sklepach)
- Blokada w **fazie przechwytywania na `document`**, nie przez atrybut `disabled`:
  `disabled` zdejmuje się w devtools w dwie sekundy, a przycisk kasy jest
  przerenderowywany po każdej zmianie koszyka (listener przypięty do elementu ginie).
- Druga warstwa na `submit` z `event.submitter.name === 'checkout'` (Enter w polu).
- Stan wizualny przez `aria-disabled`, nie `disabled`: przycisk musi zostać klikalny,
  żeby dało się pokazać komunikat „zaakceptuj regulamin".
- **Reset zgody po zmianie koszyka jest darmowy**: Shopify przerenderowuje fragment
  z serwera, a w Liquid checkbox jest odznaczony → nowa zawartość koszyka = nowa zgoda.
- Link do regulaminu: `shop.terms_of_service.url | default: '/policies/terms-of-service'`
  + `target="_blank" rel="noopener"`.

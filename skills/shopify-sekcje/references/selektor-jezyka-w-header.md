# Selektor języka w header na mobile (zamiast na dole hamburger menu)

**Wdrożone:** sklep z kosmetykami (2026-06, Sahara/DigiFist). Problem: selektor lokalizacji (`country-drawer`) siedzi w `drawer__utils` na dole nawigacji mobilnej, słabo dostępny. Cel: zawsze widoczny obok ikony koszyka.

#### GOTCHA (krytyczny): motyw ukrywa WSZYSTKIE nie-koszykowe utils na mobile

`section-header.css`: `.header__utils-item:not(.header__utils-item--cart){display:none}` poniżej 990px (search/account itd. są ukryte na mobile). Nowy `<li>` w `header__utils` **nie pokaże się na mobile** dopóki nie nadpiszesz tej reguły z **wyższą specyficznością**. `.header__utils-item:not(...)` = (0,2,0); użyj scope przez **id `#header`** → `#header .header__utils-item--lang { display:block }` = (1,1,0) wygrywa. Na desktopie (≥990) ukryj (`display:none`), bo tam jest już country-drawer w nawigacji (brak duplikacji).

#### Reużycie natywnej mechaniki lokalizacji: zero nowego JS

Motyw ma custom elementy w `global.js`:
- **`theme-dropdown`**: samodzielny inline popover (button + `.dropdown-content` absolute; obsługa open/toggle/outside-click/Escape). `handleItemClick`: `<a data-value="xx">` → ustawia `input[type=hidden].value` + dispatch `new Event('input', {bubbles:true})`.
- **`localization-form`**: słucha `input` na `[name="country_code"], [name="language_code"]` → `form.submit()`.

Czyli **wybór języka = klik w `<a data-value>` → input event → submit formularza `localization` → reload na tej samej podstronie**. Wystarczy wyrenderować `localization-form > {% form 'localization' %} > theme-dropdown` z dropdownem `language_code` (lista z `localization.available_languages`, `endonym_name`). Guard `if localization.available_languages.size > 1`.

#### Inline dropdown vs overlay drawer: wybór

- **Inline `theme-dropdown`** (zwykła rozwijana lista pod przyciskiem): gdy klient chce prostą listę PL/EN. Header **nie przycina** absolutnie pozycjonowanych dzieci (mega-menu dropdowny mają `overflow:visible` i wychodzą poza header) → popover OK bez overlay. Przy prawej krawędzi (obok koszyka) lista wychodziłaby poza viewport → `inset-inline-start:auto; inset-inline-end:0` (otwórz w lewo).
- **Overlay drawer** (`<details>` + `menu-drawer` + `.js-drawer`, wzorzec `country-drawer`): gdy chcesz pełnoekranową nakładkę. `MenuDrawer` (global.js) wymaga `details` + `summary` + `.js-drawer` + `.js-btn-close-drawer`. Cięższe; tu niepotrzebne, klient wolał listę.

#### Kompaktowy przycisk

`.dropdown-button` natywnie ma border/bg/padding/`width:100%` (wygląda jak select). Do headera nadpisz na minimal: `padding:0; border:0; background:none; width:auto; font-size:1.3rem` (pokazuje np. „PL" + chevron). Setting `enable_mobile_language_selector` (checkbox) do włącz/wyłącz. Snippet `language-selector.liquid` renderowany w `header__utils` przed `<li>` koszyka, owinięty `<li class="header__utils-item header__utils-item--lang">`.

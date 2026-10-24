# Sklep dwujęzyczny: co psuje się po przetłumaczeniu i czego Shopify nie tłumaczy wcale

Źródło: sklep z obuwiem skórzanym, 09.10.2026 (Prestige, PL główny + EN). Zgłoszenie klienta: „kolory nie są widoczne, Colour, zakładki bloga po polsku, obrazy na O nas po polsku”.

## Próbki kolorów puste tylko w drugim języku

- **Motyw dopasowuje próbkę po nazwie wartości opcji W JĘZYKU SKLEPU.** Prestige (`snippets/option-value.liquid`) porównuje
  `label | downcase` z wierszami `settings.color_swatch_config` (`Nazwa:#hex`). Gdy nie znajdzie, wstawia samą nazwę jako kolor CSS:
  `linear-gradient(to right, cognac brown, cognac brown)` → nieprawidłowy CSS → puste kółko. W PL działało, bo nazwy PL były w configu.
- **`color_swatch_config` ma osobne tłumaczenie** (Translate & Adapt > motyw, klucz `general.color_swatch_config`, zasób
  `OnlineStoreTheme`). W EN było tylko `Cognac / Dark brown / Black / Brown / Gray`, a opcje przetłumaczono na `Cognac Brown`, `Storm Black`…
  Edycja PL w `settings_data.json` nic nie da dla EN.
- To samo dotyczy filtra z metapola (S&D, prezentacja „próbka”): nazwą jest przetłumaczona wartość metapola (`Bronze` → kolor CSS `bronze` nie istnieje).
- Diagnoza curl: `grep -o 'block-swatch__color[^>]*></span><span>[^<]*'` na `/en/products/...`. Hex = OK, słowo = brak w configu.
- Recepta: tłumaczenie EN ustawienia = wszystkie nazwy EN z opcji ORAZ z filtra (`translationsRegister`, key `general.color_swatch_config`,
  digest pobrać PO zmianie PL, bo zmiana PL zmienia digest). Przy nowym kolorze: dopisać w obu językach.
- **Nazwa opcji „Colour” vs „Color”** jest bezpieczna dla próbek w Prestige: `general.label.color` w en.default.json = `"Color,Colour"`.
  W innym motywie sprawdź tę listę, zanim przetłumaczysz nazwę opcji.

## Filtr S&D z metapola: duplikaty i opóźnienie

- Wartości filtra to przetłumaczone wartości metapola per produkt, więc niespójne tłumaczenia tworzą osobne pozycje (`Gray` z Derby, `Grey` z Chelsea).
- Po `translationsRegister` na metapolu storefront pokazywał stare wartości jeszcze ok. 1,5 min (przeindeksowanie S&D). Nie poprawiaj drugi raz, odczekaj.

## Tagi artykułów: Shopify ich nie tłumaczy

- `TranslatableResourceType.ARTICLE` = title, body_html, summary_html, handle, meta_title, meta_description. Tagów brak, Translate & Adapt też ich nie ma.
- Recepta: snippet z etykietą z pliku językowego motywu, klucz po uchwycie tagu, fallback na surowy tag:
  `assign k = tag | handle | prepend: 'blog.tag_labels.'` → `assign l = k | t` → `if l contains 'translation missing'` → tag.
  `handle` transliteruje polskie znaki (`materiały` → `materialy`, `obroże` → `obroze`). Podmienić `link_to_tag` / `link_to_remove_tag`
  (generują własny tekst) na ręczne `<a href="{{ blog.url }}/tagged/{{ tag | handle }}">` w main-blog, main-article i blog-post-card.
- **curl nie widzi paska tagów** na `/blogs/news` (brak `.blog-tags` w HTML, także z ciasteczkami i UA przeglądarki), Chrome widzi.
  Pasek tagów weryfikuj w przeglądarce (`document.querySelector('.blog-tags').innerText`), kategorię na artykule wystarczy curlem.

## Obrazy z wpisanym tekstem: osobny obraz per język

- Tłumaczenie motywu nie obejmuje `image_picker`, więc grafika z polskim napisem zostaje w EN. Wzorzec: dodatkowe pole `image_en`
  w schemie bloku i `if request.locale.iso_code == 'en' and block.settings.image_en != blank`.
- Ta sama sekcja na innym szablonie (np. `page.json` dla „O nas”) ma własne ustawienia bloków: po dodaniu pola trzeba je wypełnić
  w KAŻDYM szablonie, gdzie sekcja występuje (`grep '"collection-list"' templates/*.json`).
- Slideshow z mobile: kolejność fallbacków EN mobile → EN desktop → PL mobile, inaczej na telefonie wraca polska grafika.

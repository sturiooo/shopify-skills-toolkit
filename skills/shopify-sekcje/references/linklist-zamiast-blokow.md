# Menu (`link_list`) jako szybkie źródło wielu pozycji: zamiast bloków po kolei

**Wdrożone:** sklep z pluszakami (2026-06, motyw na bazie Nook).

Gdy klient ma już zebrane kolekcje w menu i nie chce dodawać bloków jeden po drugim, daj setting `type: "link_list"` i generuj pozycje z linków. Z linku wyciągasz:

- `link.title`: etykieta
- `link.url`: adres
- `link.object.image | default: link.object.featured_image`: zdjęcie (collection_link → kolekcja ma `.image`; product_link → produkt ma `.featured_image`; url-link → `link.object` jest nil, `default` ratuje)
- `link.current`: czy to bieżąca strona (gotowy active state, bez ręcznego `request.path ==`)

**Wzorzec hybrydowy (menu + bloki):** renderuj najpierw linki menu, potem ręczne bloki: bloki dają fine-grained (własne zdjęcie/etykieta), menu daje masowe dodawanie. Wspólny licznik indeksu: `assign idx = forloop.index0 | plus: menu_count`. `total = menu_count | plus: section.blocks.size`. Tylko bloki widać w edytorze do edycji per-item; menu jest „ustaw i zapomnij".

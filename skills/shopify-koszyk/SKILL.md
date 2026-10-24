---
name: shopify-koszyk
description: "Cart API, pasek postępu do darmowej dostawy i gratisu, dopłaty jako pozycje koszyka, pola własne w koszyku, integracja z Klaviyo oraz checkboxy zgód: regulamin, marketing, blokada checkoutu z resetem zgody po zmianie koszyka. Uruchamiaj przy pracy nad koszykiem, wymogami RODO w kasie i wszystkim, co dodaje lub modyfikuje pozycje koszyka."
---

# Koszyk i checkout

Twarda zasada: **nie istnieje API "dorzuć X zł do sumy"**. Każda kwota w koszyku to realna pozycja produktowa albo Shopify Functions (Plus). Zacznij od `references/cart-api-podstawy.md`, tam są reguły obowiązujące w każdym projekcie.

## Co tu jest

Wczytuj pojedynczy plik referencyjny, nie cały katalog.

| Plik | Temat |
|---|---|
| `references/blokada-checkoutu-zgoda.md` | Blokada checkoutu + reset zgody (Checkout Consent Checkbox), adaptacje do motywów Nook, FoxEcom i Ignite. |
| `references/cart-api-podstawy.md` | Cart API: twarda wiedza dla każdego projektu. |
| `references/checkbox-regulaminu.md` | Checkbox zgody (regulamin) w koszyku: gdzie go wstawić, żeby był widoczny (2026-08, motyw Wonder). |
| `references/pakowanie-na-prezent.md` | Checkbox "pakowanie na prezent" w koszyku (dopłata): produkt-linia, nie opłata. |
| `references/pasek-postepu-i-gratis.md` | Free-gift cart progress bar (Buy X Get Y hybryda). |
| `references/pola-wlasne-i-klaviyo.md` | Pola własne w koszyku + integracja Klaviyo + checkbox zgody (2026-06, Sleek/FoxEcom). |
| `references/zgoda-marketingowa-newsletter.md` | Checkbox zgody na marketing: newsletter form (RODO). |
| `references/obowiazkowy-krok-przed-kasa.md` | Obowiązkowy krok (kreator dodatków) przed kasą: zapis stanu koszyka przy wejściu w krok, furtki do zamknięcia, test curlem (2026-09-28, Concept). |
| `references/kreator-dodatkow-w-motywie.md` | Kreator dodatków w motywie zamiast apki bundle: czego nie da się bez Plus, właściwości `_` w panelu zamówienia, wiązanie po variant_id, pomiar sprzedaży przez metapole analyticsQueryable i ShopifyQL (2026-09-29, Concept). |
| `references/prezent-bxgy-subskrypcje-i-laczenie.md` | Prezent od progu (Kup X, odbierz Y): subskrypcje nie liczą się do progu (`customerBuys.isSubscription`), łączenie z rabatem apki zestawów, ochrona przed dublem z kodem −100%, test trzech koszyków, prezent bez stanu albo tylko-B2B (2026-10-13); kod z `productDiscounts: false` czyni prezent płatnym, tani gratis zestawu przegrywa z kodem, test kodu bez kasy, blokada prezentu na sesję (2026-10-22). |

# Prezent od progu (Kup X, odbierz Y): subskrypcje i łączenie z apkami zestawów

Sklep z herbatą (motyw Maestrooo), 13.10.2026. Dwa progi prezentu (150 zł Prezent 1, 250 zł Prezent 2 zamiast niego), skrypt motywu
dodaje prezent sam, rabat automatyczny BxGy robi z niego 0 zł. Zwykły koszyk działał, dwa realne koszyki nie.

## Pozycje w subskrypcji nie liczą się do progu

- **`customerBuys.isSubscription` ma domyślnie `false`** (`DiscountCustomerBuysInput`: `isOneTimePurchase` domyślnie true).
  Koszyk z Produktem A w subskrypcji za 157,50 zł: prezent w koszyku za 15 zł, zero alokacji rabatu. Ten sam produkt jednorazowo: 0 zł.
- Objaw wygląda jak awaria skryptu prezentu albo konflikt rabatów. To nie jest jedno ani drugie: rabat po prostu nie widzi linii z selling planem.
- **Recepta:** przy każdym BxGy w sklepie z subskrypcjami (Kaching Subscriptions, natywne Subscriptions) ustaw
  `customerBuys: { isOneTimePurchase: true, isSubscription: true }`. Mutacja `discountAutomaticBxgyUpdate` przyjmuje samo to pole.

## Rabat apki zestawów (Kaching) a prezent z progu

- Rabat Kaching Bundles to `DiscountAutomaticApp` klasy PRODUCT z `combinesWith.productDiscounts: true`.
  Prezent BxGy miał `productDiscounts: false`, więc w koszyku z zestawem jeden z nich musiał wypaść.
- Łączenie działa tylko, gdy **oba** rabaty zezwalają na klasę drugiego. Po ustawieniu `productDiscounts: true` w BxGy:
  zestaw (dwa gratisy z Kaching) + Prezent 1 z progu, wszystkie trzy po 0 zł.
- Ta sama zasada chroni przed dublem: kod −100% na ten sam produkt (np. z flow Klaviyo) musi mieć **wyłączone** łączenie
  z rabatami produktowymi, wtedy Shopify nie nałoży go razem z prezentem z progu.

## Jak testować (bez zamówienia)

`/cart/add.js` + `/cart.js` w headless (`final_line_price`, `discounts[].title`). Trzy koszyki obowiązkowo:
zwykły jednorazowy, z subskrypcją (`selling_plan` w `cart/add.js`), z zestawem apki. Apka z testem A/B (Kaching `ab: "A"/"B"`
we właściwości linii) daje różne koszyki przy kolejnych przebiegach, więc test zestawu puść 2 razy.

## Prezent z wyższego progu bez stanu albo niewidoczny

`selected_or_first_available_variant` zwraca nil, gdy żaden wariant nie jest dostępny, a produkt niewidoczny dla rynku
(produkt tylko-B2B, 404 dla gościa) daje w ustawieniu motywu pusty obiekt. W obu przypadkach próg „znika” i zostaje prezent
z niższego progu. Jeśli klient chce „bez zamiennika”, sprawdź widoczność produktu-prezentu w Sklepie online i rynku detalicznym,
a w Liquid weź `| default: product.variants.first`, żeby próg był skonfigurowany, tylko niedostępny.

## Kod rabatowy, który „nie łączy się z niczym”, zabiera prezent z progu (22.10.2026)

- **Kod z `combinesWith.productDiscounts: false` wyłącza BxGy prezentu, bo BxGy to rabat klasy PRODUCT.** Zmierzone na
  `TEST-10` (−10% na zamówienie): koszyk z Produktem A 175 zł + Prezent 1. Bez kodu Prezent 1 0 zł; z kodem Prezent 1 15 zł,
  kod −19 zł od 190 zł. Klient płaci za prezent, a skrypt motywu tego nie łapie (bezpiecznik działa tylko przy dodawaniu).
- **Recepta:** kod `productDiscounts: true, orderDiscounts: false, shippingDiscounts: true`. Z zestawem apki i tak się nie połączy,
  jeśli rabat apki ma `orderDiscounts: false` (łączenie musi dopuszczać KAŻDA strona). Ze stałym rabatem klasy ORDER też nie.
- **Przy dwóch niełączących się rabatach Shopify zostawia korzystniejszy dla klienta**, więc przy tanim gratisie z zestawu kod wygrywa:
  Zestaw B (2 × 50 g) 140 zł + gratis zestawu (12 zł) z kodem −10% = −15,20 zł, gratis płatny, razem 136,80 zł. Zestaw C (gratis 12 zł,
  kod 9,40 zł) i Zestaw D zostają przy zestawie. Powiedz klientowi wprost, przy których zestawach kod „zjada” gratis.
- **Test bez kasy:** w czystej sesji `/discount/<KOD>?redirect=/cart`, potem `/cart.js`: `discount_codes[].applicable`,
  `cart_level_discount_applications`, `line_level_discount_allocations` na liniach. Kasa jest potrzebna tylko do rabatu na dostawę.

## Blokada prezentu „na sesję” jest za sztywna (22.10.2026)

- **Bezpiecznik „prezent niezrabatowany do zera, usuń i zablokuj w sessionStorage” blokował prezent do zamknięcia karty.**
  Po jednej nieudanej próbie (zestaw z gratisem, kod) Prezent 1 nie wracał już przy zwykłym koszyku od 150 zł; w świeżej karcie
  działało, co wyglądało jak losowy błąd. Recepta: zapisuj podpis koszyka (warianty, ilości, plany, kody, bez linii prezentu)
  i blokuj tylko przy tym samym podpisie. Poprawione w skrypcie prezentu motywu (`assets/gratis-tier.js`, 22.10).

# Punkty odbioru i ukrywanie metod dostawy (stan 30.09.2026, sklep z pluszakami)

## Ukrywanie metod poza Plusem

- **Funkcje dostaw z aplikacji z App Store działają na każdym planie**, własna aplikacja z Shopify Functions wymaga Plusa
  (shopify.dev/docs/apps/build/functions). Limit: 25 aktywnych reguł dostaw na sklep, ze wszystkich apek łącznie.
- **Payflow** (Appfleece, 5,0 / 115 opinii): ukryj, przemianuj, zmień kolejność. Cel wybierany po nazwie metody („zawiera”),
  cenie albo „stawki sklepu”. Darmowy plan = 1 reguła, Premium 4,99 USD/mies.
- **Warunki są w zestawach i nie łączy się ich między zestawami w jednej regule** (docs.payflow.appfleece.com/reference/condition-sets):
  zestaw 1 = tag produktu, kolekcja, wariant, `totalQuantity`, `totalWeight`; zestaw 5 = metapole wariantu/produktu,
  atrybut koszyka, właściwość linii, SKU, typ. Potrzebujesz obu? Dwie osobne reguły z tą samą akcją.
- **`totalQuantity` liczy wszystkie sztuki, także dodatki**, więc nie wyrazi „więcej niż jeden produkt główny”. Zamiast tego waga do
  wyceny (poniżej) albo tag na produktach głównych.
- **Przewoźników per wariant zapisuj jako WYKLUCZENIA, nie jako dozwolone.** Przy liście dozwolonych produkt bez pola (dodatek)
  spełnia „nie zawiera DHL” i ukrywa DHL w każdym koszyku. Wykluczenie + „zawiera” = puste pole niczego nie rusza.

## Punkty odbioru: Octolize Pickup Points PRO (4,9 / 58)

| Plan Octolize | Cena | Co daje |
|---|---|---|
| „Shopify Basic” | 9,99 USD/mies (99,99/rok) | mapa w KOSZYKU (trzeba wyłączyć Shop Pay/Apple/Google Pay) |
| „Grow & Advanced” | 14,99 USD/mies (149,99/rok) | LISTA punktów w kasie, wymaga CCS (na Grow tylko przy rocznym rozliczeniu) |
| „Shopify Plus” | 39,99 USD/mies | mapa albo lista w kasie |

- Czy sklep na Grow może wziąć plan „Basic” z mapą w koszyku: listing nie mówi, pytaj Octolize.
- **ORLEN Paczka jest obsługiwana** (opis Octolize, potwierdzone), mimo że skrócona lista na listingu jej nie ma.
  Poczta Polska też; automaty Pocztex jako osobny typ punktu do sprawdzenia w trialu.
- Przy liście w kasie punkty są zwykłymi metodami dostawy, więc Payflow ukrywa je tak samo jak kurierów. Przy mapie w koszyku
  punkt zostaje zapisany w zamówieniu nawet wtedy, gdy kasa potem ukryje paczkomat.
- Octolize ma własne min./max. wagi przy punktach, więc limit „nie mieści się do paczkomatu” da się zrobić wagą do wyceny
  (sztucznie zawyżona waga produktów gabarytowych).

## Pobranie (COD) w Payflow i apka Globe Pickup Points (2026-10-12, sklep na motywie Sleek)

- **Funkcja płatności widzi ręczną metodę COD pod nazwą „Cash on Delivery (COD)”**, niezależnie od polskiej nazwy w kasie
  („Płatność przy odbiorze”). Dopasowanie „przy odbiorze” nie działa: w trybie „Nie zawiera tekstu” chowa wszystkie płatności.
  Dopasowuj po **„COD”**. Komplet dla „przy pobraniu tylko COD”: reguła 1 „wysyłka NIE zawiera »pobranie« → ukryj zawierające COD”,
  reguła 2 „wysyłka zawiera »pobranie« → tryb »Nie zawiera tekstu« COD”. Darmowy Payflow = 1 aktywna reguła dowolnego typu,
  druga wymaga Premium 4,99 USD. Komunikat „osiągnięto limit” na nowym szablonie bywa fałszywy przy zerze reguł.
- **Globe Pickup Points** (mapa w koszyku, wiele przewoźników): widget wstrzykiwany po selektorze CSS (light DOM, style inline,
  da się nadpisać z `!important`), w zamówieniu zapisuje atrybuty `PickupPointId/Name/Address/City/PostCode/Courier`,
  które **Base odczytuje natywnie** do „Odbiór w punkcie”. Pole „COD shipping method keywords” uzupełnij nazwą stawki pobrania.
- **Punkt bez pasującej stawki Shopify = zamówienie kurierskie z adresem paczkomatu.** Każdy próg ceny kuriera potrzebuje
  bliźniaczej stawki paczkomatu (z „Paczkomat” w nazwie), inaczej Globe nie ma czym zastąpić kuriera, a Base dzieli po nazwie.

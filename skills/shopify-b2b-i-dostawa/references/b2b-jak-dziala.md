# Shopify B2B: jak to naprawdę działa i ile z tego jest natywne (2026-08, sklep z pluszakami, plan Grow)

### Meta-lekcja: nie odpowiadaj na pytania o plany z pamięci

Postawiłem klientowi tezę „natywne B2B = tylko Shopify Plus" i **była błędna**: moduł jest na Basic/Grow/Advanced.
Kosztowało to dwie przepisane wiadomości do teamu i propozycję obejścia (tagi + kody rabatowe + bramkowanie
w motywie), która była kompletnie niepotrzebna. **Matryca planów Shopify zmienia się szybko.**

- **Zawsze weryfikuj w panelu klienta:** `Ustawienia → Plan → Wyświetl wszystkie funkcje` → tabela porównawcza
  z wierszami per funkcja. To jest źródło prawdy, nie pamięć i nie ogólna wiedza o „Plus-only".
- Szybki test obecności B2B: czy w menu `Klienci` jest podzakładka **Firmy**.
- **Sidekick (asystent AI w panelu) też jest AI**: bywa trafny, ale jego twierdzenia sprawdzaj w tabeli planów.
  W tej sesji podał limit „3 katalogi" i akurat miał rację, co potwierdziłem dopiero w oficjalnej tabeli.

### Limit, który przesądza o architekturze cenników

Wiersz „Shopify B2B" w tabeli planów:
`Basic: do 3 katalogów | Grow: do 3 katalogów | Advanced: do 3 katalogów | Plus: nieograniczona liczba`

**To jest główne ograniczenie, nie brak funkcji.** Konsekwencja: poza Plusem masz **maksymalnie 3 poziomy
cenowe w całym sklepie**, niezależnie od liczby kontrahentów. Można zrobić rynek pod jedną konkretną firmę,
ale i tak zjada to jeden z trzech katalogów → indywidualne cenniki per kontrahent skalują się tylko do trzech.
Pojedyncze wyjątki z negocjowaną ceną obsługuje się **zamówieniami roboczymi (draft orders)**.

Drugie ograniczenie planów poza Plus: katalogu **nie przypniesz bezpośrednio na karcie firmy**, idzie przez rynek.

### Model danych i SZTYWNA kolejność wdrożenia

`Firma` → `Lokalizacja` → `Kontakty (klienci)`. Wszystko istotne wisi na **lokalizacji**, nie na firmie:
adres wysyłki/rozliczeniowy, ID zewnętrzne, rynki + katalogi, warunki płatności, NIP + „Pobieraj podatek",
ustawienia realizacji zakupu.

**Kolejność jest wymuszona przez panel**: przy zakładaniu firmy pole „Katalogi" pokazuje
„Brak dostępnych katalogów. Przejdź do sekcji Markets", dopóki nie istnieje katalog podpięty do rynku:

1. **Katalog** (`Rynki → Katalogi`, NIE pod Produktami): produkty + „Korekta ceny" ±% albo ceny per wariant
   z importu CSV; toggle „automatycznie uwzględniaj nowe produkty"; opcja „Uwzględnij cenę przed obniżką".
2. **Rynek** + podpięcie katalogu. Warunek rynku: **Regiony / Lokalizacje firmy / Kanały**. „Lokalizacje firmy"
   to jest właśnie rynek B2B (wybór konkretnych lokalizacji albo toggle „wszystkie istniejące i przyszłe").
3. **Firma → lokalizacja → kontakty**. Kontakt musi **wcześniej istnieć jako klient**. Uprawnienia:
   *tylko zamawianie* / *admin lokalizacji*. Zaproszenie = „Wyślij e-mail dostępu B2B".

Wymagane: **nowe konta klientów** (logowanie kodem e-mail). Sprawdź `Ustawienia → Konta klientów`.

### Czego NIE wyceniać jako pracy deweloperskiej (jest natywne)

- **Numer PO / zamówienia wewnętrznego kupującego**: pole pojawia się w kasie automatycznie dla kontaktów
  przypisanych do firmy. Zero kodu, zero apki. Można je też ustawić ręcznie na draft orderze.
  (Wcześniej wyceniałem to jako pole w koszyku, niepotrzebnie.)
- **Akceptacja zamówień**: opcja na lokalizacji „przesyłaj wszystkie zamówienia jako wersje robocze do weryfikacji".
- **Zwolnienie z podatku i NIP**: pola na lokalizacji („Pobieraj podatek”).
- **Ograniczenie adresów dostawy**: „zezwalaj klientom na wysyłkę na dowolny adres jednorazowy".

**W motywie zostaje realnie tylko:** oznaczenie cen jako netto (hurt myśli w netto, detal w brutto, a szablon
jest wspólny) oraz przełącznik lokalizacji, a ten **ma sens wyłącznie, gdy kontrahenci mają po kilka oddziałów**.

### Gotchy z panelu

- Rynek dla lokalizacji dobiera się **po adresie wysyłki**. Sprawdź status rynku docelowego: w tym sklepie
  rynek **Poland miał status „Wersja robocza"**, a Francja/Niemcy/UK były aktywne. Polscy kontrahenci wpadliby
  do nieopublikowanego rynku.
- Panel wyświetla ostrzeżenie, że **niektóre aplikacje potrafią błędnie przypisywać zamówienia B2B**
  do pojedynczego klienta zamiast do firmy → sprawdzić na pierwszych zamówieniach po starcie.
- Masowe zakładanie firm: ręcznie = natywnie, ale **Matrixify** (CSV) i **Shopify Forms** (formularz wniosku
  o konto firmowe) to apki; ustalić z klientem, czy wchodzą w grę.

### Checklista danych od klienta (mapowana 1:1 na pola formularza)

1. **Ile poziomów cenowych i jakie rabaty**: max 3; blokuje całą resztę konfiguracji
2. Firmy: nazwa, NIP, adresy, oddziały
3. Kontakty: imię, nazwisko, e-mail (to login) + kto ma być adminem lokalizacji
4. Warunki płatności per firma (przedpłata / netto 7/14/30)
5. Które firmy zwolnione z podatku
6. Czy zamówienia mają wymagać zatwierdzenia
7. Zakres asortymentu w hurcie, zasady wysyłki, czy ceny prezentujemy netto
8. Czy klient ma własną numerację kontrahentów (idzie w „ID firmy")

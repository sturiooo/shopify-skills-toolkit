# Delivery API: strefy wysyłki i stawki przez `deliveryProfileUpdate` (2026-06, sklep z obuwiem)

**Da się ustawiać strefy + stawki przez Admin GraphQL (CLI `store execute --allow-mutations`). NIE da się: live carrier rates (InPost/DHL real-time), bo wymagają Carrier Service/aplikacji.**

- Struktura input (potwierdzona introspekcją 2026-04): `deliveryProfileUpdate(id, profile)`; `profile.locationGroupsToUpdate: [{ id, zonesToCreate: [...], zonesToUpdate: [...] }]`; `profile.methodDefinitionsToDelete: [id]` (kasowanie metod istniejącej strefy).
- Strefa (`zonesToCreate`/`zonesToUpdate`): `{ name, countries: [{ code: "DE", includeAllProvinces: true }], methodDefinitionsToCreate: [...] }`.
- **GOTCHA krajów z prowincjami:** kraj wymagający prowincji (np. **GB/Wielka Brytania**) bez `includeAllProvinces: true` → userError „Kraj … musi mieć powiązaną co najmniej jedną prowincję". **Daj `includeAllProvinces: true` każdemu krajowi** (dla pozostałych nieszkodliwe).
- Metoda: `{ name, active, rateDefinition: { price: { amount: "45.40", currencyCode: "PLN" } }, weightConditionsToCreate: [...], priceConditionsToCreate: [...] }`. Stawka stała = sam `rateDefinition` bez warunków.
- **Stawki wagowe (2 progi):** dwie metody o tej samej nazwie, każda z `weightConditionsToCreate`, np. „1 para": `[{criteria:{value:0.5,unit:KILOGRAMS},operator:GREATER_THAN_OR_EQUAL_TO},{criteria:{value:1.0,unit:KILOGRAMS},operator:LESS_THAN_OR_EQUAL_TO}]`; „2+": `[{value:1.0, GREATER_THAN_OR_EQUAL_TO}]`. Klient widzi jedną, pasującą do wagi koszyka.
- **Stawka „do 5 kg":** warunek `LESS_THAN_OR_EQUAL_TO 5.0 KILOGRAMS`.
- **Mutacja jest ATOMOWA**: jeśli `userErrors != []`, NIC się nie zapisuje (cała partia rollback). Dlatego: rób partiami, czytaj `userErrors`, popraw, powtórz. Tworzenie stref jest addytywne i odwracalne (łatwo usunąć).
- **Stawki wagowe „na sucho":** jeśli produkty mają wagę 0 (eksport: `Variant Grams`=0), DPD wagowe **nie pokaże się w checkoucie** (koszyk 0 kg nie wpada w próg). Stawki konfigurujesz, ale działają dopiero gdy klient ustawi wagi (~1 kg/szt.). Komunikuj to.
- **`zonesToUpdate.countries` ZASTĘPUJE listę krajów strefy, nie dopisuje** (potwierdzone 2026-10-12, sklep z karmą dla psów). Usunięcie jednego kraju = wyślij pełną listę bez niego; dodanie = pełna lista z nim. Przed mutacją zapisz obecny stan strefy do backupu, bo pominięty kraj znika bez ostrzeżenia (`userErrors: []`). Blokada sprzedaży do kraju: wyjmij go z rynku ORAZ ze stref; sam kraj w strefie innego profilu nie otworzy kasy, jeśli nie ma go w aktywnym rynku.
- **Zmiana progu wagi istniejącej stawki** (`deliveryProfileUpdate` → `methodDefinitionsToUpdate.conditionsToUpdate`):
  `criteriaUnit` to String, nie enum. „KILOGRAMS” przechodzi walidator schematu, a serwer odrzuca („Nieprawidłowa kombinacja
  pola i jednostki kryterium”); działa `"kg"`. Mutacja jest atomowa, a CLI i tak pisze „Operation succeeded”: czytaj `userErrors`.
  Wyłączanie stawki zamiast usuwania: `{ id, active: false }` (sklep z obuwiem skórzanym, 01.10.2026).
- Generuj input **skryptem z cennika** (xlsx → JSON variables), nie ręcznie: zero literówek w cenach. Edycja istniejącej strefy = `zonesToUpdate` + `methodDefinitionsToDelete` starej metody.

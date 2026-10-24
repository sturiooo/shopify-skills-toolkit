# Kolor nie znika mimo poprawnego CSS, bo jest wypalony w pliku graficznym

Potwierdzone 22.09.2026 w sklepie z figurkami kolekcjonerskimi (motyw Nook), ale problem jest niezależny od motywu i sklepu.

## Objaw

Zmieniasz paletę, weryfikujesz CSS **na żywym renderze** (nie w plikach), reguła jest poprawna,
a klient dalej widzi stary kolor. Kolejne poprawki CSS nic nie dają, bo naprawiasz warstwę,
w której problemu nie ma.

## Rozstrzygnięcie: odczytaj piksel, nie regułę

W tym sklepie `.cs-card__media` serwowało `background: #f5f5f5`, a tła kafli były kremowe.
Przyczyna: 8 grafik kolekcji miało `#FFF8EC` **wypalone w pikselach**, `hasAlpha: no`.
Żadna zmiana w motywie tego nie ruszy.

**`sips` nie poda pojedynczego piksela**, a `--cropToHeightWidth` tnie od ŚRODKA obrazu,
nie od rogu, więc pierwszy pomiar pokazał kolor z figurki zamiast z tła i wprowadził w błąd.
`--cropOffset` też liczy się względem środka.

Rozstrzyga własny dekoder PNG: `zlib` plus defiltrowanie (typy 0 do 4), około 70 linii,
bez zależności. Odczytaj cztery rogi i piksel przy górnej krawędzi. Jeśli wszystkie mają
dokładnie ten sam kolor, to jest tło wypalone w pliku.

## Przemalowanie tła bez artefaktów

Nie podmieniaj tylko pikseli równych dokładnie staremu kolorowi, bo antyaliasing wokół obiektu
zostawi obwódkę w starym odcieniu. Licz wagę „tłowości” i przesuwaj proporcjonalnie:

```
w = max(0, 1 - dystans_RGB(piksel, stare_tlo) / TOL)     # TOL około 70
piksel += w * (nowe_tlo - stare_tlo)
```

Piksel równy tłu przechodzi w całości, krawędziowy częściowo, obiekt zostaje nietknięty.
Kontrola po konwersji: cztery rogi muszą mieć dokładnie docelowy kolor.

## Podmiana zdjęcia kolekcji przez API, dwie pułapki

- **`stagedUploadsCreate` z `resource: COLLECTION_IMAGE` zwraca `resourceUrl` równy samemu
  korzeniowi bucketa** (`https://shopify-staged-uploads.storage.googleapis.com/`), bez ścieżki.
  Prawdziwy adres trzeba złożyć samemu: `url` plus wartość parametru `key`. Podanie gołego
  `resourceUrl` daje mylące „Błąd podczas uaktualniania kolekcji za pomocą tego obrazu”,
  a w `fileCreate` kod `MISMATCHED_FILENAME_AND_ORIGINAL_SOURCE`, bo w adresie nie ma rozszerzenia.
- **Kolekcje nie przyjmują ID pliku, tylko adres URL** w `collectionUpdate(input: { image: { src } })`.
  Złożony adres staged działa wprost, bez pośredniego `fileCreate`.

Stare pliki zostają w Plikach jako osierocone: podmiana tworzy nowy plik, nie nadpisuje starego.

## Weryfikacja końcowa

Pobierz obrazki **z adresów, które serwuje sklep** (z wyrenderowanego HTML, z parametrem `width`),
i ponownie odczytaj rogi. Sprawdzanie plików lokalnych albo Admin API nie mówi nic o tym,
co dostaje przeglądarka klienta.

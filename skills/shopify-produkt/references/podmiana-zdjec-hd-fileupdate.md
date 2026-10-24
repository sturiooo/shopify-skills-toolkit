# Podmiana zdjęć produktów na wersje HD (sklep z herbatą, 19.10.2026)

Sytuacja: zdjęcia na kartach mają 800 px (przeniesione ze starej platformy), klient daje folder z „większymi wersjami”.

## Mechanizm, który nie rusza galerii

- **`fileUpdate(files:[{id: <MediaImage gid>, originalSource: <url ze stagedUploadsCreate>}])`** podmienia sam plik.
  Zostaje: id medium, pozycja w galerii, przypięcie do wariantu, ALT, nazwa pliku. Zmienia się tylko `?v=` w URL,
  więc odwołania `shopify://shop_images/<nazwa>` w szablonach JSON działają dalej.
- Format nowego pliku musi zostać taki jak obecny (nazwa pliku się nie zmienia): PNG zostaje PNG, WEBP zostaje WEBP.
- Przetestuj najpierw na tymczasowym produkcie DRAFT „ZZZ TEST”, potem usuń go.
- Cofnięcie: ten sam `fileUpdate` z plikami z backupu sprzed podmiany (katalog `przed/`).

NIE: `productDeleteMedia` + `productCreateMedia` (gubi kolejność, przypięcia do wariantów i odwołania w szablonach).

## Dopasowanie folderu klienta do zdjęć w sklepie

- Nazwy plików z Drive niczego nie mówią, dopasowuj wizualnie: dHash na miniaturach (`https://drive.google.com/thumbnail?id=<ID>&sz=w400`), potem plansze „obecne | nowe | różnica” oglądane na oko.
- Publiczny folder Drive listuje się bez logowania przez `https://drive.google.com/embeddedfolderview?id=<FOLDER>` (rekurencyjnie po podfolderach). Oryginał: `drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`.
- Zdjęcia w sklepie bywają wycinkami sesji: wytnij nowy plik z oryginału dokładnie w kadrze obecnego (dopasowanie korelacją), przeskaluj do 3000 px.
- Grafiki z napisem nałożonym na zdjęcie: nie podmieniaj (skasujesz tekst), do złożenia od nowa.

## Czego się spodziewać

Folder „wszystkie zdjęcia od klienta” to zwykle sesje, UGC i inspiracje, a nie packshoty. W tym sklepie z 87 plików
na kartach lepszą wersję miało 10. Od razu przygotuj listę produktów do dosłania oryginałów.

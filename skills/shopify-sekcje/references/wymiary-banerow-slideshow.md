# Wymiary banerów dla slideshow o stałej wysokości (2026-10-12, sklep z karmą dla psów, motyw z rodziny Horizon)

**Gdy sekcja ma stałą wysokość, a szerokość rośnie z ekranem, proporcja kadru zmienia się z każdym monitorem. Jeden plik „1920×1080” albo „2560×1000” zawsze gdzieś się obetnie (`object-fit: cover`).**

- **Najpierw odczytaj wysokość z kodu motywu, nie z oka.** Ten motyw (rodzina Horizon): `html{font-size:62.5%}`, więc 1rem = 10px; slideshow „large” = 62rem mobile (620px) i 75rem desktop (750px), niezależnie od szerokości. srcset obrazu sięga 3840.
- **Policz rozpiętość proporcji:** szerokość okna / wysokość sekcji. Przy 750px: laptop 1366 → 1,8:1, 1920 → 2,6:1, 2560 → 3,4:1. Na szerokim monitorze `cover` tnie górę i dół, na wąskim boki.
- **Specyfikacja dla grafika = kadr + strefa bezpieczna.** Daj jeden plik o proporcji ze środka zakresu (tu 2560×1000, Retina 3840×1500) i strefę bezpieczną dla najwęższego przypadku (tu 1820×1000 na środku). Wszystko ważne ma się zmieścić w strefie, reszta to tło do obcięcia.
- **Mobile osobnym plikiem**, jeśli motyw ma `image_mobile` w slajdzie (ten motyw ma). Tu 1200×1900, kluczowa treść w górnych 60%.
- **Bez tekstu w grafice.** Nagłówek, opis i przycisk idą z ustawień slajdu, inaczej tekst też się obetnie i nie przetłumaczy. Pliki JPG/WebP do ok. 1 MB.
- Grafikowi wysyłaj wszystko w jednej wiadomości (desktop, Retina, strefa, mobile, treści slajdów). Podawanie rozmiarów na raty kończy się trzema wersjami grafik.

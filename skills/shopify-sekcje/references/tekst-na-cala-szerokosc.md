# Tekst na całą szerokość kontenera (2026-10-18)

- **Nie dopasowuj skryptem po załadowaniu strony.** Zmiana `font-size` po doładowaniu fontu przesuwa wszystko pod nagłówkiem (zmierzone CLS 0,114). Dodatkowo `scrollWidth` elementu `display: block` = szerokość kontenera, więc pomiar „szerokości tekstu” na bloku nic nie daje (potrzebny `inline-block`).
- **Rozwiązanie w CSS:** rodzic `container-type: inline-size; overflow: hidden`, tekst `display: inline-block; white-space: nowrap; font-size: <k>cqw`.
- **Stałą k mierzysz raz:** szerokość tekstu przy `font-size: 100px` z załadowanym fontem (`document.fonts.ready`), k = 100 / szerokość × 100 cqw, z zapasem 0,1 do 0,2. Przykład: Archivo 850, `font-stretch: 112%`, `letter-spacing: -0.035em`, „IMIĘ NAZWISKO” (15 znaków) = 1007,8 px przy 100 px, więc `9.9cqw`.
- **Polskie znaki nad literą (Ń, Ś) obcina `overflow: hidden`** na wierszu z animacją wejścia liter: daj wierszowi `padding-top: .2em; margin-top: -.2em`.

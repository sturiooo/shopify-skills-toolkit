# Dopasowanie koloru z cudzego projektu do palety klienta (2026-08-20)

Klient przysyła zrzut z innego sklepu: „kafelki mają mieć swoje tło". **Nie kopiuj hexa**:
tło wzoru było `#f6f6f6` na **białym**, a docelowy sklep ma tło **kremowe** `#FDFDF7`; szary na
kremowym wygląda brudno. Przenoś **relację**, nie wartość:

```python
# zachowaj ten sam ODCIEŃ co tło docelowe i tę samą RÓŻNICĘ jasności co wzór
dl = (255 - 246) / 255                    # wzór: #ffffff -> #f6f6f6
nr, ng, nb = [max(0, c - round(dl * 255)) for c in (0xFD, 0xFD, 0xF7)]   # -> #F4F4EE
```
Odejmowanie równe na kanałach jest bezpieczniejsze niż konwersja przez HLS, obniżanie `L` przy
zachowanej saturacji **wzmacnia odcień** (u nas `#FDFDF7` → `#f9f9e9`, wyraźnie żółte).

**Kolor ze zrzutu pobieraj pomiarem, nie na oko.** Bez PIL: `sips --cropToHeightWidth H W
--cropOffset Y X` → dekompresja PNG (`zlib` + defiltering scanlinii Sub/Up/Average/Paeth) →
`collections.Counter` na pikselach.

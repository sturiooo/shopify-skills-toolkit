# Render mobile w headless Chrome: co mierzy, a czego nie (2026-10-18)

- **`--window-size=390,844` nie daje viewportu 390 px.** Zrzut wyglądał na stronę rozpychaną w bok (ucięty tekst z prawej), a strona była poprawna. Pomiar z emulacją: `Emulation.setDeviceMetricsOverride({ width: 390, height: 844, deviceScaleFactor: 1, mobile: true })`, potem `document.documentElement.scrollWidth` i lista elementów z `getBoundingClientRect().right > innerWidth`.
- **Elementy ukryte (`visibility: hidden`, np. zamknięte mega menu) też trafiają na listę „wystających”.** Nie powodują przewijania, ale zaśmiecają wynik: na mobile daj im `display: none`.
- **Narzędzia pomiarowe przez CDP** (emulacja dotyku, cele dotykowe, CLS, LCP) przyjmują zwykle tylko adresy `http(s)://`; plik lokalny serwuj przez `python3 -m http.server`.
- **Zrzuty wielu stron:** po kolei, nie równolegle (równoległe nie zapisały nic). Limit czasu na macOS: `perl -e 'alarm 35; exec @ARGV' chrome …`.
- **Banery cookies i popupy zasłaniają zrzut sklepu:** przez CDP usuń elementy `position: fixed` z tekstem cookie/zgod/prywatno/newsletter przed `Page.captureScreenshot` (krótki skrypt, wzór łatwo odtworzyć).

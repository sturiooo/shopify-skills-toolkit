# Praca na motywie LIVE i konflikty z edytorem: reguły potwierdzone w praktyce (2026-08)

### Osobny folder na motyw live i na roboczy
Motywy różnią się zwykle **tylko JSON-ami** (`settings_data.json`, `templates/*.json`), a pliki
`.liquid` bywają identyczne. Edytowanie plików z folderu motywu roboczego i wgrywanie ich na live
**cofa konfigurację z edytora**. Trzymaj `sklep-live/` i `sklep-roboczy/` osobno, a przed pracą
zrób `diff -rq` obu: od razu widać, co realnie się różni.

### Kolejność pushu przy zmianie schematu (twarda reguła)
**Najpierw sekcja (schemat), potem szablon JSON.** Odwrotna kolejność kończy się błędem
„Nieprawidłowa wartość dla typu w bloku …” albo cichym wycięciem nowych ustawień z template'u.
Po każdym pushu: `theme pull --only <plik>` + `diff` (pull-back), nie ufaj komunikatowi „success”.

### Klient zapisuje w edytorze → Twoje ID sekcji przestaje istnieć
Dwa razy w jednej sesji: sekcja wgrana przez CLI dostała po stronie klienta **nowe ID**
(usunął ją i dodał ponownie z edytora), a zmiany w ustawieniach przepadły. Dlatego:
- **kotwicz się po `type` sekcji, nigdy po własnym `id`**,
- **pull kontrolny pliku tuż przed pushem**: sprawdź, czy stan bazowy się nie zmienił,
- jeśli klient twierdzi, że coś wyłączył/zmienił, **potwierdź to w pobranym pliku** (raz „wyłączyłem
  blok apki” okazało się niezapisane i widget wyszedłby na produkcję podwójnie).

### Limity schematu, których Theme Check NIE łapie
- **`label` maks. 50 znaków, dotyczy też `label` w `options` selecta.** Dowiesz się dopiero z pushu
  („Invalid schema: … option Zbyt wiele znaków w label”).
- `name`/`presets[].name`/`blocks[].name` ≤ 25 znaków, `range` od 3 do 101 kroków, `default` na siatce,
  `range.max` < 10000.
- **Motywy Maestrooo mają trailing comma w swoim schemacie** (`},\n]`): Shopify to toleruje, `json.loads`
  nie. Waliduj tolerancyjnie: `json.loads(re.sub(r',(\s*[}\]])', r'\1', schema))`, a **nie „naprawiaj”** pliku.

### Który motyw pokazuje zrzut ekranu od klienta?
Zrzut „nie działa” potrafi pochodzić z **innego motywu** niż ten, na którym pracujesz (u nas: klient
patrzył na live, poprawka siedziała na roboczym). Zanim zaczniesz naprawiać: pobierz oba motywy
i porównaj konkretne pliki, albo zapytaj wprost, na którym motywie ogląda.

---

## Zmiana uchwytu kolekcji/produktu przepisuje szablony (potwierdzone 02.10.2026, sklep z pluszakami, motyw Concept)

- **Shopify po zmianie `handle` sam przepisuje w szablonach JSON ustawienia typu `collection`, `collection_list`, `product` i linki `shopify://collections/...`.** Nie rusza pól tekstowych: list uchwytów (`exclude_collections`, `highlight_handles`, `auto_exclude_handles`) ani ścieżek w polach `text`/`url`.
- Kolejność: zmień uchwyty (z `redirectNewHandle: true`), pobierz motyw NA NOWO, popraw tylko pola tekstowe, wgraj tylko te pliki. Push przygotowany na pobraniu sprzed zmiany uchwytów cofa poprawki Shopify.
- Po zmianie: przepnij cele istniejących przekierowań (`urlRedirectUpdate`), inaczej powstają łańcuchy.

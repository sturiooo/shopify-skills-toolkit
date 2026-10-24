# Cache storefrontu potrafi serwować KILKA różnych wersji naraz (2026-08-20, sklep z kawą funkcjonalną, motyw Stretch)

Po pushu `curl` zwracał na przemian trzy różne wersje strony głównej, w tym HTML z **ID sekcji
sprzed zmian** (`testimonials_slider_1` zamiast aktualnego) i treścią, której w szablonie już nie było.
Przez chwilę wyglądało to jak nadpisanie pracy klienta z edytora.

**Wnioski:**
- **`curl` bez sesji trafia w losowy węzeł CDN**; `?cb=` losuje URL, ale nie gwarantuje świeżości.
  Kolejne próby mogą wracać do STARSZEJ wersji niż poprzednia, to nie jest monotoniczne.
- **Rozstrzygający jest pull-back pliku z motywu przez Admin API**, nie HTML ze storefrontu.
  Renderu szukaj w **podglądzie edytora** (omija cache) albo w przeglądarce z sesją admina.
- **Zanim ogłosisz „ktoś nadpisał moje zmiany”, znajdź ID sekcji w podejrzanym HTML**
  (`shopify-section-template--<templateId>__<sectionId>`) i porównaj z aktualnym szablonem.
  U nas ID rozstrzygnęło sprawę w 10 sekund: to był cache sprzed pracy, nikt nic nie nadpisał.
- Lokalna kopia `templates/*.json` **rozjeżdża się z motywem** (ID sekcji zmienia się, gdy klient
  doda ją z edytora). **Buduj zmianę zawsze ze świeżo pobranego stanu**, nie z pliku na dysku,
  i kotwicz się po `type` sekcji, nie po `id`.

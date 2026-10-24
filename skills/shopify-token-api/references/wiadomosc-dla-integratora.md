# Wiadomość dla integratora (zwykły tekst, bez tabelki)

Podmień `<NAZWA SKLEPU>`, `<sklep>`, `<TOKEN>`, `<Twoje imię>`. Zakresy opisz słowami według tego, co faktycznie wydano.

---

Cześć,

przesyłam dostęp do API sklepu <NAZWA SKLEPU> dla systemu ofert.

Sklep: <sklep>.myshopify.com
Token: <TOKEN>

Token przekazujesz w nagłówku każdego zapytania:
X-Shopify-Access-Token: <TOKEN>

Adres GraphQL Admin API:
https://<sklep>.myshopify.com/admin/api/2026-07/graphql.json

Token nie wygasa, więc nie trzeba go odświeżać.

Uprawnienia (odczyt i zapis): produkty z wariantami, kolekcjami i cenami, stany magazynowe i lokalizacje, widoczność w kanałach sprzedaży, pliki i zdjęcia, tłumaczenia oraz metaobiekty.

Jeśli system będzie potrzebował czegoś więcej, na przykład zamówień, klientów albo zamówień roboczych (draft orders), daj znać, jakich dokładnie zakresów potrzebujesz. Rozszerzymy uprawnienia, ale wtedy wygeneruję nowy token, a ten trzeba będzie podmienić.

Token daje pełny dostęp do katalogu sklepu, więc trzymaj go tylko po stronie serwera i nie umieszczaj w kodzie dostępnym publicznie.

Pozdrawiam,
<Twoje imię>

---

Wersja API w adresie: aktualna stabilna (01.10.2026 = `2026-07`). Przy kolejnym użyciu sprawdź najnowszą.

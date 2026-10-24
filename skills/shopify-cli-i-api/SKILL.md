---
name: shopify-cli-i-api
description: "Workflow Shopify CLI przy wielu kontach (pull, push, przełączanie sklepów), scope'y i zaskakujące pola Admin API oraz praca na motywie LIVE równolegle z klientem w edytorze. Uruchamiaj przed pierwszym pullem nowego sklepu, przy błędach autoryzacji CLI, przy mutacjach Admin API i zawsze, gdy wgrywasz zmiany na motyw live."
---

# Shopify CLI i Admin API

Reguła nadrzędna przy pracy na live: **`pull` bezpośrednio przed pushem, buduj nową wersję z tego stanu, po pushu znowu `pull` i sprawdź konkretne klucze.** Zapis w edytorze motywu nadpisuje cały plik szablonu kopią z przeglądarki i potrafi wyciąć sekcję dodaną przez CLI.

## Co tu jest

Wczytuj pojedynczy plik referencyjny, nie cały katalog.

| Plik | Temat |
|---|---|
| `references/admin-api-scopey-i-pola.md` | Admin API: scope'y i pola, które zaskakują (2026-08); scalanie duplikatów produktów w warianty; składnia atrybucji ShopifyQL dla kanału AI. |
| `references/cli-workflow-wielu-kont.md` | Shopify CLI: workflow wielu kont, pull/push, Admin GraphQL bez aplikacji (2026-06). |
| `references/praca-na-motywie-live.md` | Praca na motywie LIVE i konflikty z edytorem: reguły potwierdzone w praktyce (2026-08); zmiana uchwytu przepisuje szablony. |

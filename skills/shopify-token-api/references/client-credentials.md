# Client credentials grant (token 24 h): tylko sklep w tej samej organizacji

Przerobione na integracji SellAsist ze sklepem klienta (08.2026).

```
POST https://<sklep>.myshopify.com/admin/oauth/access_token
{ "client_id": "...", "client_secret": "...", "grant_type": "client_credentials" }
→ { access_token, scope, expires_in: 86399 }
```

- Wymogi: apka i sklep w **tej samej organizacji** + apka **zainstalowana**. Inaczej `shop_not_permitted` / `app_not_installed`.
- **Token żyje 24 h.** Integrator przekazuje Client ID + secret i sam odnawia. Zapytaj, czy to umie; jeśli nie → stały token.
- Zakresy pochodzą z momentu instalacji. Po zmianie zakresów: nowa wersja + ponowna instalacja.
- Sklepy w organizacji agencji: `shopify store list`. Sklepy klientów, w których jesteś tylko współpracownikiem,
  tam NIE są i to normalne.
- Własne narzędzia agencji (migracje, skrypty) mogą używać tej drogi: apka w organizacji agencji, zainstalowana na sklepie
  z organizacji, token pobierany skryptem przy starcie.

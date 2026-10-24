# Domena „jest w Cloudflare”, ale nie ma jej na naszym koncie

Przypadek: sklep na motywie Sleek (domena `.pl`), 13.10.2026. W LH.pl serwery DNS `<ns-a1>` / `<ns-a2>.ns.cloudflare.com`,
a na koncie Cloudflare klienta widać tylko inną jego domenę.

## Para serwerów DNS identyfikuje konto

- **Cloudflare przydziela parę nameserwerów per konto.** Druga domena klienta = `<ns-b1>` / `<ns-b2>`, domena sklepu = `<ns-a1>` / `<ns-a2>`,
  więc to dwa różne konta, choć klient ten sam. Strefę domeny sklepu założył najpewniej poprzedni wykonawca sklepu Woo.
- Test bez logowania: `nslookup -type=NS <domena> 1.1.1.1` dla każdej domeny klienta i porównaj pary.
- Do tego LH.pl trzyma **równoległą, ślepą strefę** (`nslookup <domena> ns1.lh.pl` dał `<IP ślepej strefy>`), tak samo jak przy drugiej domenie klienta.
  Edycja w LH.pl nic nie zmieni, dopóki delegacja wskazuje Cloudflare.

## Recepta

1. Najpierw zapytaj o dostęp do tamtego konta (Members). Wtedy nic nie przenosisz.
2. Jeśli nikt nie wie, czyje to konto: na koncie klienta **Connect a domain** (nie „Transfer”, to przenosi rejestrację),
   plan Free, skan rekordów, porównanie z listą odczytaną z obecnej strefy, dopiero potem nowe NS w rejestratorze.
3. **Bez dostępu do starej strefy nie da się jej wyeksportować.** Odtwarzaj ją, odpytując znane nazwy na starym NS
   (`@`, `www`, `mail`, `smtp`, `imap`, `autoconfig`, `default._domainkey`, `_dmarc`, `send` dla Klaviyo itd.).
   **Wildcard `*` fałszuje wynik:** każda nieistniejąca nazwa (np. `kl._domainkey`) odpowiada adresem proxy, więc
   prawdziwy rekord poznasz po typie i wartości (CNAME, TXT), a nie po tym, że „coś odpowiada”.
4. **Nie łącz zmiany NS z przepięciem na Shopify.** Etap 1: nowa strefa odtwarza dzisiejszy stan (A na origin starego sklepu,
   pomarańczowa chmurka; origin sprawdź `curl --resolve <domena>:443:<ip> -k`), zmiana NS jest wtedy niewidoczna. Etap 2: Shopify.

Listę odtworzonych rekordów zapisz w notatkach projektu, zanim zmienisz NS.

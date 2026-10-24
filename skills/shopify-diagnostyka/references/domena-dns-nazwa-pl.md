# Domena Shopify w DNS nazwa.pl: weryfikacja GSC, parking zamiast sklepu, cache routera

Przypadek: sklep z obuwiem skórzanym (motyw Prestige, domena `example.com`), 12.10.2026. Sklep wyglądał na działający, a dla świata pokazywał parking nazwa.pl.

## Diagnoza: zawsze pytaj serwer autorytatywny, nie swój komputer

- **Lokalny wynik kłamie w obie strony.** Rano mój komputer dostawał 23.227.38.65 (Shopify) z cache,
  a `ns1.nazwa.pl`, 8.8.8.8 i 1.1.1.1 już 85.128.128.104 (parking). Po naprawie było odwrotnie:
  świat widział Shopify, a router Linksys (192.168.1.1) dalej parking. `ipconfig /flushdns` nie pomaga,
  bo Windows pyta router.
- **Kolejność sprawdzania:** `nslookup <domena> ns1.nazwa.pl` (prawda) → 8.8.8.8 i 1.1.1.1 (świat) →
  `nslookup <domena>` bez serwera (to, co widzi klient z Twojej sieci). Treść bez zależności od DNS:
  `curl --resolve <domena>:443:23.227.38.65 https://<domena>/`.
- **Strona parkingowa nazwa.pl:** `<title>Domena X jest utrzymywana na serwerach nazwa.pl</title>` + ramka
  `blackdown.nazwa.pl`. Odpowiada 200, więc samo sprawdzenie kodu HTTP niczego nie wykryje.
- **Status w Shopify (Ustawienia → Domeny) bywa spóźniony**: „Nie wykryto rekordów / Domena nie jest
  aktywna”, gdy autorytatywny DNS już jest dobry. Odczekaj i „Zweryfikuj połączenie”.

## Format rekordów w „Ręcznej konfiguracji DNS” nazwa.pl

- **Nazwa = pełna domena**, nie `@` i nie sam prefiks: `example.com`, `www.example.com`.
  Wpisanie `gsc` jako nazwy TXT dało rekord na `gsc.example.com` i GSC zgłosił
  „Nie udało nam się znaleźć Twojego tokenu… znaleźliśmy: v=spf1 mx a ~all”.
- **CAA:** wartość z flagą, tagiem i cudzysłowem: `0 issue "pki.goog; cansignhttpexchanges=yes"`.
  Samo `pki.goog…` przy nazwie `@` = status „błąd” w historii operacji.
- **CNAME `www` → `shops.myshopify.com` dwa razy odrzucony** (status „błąd”). Działa A
  `www.<domena>` → `23.227.38.65`; Shopify oznacza www jako „Połączona”, SSL wystawiony.
- **CAA wymagane przez Shopify** (panel domeny Shopify pokazuje braki): letsencrypt.org, globalsign.com,
  pki.goog, ssl.com. nazwa.pl domyślnie ma tylko certum.pl i letsencrypt.org.
- Zmiany mają w historii status „wykonany” / „błąd”; po „wykonany” sprawdź `ns1.nazwa.pl`, serial SOA rośnie.

## Pułapki, które psują coś obok

- **MX `10 <domena>` wskazuje na rekord A domeny.** Przestawienie A na Shopify przestawia też pocztę
  przychodzącą na Shopify (który poczty nie przyjmuje). Zanim zmienisz A: sprawdź, gdzie jest skrzynka.
  Tu poczty i tak nie było (konto nazwa.pl tylko z domenami, porty 465/587/993 na 85.128.128.104 zamknięte,
  kontrolnie Gmail z tej samej sieci odpowiadał), więc zmiana niczego nie pogorszyła. **Korekta 20.10:** klient zgłosił, że poczta nie dochodzi. Test portów logowania nie dowodzi braku poczty (serwer może przyjmować na porcie 25 i przekierowywać), a portu 25 z domowej sieci nie sprawdzisz. Przed zmianą A przenieś pocztę na host: A `mail.<domena>` → stare IP, MX → `mail.<domena>`. **Druga korekta 20.10 wieczorem:** ta recepta była błędna, bo „stare IP” 85.128.128.104 to parking nazwa.pl, nie serwer poczty. Skrzynki klienta były w **home.pl** (`<serwer>.home.pl` = `<IP serwera poczty>`, IMAP 993 i SMTP 465 otwarte), co wyszło dopiero ze zrzutu ustawień Outlooka od klienta. Naprawa: MX `10 <serwer>.home.pl`, usunąć A `mail.<domena>`, SPF `v=spf1 mx ip4:<IP serwera> include:shops.shopify.com ~all`. **Recepta:** zanim wskażesz serwer poczty, zapytaj klienta o host IMAP/SMTP z jego programu pocztowego (albo zrzut konta w Outlooku) i sprawdź ten host, a stare A domeny traktuj jako podejrzane, dopóki nie zobaczysz na nim otwartego 993.
- **Wildcard `*` A na parking** łapie `www` i każdą literówkę subdomeny; usunąć, `www` dodać jawnie.
- **Ten sam właściciel ma zwykle kilka TLD** (.com/.pl/.eu): każda to osobna strefa. Shopify może mieć
  domenę podpiętą („Nieprawidłowy DNS”), a DNS dalej na parkingu.

## Recepta dla domeny Shopify w nazwa.pl

1. A `<domena>` → 23.227.38.65, A `www.<domena>` → 23.227.38.65, usuń `*`.
2. CAA: dopisz `0 issue "globalsign.com"`, `0 issue "pki.goog; cansignhttpexchanges=yes"`, `0 issue "ssl.com"`.
3. MX/SPF/DKIM i TXT weryfikacyjne zostaw; jeśli poczta ma działać, MX na hosta dostawcy poczty.
4. Weryfikacja: `ns1.nazwa.pl`, 1.1.1.1, `curl --resolve`, Shopify → Domeny „Połączona”.

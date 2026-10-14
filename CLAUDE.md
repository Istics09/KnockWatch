# knockwatch

Saját behatolásfigyelő és automatikus tiltó eszköz Linux szerverekre (fail2ban-szerű, de több szerver között megosztott tiltólistával). Publikus GitHub-projekt, portfólió célra.

## Cél és ütemterv

1. **SSH** – `/var/log/auth.log` figyelése, IP-nkénti pontozás, tiltás. ← *jelenlegi fázis*
2. **Valós idejű futás** – napló folyamatos követése (tail / journald), daemon + systemd service.
3. **Megosztás 3 szerver között** – ha bármelyik tilt/felold, a másik kettő is alkalmazza (peer-to-peer HTTP API, megosztott tokennel, csak a VPN-címen figyelve).
4. **Port scan** – `kern.log` alapján (előfeltétel: nftables LOG szabály az eldobott csomagokra). Jel: egy IP sok különböző portra, rövid idő alatt.
5. **Web** – nginx access.log: dirbusting (sok 404, wordlist-útvonalak, gobuster/dirb user-agent) és scraping (kérésgyakoriság).
6. **Csomagolás** – Docker, systemd, GitHub Actions (tesztek), README.

## Architektúra

```
knockwatch/
├── core/
│   ├── duration.py   # "30d", "1mo", "perm" → másodperc; to_nft()
│   ├── db.py         # SQLite bans tábla (ip, reason, origin_node, created_at, expires_at)
│   └── event.py      # közös Event (timestamp, source_ip, type, details) – TODO
├── parsers/          # naplóforrásonként egy parser → Event-eket ad (yield) – TODO
├── detectors/        # Event-ekből döntés (ssh, portscan, web) – TODO
├── actions/
│   └── firewall.py   # nftables wrapper: setup / ban / unban, dry-run
├── cli.py            # ban / unban / list alparancsok – TODO
├── main.py           # TODO
├── samples/          # csak anonimizált minta-naplók
└── tests/
```

Alapelv: a parserek a nyers naplót közös `Event` objektummá alakítják, a detektorok csak Event-eket látnak. Új naplóforrás = új parser + új detektor, a mag nem változik.

## Kész

- `core/duration.py` + tesztek (egységek: s, m, h, d, w, mo=30d, y=365d, perm)
- `core/db.py` + tesztek (add_ban INSERT OR REPLACE, remove_ban, list_active)
- `actions/firewall.py` + tesztek (saját `inet knockwatch` tábla, `banned` set `flags timeout`-tal)

## Tervezési döntések

- Tiltás lejárata: az nftables set beépített timeoutja kezeli. Az nft csak napig ismer egységet → hónap/év napra váltva (`to_nft`).
- Újraindításkor az nft set kiürül → induláskor a `list_active()` alapján vissza kell tölteni a hátralévő idővel.
- Alapértelmezett automatikus tiltás: 30 nap.
- CLI időtartamok: perc, óra, nap, hét, hónap, év, perm (`m`=perc, `mo`=hónap).
- Egyelőre csak IPv4; IPv6 később külön settel.
- A 3 saját szerver IP-je fix whitelist – soha nem tilthatók.
- `nft` hiánya vagy nem-root futás esetén `FirewallError` érthető üzenettel (telepítési utasítás).

## Biztonsági szabályok (kötelező)

- Tűzfalat érintő kódot **először mindig `dry_run=True`-val** futtass.
- Éles teszthez csak dokumentációs IP-t használj (pl. `203.0.113.5`), soha ne a felhasználó vagy a szerverek IP-jét.
- Ne futtass `nft flush ruleset`-et és ne nyúlj a `knockwatch` táblán kívüli szabályokhoz.
- Vészkijárat: `nft delete table inet knockwatch`.
- Valódi naplók és adatbázis nem kerülhetnek gitbe (`data/`, `*.db` a `.gitignore`-ban).

## Kódolási konvenciók

- Python 3.12, csak standard library, ahol lehet.
- SQL-ben mindig `?` helyőrző, soha f-string.
- `subprocess`-nek mindig lista, soha `shell=True`.
- Felhasználónak szóló üzenetek magyarul.
- Minden új modulhoz teszt a `tests/` mappában; a parancsokat összerakó függvények legyenek tisztán tesztelhetők (subprocess nélkül).

## Parancsok

```
python3 -m pytest                       # tesztek
nft list set inet knockwatch banned     # aktív tiltások a tűzfalon
```

## Munkamód

- A projekt tanulási célú is: minden változtatás után röviden magyarázd el, mit és miért csináltál.
- Kis lépésekben haladj; minden lépés végén futnak a tesztek, utána commit.
- Döntést igénylő kérdésnél (pl. szinkron protokoll, küszöbértékek) kérdezz, ne találgass.
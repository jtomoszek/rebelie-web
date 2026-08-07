# Co je potřeba dodat od Pavly

Web je hotový a funkční, ale **všechny texty, ceny, kontakty a ocenění jsou
zatím vymyšlené**. Slouží jako rozvržení — aby bylo vidět, kolik textu se kam
vejde a v jakém tónu je psaný. Níž je přesný seznam toho, co dodat.

Formát je jednoduchý: ke každé položce je uvedeno, kde v webu sedí,
kolik textu se tam vejde a co tam teď stojí za výplň.

---

## 1. Kontaktní údaje — NEJVYŠŠÍ PRIORITA

Bez těchto údajů web nemůže jít ven. Vyskytují se v patičce **všech stránek**
a na `kontakt.html`.

| Údaj | Teď na webu (vymyšlené) |
|---|---|
| E-mail | `ahoj@rebelie.art` |
| Telefon | `+420 000 000 000` |
| Odkaz na Instagram | prázdný odkaz |
| Odkaz na Facebook | prázdný odkaz |
| Město / ateliér | „Ostrava" |
| IČO, případně sídlo pro fakturaci | není nikde |

> Až budou k dispozici, stačí je najít a nahradit ve všech `.html` souborech —
> jsou zapsané pokaždé stejně.

---

## 2. Ocenění — `oceneni.html`

Tohle byl výslovný požadavek, takže je na to samostatná stránka i ukázka na
homepage. **Aktuálně je tam 13 vymyšlených položek.**

Prosím dodat ve formátu, jeden řádek na ocenění:

```
rok · název soutěže nebo výstavy · místo konání a kategorie · umístění
```

Například:

```
2024 · World Bodypainting Festival · Klagenfurt, kategorie Brush & Sponge · 3. místo
2023 · Mistrovství ČR v bodypaintingu · Ostrava, kategorie Special Effects · 1. místo
```

- Vejde se jich klidně **30 a víc**, sekce je na to připravená.
- Hodí se i **fotky oceněných děl** a diplomů — je pro ně místo v sekci
  „Soutěžní tvorba" ve spodní části stránky.
- Na homepage a na stránce „O mně" je uvedeno **„15+ ocenění"** — až bude
  znám skutečný počet, upravit i tam.

---

## 3. Ceny — na všech třech stránkách kategorií

Ceny jsou **odhad, ne skutečnost**. Je potřeba je projít a opravit,
nebo mi říct, ať je vyhodím úplně (řada umělců ceny na webu nemá).

| Kde | Položka | Teď uvedeno |
|---|---|---|
| bodypainting | festivaly a eventy | od 12 000 Kč / den |
| bodypainting | focení a videoklipy | od 6 500 Kč |
| bodypainting | firemní akce a veletrhy | na míru |
| bodypainting | svatby a oslavy | od 4 500 Kč |
| oblečení | džínová bunda / křivák | od 3 500 Kč |
| oblečení | sako a kabát | od 4 500 Kč |
| oblečení | trika, mikiny, šaty | od 1 800 Kč |
| oblečení | tenisky a doplňky | od 1 500 Kč |
| obrazy | hotový obraz z galerie | od 4 500 Kč |
| obrazy | portrét na míru | od 8 000 Kč |
| obrazy | malba do dřeva | od 2 500 Kč |

Stejně tak **doby realizace** (2–6 hodin u bodypaintingu, 7–21 dní
u oblečení, 3–6 týdnů u obrazu) jsou odhadem.

---

## 4. Fakta o Pavle

Objevují se v číslech na homepage i na stránce „O mně".

| Údaj | Teď na webu | 
|---|---|
| Roky praxe | 12 |
| Počet realizací | 400+ |
| Počet ocenění | 15+ |
| Rok první soutěže | 2014 |
| Působiště | Ostrava, celá ČR i zahraničí |

---

## 5. Texty — volitelné

Texty jsou napsané tak, aby dávaly smysl a šly rovnou použít. Ale jsou psané
za Pavlu, ne Pavlou. Pokud si je bude chtít přepsat vlastními slovy, jde
hlavně o tyhle:

- **Úvodní odstavec na homepage** (~40 slov) — „Kůže, textil, plátno…"
- **Životopisná část na `o-mne.html`** (2 × ~70 slov) — „Tři povrchy,
  jeden rukopis" a „Jak jsem se k tomu dostala"
- **Úvod ke každé kategorii** (~110 slov na stránku)
- **Popisy jednotlivých služeb** (~30 slov každý)
- **Časté dotazy na `kontakt.html`** (5 otázek) — hlavně ty o bezpečnosti
  barev a praní; tam je potřeba, aby odpovídaly skutečnosti

---

## 6. Fotky

### Malba na oblečení — CHYBÍ NEJVÍC

V podkladech byly použitelné jen **4 fotky** malovaného oblečení, a dvě z nich
jsou tatáž džínová bunda ze stejného úhlu. Galerie na `obleceni.html` je proto
výrazně slabší než ostatní dvě — a přitom jde o jednu ze tří hlavních služeb.

**Prosím o 10–15 dalších fotek**, ideálně:
- hotový kus na figuríně nebo na člověku
- jednobarevné nebo klidné pozadí
- zepředu i zezadu
- k tomu pár detailů malby zblízka

### Ostatní kategorie

- **Bodypainting** — 55 fotek, bohatě stačí ✅
- **Obrazy** — 22 fotek ✅

### Doporučené doladění

Ve složce obrazů je pár snímků, které působí spíš jako soukromé fotky než jako
portfolio (např. `ob-03` u vánočního stromku). Stojí za zvážení je vyřadit —
stačí smazat soubor z `img/obrazy/` i z `img/obrazy/thumb/` a spustit
`python3 build-galerie.py`.

### Fotka Pavly

Na homepage i na stránce „O mně" je použitá fotka z ateliéru (`ob-04`).
Není to portrét, je na ní celá postava u stojanu. Pokud existuje pořádný
portrét, bude fungovat líp.

---

## 7. Ještě k zvážení

- **Prodej obrazů** — teď je to poptávka e-mailem. Pokud by měl web obrazy
  přímo prodávat, dá se doplnit ceník s rozměry u každého díla, případně
  jednoduchý e-shop.
- **Reference / recenze klientů** — silně by pomohly u bodypaintingu.
  Stačilo by 3–5 krátkých citací se jménem a typem akce.
- **Ochrana osobních údajů** — pokud bude formulář odesílat data přes
  externí službu, patří na web krátká stránka o zpracování údajů.
- **Anglická verze** — u mezinárodních soutěží a festivalů by dávala smysl.

---

## Kde co v kódu najít

Všechny vymyšlené údaje, které je potřeba nahradit, jsou v HTML souborech.
Vyhledáním následujícího si je snadno projdete:

| Hledat | Co to je |
|---|---|
| `ahoj@rebelie.art` | e-mail (všechny stránky) |
| `+420 000 000 000` | telefon (všechny stránky) |
| `instagram.com/` | odkazy na sociální sítě |
| `class="award"` | jednotlivá ocenění |
| `class="svc__price"` | ceny |
| `class="stat__num"` | čísla (12 let, 15+, 400+) |
| `class="todo"` | dvě dočasné poznámky přímo ve webu — **před spuštěním smazat** |

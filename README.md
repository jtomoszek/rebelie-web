# REBELIE — web Pavly Hanouskové

Statický web (čisté HTML, CSS a JavaScript). Žádný build, žádné závislosti,
žádný Node.js. Soubory jde otevřít dvojklikem nebo nahrát na libovolný hosting.

Vizuál vychází ze šablony [Anderdark](https://anderdark-template.webflow.io/about) —
tmavé pozadí, obří groteskní nadpisy, monospace popisky, tenké linky.
Akcentní barva je růžová z logotypu značky (`#FF00F5`) — jediná růžová
na celém webu.

---

## Struktura

```
web/
├── index.html            Domovská stránka
├── o-mne.html            O mně (podle šablony /about)
├── bodypainting.html     Živé plátno — bodypainting
├── obleceni.html         Nositelná rebelie — malba na oblečení
├── obrazy.html           Věčné plátno — obrazy
├── oceneni.html          Ocenění a soutěže
├── kontakt.html          Kontakt a poptávkový formulář
│
├── css/style.css         Veškerý vzhled (barvy a rozestupy nahoře v :root)
├── js/main.js            Menu, lightbox, animace, dopočet velikosti nadpisů
├── assets/               Loga ve formátu SVG
├── img/                  Fotky připravené pro web (velké verze + náhledy)
│
├── pripravit-fotky.sh    Převede a zmenší originály do img/
├── build-galerie.py      Vygeneruje galerie na podstránkách podle img/
└── OBSAH.md              Co je potřeba dodat od klientky
```

---

## Jak si web prohlédnout

Nejjednodušší je otevřít `index.html` v prohlížeči. Pokud by nešly načíst
fotky, spusťte místní server:

```bash
python3 -m http.server 8000
```

Pak otevřete `http://localhost:8000`.

---

## Jak přidat nové fotky

Kompletní postup, například pro malbu na oblečení:

**1. Originály** nahrajte do `Fofo Rebelie/Textil/`. Pojmenujte je
`Rebelie textil 5.jpg`, `Rebelie textil 6.jpg` atd. — číslo v názvu určuje pořadí.

**2. Připravte je pro web** (ze složky `web/`):

```bash
./pripravit-fotky.sh "../Fofo Rebelie/Textil" textil tx
```

**3. Vygenerujte galerie:**

```bash
python3 build-galerie.py
```

Hotovo. Skripty jde spouštět opakovaně — pokaždé přepíšou předchozí výsledek.

Pro ostatní kategorie:

```bash
./pripravit-fotky.sh "../Fofo Rebelie/Body painting" bodypainting bp
./pripravit-fotky.sh "../Fofo Rebelie/Art"           obrazy       ob
```

### Odebrání jedné fotky

Smažte ji z `img/<kategorie>/` i z `img/<kategorie>/thumb/`
a spusťte `python3 build-galerie.py`.

---

## Poptávkový formulář

Formulář v `kontakt.html` zatím jen otevře e-mailového klienta (`mailto:`).
Funguje všude, ale není to elegantní. Pro odesílání přímo z webu stačí
zaregistrovat některou bezplatnou službu a upravit dva atributy:

```html
<!-- původně -->
<form class="form" action="mailto:ahoj@rebelie.art" method="post" enctype="text/plain">

<!-- například s Formspree -->
<form class="form" action="https://formspree.io/f/VAS_KOD" method="POST">
```

Osvědčené služby: [Formspree](https://formspree.io),
[Web3Forms](https://web3forms.com), [Formcarry](https://formcarry.com).
Všechny mají zdarma tarif, který na tenhle web bohatě stačí.

---

## Nasazení

Web je statický, takže funguje kdekoliv:

- **Netlify / Vercel** — přetáhněte složku `web/` do okna prohlížeče, hotovo
- **GitHub Pages** — nahrajte obsah `web/` do repozitáře a zapněte Pages
- **Klasický FTP hosting** — nakopírujte obsah `web/` do `www/` nebo `public_html/`

Nasazuje se **obsah složky `web/`**, ne složka samotná — `index.html`
musí skončit v kořeni webu.

---

## Úpravy vzhledu

Všechny barvy, rozestupy a písma jsou pohromadě na začátku `css/style.css`
v bloku `:root`. Změna akcentní barvy na celém webu je jeden řádek:

```css
--pink: #ff00f5;
```

Nadpisy v hlavičkách stránek se dopočítávají JavaScriptem tak, aby přesně
vyplnily šířku sloupce (`data-fit` v HTML). Bez JavaScriptu se použije
záložní velikost z CSS, takže se nic nerozbije.

---

## Co ještě chybí

Viz **[OBSAH.md](OBSAH.md)** — seznam údajů a textů, které je potřeba dodat
od Pavly, než web půjde spustit naostro.

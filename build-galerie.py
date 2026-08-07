#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vygeneruje obsah galerií na stránkách bodypainting.html, obleceni.html a obrazy.html
podle obrázků ve složkách web/img/<kategorie>/.

Použití (ze složky web/):
    python3 build-galerie.py

Až přibudou nové fotky:
    1. nahrajte je do web/img/<kategorie>/  (velká verze, max 1800 px)
    2. vytvořte zmenšený náhled do web/img/<kategorie>/thumb/ (max 900 px)
       — o obojí se postará skript pripravit-fotky.sh
    3. spusťte tento skript znovu

Skript je opakovaně spustitelný: dřívější vygenerovanou galerii přepíše.
"""

import os
import re
import struct
import sys

# kategorie -> (složka s obrázky, cílová stránka, popisek pro alt text)
KATEGORIE = [
    ("bodypainting", "bodypainting.html", "Bodypainting od Pavly Hanouskové"),
    ("textil",       "obleceni.html",     "Ručně malované oblečení od Pavly Hanouskové"),
    ("obrazy",       "obrazy.html",       "Obraz od Pavly Hanouskové"),
]

ZDE = os.path.dirname(os.path.abspath(__file__))


def rozmery_jpeg(cesta):
    """Přečte šířku a výšku JPEGu bez externích knihoven."""
    with open(cesta, "rb") as f:
        if f.read(2) != b"\xff\xd8":
            return None
        while True:
            bajt = f.read(1)
            while bajt and bajt != b"\xff":
                bajt = f.read(1)
            while bajt == b"\xff":
                bajt = f.read(1)
            if not bajt:
                return None
            znacka = bajt[0]
            # SOF0–SOF15 kromě DHT (c4), DAC (cc) a RSTn (d0–d7)
            if 0xC0 <= znacka <= 0xCF and znacka not in (0xC4, 0xC8, 0xCC):
                f.read(3)  # délka (2 B) + přesnost (1 B)
                vyska, sirka = struct.unpack(">HH", f.read(4))
                return sirka, vyska
            delka = struct.unpack(">H", f.read(2))[0]
            f.seek(delka - 2, os.SEEK_CUR)


def blok_galerie(kategorie, popisek):
    slozka = os.path.join(ZDE, "img", kategorie)
    if not os.path.isdir(slozka):
        print("  ! chybí složka %s" % slozka)
        return "", 0

    soubory = sorted(f for f in os.listdir(slozka) if f.lower().endswith(".jpg"))
    radky = []

    for soubor in soubory:
        jmeno = os.path.splitext(soubor)[0]
        velka = "img/%s/%s" % (kategorie, soubor)
        nahled = "img/%s/thumb/%s" % (kategorie, soubor)

        if not os.path.exists(os.path.join(ZDE, nahled)):
            nahled = velka  # náhled chybí, použije se velká verze

        rozmer = rozmery_jpeg(os.path.join(ZDE, nahled))
        atributy = ' width="%d" height="%d"' % rozmer if rozmer else ""

        radky.append(
            '      <a class="gallery__item" href="%s" data-lightbox data-full="%s" title="%s">\n'
            '        <img src="%s" alt="%s — %s"%s loading="lazy">\n'
            '      </a>' % (velka, velka, jmeno, nahled, popisek, jmeno, atributy)
        )

    return "\n".join(radky), len(soubory)


def zapis(kategorie, stranka, popisek):
    cesta = os.path.join(ZDE, stranka)
    if not os.path.exists(cesta):
        print("  ! chybí stránka %s" % stranka)
        return

    with open(cesta, encoding="utf-8") as f:
        obsah = f.read()

    blok, pocet = blok_galerie(kategorie, popisek)
    znacka = "<!--GALERIE:%s-->" % kategorie
    novy = (blok + "\n      " + znacka) if blok else znacka

    # Nahradí všechno mezi <div class="gallery"> a značkou — díky tomu
    # lze skript spouštět opakovaně.
    vzor = re.compile(
        r'(<div class="gallery">\n)(?:.*?)(\s*)' + re.escape(znacka),
        re.DOTALL,
    )
    if vzor.search(obsah):
        obsah = vzor.sub(lambda m: m.group(1) + novy, obsah)
    else:
        print("  ! ve stránce %s chybí značka %s" % (stranka, znacka))
        return

    with open(cesta, "w", encoding="utf-8") as f:
        f.write(obsah)

    print("  %-20s %2d fotek" % (stranka, pocet))


def main():
    print("Generuji galerie…")
    for kategorie, stranka, popisek in KATEGORIE:
        zapis(kategorie, stranka, popisek)
    print("Hotovo.")


if __name__ == "__main__":
    sys.exit(main())

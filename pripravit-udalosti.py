#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Připraví fotky výstav a soutěží pro web.

Projde složky ve „Fofo Rebelie/Výstavy a soutěže", každou z nich převede
a zmenší do web/img/udalosti/<slug>/ a vedle toho vytvoří soubor
web/data/udalosti.json s přehledem akcí.

Použití (ze složky web/):
    python3 pripravit-udalosti.py

Až přibude nová akce:
    1. Založte složku „Název akce ROK" ve „Fofo Rebelie/Výstavy a soutěže"
    2. Fotky pojmenujte „Název akce ROK 1.jpg", „… 2.jpg" atd.
    3. Spusťte tento skript a pak build-udalosti.py

Rok se bere z názvu složky. Co v názvu není, skript si nevymýšlí –
typ akce ani místo konání se doplňují ručně v udalosti.json.

Používá jen `sips`, který je součástí macOS. Videa (.mp4) se přeskakují.
"""

import json
import os
import re
import subprocess
import sys
import unicodedata

ZDE = os.path.dirname(os.path.abspath(__file__))
ZDROJ = os.path.join(ZDE, "..", "Fofo Rebelie", "Výstavy a soutěže")
CIL = os.path.join(ZDE, "img", "udalosti")
DATA = os.path.join(ZDE, "data", "udalosti.json")

VELKA_MAX = 1400   # delší strana velké verze (px)
NAHLED_MAX = 600   # delší strana náhledu (px)
PRIPONY = (".jpg", ".jpeg", ".png", ".heic")

# Typ akce se odvozuje jen tam, kde je jednoznačný z názvu složky.
# Zbytek zůstane prázdný – doplní se ručně, nic se nedomýšlí.
TYPY = [
    (r"mistrovstv[íi]",       "Soutěž"),
    (r"v[ýy]stava|zámeček",   "Výstava"),
    (r"festival|fest\b",      "Festival"),
    (r"slavnosti",            "Slavnosti"),
    (r"otevřen[íi]",          "Firemní akce"),
]

# Místo konání se bere jen tehdy, je-li přímo v názvu složky.
MISTA = [
    (r"praha",        "Praha"),
    (r"kopřivnice",   "Kopřivnice"),
    (r"poruba",       "Ostrava-Poruba"),
    (r"ostravice",    "Ostravice"),
    (r"nov[éeě]ho jičína", "Nový Jičín"),
    (r"ostrava",      "Ostrava"),
    (r"slovenska",    "Slovensko"),
]


def slug(text):
    """Název složky → bezpečný název pro adresář a odkaz."""
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


def cislo_v_nazvu(jmeno):
    """Vytáhne pořadové číslo ze jména souboru kvůli řazení."""
    m = re.findall(r"(\d+)(?=\.[A-Za-z]+$)", jmeno)
    return int(m[0]) if m else 0


def sips(*args):
    return subprocess.run(["sips"] + list(args),
                          capture_output=True, text=True).stdout


def rozmery(cesta):
    out = sips("-g", "pixelWidth", "-g", "pixelHeight", cesta)
    w = re.search(r"pixelWidth:\s*(\d+)", out)
    h = re.search(r"pixelHeight:\s*(\d+)", out)
    return (int(w.group(1)), int(h.group(1))) if w and h else None


def poznatky_z_nazvu(nazev):
    """Rok, typ a místo – jen to, co je opravdu v názvu složky."""
    # macOS ukládá názvy souborů v rozloženém tvaru (NFD): „ý" je „y"
    # plus samostatný háček. Bez převodu na NFC by regexy s diakritikou
    # nikdy nesedly.
    nazev = unicodedata.normalize("NFC", nazev)
    rok = None
    m = re.search(r"\b(19|20)\d{2}\b", nazev)
    if m:
        rok = int(m.group(0))

    maly = nazev.lower()
    typ = next((t for vzor, t in TYPY if re.search(vzor, maly)), "")
    misto = next((m for vzor, m in MISTA if re.search(vzor, maly)), "")

    # čistý název: bez roku a bez osamocených pomlček
    cisty = re.sub(r"\b(19|20)\d{2}\b", "", nazev)
    cisty = re.sub(r"\s*-\s*$", "", cisty.strip())
    cisty = re.sub(r"\s*-\s*", " – ", cisty)
    cisty = re.sub(r"\s{2,}", " ", cisty).strip(" –")

    return rok, typ, misto, cisty


def zpracuj_slozku(cesta_slozky, nazev, jen_data=False):
    s = slug(nazev)
    ven = os.path.join(CIL, s)
    os.makedirs(os.path.join(ven, "thumb"), exist_ok=True)

    if jen_data:
        # Fotky už jsou hotové, jen se znovu poskládá přehled.
        hotove = sorted(f for f in os.listdir(ven) if f.endswith(".jpg"))
        fotky = []
        for jmeno in hotove:
            rv = rozmery(os.path.join(ven, jmeno)) or (0, 0)
            fotky.append({"soubor": jmeno, "sirka": rv[0], "vyska": rv[1]})
        rok, typ, misto, cisty = poznatky_z_nazvu(nazev)
        return {
            "slug": s, "nazev": cisty, "rok": rok, "typ": typ,
            "misto": misto, "umisteni": "", "popis": "",
            "slozka": unicodedata.normalize("NFC", nazev), "fotky": fotky,
        }

    for stary in os.listdir(ven):
        if stary.endswith(".jpg"):
            os.remove(os.path.join(ven, stary))
    for stary in os.listdir(os.path.join(ven, "thumb")):
        if stary.endswith(".jpg"):
            os.remove(os.path.join(ven, "thumb", stary))

    soubory = [f for f in os.listdir(cesta_slozky)
               if f.lower().endswith(PRIPONY)]
    soubory.sort(key=cislo_v_nazvu)

    fotky = []
    for i, f in enumerate(soubory, 1):
        zdroj = os.path.join(cesta_slozky, f)
        jmeno = "%s-%02d.jpg" % (s, i)
        velka = os.path.join(ven, jmeno)
        nahled = os.path.join(ven, "thumb", jmeno)

        rz = rozmery(zdroj)
        if not rz:
            print("    ! nelze přečíst: %s" % f)
            continue
        delsi = max(rz)

        if delsi > VELKA_MAX:
            sips("-s", "format", "jpeg", "-s", "formatOptions", "70",
                 "-Z", str(VELKA_MAX), zdroj, "--out", velka)
        else:
            sips("-s", "format", "jpeg", "-s", "formatOptions", "76",
                 zdroj, "--out", velka)

        if delsi > NAHLED_MAX:
            sips("-s", "format", "jpeg", "-s", "formatOptions", "64",
                 "-Z", str(NAHLED_MAX), velka, "--out", nahled)
        else:
            subprocess.run(["cp", velka, nahled])

        rv = rozmery(velka) or (0, 0)
        fotky.append({"soubor": jmeno, "sirka": rv[0], "vyska": rv[1]})

    rok, typ, misto, cisty = poznatky_z_nazvu(nazev)
    return {
        "slug": s,
        "nazev": cisty,
        "rok": rok,
        "typ": typ,
        "misto": misto,
        "umisteni": "",          # doplní Pavla – nic si nevymýšlíme
        "popis": "",             # volitelný krátký text k akci
        "slozka": unicodedata.normalize("NFC", nazev),
        "fotky": fotky,
    }


def main():
    if not os.path.isdir(ZDROJ):
        print("Nenašel jsem složku: %s" % ZDROJ)
        return 1

    os.makedirs(CIL, exist_ok=True)
    os.makedirs(os.path.dirname(DATA), exist_ok=True)

    jen_data = "--jen-data" in sys.argv
    if jen_data:
        print("Režim --jen-data: fotky se nepřepočítávají.\n")

    slozky = sorted(d for d in os.listdir(ZDROJ)
                    if os.path.isdir(os.path.join(ZDROJ, d)))

    udalosti = []
    for nazev in slozky:
        print("  %s" % nazev)
        u = zpracuj_slozku(os.path.join(ZDROJ, nazev), nazev, jen_data)
        print("    → %s (%d fotek)" % (u["slug"], len(u["fotky"])))
        udalosti.append(u)

    # nejnovější nahoře; akce bez roku na konec
    udalosti.sort(key=lambda u: (u["rok"] or 0), reverse=True)

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(udalosti, f, ensure_ascii=False, indent=2)

    celkem = sum(len(u["fotky"]) for u in udalosti)
    print("\nHotovo: %d akcí, %d fotek." % (len(udalosti), celkem))
    print("Přehled uložen do data/udalosti.json")
    print("Teď spusťte: python3 build-udalosti.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

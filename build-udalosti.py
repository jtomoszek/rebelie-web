#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vygeneruje sekci výstav a soutěží na oceneni.html a ukázku na index.html
podle souboru data/udalosti.json.

Použití (ze složky web/):
    python3 build-udalosti.py

Skript je opakovaně spustitelný – dřívější vygenerovaný obsah přepíše.

Chcete-li u akce doplnit umístění („1. místo"), typ nebo krátký popis,
upravte příslušnou položku v data/udalosti.json a spusťte skript znovu.
Nic se nedomýšlí: prázdné pole se prostě nezobrazí.
"""

import hashlib
import html
import json
import os
import re
import sys

ZDE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ZDE, "data", "udalosti.json")

UKAZKA_NA_HOMEPAGE = 4   # kolik nejnovějších akcí se ukáže na úvodní stránce


def e(text):
    return html.escape(str(text), quote=True)


def rozmery(cesta):
    """Šířka a výška obrázku přes sips (součást macOS)."""
    import subprocess
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", cesta],
                         capture_output=True, text=True).stdout
    w = re.search(r"pixelWidth:\s*(\d+)", out)
    h = re.search(r"pixelHeight:\s*(\d+)", out)
    return (int(w.group(1)), int(h.group(1))) if w and h else None


def otisk(cesta):
    """Krátký otisk obsahu souboru. Přidává se k URL obrázku jako ?v=…,
    aby prohlížeče po výměně fotky pod stejným názvem načetly novou."""
    try:
        with open(os.path.join(ZDE, cesta), "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    except OSError:
        return "0"


def dlazdice(u, odsazeni="      "):
    """HTML jedné akce."""
    if not u["fotky"]:
        return ""

    # Obálka dlaždice: první fotka, nebo libovolná jiná zadaná v udalosti.json
    # jako "obalka": "slug-akce/soubor.jpg" (může být i z jiné akce).
    pocet = len(u["fotky"])
    vlastni = u.get("obalka")
    if vlastni:
        slug_ob, soubor_ob = vlastni.split("/", 1)
        rv = rozmery(os.path.join(ZDE, "img", "udalosti", slug_ob, "thumb", soubor_ob))
        obalka = {"slug": slug_ob, "soubor": soubor_ob,
                  "sirka": rv[0] if rv else 0, "vyska": rv[1] if rv else 0}
    else:
        obalka = dict(u["fotky"][0], slug=u["slug"])
    fotek = "%d %s" % (pocet, "fotka" if pocet == 1 else
                       ("fotky" if pocet < 5 else "fotek"))

    # Druhý řádek popisku: jen to, co opravdu známe.
    meta = " &middot; ".join(x for x in (u.get("typ"), u.get("misto")) if x)

    o = odsazeni
    radky = [
        '%s<article class="event" data-reveal>' % o,
        '%s  <button class="event__cover" type="button" data-udalost="%s"'
        % (o, e(u["slug"])),
        '%s          aria-label="Otevřít galerii: %s – %s">'
        % (o, e(u["nazev"]), fotek),
        '%s    <img src="img/udalosti/%s/thumb/%s?v=%s" alt="%s" width="%d" height="%d" loading="lazy">'
        % (o, e(obalka["slug"]), e(obalka["soubor"]),
           otisk("img/udalosti/%s/thumb/%s" % (obalka["slug"], obalka["soubor"])),
           e(u["nazev"] + " – fotografie z akce"),
           obalka["sirka"], obalka["vyska"]),
        '%s    <span class="event__count">%s</span>' % (o, fotek),
        '%s  </button>' % o,
        '%s  <div class="event__body">' % o,
    ]
    if u.get("rok"):
        radky.append('%s    <span class="event__year">%s</span>' % (o, u["rok"]))
    radky.append('%s    <h3 class="event__name">%s</h3>' % (o, e(u["nazev"])))
    if meta:
        radky.append('%s    <p class="event__meta">%s</p>' % (o, meta))
    if u.get("popis"):
        radky.append('%s    <p class="event__meta">%s</p>' % (o, e(u["popis"])))
    if u.get("umisteni"):
        radky.append('%s    <p class="event__place">%s</p>' % (o, e(u["umisteni"])))
    radky += ['%s  </div>' % o, '%s</article>' % o]
    return "\n".join(radky)


def data_pro_js(udalosti):
    """Malý JSON pro lightbox – jen názvy a soubory, ať stránka neztloustne."""
    mapa = {u["slug"]: {"nazev": u["nazev"],
                        "fotky": ["%s?v=%s" % (f["soubor"],
                                  otisk("img/udalosti/%s/%s" % (u["slug"], f["soubor"])))
                                  for f in u["fotky"]]}
            for u in udalosti if u["fotky"]}
    return json.dumps(mapa, ensure_ascii=False, separators=(",", ":"))


def nahrad(cesta, znacka, obsah):
    """Nahradí vše mezi <div|script ...> a značkou <!--ZNACKA-->."""
    if not os.path.exists(cesta):
        print("  ! chybí %s" % os.path.basename(cesta))
        return False

    with open(cesta, encoding="utf-8") as f:
        src = f.read()

    m = "<!--%s-->" % znacka
    if m not in src:
        print("  ! ve stránce %s chybí značka %s" % (os.path.basename(cesta), m))
        return False

    vzor = re.compile(
        r'(<(?:div|script)[^>]*data-generovane="%s"[^>]*>\n)(?:.*?)(\s*)%s'
        % (re.escape(znacka), re.escape(m)),
        re.DOTALL)
    if not vzor.search(src):
        print("  ! nenašel jsem obal pro %s v %s" % (znacka, os.path.basename(cesta)))
        return False

    src = vzor.sub(lambda mo: mo.group(1) + obsah.rstrip() + "\n      " + m, src)

    with open(cesta, "w", encoding="utf-8") as f:
        f.write(src)
    return True


def main():
    if not os.path.exists(DATA):
        print("Nenašel jsem %s – spusťte nejdřív pripravit-udalosti.py" % DATA)
        return 1

    with open(DATA, encoding="utf-8") as f:
        udalosti = json.load(f)

    udalosti = [u for u in udalosti if u["fotky"]]
    celkem_fotek = sum(len(u["fotky"]) for u in udalosti)

    print("Generuji výstavy a soutěže…")

    # ---- oceneni.html: všechny akce + data pro lightbox
    vse = "\n\n".join(dlazdice(u) for u in udalosti)
    nahrad(os.path.join(ZDE, "oceneni.html"), "UDALOSTI", vse)
    nahrad(os.path.join(ZDE, "oceneni.html"), "UDALOSTI-DATA",
           "      " + data_pro_js(udalosti))
    print("  oceneni.html      %d akcí, %d fotek" % (len(udalosti), celkem_fotek))

    # ---- index.html: ukázka nejnovějších akcí
    ukazka = udalosti[:UKAZKA_NA_HOMEPAGE]
    nahrad(os.path.join(ZDE, "index.html"), "UDALOSTI",
           "\n\n".join(dlazdice(u) for u in ukazka))
    nahrad(os.path.join(ZDE, "index.html"), "UDALOSTI-DATA",
           "      " + data_pro_js(ukazka))
    print("  index.html        %d akcí (ukázka)" % len(ukazka))

    # ---- počet akcí do statistik
    for stranka in ("index.html", "o-mne.html"):
        cesta = os.path.join(ZDE, stranka)
        with open(cesta, encoding="utf-8") as f:
            src = f.read()
        novy = re.sub(r'(<p class="stat__num" data-pocet-akci>)[^<]*(</p>)',
                      r'\g<1>%d\g<2>' % len(udalosti), src)
        if novy != src:
            with open(cesta, "w", encoding="utf-8") as f:
                f.write(novy)
            print("  %-17s počet akcí → %d" % (stranka, len(udalosti)))

    print("Hotovo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

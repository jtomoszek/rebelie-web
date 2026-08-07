#!/bin/bash
# Připraví fotky pro web: převede HEIC/PNG na JPG, zmenší je a vytvoří náhledy.
#
# Použití (ze složky web/):
#     ./pripravit-fotky.sh "../Fofo Rebelie/Body painting" bodypainting bp
#     ./pripravit-fotky.sh "../Fofo Rebelie/Textil"        textil       tx
#     ./pripravit-fotky.sh "../Fofo Rebelie/Art"           obrazy       ob
#
# Argumenty:
#   1) zdrojová složka s originály
#   2) cílová kategorie (bodypainting | textil | obrazy)
#   3) předpona souborů (bp | tx | ob)
#
# POZOR: skript přepíše obsah cílové složky. Originály zůstanou nedotčené.
# Po dokončení spusťte ještě:  python3 build-galerie.py
#
# Používá pouze `sips`, který je součástí macOS — nic se neinstaluje.

set -eu

if [ $# -ne 3 ]; then
  echo "Použití: $0 <zdrojová složka> <kategorie> <předpona>" >&2
  echo "Např.:   $0 \"../Fofo Rebelie/Textil\" textil tx" >&2
  exit 1
fi

SRC="$1"
CAT="$2"
PREFIX="$3"

cd "$(dirname "$0")"
OUT="img/$CAT"

LARGE_MAX=1800   # delší strana velké verze (px)
THUMB_MAX=900    # delší strana náhledu (px)

if [ ! -d "$SRC" ]; then
  echo "Zdrojová složka neexistuje: $SRC" >&2
  exit 1
fi

mkdir -p "$OUT/thumb"
rm -f "$OUT"/*.jpg "$OUT"/thumb/*.jpg

echo "Zpracovávám: $SRC  →  $OUT"

i=0
# Řadí podle čísla v názvu souboru, aby pořadí odpovídalo originálům.
# Cesty obsahují mezery, proto se řadicí klíč vytáhne dopředu a pak zase odstraní.
find "$SRC" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.heic' \) \
  | sed -E 's|^(.*/[^/]*[^0-9]([0-9]+)\.[A-Za-z]+)$|\2\t\1|' \
  | sort -n -k1,1 \
  | cut -f2- \
  | while IFS= read -r f; do
      i=$((i + 1))
      base="$PREFIX-$(printf '%02d' "$i")"
      large="$OUT/$base.jpg"
      thumb="$OUT/thumb/$base.jpg"

      w=$(sips -g pixelWidth  "$f" 2>/dev/null | awk '/pixelWidth/{print $2}')
      h=$(sips -g pixelHeight "$f" 2>/dev/null | awk '/pixelHeight/{print $2}')
      if [ -z "${w:-}" ] || [ -z "${h:-}" ]; then
        echo "  přeskočeno (nelze přečíst): $f" >&2
        continue
      fi
      maxdim=$(( w > h ? w : h ))

      # velká verze — zmenšuje se jen tehdy, je-li originál větší
      if [ "$maxdim" -gt "$LARGE_MAX" ]; then
        sips -s format jpeg -s formatOptions 72 -Z "$LARGE_MAX" "$f" --out "$large" >/dev/null
      else
        sips -s format jpeg -s formatOptions 78 "$f" --out "$large" >/dev/null
      fi

      # náhled
      if [ "$maxdim" -gt "$THUMB_MAX" ]; then
        sips -s format jpeg -s formatOptions 68 -Z "$THUMB_MAX" "$large" --out "$thumb" >/dev/null
      else
        cp "$large" "$thumb"
      fi

      echo "  $base.jpg  ←  $(basename "$f")"
    done

echo
echo "Hotovo. Nezapomeňte spustit:  python3 build-galerie.py"

#!/usr/bin/env python3
"""
Erzeugt die App-Symbole (weisses Fragezeichen auf Kampagnenrot) als PNG.

Ohne Zusatzpakete — auf dem Mac ist kein Pillow installiert. Gezeichnet wird
ueber Abstandsfunktionen, die Kantenglaettung ergibt sich daraus rechnerisch.

Aufruf:  python3 symbole.py
"""

import math
import struct
import zlib

# Kampagnenfarben aus dem Quiz
ROT_OBEN = (0xE2, 0x14, 0x14)
ROT_UNTEN = (0xC0, 0x00, 0x00)
WEISS = (0xFF, 0xFF, 0xFF)

# ── Bausteine der Abstandsfunktion (negativ = innerhalb) ────────────────────


def sdf_kreis(x, y, mx, my, r):
    return math.hypot(x - mx, y - my) - r


def sdf_kapsel(x, y, ax, ay, bx, by, r):
    """Strecke von A nach B mit runden Enden."""
    pax, pay = x - ax, y - ay
    bax, bay = bx - ax, by - ay
    t = (pax * bax + pay * bay) / (bax * bax + bay * bay)
    t = max(0.0, min(1.0, t))
    return math.hypot(pax - bax * t, pay - bay * t) - r


# Der Bogen des Fragezeichens: Ring um MITTE mit Radius RING_R, aber nur
# ausserhalb der Luecke unten links (klassische Form des Zeichens).
BOGEN_MX, BOGEN_MY = 0.0, -0.30
RING_R = 0.34
DICKE = 0.105
LUECKE_VON, LUECKE_BIS = -155.0, -60.0   # Grad, mathematische Zaehlweise


def _punkt_auf_ring(grad):
    b = math.radians(grad)
    return BOGEN_MX + RING_R * math.cos(b), BOGEN_MY - RING_R * math.sin(b)


ENDE_A = _punkt_auf_ring(LUECKE_VON)     # freies Ende unten links
ENDE_B = _punkt_auf_ring(LUECKE_BIS)     # Uebergang in den Schaft


def sdf_fragezeichen(x, y):
    # Bogen
    winkel = math.degrees(math.atan2(-(y - BOGEN_MY), x - BOGEN_MX))
    if LUECKE_VON < winkel < LUECKE_BIS:
        d = 1e9                          # in der Luecke: nichts zeichnen
    else:
        d = abs(math.hypot(x - BOGEN_MX, y - BOGEN_MY) - RING_R) - DICKE

    # Runde Kappen an den beiden Schnittkanten
    d = min(d, sdf_kreis(x, y, ENDE_A[0], ENDE_A[1], DICKE))
    d = min(d, sdf_kreis(x, y, ENDE_B[0], ENDE_B[1], DICKE))

    # Schaft: vom Bogenende leicht einwaerts, dann gerade nach unten
    d = min(d, sdf_kapsel(x, y, ENDE_B[0], ENDE_B[1], 0.02, 0.14, DICKE))
    d = min(d, sdf_kapsel(x, y, 0.02, 0.14, 0.0, 0.32, DICKE))

    # Punkt
    d = min(d, sdf_kreis(x, y, 0.0, 0.62, 0.135))
    return d


# ── PNG schreiben ──────────────────────────────────────────────────────────


def schreibe_png(pfad, groesse, pixel):
    def block(typ, daten):
        kopf = struct.pack('>I', len(daten)) + typ
        return kopf + daten + struct.pack('>I', zlib.crc32(typ + daten) & 0xFFFFFFFF)

    roh = bytearray()
    for zeile in range(groesse):
        roh.append(0)                                    # Filter "keiner"
        roh += pixel[zeile * groesse * 3:(zeile + 1) * groesse * 3]

    datei = (b'\x89PNG\r\n\x1a\n'
             + block(b'IHDR', struct.pack('>IIBBBBB', groesse, groesse, 8, 2, 0, 0, 0))
             + block(b'IDAT', zlib.compress(bytes(roh), 9))
             + block(b'IEND', b''))
    with open(pfad, 'wb') as f:
        f.write(datei)


def zeichne(pfad, groesse, inhalt=0.95):
    """inhalt = wie gross das Fragezeichen auf der Kachel sitzt."""
    pixel = bytearray(groesse * groesse * 3)
    kante = 2.0 / groesse            # ein Bildpunkt im Zeichenraum

    for py in range(groesse):
        v = (py + 0.5) / groesse * 2.0 - 1.0
        # Hintergrund: sehr dezenter Verlauf, damit die Kachel nicht flach wirkt
        mischung = (py + 0.5) / groesse
        grund = tuple(round(ROT_OBEN[i] + (ROT_UNTEN[i] - ROT_OBEN[i]) * mischung)
                      for i in range(3))
        for px in range(groesse):
            u = (px + 0.5) / groesse * 2.0 - 1.0
            d = sdf_fragezeichen(u / inhalt, v / inhalt) * inhalt
            deckung = max(0.0, min(1.0, 0.5 - d / kante))
            i = (py * groesse + px) * 3
            for k in range(3):
                pixel[i + k] = round(grund[k] + (WEISS[k] - grund[k]) * deckung)

    schreibe_png(pfad, groesse, pixel)
    print(f'  {pfad}  ({groesse}x{groesse})')


if __name__ == '__main__':
    print('Symbole werden gezeichnet:')
    zeichne('icon-192.png', 192)
    zeichne('icon-512.png', 512)
    zeichne('apple-touch-icon.png', 180)
    zeichne('favicon.png', 32)
    # Fuer Android: Inhalt kleiner, damit runde Masken nichts abschneiden
    zeichne('icon-maskable-512.png', 512, inhalt=0.72)
    print('Fertig.')

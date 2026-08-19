#!/usr/bin/env python3
"""
Erzeugt einen QR-Code als SVG — ohne Zusatzpakete.

Auf dem Mac liegt keine QR-Bibliothek (segno, qrcode, PIL fehlen alle), deshalb
ist der Kodierer hier von Hand geschrieben: Byte-Modus, Reed-Solomon ueber
GF(256), Maskenwahl nach den vier Strafregeln der Norm.

Weil ein falscher QR-Code auf einem Aushang erst am Stand auffaellt, prueft
sich das Skript selbst: `pruefe()` liest den fertigen Code aus der Matrix
zurueck — Format, Maske, Verschraenkung, Reed-Solomon-Syndrome, Nutzlast.
Kommt dabei nicht wieder heraus, was hineinging, bricht es ab.

Aufruf:  python3 qr.py
"""

import sys

# ── Rechnen in GF(256), Primpolynom 0x11D ──────────────────────────────────

EXP = [0] * 512
LOG = [0] * 256

_x = 1
for _i in range(255):
    EXP[_i] = _x
    LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11D
for _i in range(255, 512):
    EXP[_i] = EXP[_i - 255]


def mal(a, b):
    if a == 0 or b == 0:
        return 0
    return EXP[LOG[a] + LOG[b]]


def generatorpolynom(grad):
    g = [1]
    for i in range(grad):
        neu = [0] * (len(g) + 1)
        for j, c in enumerate(g):
            neu[j] ^= c                      # g * x
            neu[j + 1] ^= mal(c, EXP[i])     # g * alpha^i
        g = neu
    return g


def fehlerkorrektur(daten, anzahl):
    g = generatorpolynom(anzahl)
    rest = list(daten) + [0] * anzahl
    for i in range(len(daten)):
        f = rest[i]
        if f:
            for j, c in enumerate(g):
                rest[i + j] ^= mal(c, f)
    return rest[len(daten):]


def syndrome(codewort, anzahl):
    """Alle Werte 0 = das Codewort ist in sich stimmig."""
    out = []
    for i in range(anzahl):
        s = 0
        for c in codewort:
            s = mal(s, EXP[i]) ^ c
        out.append(s)
    return out


# ── Tabellen der Norm, Fassungen 1 bis 6 ───────────────────────────────────
# Fassung: {Stufe: (EC-Codewoerter je Block, [(Anzahl Bloecke, Datencodewoerter je Block)])}

TABELLE = {
    1: {'L': (7, [(1, 19)]),  'M': (10, [(1, 16)]), 'Q': (13, [(1, 13)]),           'H': (17, [(1, 9)])},
    2: {'L': (10, [(1, 34)]), 'M': (16, [(1, 28)]), 'Q': (22, [(1, 22)]),           'H': (28, [(1, 16)])},
    3: {'L': (15, [(1, 55)]), 'M': (26, [(1, 44)]), 'Q': (18, [(2, 17)]),           'H': (22, [(2, 13)])},
    4: {'L': (20, [(1, 80)]), 'M': (18, [(2, 32)]), 'Q': (26, [(2, 24)]),           'H': (16, [(4, 9)])},
    5: {'L': (26, [(1, 108)]),'M': (24, [(2, 43)]), 'Q': (18, [(2, 15), (2, 16)]),  'H': (22, [(2, 11), (2, 12)])},
    6: {'L': (18, [(2, 68)]), 'M': (16, [(4, 27)]), 'Q': (24, [(4, 19)]),           'H': (28, [(4, 15)])},
}

AUSRICHTUNG = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34]}
RESTBITS = {1: 0, 2: 7, 3: 7, 4: 7, 5: 7, 6: 7}
STUFENBITS = {'L': 0b01, 'M': 0b00, 'Q': 0b11, 'H': 0b10}


def datencodewoerter(fassung, stufe):
    return sum(n * d for n, d in TABELLE[fassung][stufe][1])


def waehle_fassung(laenge, wunsch=('Q', 'M', 'L')):
    """Fehlerkorrektur zuerst, Groesse zweitrangig.

    Umgekehrt herum — kleinste Fassung zuerst — kaeme fuer diese Adresse Stufe L
    heraus, also 7 % Toleranz. Der Code soll aber auf ein Blatt gedruckt werden,
    das angefasst, geknickt und schraeg fotografiert wird. Stufe Q vertraegt 25 %
    Schaden und kostet hier nur acht Module mehr Kantenlaenge.
    """
    for stufe in wunsch:
        for fassung in sorted(TABELLE):
            if (datencodewoerter(fassung, stufe) * 8 - 12) // 8 >= laenge:
                return fassung, stufe
    raise ValueError('Text zu lang fuer die Fassungen 1-6')


# ── Nutzdaten zu Codewoertern ──────────────────────────────────────────────

def bitfolge(text, fassung, stufe):
    roh = text.encode('utf-8')
    bits = [0, 1, 0, 0]                                   # Modus: Byte
    bits += [(len(roh) >> i) & 1 for i in range(7, -1, -1)]   # Laenge, 8 Bit (Fassung 1-9)
    for b in roh:
        bits += [(b >> i) & 1 for i in range(7, -1, -1)]

    gesamt = datencodewoerter(fassung, stufe) * 8
    bits += [0] * min(4, gesamt - len(bits))              # Abschluss
    while len(bits) % 8:
        bits.append(0)
    fueller = [0xEC, 0x11]
    i = 0
    while len(bits) < gesamt:
        bits += [(fueller[i % 2] >> k) & 1 for k in range(7, -1, -1)]
        i += 1

    return [int(''.join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]


def verschraenke(codewoerter, fassung, stufe):
    ec_je_block, aufbau = TABELLE[fassung][stufe]
    bloecke, pos = [], 0
    for anzahl, je_block in aufbau:
        for _ in range(anzahl):
            bloecke.append(codewoerter[pos:pos + je_block])
            pos += je_block
    ec = [fehlerkorrektur(b, ec_je_block) for b in bloecke]

    aus = []
    for i in range(max(len(b) for b in bloecke)):
        for b in bloecke:
            if i < len(b):
                aus.append(b[i])
    for i in range(ec_je_block):
        for e in ec:
            aus.append(e[i])
    return aus, bloecke, ec


# ── Matrix ─────────────────────────────────────────────────────────────────

def grundmuster(fassung):
    n = 17 + 4 * fassung
    m = [[0] * n for _ in range(n)]
    res = [[False] * n for _ in range(n)]

    def block(zeile, spalte, hoehe, breite, wert):
        for z in range(zeile, zeile + hoehe):
            for s in range(spalte, spalte + breite):
                if 0 <= z < n and 0 <= s < n:
                    m[z][s] = wert
                    res[z][s] = True

    for z, s in ((0, 0), (0, n - 7), (n - 7, 0)):
        block(z - 1, s - 1, 9, 9, 0)                      # Trennstreifen
        block(z, s, 7, 7, 1)
        block(z + 1, s + 1, 5, 5, 0)
        block(z + 2, s + 2, 3, 3, 1)

    mitten = AUSRICHTUNG[fassung]
    for z in mitten:
        for s in mitten:
            if (z < 9 and s < 9) or (z < 9 and s > n - 10) or (z > n - 10 and s < 9):
                continue
            block(z - 2, s - 2, 5, 5, 1)
            block(z - 1, s - 1, 3, 3, 0)
            block(z, s, 1, 1, 1)

    for i in range(8, n - 8):                             # Zeitmuster
        m[6][i] = m[i][6] = (i + 1) % 2
        res[6][i] = res[i][6] = True

    m[n - 8][8] = 1                                       # dunkles Modul
    res[n - 8][8] = True
    for i in range(9):                                    # Platz fuer die Formatangabe
        if i != 6:
            res[8][i] = res[i][8] = True
    for i in range(8):
        res[8][n - 1 - i] = res[n - 1 - i][8] = True

    return m, res


def platziere(m, res, bits):
    n = len(m)
    idx, spalte, aufwaerts = 0, n - 1, True
    while spalte > 0:
        if spalte == 6:
            spalte -= 1
        for i in range(n):
            zeile = n - 1 - i if aufwaerts else i
            for d in (0, 1):
                s = spalte - d
                if not res[zeile][s]:
                    m[zeile][s] = bits[idx] if idx < len(bits) else 0
                    idx += 1
        spalte -= 2
        aufwaerts = not aufwaerts
    return idx


MASKEN = [
    lambda z, s: (z + s) % 2 == 0,
    lambda z, s: z % 2 == 0,
    lambda z, s: s % 3 == 0,
    lambda z, s: (z + s) % 3 == 0,
    lambda z, s: (z // 2 + s // 3) % 2 == 0,
    lambda z, s: (z * s) % 2 + (z * s) % 3 == 0,
    lambda z, s: ((z * s) % 2 + (z * s) % 3) % 2 == 0,
    lambda z, s: ((z + s) % 2 + (z * s) % 3) % 2 == 0,
]


def strafe(m):
    n = len(m)
    p = 0

    for linien in (m, [list(sp) for sp in zip(*m)]):
        for linie in linien:
            lauf, vorher = 1, linie[0]
            for wert in linie[1:]:
                if wert == vorher:
                    lauf += 1
                else:
                    if lauf >= 5:
                        p += 3 + (lauf - 5)
                    lauf, vorher = 1, wert
            if lauf >= 5:
                p += 3 + (lauf - 5)

    for z in range(n - 1):
        for s in range(n - 1):
            if m[z][s] == m[z][s + 1] == m[z + 1][s] == m[z + 1][s + 1]:
                p += 3

    muster = ([1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1])
    for linien in (m, [list(sp) for sp in zip(*m)]):
        for linie in linien:
            for i in range(n - 10):
                if list(linie[i:i + 11]) in muster:
                    p += 40

    dunkel = sum(sum(z) for z in m) * 100 / (n * n)
    p += 10 * (int(abs(dunkel - 50) / 5))
    return p


def formatbits(stufe, maske):
    wert = (STUFENBITS[stufe] << 3) | maske
    rest = wert << 10
    # Bis der Rest wirklich unter 11 Bit liegt. Eine Abbruchbedingung auf
    # "Bit 14 gesetzt" reicht nicht: der Rest bleibt dann bis zu 14 Bit lang
    # und laeuft beim Zusammensetzen in die Datenbits hinein. Faellt nur bei
    # bestimmten Stufe-Masken-Paaren auf.
    while rest.bit_length() >= 11:
        rest ^= 0b101_0011_0111 << (rest.bit_length() - 11)
    return ((wert << 10) | rest) ^ 0b101_0100_0001_0010


def schreibe_format(m, stufe, maske):
    n = len(m)
    f = formatbits(stufe, maske)
    bit = lambda i: (f >> i) & 1
    # Reihenfolge genau nach Norm: Bit 0 sitzt oben in Spalte 8, nicht links in
    # Zeile 8. Spiegelverkehrt gelegt faellt es keiner Gegenprobe auf, die mit
    # derselben Annahme zurueckliest — ein fremder Decoder scheitert trotzdem.
    for i in range(6):
        m[i][8] = bit(i)
    m[7][8], m[8][8], m[8][7] = bit(6), bit(7), bit(8)
    for i in range(9, 15):
        m[8][14 - i] = bit(i)
    for i in range(8):
        m[8][n - 1 - i] = bit(i)
    for i in range(8, 15):
        m[n - 15 + i][8] = bit(i)


# ── Kodieren ───────────────────────────────────────────────────────────────

def kodiere(text):
    fassung, stufe = waehle_fassung(len(text.encode('utf-8')))
    strom, _, _ = verschraenke(bitfolge(text, fassung, stufe), fassung, stufe)

    bits = []
    for c in strom:
        bits += [(c >> i) & 1 for i in range(7, -1, -1)]
    bits += [0] * RESTBITS[fassung]

    grund, res = grundmuster(fassung)
    platziere(grund, res, bits)

    beste, beste_strafe = None, None
    for maske in range(8):
        m = [zeile[:] for zeile in grund]
        for z in range(len(m)):
            for s in range(len(m)):
                if not res[z][s] and MASKEN[maske](z, s):
                    m[z][s] ^= 1
        schreibe_format(m, stufe, maske)
        p = strafe(m)
        if beste_strafe is None or p < beste_strafe:
            beste, beste_strafe, beste_maske = m, p, maske

    return beste, fassung, stufe, beste_maske, beste_strafe


# ── Gegenprobe: den fertigen Code wieder auslesen ──────────────────────────

def pruefe(m, fassung, stufe, maske):
    n = len(m)
    bericht = {}

    gelesen = 0
    for i in range(6):
        gelesen |= m[i][8] << i
    gelesen |= m[7][8] << 6
    gelesen |= m[8][8] << 7
    gelesen |= m[8][7] << 8
    for i in range(9, 15):
        gelesen |= m[8][14 - i] << i
    entpackt = gelesen ^ 0b101_0100_0001_0010
    bericht['stufe_gelesen'] = {v: k for k, v in STUFENBITS.items()}[(entpackt >> 13) & 0b11]
    bericht['maske_gelesen'] = (entpackt >> 10) & 0b111

    _, res = grundmuster(fassung)
    roh = [zeile[:] for zeile in m]
    for z in range(n):
        for s in range(n):
            if not res[z][s] and MASKEN[maske](z, s):
                roh[z][s] ^= 1

    bits, idx, spalte, aufwaerts = [], 0, n - 1, True
    while spalte > 0:
        if spalte == 6:
            spalte -= 1
        for i in range(n):
            zeile = n - 1 - i if aufwaerts else i
            for d in (0, 1):
                s = spalte - d
                if not res[zeile][s]:
                    bits.append(roh[zeile][s])
        spalte -= 2
        aufwaerts = not aufwaerts
    strom = [int(''.join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits) - RESTBITS[fassung], 8)]

    ec_je_block, aufbau = TABELLE[fassung][stufe]
    laengen = [d for anzahl, d in aufbau for _ in range(anzahl)]
    bloecke = [[] for _ in laengen]
    idx = 0
    for i in range(max(laengen)):
        for b, L in enumerate(laengen):
            if i < L:
                bloecke[b].append(strom[idx]); idx += 1
    ec = [[] for _ in laengen]
    for i in range(ec_je_block):
        for b in range(len(laengen)):
            ec[b].append(strom[idx]); idx += 1

    bericht['syndrome_alle_null'] = all(
        set(syndrome(bloecke[b] + ec[b], ec_je_block)) == {0} for b in range(len(laengen)))

    daten = [c for b in bloecke for c in b]
    dbits = []
    for c in daten:
        dbits += [(c >> i) & 1 for i in range(7, -1, -1)]
    modus = int(''.join(map(str, dbits[0:4])), 2)
    laenge = int(''.join(map(str, dbits[4:12])), 2)
    nutz = bytes(int(''.join(map(str, dbits[12 + 8 * i:20 + 8 * i])), 2) for i in range(laenge))
    bericht['modus'] = modus
    bericht['text_gelesen'] = nutz.decode('utf-8', 'replace')
    return bericht


# ── Ausgabe ────────────────────────────────────────────────────────────────

def als_svg(m, ruhe=4):
    n = len(m)
    kante = n + 2 * ruhe
    pfad = []
    for z in range(n):
        for s in range(n):
            if m[z][s]:
                pfad.append(f'M{s + ruhe} {z + ruhe}h1v1h-1z')
    # width/height muessen mit dran: ohne sie rastert Chrome das SVG mit 150 px,
    # bei 45 Modulen also 3,33 Pixel je Modul. Was daraus hochskaliert wird, ist
    # verwaschen und wurde im Test von keinem Decoder mehr gelesen. Mit einem
    # ganzzahligen Vielfachen der Modulzahl faellt jedes Modul auf volle Pixel.
    px = kante * 10
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{px}" '
            f'viewBox="0 0 {kante} {kante}" '
            f'shape-rendering="crispEdges" role="img" aria-label="QR-Code zum Quiz">'
            f'<rect width="{kante}" height="{kante}" fill="#fff"/>'
            f'<path d="{"".join(pfad)}" fill="#000"/></svg>')


if __name__ == '__main__':
    ziel = sys.argv[1] if len(sys.argv) > 1 else 'https://junejunilia.github.io/gleichstellungs-quiz/'
    m, fassung, stufe, maske, p = kodiere(ziel)

    print(f'Ziel      {ziel}  ({len(ziel.encode())} Bytes)')
    print(f'Fassung   {fassung}  ({len(m)}x{len(m)} Module)')
    print(f'Stufe     {stufe}   Maske {maske}   Strafpunkte {p}')

    b = pruefe(m, fassung, stufe, maske)
    print('\nGegenprobe — aus der fertigen Matrix zurueckgelesen:')
    print(f'  Stufe aus der Formatangabe   {b["stufe_gelesen"]}   {"ok" if b["stufe_gelesen"] == stufe else "FALSCH"}')
    print(f'  Maske aus der Formatangabe   {b["maske_gelesen"]}   {"ok" if b["maske_gelesen"] == maske else "FALSCH"}')
    print(f'  Modus                        {b["modus"]}   {"ok (Byte)" if b["modus"] == 4 else "FALSCH"}')
    print(f'  Reed-Solomon-Syndrome        {"alle null, ok" if b["syndrome_alle_null"] else "NICHT NULL"}')
    print(f'  Text                         {"ok" if b["text_gelesen"] == ziel else "FALSCH: " + b["text_gelesen"]}')

    if not (b['stufe_gelesen'] == stufe and b['maske_gelesen'] == maske and b['modus'] == 4
            and b['syndrome_alle_null'] and b['text_gelesen'] == ziel):
        sys.exit('\nGegenprobe fehlgeschlagen — nichts geschrieben.')

    with open('qr.svg', 'w') as f:
        f.write(als_svg(m))
    print('\nqr.svg geschrieben.')

# Gleichstellungs-Quiz — als App auf Tablet und iPad

Das Quiz startet vom Startbildschirm wie eine App: ohne Browserleiste, im Vollbild,
und **ohne Netz**, sobald es einmal geladen war.

## Warum es als lokale Datei nicht ging

Weder iPad noch Android-Tablet können eine HTML-Datei aus dem Dateispeicher auf den
Startbildschirm legen — „Zum Home-Bildschirm" gibt es für `file://`-Adressen schlicht
nicht. Das Quiz braucht deshalb eine Internetadresse. Danach lädt es sich beim ersten
Öffnen selbst aufs Gerät und läuft ab da offline weiter.

## Was hier liegt

| Datei | wofür |
|---|---|
| `index.html` | das Quiz |
| `manifest.webmanifest` | Name, Farben, Symbol — damit Android es als App behandelt |
| `sw.js` | lädt das Quiz aufs Gerät, damit es ohne Netz läuft |
| `icon-*.png`, `apple-touch-icon.png`, `favicon.png` | die Symbole |
| `symbole.py` | erzeugt die Symbole neu (`python3 symbole.py`) |
| `.nojekyll` | schaltet bei GitHub Pages die überflüssige Jekyll-Verarbeitung ab |

Alle Pfade sind **relativ**. Dieselben Dateien laufen dadurch unverändert auf GitHub
Pages *und* auf der eigenen Website — es muss nichts angepasst werden.

## Veröffentlichen: GitHub Pages

```bash
gh repo create gleichstellungs-quiz --public --source=. --remote=origin --push
gh api -X POST repos/:owner/gleichstellungs-quiz/pages -f source[branch]=main -f source[path]=/
```

Danach steht das Quiz nach ein bis zwei Minuten unter
`https://junejunilia.github.io/gleichstellungs-quiz/`.

Alternativ von Hand: Repository auf github.com anlegen, Dateien hochladen, dann unter
*Settings → Pages* als Quelle `main` und `/ (root)` wählen.

## Veröffentlichen: eigene Website als Ausweichweg

Den **Inhalt** dieses Ordners (nicht den Ordner selbst) per FTP in ein Verzeichnis
`quiz` auf den Webspace legen. Erreichbar dann unter `https://…/quiz/`.

Wichtig: **HTTPS ist Pflicht.** Über `http://` verweigert der Browser den Service
Worker, dann läuft das Quiz nur mit Netzverbindung.

## Aufs iPad holen

Adresse in **Safari** öffnen — Chrome kann das auf iOS nicht.

1. `https://junejunilia.github.io/gleichstellungs-quiz/` aufrufen
2. Teilen-Symbol (Kasten mit Pfeil nach oben)
3. *Zum Home-Bildschirm*
4. Name bestätigen, *Hinzufügen*

## Auf Android als App installieren

Hier gibt es einen Unterschied, den es auf dem iPad nicht gibt: Android kann entweder eine
**echte App** installieren oder nur eine **Verknüpfung** anlegen. Die Verknüpfung sieht fast
gleich aus, öffnet aber Chrome samt Adressleiste. Für den Stand ist das der falsche Weg.

Voraussetzung ist **Chrome**, Samsung Internet oder Edge — nicht der Browser, der sich
innerhalb einer anderen App öffnet (etwa aus WhatsApp heraus), und nicht der Dateimanager.

1. Chrome öffnen und `https://junejunilia.github.io/gleichstellungs-quiz/` aufrufen
2. Warten, bis das Quiz vollständig zu sehen ist — Chrome prüft in diesem Moment das Manifest
3. Drei-Punkte-Menü oben rechts
4. Dort steht je nach Chrome-Fassung **„App installieren"** oder **„Zum Startbildschirm hinzufügen"**
5. Erscheint ein Dialog mit zwei Möglichkeiten: **„Installieren"** wählen, *nicht*
   „Verknüpfung erstellen"

|  | Installieren | Verknüpfung erstellen |
|---|---|---|
| Startet | im Vollbild, ohne Adressleiste | in Chrome, mit Adressleiste |
| Symbol | eigenes rotes App-Symbol | Chrome-Symbol mit kleinem Aufkleber |
| Zu finden in | App-Übersicht **und** Startbildschirm | nur Startbildschirm |
| Läuft offline | ja | nein |

**Woran man erkennt, dass es geklappt hat:** Nach dem Start ist oben **keine Adressleiste**
zu sehen, und das Quiz taucht in der App-Übersicht (vom unteren Rand nach oben wischen)
zwischen den normalen Apps auf.

Bei Samsung-Tablets mit *Samsung Internet*: Menü unten rechts → *Seite hinzufügen zu* →
*Startbildschirm*.

### Wenn „Installieren" nicht angeboten wird

Fast immer liegt es an einem dieser drei Punkte:

- Die Adresse wurde über `http://` statt `https://` geöffnet
- Es ist kein echtes Chrome, sondern ein In-App-Browser
- Die Seite war noch nicht fertig geladen, als das Menü geöffnet wurde

Am Quiz selbst liegt es nicht: Manifest, beide Symbolgrößen, das maskable-Symbol,
`display: standalone` und der Service Worker sind vorhanden und gegen die Live-Adresse geprüft.

### Das Tablet für den Stand einrichten

Die Menüpfade heißen je nach Hersteller und Android-Fassung etwas anders — Samsung benennt
einiges um. Unten stehen die Bezeichnungen der Grundausstattung.

**Bildschirm nicht ausgehen lassen.** Unter *Einstellungen → Display → Bildschirm-Timeout*
gibt es — anders als beim iPad — meist **kein „Nie", sondern höchstens 30 Minuten**. Für einen
Standtag zu wenig. Der verlässliche Weg führt über die Entwickleroptionen:

1. *Einstellungen → Über das Tablet* → siebenmal auf *Build-Nummer* tippen
2. *Einstellungen → System → Entwickleroptionen* → **Aktiv lassen** einschalten

Der Bildschirm bleibt dann an, **solange das Tablet am Strom hängt**. Ladekabel und
Steckdosenplatz am Stand also mit einplanen.

**Quiz festnageln,** damit Besucherinnen nicht versehentlich in anderen Apps landen:

1. Einschalten unter *Einstellungen → Sicherheit → Weitere Sicherheitseinstellungen →
   App-Anheften* (je nach Fassung auch *Sicherheit und Datenschutz → Weitere Einstellungen*)
2. Quiz starten, Übersichtstaste drücken, oben auf das App-Symbol tippen → *Anheften*
3. Lösen: *Zurück* und *Übersicht* gleichzeitig gedrückt halten — bei Gestensteuerung
   stattdessen vom unteren Rand nach oben wischen und halten

**Ruhe im Bild.** In den Schnelleinstellungen (von oben herunterwischen) *Bitte nicht stören*
einschalten und *Automatisch drehen* ausschalten. Sonst poppen Benachrichtigungen über dem
Quiz auf oder das Bild kippt, wenn jemand das Tablet anhebt.

**Chrome nicht deinstallieren oder deaktivieren.** Die installierte App läuft auf Chromes
Unterbau. Ist Chrome weg, startet auch das Quiz nicht mehr.

### Eine neue Fassung aufs Tablet holen

Nach einem Upload mit hochgezählter Zahl in `sw.js` (siehe *Quiz ändern* weiter unten):

1. Anheften lösen, App aus der Übersicht **vollständig schließen**
2. Einmal **mit Netz** starten — dabei lädt sich die neue Fassung im Hintergrund
3. Nochmal schließen und starten — jetzt ist sie zu sehen

Der zweite Start ist nötig: Beim ersten zeigt das Tablet noch die Fassung, die es schon
gespeichert hatte. Wer nur einmal startet und nichts Neues sieht, hält den Upload
fälschlich für misslungen.

### Wieder entfernen

Symbol lange gedrückt halten → *Deinstallieren* (bei einer Verknüpfung heißt es *Entfernen*).

## Nach dem Installieren — auf beiden Systemen

Einmal vom Symbol starten, solange noch WLAN da ist. Dabei lädt sich das Quiz aufs Gerät.
Ab dann läuft es auch ohne Netz.

## Für den Einsatz am Stand — iPad

Für Android steht das weiter oben unter *Das Tablet für den Stand einrichten*.

- **Automatische Sperre aus:** *Einstellungen → Anzeige & Helligkeit → Automatische Sperre → Nie*
- **Quiz festnageln:** *Einstellungen → Bedienungshilfen → Geführter Zugriff* einschalten, dann
  in der App dreimal die Seitentaste drücken. Beenden ebenso — mit dem dort vergebenen Code.
- **Ruhe im Bild:** *Nicht stören* im Kontrollzentrum einschalten, Drehsperre aktivieren.
- **Vorher testen** (gilt für beide Systeme): einmal im Flugmodus starten. Läuft es, ist alles
  richtig eingerichtet.

## Quiz ändern

Nach jeder Änderung an `index.html` in `sw.js` die Zahl hochzählen:

```js
const SPEICHER = 'quiz-v2';   // war v1
```

Ohne das zeigen Geräte, die die App schon einmal geöffnet haben, weiter den alten Stand —
das ist der häufigste Stolperstein. Danach neu hochladen und die App auf dem Tablet einmal
schließen und wieder öffnen.

> Hinweis zum Inhalt: Die Zahlen zu Entgeltgruppe und Rente stammen aus der Vorlage und
> sind hier nicht geprüft worden. Vor dem Stand einmal gegen die aktuelle Entgelttabelle
> gegenlesen.

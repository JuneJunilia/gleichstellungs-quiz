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

## Aufs Tablet holen

**iPad:** Adresse in **Safari** öffnen (nicht Chrome — nur Safari kann das) →
Teilen-Symbol → *Zum Home-Bildschirm* → *Hinzufügen*.

**Android:** Adresse in **Chrome** öffnen → Drei-Punkte-Menü → *App installieren*
bzw. *Zum Startbildschirm hinzufügen*.

Danach einmal vom Startbildschirm starten, solange noch WLAN da ist. Ab dann läuft es
auch ohne.

## Für den Einsatz am Stand

- **Automatische Sperre aus:** iPad → *Einstellungen → Anzeige & Helligkeit →
  Automatische Sperre → Nie*. Android → *Einstellungen → Display → Bildschirm-Timeout*.
- **Gerät festnageln,** damit Besucherinnen nicht aus dem Quiz herauskommen:
  iPad → *Einstellungen → Bedienungshilfen → Geführter Zugriff* einschalten, dann in der
  App dreimal die Seitentaste drücken. Android → *App-Anheften* in den Sicherheitseinstellungen.
- **Vorher testen:** einmal im Flugmodus starten. Läuft es, ist alles richtig eingerichtet.

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

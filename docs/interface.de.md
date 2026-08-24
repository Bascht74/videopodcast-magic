# Die Oberfläche

*In English: [interface.md](interface.md). Zurück zum
[Inhalt](README.de.md).*

## Die vier Reiter

Vier Reiter, in der Reihenfolge, in der man sie braucht.

- **Dateien & Produktion**: oben die Dateiliste, darunter ein schmaler
  Streifen mit Produktionsname, gesprochener Sprache und Ausgabeordner.
  Dateien oder ganze Ordner hineinziehen, hinzufügen oder ein früheres
  Projekt öffnen. Solange die Liste leer ist, steht dort eine
  Ablegefläche, die den Ablauf erklärt.

  Das Programm nennt den Blick auf das Material vor einem Lauf den
  Vorflug. Jede Datei bekommt daraus schon beim Hinzufügen ein
  Prüfzeichen: ✓ nichts zu bemängeln, ! ein Hinweis, ✕ so geht es nicht.
  Unter der Liste steht das Ergebnis in einem Satz;
  [Vorflug](preflight.de.md) sagt, was jedes Prüfzeichen bedeutet.

  **Projekt öffnen ...** steht nur auf der Ablegefläche. Ein geöffnetes
  Projekt nimmt jederzeit neue Dateien auf.

  Eine Datei mit mehr als einem Kanal sagt darunter, was aus ihr wird: je
  Kanal eine Zeile, mit einem Häkchen, das in der ersten Zeile
  **mit Channel 2 zusammenlegen** anbietet, und daneben, was gemessen
  wurde. Das Programm benennt Kanäle, in denen nichts steht, und lässt
  sie aus allem Weiteren heraus.
  [Kanäle: eine Spur oder zwei?](channels.de.md) sagt, wie das Programm
  die beiden unterscheidet.

  Eine einzelne Fortsetzungsdatei lässt sich für sich entfernen. Sie
  bleibt dann draußen, obwohl sie im Ordner liegt, und später wieder
  hinzugefügt ist sie eine eigene Aufnahme. Erst wenn die ganze Aufnahme
  entfernt und wieder hinzugefügt wird, gehören die Blöcke wieder
  zusammen.

  ![Die Dateiliste](images/files.de.png)

  *Die Liste nach dem Öffnen eines Projekts, mit den Prüfzeichen aus
  dem Vorflug und dem Streifen darunter.*
- **Zuordnung & Zeitfenster**: links die Tabellen, rechts der Player.
  Erscheint mit den Dateien.

  Neben dem Player ermittelt der Knopf **Sprecher trennen**, wer wann
  spricht, auf diesem Rechner. Die Stimmen stehen danach in einer
  eigenen Tabelle unter der Zuordnungstabelle
  ([Spracherkennung und Sprechertrennung](speech.de.md)).

  ![Zuordnungstabelle und Player](images/assignment.de.png)

  *Oben, welche Aufnahme zu welcher Kamera gehört, unten, was aus
  jeder Kamera wird.*
- **Resolve-Schnitt**: eine Zeile, die sagt, ob Resolve antwortet, mit
  dem Weg zu den Einstellungen daneben. Dann das Zeitfenster, die Werte
  für den Kameraschnitt und der Kasten **Sprecher**, dessen Überschrift
  die Quelle der Sprecher nennt. Zuletzt der Kasten
  **Kameraschnitt -- Vorschau** mit Schnittband und abspielbarer
  Vorschau.

  Beide hinteren Reiter stehen mit und ohne getrennte Spuren da. Ohne sie
  zeigt die Zuordnungsspalte grau „in alle Kameras“, und Regler und
  Vorschau für den Kameraschnitt weichen einer Zeile, die das sagt.
- **Ausgabe**: erscheint, sobald etwas läuft, in denselben Farben wie
  das Terminal, mit den Knöpfen **Ergebnis-Ordner öffnen** und
  **Resolve-Projekt anlegen**.

**Multitrack (je Sprecher eine Spur)** hat eine eigene Zeile über dem
Auphonic-Kasten. Eine Spur je Sprecher ist die Grundlage für den
Kameraschnitt, mit auphonic.com oder ohne; nach dem API Key fragt das
Programm erst auf dem Weg über auphonic.com.

**Sprache** neben dem Produktionsnamen ist die in der Aufnahme gesprochene
Sprache, vorbelegt aus der Systemsprache. Sie wird zur Kennzeichnung der
geschriebenen Tonspur und sagt auphonic.com, was es beim Transkribieren
erwarten soll. „nicht gesetzt“ lässt die Spur ungekennzeichnet und
überlässt der Erkennung die Sprache.

**Probelauf** ist der Lauf, der misst und berichtet, aber nichts schreibt.
Er und **Start** bleiben gesperrt, solange etwas offen ist, und
**daneben steht, was**:

- keine Dateien,
- kein Produktionsname,
- weniger als zwei Aufnahmen für Multitrack,
- eine Aufnahme ohne Sprechernamen,
- alle Aufnahmen unter demselben Namen,
- zwei Kameras mit derselben Ausgabedatei.

Das Feld oder die Zeile, die gemeint ist, wird rot. Ein Häkchen hinter
einem Reiter heißt: dort ist nichts mehr offen.

Dann eine Zusammenfassung: wie viele Kameras und Tonspuren, wie lang, welches
Preset, wie viele Dateien entstehen, wieviel Platz sie brauchen und wieviel
frei ist. Wenn der Lauf bestehende Dateien überschreiben würde, zeigt ein
Fenster erst, welche.

Der Player hat Abspielen und Pause, sekunden- und frameweise vor und
zurück, Lautstärke und Tempo; links der Timecode, rechts die Position, ab
dem In-Punkt gezählt.

- Ein Klick auf eine Tabellenzeile holt die Datei an dieselbe Stelle im
  Geschehen, so lassen sich zwei Kameras vergleichen. Gespielt wird die
  zugeordnete Aufnahme, nicht der Kameraton.
- In-Punkt und Out-Punkt nehmen die Stelle aus dem Bild, ein blauer
  Streifen zeigt das Fenster, und beim Ziehen laufen nur die Zahlen mit.
  Solange die Zeitachse fehlt, sind sie gesperrt.
- Formate, die der Rechner nicht abspielen kann (MXF, R3D, manche
  ProRes-Spielarten), bekommen einen Knopf für `ffplay`.

Die Ausgabe landet zusätzlich in `videopodcast-magic.log` neben dem Script,
mit Fassung, Zeit und Rechner in der Kopfzeile und einer Trennlinie je Lauf;
vom vorletzten Lauf bleibt `videopodcast-magic_1.log`. Auch was Qt und ffmpeg
an Python vorbei ausgeben, steht darin.

Neben **Start** läuft **ein Balken für alles Ausstehende**, mit einer
Zeile daneben, woran gerade gearbeitet wird; er läuft immer nur vorwärts.
Er deckt beide Hälften ab: das Messen nach jeder Änderung an der
Dateiliste und den Lauf selbst. Zu diesem Messen gehören Hüllkurven,
Kameraton, Kanäle und die Prüfung, und eine Hüllkurve ist die Lautheit
über die Länge einer Spur.

Ein Abschnitt, der echte Prozente meldet, nimmt den Balken mit. Bei einem
Abschnitt, der nichts meldet, kriecht er langsam weiter und bleibt vor
dem Ende stehen.

### Was hinter Einstellungen ... steht

Der Knopf **Einstellungen ...** sitzt im Fußbereich, neben **Start**.
Dahinter steht, was man einmal einrichtet und dann nicht mehr anfasst:
der Schlüssel für auphonic.com samt Häkchen, das ihn ablegt, und ob
Resolve antwortet. Das Preset und die Transkription gehören zur
Produktion und stehen dort, wo über die Spuren entschieden wird: unter
der Zuordnungstabelle.

Das Fenster hinter dem Knopf hat zwei Kästen.

- **Zugang zu auphonic.com**: das Feld für den API Key und das Häkchen,
  das ihn behält (**Im Schlüsselbund speichern** auf dem Mac, **In der
  Registry speichern** unter Windows). **Verbinden** prüft den Schlüssel
  und holt die Presets.
- **Verbindung zu Resolve**: ob Resolve antwortet, mit Fassung, wenn ja,
  und den Gründen, wenn nein. **Erneut prüfen** fragt noch einmal, das
  Öffnen des Fensters ebenso.
  [DaVinci Resolve](resolve.de.md) sagt, was ein Nein bedeutet.

![Das Einstellungsfenster](images/settings.de.png)

*Hinter Einstellungen ...: der Schlüssel für auphonic.com, und ob
Resolve antwortet.*

## Alles über Menü oder Taste erreichen

Die Menüleiste trägt vier Menüs: **Datei**, **Ansicht**, **Wiedergabe**
und **Hilfe**. **Hilfe** enthält den Weg in dieses Handbuch, **Was sich
in dieser Fassung geändert hat**, **Nach Update suchen ...** und **Über
Video Podcast Magic**.

Auf dem Mac sitzt die Menüleiste oben am Bildschirmrand, sonst oben im
Fenster. **Einstellungen ...** wandert dort ins Programmmenü und steht
sonst überall unter **Datei**.

Alles, was über einen Knopf geht, geht auch über eine Taste. Die Tasten
ohne Zusatztaste gehören dem Player und wirken nur, solange er den
Fokus hat.

| Taste | Was sie tut |
|---|---|
| `Cmd+O` | Dateien hinzufügen |
| `Cmd+Rückschritt` | Das Ausgewählte entfernen |
| `Cmd+Umschalt+O` | Ausgabeordner wählen |
| `Cmd+R` | Start |
| `Cmd+Umschalt+R` | Probelauf |
| `Cmd+1` `Cmd+2` `Cmd+3` | Auf diesen Reiter |
| `Cmd+,` | Einstellungen |

Im Player:

| Taste | Was sie tut |
|---|---|
| `Leertaste` | Abspielen und anhalten |
| `L` | Vorwärts abspielen, mit jedem Druck doppelt so schnell |
| `K` | Anhalten, zurück auf 1× |
| `Links` `Rechts` | Ein Frame |
| `Umschalt+Links` `Umschalt+Rechts` | Eine Sekunde |
| `Alt+Links` `Alt+Rechts` | Zehn Sekunden |
| `I` `O` | In-Punkt setzen, Out-Punkt setzen |
| `Umschalt+I` `Umschalt+O` | Zum In-Punkt, zum Out-Punkt springen |

`L` verdoppelt bis 8×, und das Tempo steht am Vorlauf-Knopf. Der Player
hat kein `J`: Qt spielt hier nichts rückwärts, gemessen.

Unter Windows und Linux steht `Strg` statt `Cmd`. Es ist die Belegung,
die die Schnittprogramme gemeinsam haben.

## Sich selbst aktuell halten

Kurz nachdem das Fenster steht, fragt das Programm github.com, ob es eine
neuere Fassung gibt. Es sieht nur dann nach, nicht während eines Laufs.
Das ist eine Frage nach einer Nummer.

Wenn es eine gibt, nennt ein Fenster sie und die Fassung, die hier läuft.
Es zeigt, was sich in der neuen Fassung geändert hat, in ihren eigenen
Worten, und darunter die Adresse. Zwei Knöpfe:

- **Später** lässt die laufende Fassung an ihrem Platz.
- **Aktualisieren** holt die neue Fassung, setzt sie an die Stelle der
  Datei und startet das Programm neu.

Das Programm liest, was herunterkommt, bevor es das benutzt: es muss
lesbarer Text sein, es muss wie dieses Programm aussehen, und es muss
sich übersetzen lassen. Wenn eine der drei Prüfungen fehlschlägt, bleibt
die Datei liegen, die funktioniert, und das Fenster sagt, was nicht
stimmte.

Die Fassung, die lief, bleibt als `videopodcast-magic.py.old` neben der
neuen liegen. **Hilfe > Zurück auf 2.3.0-beta** setzt sie wieder ein;
der Eintrag nennt die Nummer aus dieser Datei und steht nur im Menü,
solange die Datei da ist.

Es wird vorher gefragt, und die aufbewahrte Datei muss dieselben drei
Prüfungen bestehen wie das, was herunterkommt. Danach startet das
Programm neu. Die Datei ist damit aufgebraucht, und vorwärts geht es
wieder über das Update aus dem Netz.

Das Häkchen **Nicht mehr nachfragen** hält das Programm davon ab, von
selbst nachzusehen. Über **Hilfe > Nach Update suchen ...** geht es
weiterhin.

## Wie die Zeitachse ohne Timecode entsteht

Wenn eine Datei keinen Timecode trägt, misst die Oberfläche im
Hintergrund, wo sie liegt, mit dem Verfahren des Laufs selbst. Danach
springt der Player zwischen den Dateien auf dieselbe Stelle im Geschehen,
und In-Punkt und Out-Punkt gelten für alle gleich.

Ein einziger Timecode genügt, um die Achse daran zu hängen; ohne jeden zählt
sie ab dem Anfang des Materials und wird als virtueller Timecode angezeigt.

Die Achse steht in der Projektdatei, mit Größe und Änderungszeit jeder
Datei, und der nächste Start übernimmt sie. Dateien, die nicht dazu
passen, erscheinen rot. Mehr über die Projektdatei steht in
[camera-cut.de.md](camera-cut.de.md).

## Wenn etwas klemmt

- **Start** bleibt gesperrt: die Zeile daneben nennt, was fehlt, und das
  gemeinte Feld oder die gemeinte Zeile wird rot. Ist das nachgetragen,
  gibt der Knopf sich frei.
- **Der Player zeigt kein Bild**: an seine Stelle tritt ein Knopf, der
  die Datei an `ffplay` übergibt; das öffnet ein eigenes Fenster.
- **In-Punkt und Out-Punkt sind gesperrt**: das Programm misst die
  Zeitachse noch. Der Balken neben **Start** sagt, was gerade läuft.
- **Das Update ging nicht durch**: die Datei, die funktioniert, bleibt
  liegen, und das Fenster sagt, was nicht stimmte. **Hilfe > Nach Update
  suchen ...** versucht es noch einmal.
- **Beim Nachfragen mitschicken**: die Fassung aus `--version`, das
  Betriebssystem, `videopodcast-magic.log` und was man vorhatte, vor
  den Einzelheiten des Fehlers.

Das ist das ganze Fenster. Im nächsten Kapitel, [Vorflug](preflight.de.md),
geht es um die Prüfungen vor einem Lauf und um die Bedeutung jedes
Prüfzeichens in der Dateiliste.

### Weitere Optionen über die Kommandozeile

Im Fenster gibt es diese Optionen nicht.

`--update-check` holt das ungefragte Nachsehen zurück, nachdem das
Häkchen **Nicht mehr nachfragen** gesetzt wurde.

`--no-update-check` setzt dasselbe Nein wie dieses Häkchen. Ein Lauf von
der Kommandozeile sieht ohnehin nicht nach: aus einem Script gestartet,
darf er an keiner Frage stehen bleiben.

`VPM_NO_UPDATE_CHECK` in der Umgebung schaltet das Ganze ab, den
Menüeintrag mit. Der Eintrag sagt das dann, statt nachzusehen. Diese
Variable setzt, wer die Maschine betreibt.

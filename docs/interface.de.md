# Die Oberfläche

*In English: [The interface](interface.md). Zurück zum [Inhalt](README.de.md).*

## Die Oberfläche

Vier Reiter, in der Reihenfolge, in der man sie braucht. Der Knopf
**Einstellungen ...** sitzt im Fußbereich, neben **Start**. Dahinter steht, was
man einmal einrichtet und dann nicht mehr anfasst: der Schlüssel für
auphonic.com samt Häkchen, das ihn ablegt, und ob Resolve antwortet. Was zur
Produktion gehört -- das Preset, die Transkription -- steht dort, wo über die
Spuren entschieden wird: unter der Zuordnungstabelle.

Das Fenster hinter dem Knopf hat zwei Kästen.

- **Zugang zu auphonic.com** -- das Feld für den API Key, das Häkchen,
  das ihn behält (**Im Schlüsselbund speichern** auf dem Mac, **In der
  Registry speichern** unter Windows) und **Verbinden**, das den
  Schlüssel prüft und die Presets holt.
- **Verbindung zu Resolve** -- ob Resolve antwortet, mit Version, wenn
  ja, und den Gründen, wenn nein. **Erneut prüfen** fragt noch einmal,
  das Öffnen des Fensters ebenso.

![Das Einstellungsfenster](images/settings.de.png)

*Hinter Einstellungen ...: der Schlüssel für auphonic.com, und ob
Resolve antwortet.*

- **Dateien & Produktion** -- oben die Dateiliste, darunter ein schmaler
   Streifen mit Produktionsname, gesprochener Sprache und Ausgabeordner.
   Dateien oder ganze Ordner hineinziehen, hinzufügen oder ein früheres
   Projekt öffnen; solange die Liste leer ist, steht dort eine Ablegefläche,
   die den Ablauf erklärt.

   Jede Datei bekommt ein Prüfzeichen aus dem Vorflug, der schon beim
   Hinzufügen läuft: ✓ nichts zu bemängeln, ! ein Hinweis, ✕ so geht es
   nicht. Unter der Liste steht das Ergebnis in einem Satz.

   **Projekt öffnen ...** steht nur auf der Ablegefläche. Umgekehrt lassen sich
   zu einem geöffneten Projekt jederzeit Dateien dazunehmen.

   Eine Datei mit mehr als einem Kanal sagt darunter, was aus ihr wird:
   je Kanal eine Zeile, mit einem Haken, der
   **mit Channel 2 zusammenlegen** anbietet, und daneben, was gemessen
   wurde. Kanäle, in denen nichts steht, werden benannt und bleiben aus
   allem Weiteren heraus.

   Eine einzelne Fortsetzungsdatei lässt sich für sich entfernen. Sie
   bleibt dann draußen, obwohl sie im Ordner liegt, und später wieder
   hinzugefügt ist sie eine eigene Aufnahme. Erst wenn die ganze Aufnahme
   entfernt und wieder hinzugefügt wird, gehören die Blöcke wieder
   zusammen.

   ![Die Dateiliste](images/files.de.png)

   *Die Liste nach dem Öffnen eines Projekts, mit den Prüfzeichen aus
   dem Vorflug und dem Streifen darunter.*
- **Zuordnung & Zeitfenster** -- links die Tabellen, rechts der Player.
   Erscheint mit den Dateien.

   Neben dem Player ermittelt der Knopf **Sprecher trennen**, wer wann
   spricht, auf diesem Rechner und ohne Hochladen; die Stimmen stehen
   danach in einer eigenen Tabelle unter der Zuordnungstabelle
   ([Spracherkennung und Sprechertrennung](speech.de.md)).

   ![Zuordnungstabelle und Player](images/assignment.de.png)

   *Oben, welche Aufnahme zu welcher Kamera gehört, unten, was aus
   jeder Kamera wird.*
- **Resolve-Schnitt** -- eine Zeile, die sagt, ob Resolve antwortet, mit
   dem Weg zu den Einstellungen daneben, das Zeitfenster, die Werte für
   den Kameraschnitt, der Kasten **Sprecher**, dessen Überschrift die
   Quelle der Sprecher nennt, und der Kasten
   **Kameraschnitt -- Vorschau** mit Schnittband und abspielbarer Vorschau.

   Beide hinteren Reiter stehen mit und ohne getrennte Spuren da. Ohne sie
   zeigt die Zuordnungsspalte grau „in alle Kameras", und Regler und Vorschau
   für den Kameraschnitt weichen einer Zeile, die das sagt.
- **Ausgabe** -- erscheint, sobald etwas läuft, in denselben Farben wie das
   Terminal, mit den Knöpfen **Ergebnis-Ordner öffnen** und
   **Resolve-Projekt anlegen**.

**Multitrack (je Sprecher eine Spur)** hat eine eigene Zeile über dem
Auphonic-Kasten und braucht keinen API Key: eine Spur je Sprecher ist die
Grundlage für den Kameraschnitt, mit auphonic.com oder ohne.

**Sprache** neben dem Produktionsnamen ist die in der Aufnahme gesprochene
Sprache, vorbelegt aus der Systemsprache. Sie wird zur Kennzeichnung der
geschriebenen Tonspur und sagt auphonic.com, was es beim Transkribieren
erwarten soll. „nicht gesetzt" lässt die Spur ungekennzeichnet und überlässt
der Erkennung die Sprache.

**Start** und **Probelauf** bleiben gesperrt, solange etwas offen ist --
und **daneben steht, was**:

- keine Dateien,
- kein Produktionsname,
- zu wenige Aufnahmen für Multitrack,
- eine Aufnahme ohne Sprechernamen,
- alle Aufnahmen unter demselben Namen,
- zwei Kameras mit derselben Ausgabedatei.

Das Feld oder die Zeile, die gemeint ist, wird rot. Ein Haken hinter
einem Reiter heißt: dort ist nichts mehr offen.

Dann eine Zusammenfassung: wie viele Kameras und Tonspuren, wie lang, welches
Preset, wie viele Dateien entstehen, wieviel Platz sie brauchen und wieviel
frei ist. Würden bestehende Dateien überschrieben, zeigt ein Fenster erst,
welche.

Der Player hat Abspielen und Pause, sekunden- und bildweise vor und
zurück, Lautstärke und Tempo; links der Timecode, rechts die Position, ab
dem In point gezählt.

- Ein Klick auf eine Tabellenzeile holt die Datei an dieselbe Stelle im
  Geschehen, so lassen sich zwei Kameras vergleichen. Gespielt wird die
  zugeordnete Aufnahme, nicht der Kameraton.
- In point und Out point nehmen die Stelle aus dem Bild, ein blauer
  Streifen zeigt das Fenster, und beim Ziehen laufen nur die Zahlen mit.
- Formate, die der Rechner nicht abspielen kann (MXF, R3D, manche
  ProRes-Spielarten), bekommen einen Knopf für `ffplay`.

Die Ausgabe landet zusätzlich in `videopodcast-magic.log` neben dem Script,
mit Version, Zeit und Rechner in der Kopfzeile und einer Trennlinie je Lauf;
vom vorletzten Lauf bleibt `videopodcast-magic_1.log`. Auch was Qt und ffmpeg
an Python vorbei ausgeben, steht darin.

Neben **Start** läuft **ein Balken für alles Ausstehende**, mit einer
Zeile daneben, woran gerade gearbeitet wird. Er deckt beide Hälften ab:
das Messen nach jeder Änderung an der Dateiliste -- Hüllkurven,
Kameraton, Kanäle, die Prüfung -- und den Lauf selbst. Wo ein Abschnitt
echte Prozente meldet, folgt der Balken ihnen; wo einer nichts meldet,
kriecht er langsam weiter und bleibt vor dem Ende stehen. Rückwärts geht
er nie.

## Menü und Tasten

Die Menüleiste trägt, wofür im Fenster kein Platz ist und was das
System dort erwartet: **Über das Programm**, **Einstellungen** und
**Hilfe** mit dem Weg in dieses Handbuch. Auf dem Mac sitzt sie oben am
Bildschirmrand, sonst oben im Fenster.

Alles, was über einen Knopf geht, geht auch über eine Taste. Die Tasten
ohne Zusatztaste gehören dem Spieler und wirken nur, solange er den
Fokus hat -- sonst setzte ein bloßes `I` den In-Punkt, während jemand
gerade einen Namen in ein Feld tippt.

| Taste | Was sie tut |
|---|---|
| `Cmd+O` | Dateien hinzufügen |
| `Cmd+Rückschritt` | Das Ausgewählte entfernen |
| `Cmd+Umschalt+O` | Ausgabeordner wählen |
| `Cmd+R` | Start |
| `Cmd+Umschalt+R` | Probelauf |
| `Cmd+1` `Cmd+2` `Cmd+3` | Auf diesen Reiter |
| `Cmd+,` | Einstellungen |

Im Spieler:

| Taste | Was sie tut |
|---|---|
| `Leertaste` | Abspielen und anhalten |
| `Links` `Rechts` | Ein Einzelbild |
| `Umschalt+Links` `Umschalt+Rechts` | Eine Sekunde |
| `Alt+Links` `Alt+Rechts` | Zehn Sekunden |
| `I` `O` | In-Punkt setzen, Out-Punkt setzen |
| `Umschalt+I` `Umschalt+O` | Zum In-Punkt, zum Out-Punkt springen |

Unter Windows und Linux steht `Strg` statt `Cmd`. Es ist die Belegung,
die die Schnittprogramme gemeinsam haben -- wer schneidet, muss nichts
umlernen.

## Sich selbst aktuell halten

Kurz nachdem das Fenster steht -- nicht beim Start und nie während eines
Laufs -- fragt das Programm github.com, ob es eine neuere Fassung gibt.
Das ist eine Frage nach einer Nummer, gesendet wird nichts.

Gibt es eine, nennt ein Fenster sie und die Fassung, die hier läuft.
Hinter **Details einblenden** steht, was sich in der neuen Fassung
geändert hat, in ihren eigenen Worten, und darunter die Adresse. Zwei
Knöpfe:

- **Später** ändert nichts.
- **Aktualisieren** holt die neue Fassung, setzt sie an die Stelle der
  Datei und startet das Programm neu.

Was herunterkommt, wird gelesen, bevor es benutzt wird: es muss lesbarer
Text sein, es muss wie dieses Programm aussehen, und es muss sich
übersetzen lassen. Ist es das nicht, bleibt die Datei liegen, die
funktioniert, und das Fenster sagt, was nicht stimmte.

Die Fassung, die lief, bleibt als `videopodcast-magic.py.old` neben der
neuen liegen. Erweist sich die neue als falsch, bekommt diese Datei
wieder ihren alten Namen; Netz braucht es dafür nicht.

Das Häkchen **Nicht mehr nachfragen** hält das Programm davon ab, von
selbst nachzusehen. Über **Hilfe > Jetzt nach einer neueren Fassung
sehen** geht es weiterhin, und `--update-check` auf der Kommandozeile
holt das ungefragte Nachsehen zurück.

Die Kommandozeile fragt nie. Ein Lauf aus einem Skript sieht nicht nach
und bleibt für keine Frage stehen; `--no-update-check` setzt dort
dasselbe Nein wie das Häkchen, `--update-check` nimmt es zurück.

`VPM_NO_UPDATE_CHECK` in der Umgebung schaltet das Ganze ab, den
Menüeintrag mit -- der sagt das dann, statt nachzusehen. Diese Variable
setzt, wer die Maschine betreibt.

## Zeitachse ohne Timecode

Trägt eine Datei keinen Timecode, misst die Oberfläche im Hintergrund, wo
sie liegt -- mit dem Verfahren des Laufs selbst. Danach springt der Player
zwischen den Dateien auf dieselbe Stelle im Geschehen, und In point und
Out point gelten für alle gleich.

Ein einziger Timecode genügt, um die Achse daran zu hängen; ohne jeden zählt
sie ab dem Anfang des Materials und wird als virtueller Timecode angezeigt.
Solange die Achse fehlt, sind In point und Out point gesperrt.

Die Achse steht in der Projektdatei, mit Größe und Änderungszeit jeder Datei,
und wird beim nächsten Start übernommen; was sonst noch darin steht, sagt
[camera-cut.de.md](camera-cut.de.md). Dateien, die nicht dazu passen,
erscheinen rot.

# Der einfache Fall

*In English: [The simple path](simple-path.md). Zurück zum [Inhalt](README.de.md).*

## Der einfache Fall

Der einfache Weg ist der Lauf ohne das Häkchen **Multitrack (je Sprecher
eine Spur)**. Es steht im Kasten **Produktion** auf dem Reiter
**Dateien & Produktion** und ein zweites Mal über den Tabellen auf dem
Reiter **Zuordnung & Zeitfenster**.

Beide Wege schreiben dieselbe Art Datei: MOV, Bild umkopiert, Ton
unkomprimiert, der `colr`-Block und die QuickTime-Schlüssel der Kamera
mitgenommen.

Was der einfache Weg genauso kann wie Multitrack:

- **Zeitfenster.** Die Knöpfe **In markieren** und **Out markieren**
  wirken auch hier (auf der Kommandozeile `--in-point` und `--out-point`),
  in den Schreibweisen aus [multitrack.de.md](multitrack.de.md), Abschnitt
  „Zeitfenster". Beschnitten wird der Ton; das Bild bleibt ganz und behält
  seinen Timecode.
- **Vorschau Player.** Derselbe Reiter, dieselben Knöpfe.
- **Resolve-Projekt.** Mehrere Kameras geben eine Timeline mit allen
  nebeneinander, fertig für Multicam; eine Kamera eine gerade.

Es fehlen Kameraschnitt, Sprechzeiten und Schnittprognose: die brauchen je
Sprecher eine Spur.

Was herauskommt, hängt am Material:

- **Nur Ton.** Fortsetzungsdateien werden zusammengesetzt und geschrieben.
- **Ton und Bild.** Der Ton wird ausgerichtet und in die Videodatei gelegt.
- **Nur ein Video.** Dessen eigener Ton, links und rechts getrennt.

### Die Einzelaufnahmen neben dem Mix

Ohne Multitrack geht aller Ton in eine Spur. Liefen mehrere Aufnahmen
gleichzeitig, geht jede davon zusätzlich als eigene Spur ins Video,
hinter dem Mix, auf derselben Achse und in derselben Länge.

Ob sie gleichzeitig liefen, liest der Lauf am Timecode ab. Aufnahmen, die
sich überlappen, waren mehrere Mikrofone gleichzeitig. Blöcke, die
aufeinander folgen, sind eine Aufnahme und bekommen keine zusätzlichen
Spuren.

Die Einzelspuren sind unbearbeitet: nur der Mix geht zu auphonic.com,
also kein De-Bleed und kein Leveler auf ihnen. Sie kosten rund 520 MB je
Spur und Stunde. Kommt der Mix von auphonic.com in anderer Länge zurück
als sie haben — etwa mit vorangestelltem Jingle im Gratis-Tarif — fallen
sie von selbst weg, und der Lauf sagt es.

Fortsetzungsdateien findet das Script selbst; der erste nummerierte Block
genügt. Als Fortsetzung gilt nur, was lückenlos anschließt — geprüft am
Timecode, sonst an der Blockgröße. Ein späterer Take mit derselben
Namensform wird nicht angehängt.

Der Versatz wird immer gemessen, auch wenn beide Seiten Timecode tragen.
Liegt er beidseitig vor, sagt der Lauf am Ende, wie weit er vom gemessenen
Wert abweicht.

### Blöcke mit Uhrzeit statt Zähler

Namen mit Datum und Uhrzeit gelten ebenso als Blöcke:
`r_260808_185628.wav` und `r_260808_190128.wav`. Ein Recorder nummeriert
seine Dateien; ein Mischer schreibt oft stattdessen die Uhrzeit.

Der nächste Block gehört dazu, wenn er dort beginnt, wo der vorige endet,
auf zwei Sekunden genau. Wo jeder Block dieselbe Uhrzeit trägt — den
Beginn der Session, mit der echten Nummer dahinter — gilt weiter die
Zähler-Regel.

### Blöcke von Hand zusammenlegen

Wo die Dateinamen der Suche nichts hergeben, trägt die Aufnahme in der
Dateiliste auf dem Reiter **Dateien & Produktion** ein Auswahlfeld
**gehört zu**. Es legt diese Aufnahme in eine andere, mit allen Blöcken,
die sie hat (auf der Kommandozeile `--together A B C`, in dieser
Reihenfolge, wiederholbar für mehrere). Jeder genannte Name bringt die
Blöcke mit, die ohnehin schon zu ihm gehören.

Die Gegenrichtung: die Zeile des Blocks in der Dateiliste auswählen und
**Entfernen** drücken — er bleibt dann aus der gefundenen Aufnahme
draußen (auf der Kommandozeile `--apart`). Beides schlägt die Messung.
Eine für sich gestellte Datei bleibt auch aus einer Gruppe draußen, in
die sie gelegt wurde. Beides steht im Projekt.

### Je Videodatei

Jede Videodatei kommt zurück mit unverändertem Bild (`-c:v copy`), dem
neuen Ton als erster Spur und der Kameraspur dahinter, beide benannt und
der Timecode erhalten.

### Warum MOV

Ziel ist immer MOV, auch bei MP4-Quellen; neu berechnet wird dabei nichts.
MOV trägt die Spurnamen und den unkomprimierten Ton, MP4 beides nicht.
`--container` gibt es nicht.

### Weitere Optionen über die Kommandozeile

Diese Optionen gibt es im Fenster nicht.

- `--no-single-tracks` lässt die Einzelaufnahmen aus dem Video weg.
- `--no-camera-audio` lässt die eigene Spur der Kamera aus der neuen
  Datei weg.
- `--help` kennzeichnet jeden Schalter mit `[simple path only]` oder
  `[multitrack only]`. Beide Marker bleiben englisch, auch bei
  `--lang de`.

# Multitrack: mehrere Sprecher, mehrere Kameras

*In English: [Multitrack: several speakers, several cameras](multitrack.md). Zurück zum [Inhalt](README.de.md).*

## Multitrack: mehrere Sprecher, mehrere Kameras

Mehrere Leute am Tisch, jeder mit einem Mikrofon, auf dem alle zu hören
sind. Dieses Übersprechen aus dem Ton zu nehmen ist das Einzige, was nur
auphonic.com kann. `--without-auphonic` macht den Rest lokal:
ausgerichtet, gemischt, Lautheit gesetzt, Kameraschnitt inbegriffen — nur
ohne De-Bleed, Leveler und Rauschentfernung.

Davor kommt alles auf eine gemeinsame Zeitachse, Uhrengang eingerechnet.
Das Fenster kommt allein aus den Kameras; fehlt darin der Ton, wird Stille
eingesetzt. Zeilen mit demselben Sprechernamen werden zu einer Spur
zusammengefasst und über ihren Timecode hintereinandergelegt. Das ist
richtig, wenn die Aufnahme zwischendurch gestoppt wurde.

### Die Zuordnung

Auf dem Reiter „2. Zuordnung & Zeitfenster“ stehen links zwei Tabellen.
Die obere hat je Tonaufnahme eine Zeile: Datei, Sprechername, wohin sie
gehört, Timecode. Das Auswahlfeld listet die Kameras, danach zwei
Sonderfälle:

- **nur in den Mix** — im Full-Mix, aber bei niemandem die erste Spur. Für
  jemanden, der zu hören, aber nicht zu sehen ist.
- **Audio ignorieren** — bleibt ganz außen vor, der Sprechername wird
  grau. Für eine Aufnahme, deren Video noch fehlt.

Die untere Tabelle hat je Kamera eine Zeile: Typ (Inhalt, Vorspann,
Abspann, Video ignorieren), wie die neue Datei heißt, welchen Ton sie
bekommt, das Häkchen für ihren eigenen Ton. Ein Klick auf eine Zeile holt
die Datei in den Player. Dateien, die nicht zur gemessenen Zeitachse
passen, stehen in Rot — hier wie in der Dateiliste.

Über den Tabellen steht das Häkchen **Multitrack** ein zweites Mal. Es
ist dasselbe Häkchen wie unter Produktion und derselbe Wert — klickt man
eines, zeigen beide es. Multitrack will zwei getrennte Aufnahmen, und
eine Kamera zählt als eine, sobald bei ihr **als Spur** gesetzt ist. Auf
der Kommandozeile zählt es genauso und liest dafür die Zuordnungsdatei.

### Ohne getrennte Tonaufnahmen

Sind nur Kameras da — mindestens zwei —, wird ihr eigener Ton zur Spur, je
Kamera eine. Sonst kann eine einzelne Kamera ihren Ton trotzdem
beisteuern: Häkchen **als Spur** in der Spalte „eigener Ton“. Sie bekommt
dann eine Zeile in der oberen Tabelle, mit ihrem Sprechernamen, und zählt
wie jede andere Spur — aufbereitet, im Full-Mix, in der Sprecherstatistik
und als erste Tonspur ihrer eigenen Kamera. Ohne Multitrack hätte der
Lauf bei reinem Kameramaterial nichts hineinzulegen und bräche ab.

„Wie jede andere Spur“ schließt die Kanäle ein. Das Häkchen sagt nicht
mehr als „diesen Ton nicht wegwerfen“; was daraus wird, entscheidet
dieselbe Messung wie bei einer Recorder-Datei. Eine Kamera, deren zwei
Kanäle zwei Ansteckmikrofone tragen — die DJI Osmo macht das —, ergibt
zwei Zeilen mit zwei Sprechernamen, beurteilt und geschnitten wie eine
zweikanalige Recorder-Datei. Eine Kamera mit einem echten Stereopaar
behält es als eine zweikanalige Spur. Auf der Kommandozeile geschieht
dasselbe ohne Oberfläche: `videopodcast-magic.py Osmo.mov Weitwinkel.mov
--multitrack` liest die Osmo als zwei Sprecher und den Weitwinkel als einen
— und schreibt trotzdem je Kamera eine Datei.

Zu welcher Kamera so eine Spur gehört, ist eine eigene Frage, und das
Auswahlfeld beantwortet sie: ein Ansteckmikrofon, das in einer Kamera
steckt, heißt nicht, dass diese Kamera die Person filmt. Die Kamera, aus
der der Ton kommt, ist die Vorauswahl, mehr nicht.

### Vorarbeit im Hintergrund

Den Kameraton herauszuziehen und die Hüllkurve zu lesen dauert bei langen
4K-Dateien Minuten. Beides beginnt, sobald die Tabelle steht, bis zu vier
Dateien gleichzeitig, angezeigt als ein Balken unter den Tabellen.
Weiterarbeiten geht derweil; wer zu früh auf Start drückt, wartet nur
kurz.

### Mehrere Dateien gleichzeitig

Auch der Lauf arbeitet parallel: mehrere Kameradateien gleichzeitig. Der
Bericht jeder Datei erscheint am Stück, sobald sie fertig ist, unter einem
gemeinsamen Balken. `--parallel COUNT` legt die Zahl fest: `0` — die
Voreinstellung — entscheidet selbst, `1` nimmt eine Datei nach der
anderen. Die geschriebenen Dateien sind in beiden Fällen byteweise
identisch.

Wird eine Datei aus der Liste entfernt, fliegt sie aus der Warteschlange,
ihre Hüllkurve wird vergessen und die schon herausgezogene Tondatei
gelöscht. Sonst bleiben die Hüllkurven im Ablageordner des Systems
(`~/Library/Caches/videopodcast-magic/envelopes/`, unter Windows
`%LOCALAPPDATA%`), benannt nach Pfad, Größe und Änderungszeit der
Quelldatei. Was älter als dreißig Tage ist, wird beim Start weggeräumt.

### Zeitfenster

Voreingestellt reicht das Fenster so weit wie die Kameras. In point und
Out point setzen es enger:

| Angabe        | Bedeutung                      |
|---------------|--------------------------------|
| `17:20:14`    | absolut, Uhrzeit               |
| `17:20:14:00` | absolut, mit Bildern           |
| `+12:30`      | ab Anfang des Fensters         |
| `90`          | dasselbe, in Sekunden          |
| `-30`         | bei Out point: vom Ende zurück |

Auf der Kommandozeile `--in-point` und `--out-point`. In der Oberfläche
kommen beide aus dem Player: anhalten, wo es anfangen soll, „In markieren“
drücken. Unter dem Bild stehen vier Knöpfe: „In markieren“ und
„Out markieren“ setzen die Grenzen, „zu In point“ und „zu Out point“
springen sie wieder an. Der Reiter „3. Resolve-Schnitt“ wiederholt beides
als Zeile: In point, Out point, Dauer.

Gesperrt sind die Knöpfe nur, solange die gemeinsame Zeitachse fehlt.
Danach gelten sie für alle Dateien gleich, auch für die ohne Timecode.

### Was in die Kameradateien kommt

Erste Tonspur jeder Kameradatei ist die Mischung genau der Sprecher in
diesem Bild — `Mix <A> + <B>`, bei nur einem sein Name. Danach dieselben
Sprecher einzeln, dann `Full-Mix (…)`, zuletzt `Camera Original`. Die
Lautheit wird über die Summe bestimmt und auf alle Spuren gleich
angewendet, damit die Verhältnisse bleiben (`--lufs`, voreingestellt −16).

Die Spuren werden außerdem als Dateien abgelegt, in `auphonic-tracks/` als
`final_<Name>_<Timecode>.wav` — Timecode im Namen und im bext-Block, dazu
iXML für Premiere und Media Composer.

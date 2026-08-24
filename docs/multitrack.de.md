# Multitrack: mehrere Sprecher, mehrere Kameras

*In English: [multitrack.md](multitrack.md). Zurück zum
[Inhalt](README.de.md).*

## Was Multitrack tut

Mehrere Leute am Tisch, jeder mit einem Mikrofon, auf dem alle zu hören
sind. Dieses Übersprechen aus dem Ton zu nehmen ist das Einzige, was nur
auphonic.com kann.

Multitrack ist der Weg für eine Spur je Person. Wenn alle auf einer
gemeinsamen Aufnahme sind, übernimmt die Sprechertrennung
([Spracherkennung und Sprechertrennung](speech.de.md)).

Alles andere läuft lokal. [Aufbereitung über auphonic.com](auphonic.de.md)
beschreibt den Weg dahin (auf der Kommandozeile `--without-auphonic`). Das
Programm richtet dann den Ton aus, mischt ihn, setzt die Lautheit und baut
den Kameraschnitt. Es lässt De-Bleed, Leveler und Rauschentfernung aus.

Alles kommt auf eine gemeinsame Zeitachse, Uhrengang eingerechnet. Das
Fenster kommt allein aus den Kameras; Lücken darin füllt das Programm
mit Stille. Zeilen mit demselben Sprechernamen werden zu einer Spur
zusammengefasst und über ihren Timecode hintereinandergelegt. Eine
Aufnahme, die zwischendurch gestoppt wurde, kommt am Stück zurück.

### Die Zuordnung setzen

Auf dem Reiter **Zuordnung & Zeitfenster** stehen links zwei Tabellen.
Die obere hat je Tonaufnahme eine Zeile: **Tonaufnahme**,
**Sprechername**, **gehört zu**, Timecode. Das Auswahlfeld **gehört zu**
listet die Kameras, danach zwei Sonderfälle:

- **nur in den Mix**: im Full-Mix, aber bei niemandem die erste Spur. Für
  jemanden, der zu hören, aber nicht zu sehen ist.
- **Audio ignorieren**: bleibt ganz außen vor, der Sprechername wird
  grau. Für eine Aufnahme, deren Video noch fehlt.

Die untere Tabelle hat je Kamera eine Zeile: **Typ** (**Inhalt**,
**Vorspann**, **Abspann**, **Video ignorieren**), **neue Datei heißt**
und **bekommt Audio von**. Die letzte Spalte ist **eigener Ton**, mit
dem Häkchen **als Spur**. Ein Klick auf eine Zeile holt die Datei in den
Player. Dateien, die nicht zur gemessenen Zeitachse passen, stehen in
Rot, hier wie in der Dateiliste.

Unter den Tabellen steht das Häkchen **Multitrack** ein zweites Mal. Es
ist dasselbe Häkchen wie unter **Produktion**: klickt man eines, zeigen
beide es. Multitrack will zwei getrennte Aufnahmen, und eine Kamera zählt
als eine, sobald sie das Häkchen **als Spur** trägt. Auf der Kommandozeile
(`--multitrack`) zählt es genauso.

![Die beiden Tabellen der Zuordnung](images/assignment.de.png)

*Reiter Zuordnung & Zeitfenster: die Aufnahmen mit ihrer Kamera, die
Kameras mit der Spalte eigener Ton, und unter beiden Tabellen das
Häkchen Multitrack und der Kasten für auphonic.com.*

### Kameraton zur Spur machen

Bei reinem Kameramaterial wird der eigene Ton der Kameras zur Spur, je
Kamera eine. Dafür braucht es mindestens zwei Kameras. Ohne Multitrack
hat der Lauf dann nichts hineinzulegen und bricht ab.

Eine einzelne Kamera kann ihren Ton ebenso beisteuern: Häkchen **als
Spur** in der Spalte **eigener Ton**. Sie bekommt dann eine Zeile in der
oberen Tabelle, mit ihrem Sprechernamen. Sie zählt wie jede andere Spur:
aufbereitet, im Full-Mix, in der Sprechzeit für den Kameraschnitt
mitgezählt und als erste Tonspur ihrer eigenen Kamera.

„Wie jede andere Spur“ schließt die Kanäle ein. Das Häkchen bewahrt nur
den Ton; dieselbe Messung wie bei einer Recorder-Datei entscheidet, was
daraus wird.

- **Zwei Ansteckmikrofone auf den zwei Kanälen** ergeben zwei Zeilen mit
  zwei Sprechernamen. Das Programm beurteilt und schneidet sie wie eine
  zweikanalige Recorder-Datei.
- **Ein echtes Stereopaar** bleibt eine zweikanalige Spur.

Das Auswahlfeld **gehört zu** bestimmt, zu welcher Kamera so eine Spur
gehört; die Kamera, aus der der Ton kommt, ist nur die Vorauswahl. Ein
Ansteckmikrofon, das in einer Kamera steckt, heißt nicht, dass diese
Kamera die Person filmt.

### Was das Programm im Hintergrund liest

Das Programm liest Kameraton und Hüllkurve, sobald die Tabelle steht,
bis zu vier Dateien gleichzeitig. Ein Balken unter den Tabellen zeigt
es. Bei langen 4K-Dateien dauert das Minuten. Weiterarbeiten geht
derweil. Das Programm beginnt den Lauf erst, wenn die Vorarbeit fertig
ist.

### Mehrere Dateien gleichzeitig laufen lassen

Auch der Lauf arbeitet parallel: mehrere Kameradateien gleichzeitig. Der
Bericht jeder Datei erscheint am Stück, sobald sie fertig ist, unter einem
gemeinsamen Balken.

**Entfernen** nimmt eine Datei aus der Liste: sie fliegt aus der
Warteschlange, das Programm vergisst ihre Hüllkurve und löscht die schon
herausgezogene Tondatei.

Sonst bleiben die Hüllkurven im Ablageordner des Systems
(`~/Library/Caches/videopodcast-magic/envelopes/`, unter Windows
`%LOCALAPPDATA%`), benannt nach Pfad, Größe und Änderungszeit der
Quelldatei. Beim Start räumt das Programm alles weg, was älter als
dreißig Tage ist.

### Das Zeitfenster setzen

Voreingestellt reicht das Fenster so weit wie die Kameras. So wird der
Anfang gesetzt:

1. Auf dem Reiter **Zuordnung & Zeitfenster** die Zeile der Datei
   anklicken. Sie kommt in den **Vorschau Player**.
2. Das Bild dort anhalten, wo das Fenster anfangen soll.
3. **In markieren** drücken (auf der Kommandozeile `--in-point`).

**Out markieren** setzt die andere Grenze genauso (`--out-point`). **zu
In-Punkt** und **zu Out-Punkt** springen die beiden Marken wieder an.
Der Reiter **Resolve-Schnitt** wiederholt beides als Zeile: In-Punkt,
Out-Punkt, Dauer.

Beide Grenzen nehmen diese Angaben:

| Angabe        | Bedeutung                      |
|---------------|--------------------------------|
| `17:20:14`    | absolut, Uhrzeit               |
| `17:20:14:00` | absolut, mit Bildern           |
| `+12:30`      | ab Anfang des Fensters         |
| `90`          | dasselbe, in Sekunden          |
| `-30`         | bei Out-Punkt: vom Ende zurück |

Die Knöpfe bleiben gesperrt, solange die gemeinsame Zeitachse fehlt.
Danach gelten sie für alle Dateien gleich, auch für die ohne Timecode.

### Was in die Kameradateien kommt

Erste Tonspur jeder Kameradatei ist der Mix genau der Sprecher in diesem
Bild: `Mix <A> + <B>`. Bei nur einem Sprecher ist es sein Name. Danach
dieselben Sprecher einzeln, dann `Full-Mix (…)`, zuletzt
`Camera Original`. Die Lautheit wird über die Summe bestimmt und auf
alle Spuren gleich angewendet, damit die Verhältnisse bleiben.

Die Spuren werden außerdem als Dateien abgelegt, in `auphonic-tracks/`
als `final_<Name>_<Timecode>.wav`. Der Timecode steht im Namen und im
bext-Block, dazu iXML für Premiere und Media Composer.

### Wenn etwas klemmt

- **Eine Zeile steht in Rot.** Der Ton dieser Datei passt nicht zu dem
  der anderen, sie bekommt also keinen Platz auf der gemeinsamen
  Zeitachse. In der Spalte **Typ** den Eintrag **Video ignorieren**
  wählen oder die Datei mit **Entfernen** aus der Liste nehmen.
- **In markieren und Out markieren bleiben gesperrt.** Die gemeinsame
  Zeitachse steht noch nicht. Den Balken unter den Tabellen abwarten.
- **Der Lauf bricht bei reinem Kameramaterial ab.** Multitrack ist aus.
  Das Häkchen **Multitrack** setzen; dann wird jede Kamera zu einer
  eigenen Spur.
- **Ein Sprecher fehlt im Full-Mix.** Bei dieser Zeile steht in der
  Spalte **gehört zu** der Eintrag **Audio ignorieren**.

Die Spuren sind zugeordnet, das Fenster steht, und jede Kameradatei
trägt ihren eigenen Mix. Als Nächstes kommt die Frage, wer was sagt:
[Spracherkennung und Sprechertrennung](speech.de.md).

### Weitere Optionen über die Kommandozeile

Diese Optionen gibt es im Fenster nicht.

- `--parallel COUNT` legt fest, wie viele Kameradateien gleichzeitig
  laufen: `0` ist die Vorgabe und entscheidet selbst, `1` nimmt eine
  Datei nach der anderen. Mehr Dateien, als die Liste hält, laufen auch
  bei einer höheren Zahl nicht. Die geschriebenen Dateien sind in beiden
  Fällen byteweise identisch.
- `--lufs` setzt die Lautheit, auf die die Summe gebracht wird,
  voreingestellt −16. Die üblichen Zielwerte je Plattform stehen im
  [Vorflug](preflight.de.md).

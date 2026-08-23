# Multitrack: mehrere Sprecher, mehrere Kameras

*In English: [Multitrack: several speakers, several cameras](multitrack.md). Zurück zum [Inhalt](README.de.md).*

## Multitrack: mehrere Sprecher, mehrere Kameras

Mehrere Leute am Tisch, jeder mit einem Mikrofon, auf dem alle zu hören
sind. Dieses Übersprechen aus dem Ton zu nehmen ist das Einzige, was nur
auphonic.com kann.

Multitrack ist der Weg für eine Spur je Person. Sind alle auf einer
gemeinsamen Aufnahme, übernimmt die Sprechertrennung
([Spracherkennung und Sprechertrennung](speech.de.md)).

Alles andere läuft lokal. Im Kasten **Aufbereitung bei auphonic.com
(optional)** auf dem Reiter **2. Zuordnung & Zeitfenster** im Auswahlfeld
**Preset:** den Eintrag **ohne Auphonic arbeiten** wählen (auf der
Kommandozeile `--without-auphonic`). Der Lauf ist dann ausgerichtet,
gemischt, Lautheit gesetzt, Kameraschnitt inbegriffen — nur ohne
De-Bleed, Leveler und Rauschentfernung.

Alles kommt auf eine gemeinsame Zeitachse, Uhrengang eingerechnet. Das
Fenster kommt allein aus den Kameras; fehlt darin der Ton, wird Stille
eingesetzt. Zeilen mit demselben Sprechernamen werden zu einer Spur
zusammengefasst und über ihren Timecode hintereinandergelegt. Eine
Aufnahme, die zwischendurch gestoppt wurde, kommt am Stück zurück.

### Die Zuordnung

Auf dem Reiter **2. Zuordnung & Zeitfenster** stehen links zwei Tabellen.
Die obere hat je Tonaufnahme eine Zeile: **Tonaufnahme**,
**Sprechername**, **gehört zu**, Timecode. Das Auswahlfeld **gehört zu**
listet die Kameras, danach zwei Sonderfälle:

- **nur in den Mix** — im Full-Mix, aber bei niemandem die erste Spur. Für
  jemanden, der zu hören, aber nicht zu sehen ist.
- **Audio ignorieren** — bleibt ganz außen vor, der Sprechername wird
  grau. Für eine Aufnahme, deren Video noch fehlt.

Die untere Tabelle hat je Kamera eine Zeile: **Typ** (**Inhalt**,
**Vorspann**, **Abspann**, **Video ignorieren**), **neue Datei heißt**,
**bekommt Audio von** und **eigener Ton** mit dem Häkchen **als Spur**.
Ein Klick auf eine Zeile holt die Datei in den Player. Dateien, die nicht
zur gemessenen Zeitachse passen, stehen in Rot — hier wie in der
Dateiliste.

Über den Tabellen steht das Häkchen **Multitrack** ein zweites Mal. Es
ist dasselbe Häkchen wie unter **Produktion**: klickt man eines, zeigen
beide es. Multitrack will zwei getrennte Aufnahmen, und eine Kamera zählt
als eine, sobald bei ihr **als Spur** gesetzt ist. Auf der Kommandozeile
(`--multitrack`) zählt es genauso.

### Ohne getrennte Tonaufnahmen

Sind nur Kameras da — mindestens zwei —, wird ihr eigener Ton zur Spur,
je Kamera eine. Ohne Multitrack hat der Lauf bei reinem Kameramaterial
nichts hineinzulegen und bricht ab.

Eine einzelne Kamera kann ihren Ton ebenso beisteuern: Häkchen **als
Spur** in der Spalte **eigener Ton**. Sie bekommt dann eine Zeile in der
oberen Tabelle, mit ihrem Sprechernamen, und zählt wie jede andere Spur —
aufbereitet, im Full-Mix, in der Sprechzeit für den Kameraschnitt
mitgezählt und als erste Tonspur ihrer eigenen Kamera.

„Wie jede andere Spur“ schließt die Kanäle ein. Das Häkchen sagt nicht
mehr als: diesen Ton nicht wegwerfen. Was aus dem Ton wird, entscheidet
dieselbe Messung wie bei einer Recorder-Datei.

- **Zwei Ansteckmikrofone auf den zwei Kanälen** ergeben zwei Zeilen mit
  zwei Sprechernamen, beurteilt und geschnitten wie eine zweikanalige
  Recorder-Datei.
- **Ein echtes Stereopaar** bleibt eine zweikanalige Spur.

Zu welcher Kamera so eine Spur gehört, stellt das Auswahlfeld **gehört
zu** ein; die Kamera, aus der der Ton kommt, ist nur die Vorauswahl. Ein
Ansteckmikrofon, das in einer Kamera steckt, heißt nicht, dass diese
Kamera die Person filmt.

### Vorarbeit im Hintergrund

Kameraton und Hüllkurve werden gelesen, sobald die Tabelle steht, bis zu
vier Dateien gleichzeitig, angezeigt als ein Balken unter den Tabellen.
Bei langen 4K-Dateien dauert das Minuten. Weiterarbeiten geht derweil;
wer zu früh auf **Start** drückt, wartet nur kurz.

### Mehrere Dateien gleichzeitig

Auch der Lauf arbeitet parallel: mehrere Kameradateien gleichzeitig. Der
Bericht jeder Datei erscheint am Stück, sobald sie fertig ist, unter einem
gemeinsamen Balken.

**Entfernen** nimmt eine Datei aus der Liste: sie fliegt aus der
Warteschlange, ihre Hüllkurve wird vergessen und die schon
herausgezogene Tondatei gelöscht.

Sonst bleiben die Hüllkurven im Ablageordner des Systems
(`~/Library/Caches/videopodcast-magic/envelopes/`, unter Windows
`%LOCALAPPDATA%`), benannt nach Pfad, Größe und Änderungszeit der
Quelldatei. Was älter als dreißig Tage ist, wird beim Start weggeräumt.

### Zeitfenster

Voreingestellt reicht das Fenster so weit wie die Kameras. Im
**Vorschau Player** auf dem Reiter **2. Zuordnung & Zeitfenster** stehen
unter dem Bild vier Knöpfe: **In markieren** und **Out markieren** setzen
die Grenzen, **zu In-Punkt** und **zu Out-Punkt** springen sie wieder an.
Anhalten, wo es anfangen soll, **In markieren** drücken (auf der
Kommandozeile `--in-point` und `--out-point`). Der Reiter
**3. Resolve-Schnitt** wiederholt beides als Zeile: In-Punkt, Out-Punkt,
Dauer.

Beide Grenzen nehmen diese Angaben:

| Angabe        | Bedeutung                      |
|---------------|--------------------------------|
| `17:20:14`    | absolut, Uhrzeit               |
| `17:20:14:00` | absolut, mit Bildern           |
| `+12:30`      | ab Anfang des Fensters         |
| `90`          | dasselbe, in Sekunden          |
| `-30`         | bei Out-Punkt: vom Ende zurück |

Gesperrt sind die Knöpfe nur, solange die gemeinsame Zeitachse fehlt.
Danach gelten sie für alle Dateien gleich, auch für die ohne Timecode.

### Was in die Kameradateien kommt

Erste Tonspur jeder Kameradatei ist die Mischung genau der Sprecher in
diesem Bild — `Mix <A> + <B>`, bei nur einem sein Name. Danach dieselben
Sprecher einzeln, dann `Full-Mix (…)`, zuletzt `Camera Original`. Die
Lautheit wird über die Summe bestimmt und auf alle Spuren gleich
angewendet, damit die Verhältnisse bleiben.

Die Spuren werden außerdem als Dateien abgelegt, in `auphonic-tracks/` als
`final_<Name>_<Timecode>.wav` — Timecode im Namen und im bext-Block, dazu
iXML für Premiere und Media Composer.

### Weitere Optionen über die Kommandozeile

Diese Optionen gibt es im Fenster nicht.

- `--parallel COUNT` legt fest, wie viele Kameradateien gleichzeitig
  laufen: `0` — die Voreinstellung — entscheidet selbst, `1` nimmt eine
  Datei nach der anderen. Die geschriebenen Dateien sind in beiden Fällen
  byteweise identisch.
- `--lufs` setzt die Lautheit, auf die die Summe gebracht wird,
  voreingestellt −16.

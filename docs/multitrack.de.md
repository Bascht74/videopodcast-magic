# Multitrack: mehrere Sprecher, mehrere Kameras

*In English: [multitrack.md](multitrack.md). Zurück zum
[Inhalt](README.de.md).*

## Was Multitrack tut

Mehrere Leute am Tisch, jeder mit einem Mikrofon, auf dem alle zu hören
sind. Dieses Übersprechen aus dem Ton zu nehmen ist das Einzige, was nur
auphonic.com kann.

Multitrack ist das Häkchen für eine Spur je Person. Alle auf einer
Aufnahme bleiben eine Spur. Die Sprechertrennung hält die Stimmen darin
auseinander und liefert den Schnitt, nicht je eine Spur
([Spracherkennung und Sprechertrennung](speech.de.md)).

Das Häkchen entscheidet, wie die Aufnahmen zusammengefasst werden, und
sonst nichts: mit Häkchen bekommt jede Person eine eigene Spur, mit
Namen und Kamera; ohne Häkchen laufen alle zusammen in den Full-Mix.
Die gemeinsame Zeitachse, der Kameraschnitt und die Dateien am Ende
sind mit Häkchen dieselben wie ohne.

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
**Sprechername**, **gehört zu**, Timecode, **Sprecher**. Ein in
**Sprechername** getippter Name sagt, dass die Aufnahme diese eine
Person ist; der eine Eintrag, den man stattdessen wählen kann,
**mehrere Sprecher**, sagt, dass es mehrere sind, und die gefundenen
Stimmen hängen danach als eingerückte eigene Zeilen unter dieser Zeile.
Erst eine gegebene Antwort zeigt sie: eine Aufnahme, deren Trennung
schon gespeichert ist und für die niemand geantwortet hat, behält ein
leeres Feld und keine Stimmzeilen. Das Gemessene geht dabei nicht
verloren -- die Stimmen bleiben im Projekt und im Ablageordner, und
wählt man später **mehrere Sprecher**, stehen sie sofort da, mit ihren
Namen und Kameras und ohne neue Rechnung. Die letzte Spalte sagt, wie
weit das gekommen ist, und bietet währenddessen **Abbrechen**
([Spracherkennung und Sprechertrennung](speech.de.md)). Sie trägt noch
eine Zeile, *Nur ein Sprecher -- Spur auftrennen?*, in jeder Zeile, die
einen Namen hat und nicht auf **mehrere Sprecher** steht; ein Klick
setzt das Feld auf **mehrere Sprecher**, und die Stimmen erscheinen.
Sind schon Stimmen gespeichert, bietet dieselbe Zeile stattdessen an,
sie zu zeigen. Das Auswahlfeld **gehört zu** listet die Kameras, danach
zwei Sonderfälle:

- **nur in den Mix**: im Full-Mix, aber bei niemandem die erste Spur. Für
  jemanden, der zu hören, aber nicht zu sehen ist.
- **Audio ignorieren**: bleibt ganz außen vor, der Sprechername wird
  grau. Für eine Aufnahme, deren Video noch fehlt.

**Sprechername** startet leer, mit dem aus dem Dateinamen geratenen
Namen grau daneben. Tippt man nichts, gilt der Vorschlag -- aber nur,
wenn er mit einem Buchstaben beginnt, in irgendeinem Alphabet, nicht
nur in a bis z. Ein Vorschlag wie `0008A` tut das nicht, das Feld
bleibt leer, und bei Multitrack bleibt **Start** gesperrt, bis ein Name
da ist: der Name wird bei auphonic.com zur Bezeichnung dieser Spur und
dort von Leuten gelesen, die die Datei nie gesehen haben. Ein
getippter Name gilt so, wie er getippt wurde.

Die untere Tabelle hat je Kamera eine Zeile: **Kamera**, **neue Datei
heißt**, **bekommt Audio von** und **Kameraton**. Was eine Datei ist --
Inhalt, Vorspann, Abspann oder ignoriert -- wird jetzt in der Dateiliste
gefragt, in der Spalte **Typ**, beim Material, um das es geht. Ein Klick
auf eine Zeile holt die Datei in den Player. Dateien, die nicht zur
gemessenen Zeitachse passen, stehen in Rot, hier wie in der Dateiliste;
eine Datei, die überhaupt keinen Platz hat, schlägt das Programm zum
Weglassen vor.

Unter den Tabellen steht das Häkchen **Multitrack** ein zweites Mal. Es
ist dasselbe Häkchen wie unter **Produktion**: klickt man eines, zeigen
beide es. Auf der Kommandozeile (`--multitrack`) zählt es genauso.

Multitrack braucht zwei Eingangsspuren. Drei Dinge zählen als Spur:

- eine eigene Aufnahme,
- ein Kanal eines mehrkanaligen Aufnahmegeräts,
- der Ton einer Videodatei, deren **Kameraton** auf **Ton verwenden**
  steht.

Das Programm zählt die Zeilen der oberen Tabelle, ohne die auf **Audio
ignorieren**. Der Kameraschnitt braucht dieses Feld nicht.

![Die beiden Tabellen der Zuordnung](images/assignment.de.png)

*Reiter Zuordnung & Zeitfenster: die Aufnahmen mit ihrer Kamera, die
Kameras mit der Spalte Kameraton, und unter beiden Tabellen das
Häkchen Multitrack und der Kasten für auphonic.com.*

### Kameraton zur Spur machen

Ob eine Kamera ihren Ton beisteuert, wird bei der Datei gefragt: in der
Dateiliste auf dem Reiter **Dateien & Produktion**, in der Spalte
**Kameraton**. Sie steht auf **Ton nicht verwenden**, bis jemand etwas
anderes sagt, bei jeder Kamera und bei wie vielen auch immer. Messen
lässt sich diese Antwort nicht -- zwei Funkmikrofone, direkt in die
Videospur aufgenommen, sehen genauso aus wie das eigene Mikrofon der
Kamera im Raum; das weiß nur, wer dabei war.

Dasselbe Feld steht in der Kameratabelle neben dem Player, auf demselben
Wert: ändert man eines, zeigen beide es. Was vorher bekannt ist, steht
beim Material; was erst beim Hören auffällt, wird dort geändert, wo es
zu hören ist.

Ein Fall entscheidet sich selbst: genau eine Videodatei mit Ton und
keine Tonaufnahme daneben. Dann ist dieser Ton der einzige, den es gibt,
und das Feld steht auf **Ton verwenden**, ausgegraut, mit der Begründung
daneben. Es ist hergeleitet, nicht gespeichert -- kommt eine Tonaufnahme
dazu, ist es wieder eine Frage ([Der einfache Weg](simple-path.de.md)).

Auf **Ton verwenden** gestellt, bekommt die Kamera eine Zeile in der
oberen Tabelle, mit ihrem Sprechernamen. Sie zählt wie jede andere Spur:
aufbereitet, im Full-Mix, in der Sprechzeit für den Kameraschnitt
mitgezählt und als erste Tonspur ihrer eigenen Kamera.

„Wie jede andere Spur“ schließt die Kanäle ein. Das Feld bewahrt nur
den Ton; dieselbe Messung wie bei einer Recorder-Datei entscheidet, was
daraus wird.

- **Zwei Ansteckmikrofone auf den zwei Kanälen** ergeben zwei Zeilen mit
  zwei Sprechernamen. Das Programm beurteilt und schneidet sie wie eine
  zweikanalige Recorder-Datei. Diese eine Kamera ist dann zwei
  Eingangsspuren.
- **Ein echtes Stereopaar** bleibt eine zweikanalige Spur.

Das Auswahlfeld **gehört zu** bestimmt, zu welcher Kamera so eine Spur
gehört; die Kamera, aus der der Ton kommt, ist nur die Vorauswahl. Ein
Ansteckmikrofon, das in einer Kamera steckt, heißt nicht, dass diese
Kamera die Person filmt.

Setzt niemand das Feld und gibt es auch keine Tonaufnahme, ist nichts zu
hören: **Start** bleibt gesperrt und sagt es darunter. Das Ausrichten
hängt nicht daran -- die Zeitachse wird über die Hüllkurve jeder Datei
gemessen, gleich wie das Feld steht.

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
alle Spuren gleich angewendet, damit die Verhältnisse bleiben. Welches
Ziel gilt, kommt aus **Lautheit** in der Gruppe **Produktion** oder von
`--lufs`; ohne beides wird der Ton aus den Quelldateien übernommen und
nichts angepasst ([Vorflug](preflight.de.md)).

Die Spuren werden außerdem als Dateien abgelegt, in `auphonic-tracks/`
als `final_<Name>_<Timecode>.wav`. Der Timecode steht im Namen und im
bext-Block, dazu iXML für Premiere und Media Composer.

### Wenn etwas klemmt

- **Eine Zeile steht in Rot.** Der Ton dieser Datei passt zu schlecht
  zu dem der anderen, um sie einzuordnen, sie bekommt also keinen Platz
  auf der gemeinsamen Zeitachse. In der Spalte **Typ** der Dateiliste
  den Eintrag **Video ignorieren** wählen oder die Datei mit
  **Entfernen** aus der Liste nehmen.
- **Eine Zeile steht von selbst auf Video ignorieren.** Diese Datei hat
  überhaupt keinen Platz: Ihr Ton hat mit dem übrigen Material nichts
  gemeinsam, und einen Timecode trägt sie auch nicht. Das Programm
  schlägt vor, sie wegzulassen, statt sie auf gut Glück irgendwohin zu
  legen; das Protokoll nennt die Datei. Sie braucht einen Timecode, der
  zu den anderen Aufnahmen passt -- den muss ein anderes Programm setzen
  --, oder der Vorschlag bleibt stehen. Eine von Hand gegebene Antwort
  entscheidet die Zeile endgültig; lässt sich die Datei wieder
  einordnen, bekommt sie ihren alten **Typ** zurück
  ([Die Oberfläche](interface.de.md)).
- **In markieren und Out markieren bleiben gesperrt.** Die gemeinsame
  Zeitachse steht noch nicht. Den Balken unter den Tabellen abwarten.
- **Mehrere Kameras, keine Tonaufnahme, und Start bleibt gesperrt.**
  Keine Kamera steuert ihren Ton bei. Bei jeder Kamera, die zu hören
  sein soll, **Kameraton** auf **Ton verwenden** stellen; dann ist jede
  eine Spur. Von selbst werden sie es nicht mehr: einer Kamera, die eine
  brauchbare Spur aufnimmt, sieht man das nicht an -- sie kann ebenso
  nur im selben Raum filmen.
- **Ein Sprecher fehlt im Full-Mix.** Bei dieser Zeile steht in der
  Spalte **gehört zu** der Eintrag **Audio ignorieren**.

Die Spuren sind zugeordnet, das Fenster steht, und jede Kameradatei
trägt ihren eigenen Mix. Als Nächstes kommt die Frage, wer was sagt:
[Spracherkennung und Sprechertrennung](speech.de.md).

### Weitere Optionen über die Kommandozeile

Diese Option gibt es im Fenster nicht.

- `--parallel COUNT` legt fest, wie viele Kameradateien gleichzeitig
  laufen: `0` ist die Vorgabe und entscheidet selbst, `1` nimmt eine
  Datei nach der anderen. Mehr Dateien, als die Liste hält, laufen auch
  bei einer höheren Zahl nicht. Die geschriebenen Dateien sind in beiden
  Fällen byteweise identisch.

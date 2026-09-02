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
sind mit Häkchen dieselben wie ohne. Auch wer im Schnitt landet, hängt
nicht daran, woher er kommt: eine eigene Aufnahme, der Ton einer Kamera,
ein Kanal eines Recorders und eine Stimme, die die Trennung gefunden
hat, zählen gleich -- draußen bleibt nur, wer auf **nicht verwenden**
steht.

Alles andere läuft lokal. [Aufbereitung über auphonic.com](auphonic.de.md)
beschreibt den Weg dahin (auf der Kommandozeile `--without-auphonic`). Das
Programm richtet dann den Ton aus, mischt ihn, setzt die Lautheit und baut
den Kameraschnitt. Es lässt De-Bleed, Leveler und Rauschentfernung aus.
Hören die Mikrofone einander zu gut, um noch zu sagen, wer spricht, nimmt
die Sprechertrennung ihnen diese Frage ab und hört alle Spuren zugleich
ab ([Spracherkennung und Sprechertrennung](speech.de.md)).

Alles kommt auf eine gemeinsame Zeitachse, Uhrengang eingerechnet. Das
Fenster kommt allein aus den Kameras, und wo es gar keine gibt, aus den
Spuren selbst; Lücken darin füllt das Programm mit Stille. Zeilen mit demselben Sprechernamen werden zu einer Spur
zusammengefasst und über ihren Timecode hintereinandergelegt. Eine
Aufnahme, die zwischendurch gestoppt wurde, kommt am Stück zurück.

### Die Zuordnung setzen

Auf dem Reiter **Zuordnung & Zeitfenster** stehen links zwei Tabellen.
Die obere hat je Tonaufnahme eine Zeile: **Tonaufnahme**,
**Sprechername**, **gehört zu**, Timecode, **Sprecher**. Unter Timecode
steht die gemessene Lage, mit **errechnet** dahinter, oder mit
**virtuell**, wo die Achse an keiner Uhr hängt; nur eine Datei, für die
die Messung keinen Platz gefunden hat, zeigt dort ihre eigene Uhr, und
zwar ohne Zusatz -- und eine Datei, die weder das eine noch das andere
hat, zeigt **kein Timecode** ([Die Oberfläche](interface.de.md), „Wie
die Zeitachse gemessen wird“). Ein in
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
([Spracherkennung und Sprechertrennung](speech.de.md)). Dort startet
nichts eine Trennung: ein über **mehrere Sprecher** getippter Name
blendet die Stimmzeilen wieder aus und behält das Errechnete, und
zurück holt sie die Antwort im Feld. Das Auswahlfeld **gehört zu**
listet die Kameras, danach zwei Sonderfälle:

- **ohne eigene Kamera**: im Full-Mix, aber bei niemandem die erste
  Spur. Für jemanden, der zu hören, aber nicht zu sehen ist.
- **nicht verwenden**: bleibt ganz außen vor, der Sprechername wird
  grau. Für eine Aufnahme, deren Video noch fehlt.

Das Auswahlfeld steht mit dem Häkchen **Multitrack** da und ohne es: zu
welcher Kamera eine Aufnahme gehört, ist so oder so dieselbe Frage, und
der Kameraschnitt stellt sie mit gesetztem Häkchen wie ohne. Das Häkchen
anzuklicken nimmt darum nichts weg -- eine von Hand gewählte Kamera
bleibt stehen. Nur wo eine Aufnahme ihre Stimmen als eigene Zeilen
zeigt, weicht das Feld: dann tragen die Zeilen darunter die Kameras, und
die Zelle der Aufnahme sagt das grau.

**Sprechername** startet leer, mit dem aus dem Dateinamen geratenen
Namen grau daneben. Tippt man nichts, gilt der Vorschlag -- aber nur,
wenn er mit einem Buchstaben beginnt, in irgendeinem Alphabet, nicht
nur in a bis z. Ein Vorschlag wie `0008A` tut das nicht, das Feld
bleibt leer, und bei Multitrack bleibt **Start** gesperrt, bis ein Name
da ist: der Name wird bei auphonic.com zur Bezeichnung dieser Spur und
dort von Leuten gelesen, die die Datei nie gesehen haben. Ein
getippter Name gilt so, wie er getippt wurde.

Ein Name gehört einer Person, und darum steht er einmal auf dem Blatt.
Tippt man einen, den es dort schon gibt, wird das Feld rot -- auf beiden
Ebenen, gleich ob der zweite Träger eine Aufnahme ist oder eine Stimme
darunter.

Was daraus folgt, ist zweierlei. Zwei Aufnahmen desselben Namens sind
eine Frage und keine Weigerung: die Zeile unter der Tabelle nennt ihn
und sagt **kommt mehrfach vor. Die Aufnahmen werden zu einer Spur
zusammengefasst und nach Timecode hintereinandergelegt -- richtig, wenn
zwischendurch gestoppt wurde**, und genau dafür ist dieses
Zusammenfassen da. Eine Stimme dagegen lässt sich mit nichts
zusammenfassen -- sie ist eine Person in einer Trennung --, und deshalb
sperrt eine Stimme, die einen fremden Namen trägt, den **Start**; die
Zeile unter dem Knopf nennt ihn und sagt **steht auf mehr als einem
Sprecher -- ein Name ist eine Person, und jede Person braucht einen
eigenen**.

Die untere Tabelle hat je Kamera eine Zeile: **Kamera**, **neue Datei
heißt**, **bekommt Audio von**, **Typ** und **Kameraton**. Die beiden
letzten stehen auch in der Dateiliste, auf demselben Wert, und sie
stehen hier ein zweites Mal, weil der Player hier ist: dass ein Clip in
Wahrheit ein Abspann ist, fällt beim Ansehen auf. Ein Klick auf eine
Zeile holt die Datei in den Player.

**neue Datei heißt** ist das, was aus dieser Kamera herauskommen wird.
Bis jemand darüberschreibt, ist es ein Vorschlag, gebaut aus dem
Produktionsnamen, der Kamera und den Sprechern davor. **bekommt Audio
von** daneben nennt dieselben Sprecher. Eine Kamera, der niemand
zugeordnet ist, sagt dort **den Mix aus allen Spuren**, und der
Weitwinkel sagt **kein Sprecher -- das ist der Weitwinkel** -- oder
nennt den, der ihm vorher zugeordnet war und auf **ohne eigene Kamera**
gewechselt ist.

**Ein nur vorgeschlagener Name zählt in beidem mit.** Das Namensfeld
einer Aufnahme steht leer da, mit dem aus dem Dateinamen geratenen
Namen in Grau darin, und mit diesem Namen arbeitet der Lauf -- also
gehört er in den Dateinamen der Kamera und in **bekommt Audio von**.
Bisher fehlte er in beidem, während der Lauf ihn hatte, und die Kamera
ging unter einem Dateinamen ohne Menschen darin nach Resolve. Wer den
Namen eintippt, ändert daran nichts: es war schon vorher der Name, der
galt.

Eine Datei, für die die Messung keinen Platz findet, ist in dieser
Tabelle nicht vermerkt. Jeder Vermerk zu einer Datei steht in der
Dateiliste, wo die Dateien ausgewählt werden und wo er gelesen ist,
bevor jemand bis hierher kommt. Hier zeigt allein der **Typ**, was aus
ihr geworden ist: **Inhalt** und **Weitwinkel** sind gesperrt, und im
Feld steht die eigene Antwort des Programms -- **Vorspann**, oder
**Video ignorieren**, wenn eine andere Datei den Vorspann schon hält
oder wenn an der Datei überhaupt nichts zu messen war
([Die Oberfläche](interface.de.md)).

Unter den Tabellen steht das Häkchen **Multitrack** ein zweites Mal. Es
ist dasselbe Häkchen wie unter **Produktion**: klickt man eines, zeigen
beide es. Auf der Kommandozeile (`--multitrack`) zählt es genauso.

Multitrack braucht zwei Eingangsspuren. Drei Dinge zählen als Spur:

- eine eigene Aufnahme,
- ein Kanal eines mehrkanaligen Aufnahmegeräts,
- der Ton einer Videodatei, deren **Kameraton** auf **Ton verwenden**
  steht.

Das Programm zählt die Zeilen der oberen Tabelle, ohne die auf **nicht
verwenden**. Der Kameraschnitt braucht dieses Feld nicht.

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

**Eine Uhrzeit geht auch dann, wenn die längste Kamera keine Uhr
trägt.** In ihr wird das Fenster gezählt, aber sie muss nicht die sein,
die die Tageszeit kennt: die Achse hängt dann an den Uhren der übrigen
Dateien, und der Lauf sagt, an welchen er sie gehängt hat und worauf ihr
erstes Bild damit steht. Erst wenn keine einzige Datei auf der Achse
eine Uhr trägt, hat eine Uhrzeit nichts, worüber sie sich umrechnen
ließe; dann sagt der Lauf das und hält an, und es geht nur noch eine
Angabe ab Fensteranfang — `+12:30`, `90`, `-30`.

### Wieviel von jeder Kamera geschrieben wird

Am Zeitfenster hängt, was am Ende im Ausgabeordner liegt. Sobald eine
der beiden Marken steht, wird jede Kamera nur noch für dieses Stück
geschrieben und nicht mehr für den ganzen Dreh. Bei fünf Minuten aus
einem echten Interview lagen danach 6,09 GB im Ordner, wo derselbe Lauf
vorher 83,57 GB hinterlassen hat.

Ohne Marke wird nichts abgeschnitten. Jede Kamera kommt dann in voller
Länge heraus, genau wie bisher.

Jede geschriebene Kamera trägt an beiden Enden eine Sekunde mehr als das
Fenster, und vorne geht das Programm von dort aus noch bis zum Keyframe
davor zurück. Dieser Rand ist Vorlauf und kein Versehen. Der Lauf prüft
seine Kameras selbst nach und nennt eine schon ab einem einzigen Bild
falsch eingeordnet -- eine Sekunde ist also das Zwanzigfache dessen, was
er durchgehen lässt. Und ein Bild, das zwischen zwei Keyframes anfängt,
liegt bis zu 400 Millisekunden neben seinem eigenen Ton. Der Rand kauft
beides, und er kostet eine Sekunde Bild an jedem Ende.

Am Schnitt ändert das nichts. Dieselben Einstellungen stehen zu
denselben Zeitpunkten wie vorher, auf die Millisekunde, und in den
geschriebenen Dateien steht der Ton, der dort war.

Jede Kamera meldet eine Zeile **Zeitfenster**: wieviel von ihr
geschrieben wurde und ab welcher Stelle der Aufnahme. Nach der Liste der
geschriebenen Dateien nennt eine Zeile, was die Kameras zusammen tragen
und wieviel aufgenommen worden war. Lassen sich die Keyframes einer
Kamera nicht lesen, sagt das Programm es und lässt den Anfang dieser
Kamera stehen.

Im selben Block meldet jede Kamera ihren Versatz und ihren Uhrengang.
Eine meldet keinen: **Uhrengang: nichts gemessen -- das ist die
Referenz, gegen die die anderen gehalten werden**. Es ist die längste
Kamera, die, gegen die alle anderen gemessen wurden, und an ihr hat
also keine Messung etwas ergeben. Früher stand dort eine Reihe Nullen
-- null ppm, null von null Punkten --, die aussah wie eine Messung und
keine war.

Wer mehr braucht, als das Fenster hergibt, setzt **In markieren** und
**Out markieren** weiter auseinander und lässt noch einmal laufen. Einen
eigenen Schalter dafür gibt es nicht.

### Was in die Kameradateien kommt

Erste Tonspur jeder Kameradatei ist der Mix genau der Sprecher in diesem
Bild: `Mix <A> + <B>`. Bei nur einem Sprecher ist es sein Name. Danach
dieselben Sprecher einzeln, dann `Full-Mix`, zuletzt
`Camera Original`. Früher stand die Gesamtmischung im Laufplan mit ihren
Zutaten in Klammern dahinter; jetzt steht dort der bloße Name
`Full-Mix`, derselbe, den die geschriebene Spur trägt und den sie auch
in Resolve hat. Die Lautheit wird über die Summe bestimmt und auf
alle Spuren gleich angewendet, damit die Verhältnisse bleiben. Welches
Ziel gilt, kommt aus **Lautheit** in der Gruppe **Produktion** oder von
`--lufs`; ohne beides wird der Ton aus den Quelldateien übernommen und
nichts angepasst ([Vorflug](preflight.de.md)).

Die Spuren werden außerdem als Dateien abgelegt, in `auphonic-tracks/`
als `final_<Name>_<Timecode>.wav`. Der Timecode steht im Namen und im
bext-Block, dazu iXML für Premiere und Media Composer.

### Multitrack ganz ohne Kamera

Manchmal gibt es gar kein Bild: mehrere Mikrofone an einem Tisch, und
nichts filmt. Ein Lauf mit dem Häkchen und ohne Videodatei wurde früher
abgewiesen, weil die Zeitachse fehlte. Jetzt baut das Programm die Achse
aus den Spuren selbst -- sie werden gegeneinander gelegt statt gegen
eine Kamera.

Referenz ist die längste Aufnahme, aus demselben Grund wie sonst die
längste Kamera: sie überschneidet sich am meisten mit den übrigen. Jede
andere Spur wird dagegen gemessen, Versatz und Uhrengang in einem Zug,
und das Protokoll nennt die Referenz mit ihrer Laufzeit und jede Spur
mit dem, was gefunden wurde. Eine Spur, die keinen Platz bekommt, wird
genannt und bleibt draußen.

Das Fenster fasst alles, was irgendeine Spur gehört hat. Eine Aufnahme,
die später eingeschaltet wurde, bekommt Stille davor, eine früher
ausgeschaltete Stille dahinter, und das Protokoll sagt, wieviel und bei
welcher Spur. Ein stiller Rand kostet weniger als eine abgeschnittene
Aufnahme.

Heraus kommt je Stimme eine Datei im Ausgabeordner, sie heißt
`<Sprechername>_aligned.wav`: alle gleich lang, alle am selben Punkt
beginnend, wie die Tonaufbereitung es braucht. Ist kein Ausgabeordner
gesetzt, landen sie neben der ersten Aufnahme. Mit Schlüssel gehen
dieselben Spuren außerdem als **eine** Multitrack-Produktion zu
auphonic.com, und was zurückkommt, wird gegen das gehalten, was
hochgegangen ist; ohne Schlüssel oder mit `--without-auphonic` bleiben
sie auf diesem Rechner.

In-Punkt und Out-Punkt gelten auch hier (`--in-point`, `--out-point`),
aber nur als Angabe ab Fensteranfang -- `+12:30`, `90`, `-30`. Eine
Uhrzeit hat nichts, worüber sie umgerechnet werden könnte, denn es gibt
keine Kamera, an deren Timecode die Achse hängt; das Programm sagt es
und hält an.

**Ein Lautheitsziel tut dem Ton auf diesem Weg nichts.** Ein Gewinn je
Spur brächte die Stimmen genau um das Gleichgewicht, für das dieser Weg
da ist; die Spuren gehen also so heraus, wie sie aufgenommen wurden, und
die Lautheit wird dort gesetzt, wo sie gemischt werden. Mit `--lufs` und
ohne Schlüssel sagt der Lauf das in einer Zeile; mit Schlüssel wird der
Wert weiterhin gegen das gehalten, worauf das Preset mastert
([Vorflug](preflight.de.md)).

### Wenn etwas klemmt

- **Multitrack, kein Bild, und der Lauf hält sofort an.** Nach dem
  Zusammenfassen bleibt nur eine Spur übrig, und Multitrack heißt eine
  Spur je Stimme. Statt zwei Menschen in eine Datei zu kleben, hält der
  Lauf an, bevor er etwas zusammenfügt. Wo zwei Menschen für eine
  Aufnahme genommen wurden, hält `--apart` einen Block heraus.
- **Nur eine Spur hat einen Platz gefunden.** Die übrigen ließen sich
  nicht gegen die Referenz messen, und eine Spur allein hat nichts mehr,
  wogegen sie liegen könnte. Die Zeilen darüber nennen jede einzelne und
  den Grund.
- **Eine Zeile ist vermerkt, und der Vermerk ist nicht rot.** Unter dem
  Namen steht **Ton nicht erkannt; über den Timecode platziert**. Zu tun
  ist nichts: Der Ton dieser Datei wurde nicht erkannt, ihre Uhr setzt
  sie aber framegenau zwischen die anderen, und einer der beiden Wege zu
  einem Platz genügt. Die Datei liegt auf der Achse und geht in den Lauf.
  Ist es eine Kamera, nennt der Lauf sie beim Schreiben der
  Übergabedatei noch einmal -- allein nach Timecode gesetzt
  ([DaVinci Resolve](resolve.de.md), „Wo jede Kamera sitzt“).
- **Eine Zeile steht in Rot.** Diese Datei hat überhaupt keinen Platz:
  Ihr Ton hat mit dem übrigen Material nichts gemeinsam, und auch kein
  Timecode ordnet sie zwischen die anderen ein. In der Spalte **Typ**
  der Dateiliste den Eintrag **Video ignorieren** wählen oder die Datei
  mit **Entfernen** aus der Liste nehmen.
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
- **Eine Stimme trägt einen Namen, den schon jemand anderes hat, und
  Start bleibt gesperrt.** Ein Name ist eine Person, und der Schnitt
  setzt eine Person auf eine Kamera; derselbe Name zweimal wäre eine
  Person an zwei Stellen. Der
  Stimme in ihrer eingerückten Zeile unter der Aufnahme einen eigenen
  Namen geben. Zwei **Aufnahmen** desselben Namens sind etwas anderes --
  die werden mit Absicht zu einer Spur zusammengefasst und wollen nur
  bestätigt werden; zu ändern ist also die eingerückte Zeile, nicht die
  der Aufnahme.
- **Ein Sprecher fehlt im Full-Mix.** Bei dieser Zeile steht in der
  Spalte **gehört zu** der Eintrag **nicht verwenden**.

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

# Spracherkennung und Sprechertrennung

*In English: [speech.md](speech.md). Zurück zum
[Inhalt](README.de.md).*

## Was auf diesem Rechner läuft

Das Programm schreibt mit, was gesprochen wird, und es trennt die
Stimmen einer Aufnahme. Beides läuft auf diesem Rechner, ohne Konto und
ohne Hochladen, und bevor irgendetwas zu auphonic.com geht.

### Die Sprecher trennen

Auf dem Reiter **Zuordnung & Zeitfenster** trägt jede Aufnahme einen
**Sprechernamen** und eine Spalte **Sprecher**. Ein in das Namensfeld
getippter Name sagt, dass die Aufnahme diese eine Person ist. Der eine
Eintrag, den man stattdessen wählen kann, **mehrere Sprecher**, sagt,
dass es mehrere sind, und das Programm ermittelt daraufhin, wer wann in
genau dieser Aufnahme spricht. Während ein Durchgang läuft, bietet die
Zelle **Sprecher** dieser Zeile **Abbrechen** an, und die übrigen
Zeilen bieten nichts: es wird eine Aufnahme nach der anderen getrennt.

Das Feld startet leer, mit dem Namen, den der Dateiname nahelegt, grau
darin. Sonst füllt es niemand. Eine Aufnahme, die eine Trennung trägt,
für die niemand geantwortet hat, zeigt ein leeres Feld und keine
Stimmen: erst eine Antwort holt sie hoch. Sie holt sie sofort hoch, mit
den Namen und Kameras, die sie schon hatten, und gerechnet wird nichts
zweimal -- ein Fehlklick kostet also keine Zeit.

Es sich anders zu überlegen geht durch dasselbe Feld und nur durch
dieses. Steht ein Name darin, gibt **mehrere Sprecher** diese Aufnahme
an die Trennung; stehen die Stimmen darunter, blendet ein über die
Antwort getippter Name sie wieder aus und wirft nichts weg. Die Zelle
**Sprecher** ist eine Auskunft und keine Frage: nichts darin startet
eine Trennung.

Ist eine Aufnahme getrennt, steht **Getrennt: 4 Sprecher** in ihrer
Zelle **Sprecher**. Jede Aufnahme trägt ihre eigene: eine zweite zu
trennen nimmt der ersten nichts weg, beide Zellen sagen ihre eigene
Zahl, und die Stimmen beider bleiben in ihren Zeilen stehen. Die
Projektdatei behält sie alle.

Unter den Aufnahmen bietet eine Zeile die Trennung an, und nur dort,
wo sie gebraucht wird. Ein Mac rechnet sie von selbst und bekommt gar
keine Zeile. Überall sonst steht sie beim ersten Mal da, mit **Auf
diesem Rechner nicht** daneben. Das Projekt merkt sich die Antwort: ein
Projekt, das nein gesagt hat, liest es auf dieser Zeile und wird nicht
wieder gefragt.

Auf einem Mac läuft die Trennung bei einer Aufnahme von selbst, sobald
die Dateien da sind. Bei mehr als einer Aufnahme läuft von selbst
nichts; die Antwort **mehrere Sprecher** in der Zeile startet sie.

Die Trennung ist der Weg für **eine gemeinsame Aufnahme**, auf der alle
zu hören sind. Sie braucht das Häkchen **Multitrack (je Sprecher eine
Spur)** nicht: die Spalte steht auf beiden Wegen da, auch bei einer
einzigen Kamera. Wo eine Person ein eigenes Mikrofon hat und die
Mikrofone auseinanderzuhalten sind, ist diese Spur die Wahrheit, und es
gibt nichts zu trennen; hören sie einander dafür zu gut, legt ein Lauf
ohne auphonic.com sie zusammen und trennt sie gemeinsam („Wenn die
Mikrofone einander hören“ weiter unten). Die Trennung sagt, wer wann
spricht; sie macht aus einer Aufnahme keine Spur je Sprecher.

Gibt es keine eigene Aufnahme, hört die Trennung den Ton einer Kamera
ab. Auch eine Kamera, deren Ton zu schlecht zu den anderen passt, um sie
danach einzuordnen, ist dafür zugelassen, solange ihr Timecode ihr einen
Platz unter den anderen gibt; heraus bleibt nur eine Datei, die
überhaupt keinen Platz hat. Denn was eine Trennung braucht, ist ein
Platz auf der gemeinsamen Zeitachse, und den gibt eine Uhr ebenso wie
ein wiedererkannter Ton -- wie gut der Kameraton ist, entscheidet hier
nichts.

**Woher jemand kommt, macht keinen Unterschied.** Wer zu hören ist, ist
im Schnitt: eine Aufnahme mit einer Person darauf, der Ton einer Kamera
mit einer Person darauf, eine Aufnahme, die sich mehrere teilen, und
jede Stimme, die eine Trennung auf einer von ihnen gefunden hat. Sie
zählen miteinander und nicht gegeneinander, und eine Trennung auf einer
Aufnahme nimmt von den anderen niemanden weg. Nur **nicht verwenden**
hält jemanden heraus, bei der Aufnahme wie bei der Stimme. Gemessen an
zwei Stimmen aus einer getrennten Aufnahme und einer dritten Person am
eigenen Mikrofon, jede mit einer Kamera: alle drei reden im Schnitt, und
das Bild geht auf alle drei Kameras.

Worauf die Trennung rechnet, kam mit der Installation; eingerichtet
werden muss dafür nichts. Geholt wird nur noch das Modell selbst, etwa
33 MB, beim ersten Trennen, und das ohne Rückfrage. [Was gebraucht
wird](requirements.de.md#das-programm-installieren) sagt, woher das
Modell kommt.

Auf der ganzen Datei hört die Trennung auch den Vorlauf vor der
Sendung. Beim Umrechnen wird auf das Zeitfenster geschnitten, aber die
Sprecherzahl in der Tabelle ist die des ungeschnittenen Laufs. Ein
Gespräch im Vorlauf bringt eine Stimme mehr in die Tabelle, als in der
Folge vorkommt.

Eine Stimme in der Tabelle und eine Kamera heißt kein Schnitt: niemand
übergibt, und es gibt keine Stelle, wohin das Bild sonst ginge. Die
Passagen gehen in die Übergabedatei, und der Lauf geht bis zum Ende
durch. Bei einer zweiten Kamera gibt es eine solche Stelle: diese eine
Kamera steht, und der Weitwinkel bricht sie auf. Am 25.8.2026 gemessen
ergaben fünf Minuten auf zwei Kameras 15 Einstellungen, davon 7 im
Weitwinkel; dieselben fünf Minuten auf einer Kamera ergaben 1.

### Wenn die Mikrofone einander hören

Sitzen zwei Menschen dicht beieinander, liegt jeder auf dem Mikrofon des
anderen. Jede Spur trägt dann den Nachbarn mit, und eine Trennung, die
jede Spur für sich abhört, findet in jeder Passage jeder Spur jemanden:
alle sehen so aus, als hätten sie fast ununterbrochen geredet, und wer
wirklich gesprochen hat, steht in der Antwort nicht mehr drin.

Wo das so ist, fragt das Programm die Mikrofone nicht mehr einzeln ab.
Es legt die ausgerichteten Aufnahmen zu einer einzigen zusammen, lässt
die Trennung diese eine abhören und gibt jeder gefundenen Stimme den
Namen des Mikrofons, zu dem sie gehört. Auf diesen Namen kommt alles an:
eine Stimme aus einer zusammengelegten Aufnahme hieße sonst Sprecher 1,
und hinter diesem Namen steht niemand -- also auch keine Kamera, und der
Schnitt stünde von Anfang bis Ende im Weitwinkel.

**Zu gut** ist gemessen und nicht angenommen. Jede Aufnahme wird gegen
jede andere gehalten, in beide Richtungen, an den Stellen, an denen
einer allein redet; ist der kleinste dieser Abstände unter 20 dB, werden
die Mikrofone zusammengelegt. Sie gehen hinein, wie sie aufgenommen
wurden. Sie vorher gleich laut zu machen würde genau den Unterschied
einebnen, von dem die Benennung lebt, denn die Aufnahmepegel sind hier
so groß wie das Übersprechen.

Gemessen benennen die Spuren für sich 37,5 Prozent der Rede richtig, die
zusammengelegte Aufnahme 97,6. An Material, dessen Wahrheit auf die
Millisekunde feststeht, stieg die richtig benannte Rede von 72,5 auf
92,7 Prozent, und die Zeit, in der das Bild auf derselben Kamera steht
wie bei einem Lauf über auphonic.com, von 46 auf 96,5 Prozent.

**Nur bei einem Lauf ohne auphonic.com.** Der De-Bleed dort nimmt die
Nachbarn aus den Spuren heraus, und danach antwortet jede Spur für sich
besser, als jedes Zusammenlegen es könnte. Ein Lauf, der hochlädt, und
einer, der auf schon aufbereitete Spuren gerichtet ist, gehen deshalb
den Weg wie bisher: eine Stimme je Spur, aus den Mikrofonen gemessen.

**Und nur dort, wo der Lauf die Trennung selbst ermittelt.** Eine
Trennung, die das Fenster schon gemacht hat, reist mit dem Lauf mit und
wird genommen, wie sie ist. Wer im Fenster bei einer Aufnahme **mehrere
Sprecher** antwortet, bekommt den Schnitt aus dieser einen Aufnahme;
zusammengelegt wird dann nichts. Hat das Fenster nichts getrennt -- der
übliche Fall bei einem Mikrofon je Person, wo in jeder Zeile ein Name
steht --, entscheidet der Lauf, und er legt zusammen. Auf der
Kommandozeile entscheidet er ebenso, sofern ihm nicht `--speakers-from`
oder `--speakers-local` etwas mitgibt.

Was von beidem geschehen ist, sagt das Protokoll. Statt die Aufnahme zu
nennen, sagt der Block **SPRECHER WERDEN GETRENNT** dann, dass die
Mikrofone einander zu gut hören, um zu sagen, wer spricht, und wie viele
davon auf einmal abgehört werden. Unter **SPRECHER -- NACH STIMMEN
GETRENNT** kommen die Stimmen **Aus der Trennung in diesem Lauf**, und
je Stimme sagt eine Zeile, zu welchem Mikrofon sie gehört und wie viele
dB sie **vor dem nächsten Mikrofon** steht, **der Aufnahmepegel
herausgerechnet**.

Diese Zahl entscheidet, und ein dB davon genügt. Von jedem Mikrofon wird
vorher sein eigener Pegel herausgerechnet: ein lauter gedrehtes
Aufnahmegerät würde sonst die Stimmen des ganzen Raums einsammeln. Eine
Stimme, vor der kein Mikrofon weit genug steht, behält ihre Bezeichnung
und bekommt keine Kamera, und zwei Stimmen, die auf dasselbe Mikrofon
zeigen, heben einander auf, denn ein Mikrofon ist eine Person. Mehr
Stimmen als Mikrofone -- jemand im Raum ohne eigenes, oder eine Stimme
aus dem Vorlauf -- und keine einzige wird zugeordnet. Lässt sich am Ende
keiner Stimme ein Mikrofon geben, sagt das Protokoll, dass stattdessen
die Spuren gemessen werden, und der Schnitt ist der, der er immer war:
eine Stimme je Spur.

### Die Stimmen benennen

Die Stimmen haben keine eigene Tabelle. Sie hängen unter der Aufnahme,
in der sie gehört wurden, als eingerückte Zeilen derselben Liste: in
der ersten Spalte steht **Stimme**, damit die Stufe überhaupt zu sehen
ist, daneben stehen der **Sprechername** und unter **gehört zu** die
Kamera. Die Namen sind mit Sprecher 1, Sprecher 2 und so fort vorbelegt,
nach Sprechzeit, die längste zuerst. Gezählt wird nicht bei jeder
Aufnahme von vorn: ein Name, den das Programm selbst vergibt, nimmt die
erste Zahl, die niemand hat -- über alle Trennungen und über die Zeilen
der Zuordnungstabelle darüber hinweg. Sind Sprecher 1 und Sprecher 2
vergeben, heißt die nächste Stimme Sprecher 3. Ein von Hand gegebener
Name wird nie umnummeriert, und eine frei gewordene Zahl wird wieder
gefüllt. Keine Zeit steht in der Zeile: um welche Aufnahme es geht, sagt
die Zeile darüber, und wie lange jemand redet, entscheidet hier niemand.

**Zwei Sprecher dürfen nicht denselben Namen tragen.** Ein Name ist eine
Person, und der Schnitt setzt eine Person auf eine Kamera; zwei gleiche
Namen kommen dort als eine Person an, und diese eine Kamera steht dann
zweimal an verschiedenen Stellen desselben Schnitts. Darum wird ein
Name, den schon jemand anderes trägt, bereits beim Tippen rot, und der
Hinweis am Feld sagt, woran es liegt. Trägt eine Stimme den zweiten,
wartet **Start**, bis sie einen eigenen hat: eine Stimme ist eine Person
in einer Trennung und lässt sich mit nichts zusammenfassen. Zwei
Aufnahmen gleichen Namens sind dagegen eine Frage und keine Weigerung --
sie sollen zu einer Spur werden, nach Timecode hintereinandergelegt
([Multitrack](multitrack.de.md)).

Sobald die Worte aufgeschrieben sind, werden aus diesen Namen
Vorschläge, die etwas sagen. Wer fragt und wer antwortet, lässt sich am
Gesprochenen ablesen: das Programm zählt für jede Stimme im Zeitfenster,
wie viele ihrer Sätze auf ein Fragezeichen enden, und schlägt **Gast**
für den vor, der am wenigsten fragt und am längsten redet, **Moderation**
für die übrigen. Vorgeschlagen wird nur über einen Namen, den das
Programm selbst vergeben hat — ein getippter wird nie angerührt, auch
keiner, der aussieht wie einer des Programms.

Dieselbe Zählung sagt, wann eine Stimme keine Sprecherin ist. Eine, die
im Zeitfenster zu wenige Sätze zusammenbringt, wird für **nicht
verwenden** vorgeschlagen, mit einer Zeile im Protokoll, welche und
warum. Das trifft den Fall, dass eine Trennung jemanden in zwei teilt,
und den, dass eine Stimme aus den Minuten vor dem Interview stammt.
Verschiebt man den In-Punkt, folgt der Vorschlag sofort: wird das
Fenster breiter, kommt die Stimme an ihre Kamera zurück und bekommt
ihren Namen aus der neuen Rangfolge.

**Nicht verwenden** heißt bei einer Stimme, dass es sie nicht gibt.
Keine Kamera, keine Spur, kein Sprecher bei auphonic.com, keine Zeile im
Transkript und keine bei den Redeanteilen; wo sie sprach, spricht
niemand, und das Bild bleibt bei dem, bei dem es war, bis die nächste
zählende Stimme kommt. Was getrennt wurde, bleibt trotzdem in der
Projektdatei — die Stimme wieder einzuschalten kostet also kein Rechnen.

Das Aufschreiben kostet für anderthalb Stunden Aufnahme etwa eine halbe
Minute. Es läuft einmal, im Hintergrund, sobald eine Trennung vorliegt —
die lange Rechnung, die jemand entweder angestoßen hat oder nach der
gefragt wurde — und nie beim bloßen Hinzufügen von Dateien. Es
installiert nichts und lädt nichts herunter: es nimmt die Erkennung, die
macOS mitbringt, und den anderen Weg nur dort, wo ein Lauf ihn schon
gelegt hat.

Eine Aufnahme, die Stimmen zeigt, kommt aufgeklappt hoch, mit einem
Dreieck davor, das sie zuklappt. In ihrem eigenen
**gehört zu** steht grau **die Stimmen darunter tragen die Kameras**, und die
Zeilen darunter tragen die Zuordnung;
klappt man sie zu, steht dort, was das Zuklappen vom Schirm nimmt -- die
Kameras: **auf 2 Kameras**, und **auf 1 Kamera, 1 ohne**, wenn eine
Stimme noch keine hat. Die Zahl der Stimmen steht dort nicht noch
einmal, denn die Zelle **Sprecher** derselben Zeile sagt sie schon. Die
Zuordnung steht immer auf genau einer Ebene, nie auf zweien. Aufnahmen,
die keine Stimmen zeigen, sind eine flache Liste, ohne Dreiecke.

1. Den **Sprechernamen** der Aufnahme mit **mehrere Sprecher**
   beantworten, dem einen Eintrag, den das Feld zur Wahl stellt. Auf
   einem Mac ist die Trennung bei einer Aufnahme schon gelaufen, und
   die Antwort holt die Stimmen nur noch auf den Schirm.
2. Die Zeile einer Stimme anklicken. Der Player rechts öffnet die
   Aufnahme dort, wo diese Stimme am längsten redet, und spielt sofort.
   Anklicken ist der Weg, eine Stimme zu hören; einen Knopf gibt es
   dafür nicht.
3. Den **Sprechernamen** in dieser Zeile mit dem Namen der Person
   überschreiben.
4. Bei einer fehlenden Stimme unter den Aufnahmen **Ein Sprecher mehr
   in `<Datei>`** drücken. Der Knopf hört dieselbe Aufnahme noch
   einmal ab, mit einem Sprecher mehr, als der letzte Durchgang
   gefunden hat. Dann zurück zu Schritt 2. Bei mehr als einer Aufnahme
   wandert der Name vom Knopf in ein Auswahlfeld daneben.

Eine gesetzte Zahl schärft die Trennung. Eine falsche Zahl vervierfacht
die Bildzeit auf der falschen Person. Deshalb wird sie nur gesetzt,
wenn die Zahl bekannt ist. Die Messungen stehen in [What was
measured](../development/measurements.md) (englisch).

![Die Stimmen einer Aufnahme](images/voices.de.png)

*Reiter Zuordnung & Zeitfenster: die Stimmen unter der Aufnahme, in
der sie gehört wurden.*

### Was aufgehoben wird und was neu gerechnet wird

Die Trennung und die mitgeschriebenen Wörter werden auf diesem Rechner
aufgehoben, außerhalb des Projekts. Eine Aufnahme, die einmal getrennt
oder einmal abgehört wurde, wird beim nächsten Mal zurückgelesen statt
noch einmal gerechnet -- auch in einem anderen Projekt, auch nachdem
das Programm zu war, auch Tage später. Darum ist ein zweiter Anlauf auf
demselben Material auf einmal schnell.

**Zurückgelesen ist keine Näherung.** Es ist, was die erste Rechnung
ergeben hat, unverändert aufgehoben: dieselben Abschnitte auf die
Tausendstelsekunde genau, dieselben Wörter an denselben Stellen.
Gerechnet wird nichts ein zweites Mal, also kann auch nichts anderes
herauskommen.

Was von beidem geschehen ist, sagt das Protokoll. Wurde eine Trennung
zurückgelesen, steht unter der Überschrift die Zeile **Schon einmal
getrennt: zurückgelesen, nicht neu gemessen.**; muss eine gemessen
werden, steht dort stattdessen, wieviel Rechenzeit die Aufnahme gleich
kostet. Bei den Wörtern endet die Zeile auf **zurückgelesen** statt auf
den Sekunden, die die Erkennung gebraucht hat.

**Bei den Wörtern entscheidet der Inhalt der Datei** -- nicht ihr Name
und nicht ihre Uhrzeit. Eine Aufnahme, die umbenannt, in einen anderen
Ordner geschoben oder auf eine andere Platte kopiert wurde, ist
dieselbe Aufnahme und wird nicht noch einmal abgehört. Eine Datei, die
unter demselben Namen in derselben Sekunde neu geschrieben wurde und
anderen Ton enthält, wird abgehört: verglichen wird, was darin steht,
und nicht das Schild darauf. Die Datei dafür einmal durchzulesen kostet
etwa eine Drittelsekunde je Gigabyte -- gegen eine halbe Minute für
anderthalb Stunden auf einem Mac und die vielen Minuten dort, wo
faster-whisper die Arbeit tut. Die Sprache und der Weg gehören ebenso
dazu: dieselbe Aufnahme auf deutsch und auf englisch ergibt andere
Wörter, und die beiden Erkenner schreiben auch nicht dasselbe.

**Bei der Trennung entscheidet die Aufnahme, wie sie liegt** -- ihr
Ort, ihre Größe und wann sie zuletzt geändert wurde -- dazu das Modell,
eine von Hand gesetzte Sprecherzahl und die Art, wie das Programm die
Antwort ermittelt: eine Fassung, die daran etwas ändert, misst neu,
statt herauszugeben, was eine ältere Rechnung geschrieben hat. Neu
gerechnet wird also, wenn die Quelldatei wechselt, wenn sie sich ändert,
wenn sie umbenannt oder verschoben wird oder wenn jemand eine Zahl
setzt. Ein verschobenes Zeitfenster, ein neuer In-Punkt, ein geänderter
Versatz oder ein umbenannter Sprecher laufen mit der vorhandenen
Trennung weiter. Die Trennung aus dem Fenster reist mit dem Lauf mit,
und das Programm rechnet sie nur noch auf dessen Zeitachse um.

Eine von Hand gesetzte Sprecherzahl gehört zu der Aufnahme, für die sie
gesetzt wurde. Der Knopf in einer anderen Zeile verwirft sie und zählt
neu.

Beides liegt im Ablageordner des Systems, neben den Hüllkurven
(`~/Library/Caches/videopodcast-magic/`, unter Windows
`%LOCALAPPDATA%`), in `words/` und `speakers/`. Eine aus mehreren
Mikrofonen zusammengelegte Aufnahme liegt ebenfalls in `speakers/`,
unter einem Namen aus den Aufnahmen, die in ihr stecken -- dasselbe
Material findet sie also wieder, statt sie ein zweites Mal zu bauen.
Dort bleibt alles. Es wegzuwerfen macht nichts kaputt; es heißt nur,
dass noch einmal gerechnet wird.

### Woher die Sprecher kamen

Das Protokoll sagt es. Zwei Marken zum Suchen:
`SPRECHER -- NACH STIMMEN GETRENNT` und `SPRECHER -- HIER GEMESSEN`.
Wo beides zutrifft, stehen beide Marken in einem Protokoll, eine unter
der anderen: die erste sagt, woher die Trennungen kommen und wie viele
Stimmen sie zusammen tragen, die zweite nennt die Spuren, für die keine
Trennung spricht. Darunter kommt je Sprecher eine Zeile mit Redezeit und
Zahl der Passagen, und diese Liste ist die ganze Besetzung des Schnitts.

Die Messung unter der zweiten Marke braucht je Person eine Spur, und sie
liest jede Spur, auch die, für die schon eine Trennung spricht: das
Übersprechen wird herausgerechnet, indem die Mikrofone gegeneinander
gehalten werden, und eine Spur, die dabei fehlte, hörte ihren Nachbarn
und zählte das als Sprechen. Lässt sich eine Trennung nicht verwenden,
sagt das Protokoll warum, und der Lauf geht mit dem weiter, was die
Spuren sagen.

Wo die Mikrofone zusammengelegt wurden, bleibt die zweite Marke aus. Die
zusammengelegte Aufnahme spricht für jede Spur, also wird keine Spur ein
zweites Mal gemessen, und niemand steht zweimal im Schnitt: wer darin
ist, ist eine Stimme. Konnte keiner Stimme ein Mikrofon gegeben werden,
ist es umgekehrt -- die Stimmen werden fallengelassen, und jede Spur
wird gemessen wie zuvor.

### Was der Probelauf von den Sprechern zeigt

Der **Probelauf** schreibt kein Ergebnis und lässt das Messen liegen --
mit der einen Ausnahme am Ende dieses Abschnitts. Liegt die Trennung
einer Aufnahme schon auf diesem Rechner, zeigt er den Schnitt, den er
machen würde: der Block nennt die Aufnahme, sagt, dass die Abschnitte
zurückgelesen wurden, und zählt die Stimmen auf.

```
SPRECHER WERDEN GETRENNT
  In recorder.wav, auf diesem Rechner.
  Schon einmal getrennt: zurückgelesen, nicht neu gemessen.

  SPEAKER_00  0:00:08,600 in 2 Abschnitten
  SPEAKER_01  0:00:04,000 in 1 Abschnitten
```

Die Stimmen tragen die Bezeichnungen aus der Trennung, weil ihnen
niemand einen Namen gegeben hat: ein Lauf von der Kommandozeile hat
kein Fenster, aus dem er welche nehmen könnte. Eine Trennung aus einer
Projekt- oder Zuordnungsdatei steht genauso da, unter den Namen, die
darin stehen.

Liegt nichts vor, hört der Probelauf an dieser Stelle auf. Er sagt,
wieviel Rechenzeit die Trennung kosten würde, dann **(nur gemessen:
nichts getrennt)**, und es folgen keine Stimmen. Das ist der ganze
Unterschied: liegen bleibt nur, was wirklich gemessen werden müsste.
Eine Trennung zurückzulesen kostet nichts, also geschieht es, und das
Ergebnis steht da.

Die Aufzählung steht hier oder nirgends. Ein voller Lauf sagt weiter
unten, wer wie lange redet, unter den beiden Marken von eben; ein
Probelauf endet vorher und zählt die Stimmen deshalb dort auf, wohin er
kommt.

Eines tut er doch. Ob die Mikrofone zusammengelegt werden, entscheidet
sich, bevor die Trennung überhaupt verlangt wird -- diesen Teil tut der
Probelauf also: er misst, wie weit die Mikrofone auseinanderstehen,
schreibt die zusammengelegte Aufnahme neben die Trennungen und hört erst
danach auf. Liegen bleibt die Trennung selbst.

### Wie das Programm den Text mitschreibt

Die Erkennung nimmt einen von zwei Wegen, und der Unterschied zeigt sich
allein an der Uhr.

* **macOS 26 bringt sie mit.** Die Erkennung steckt im Betriebssystem;
  eine Stunde Ton in gut 20 Sekunden. Sie verlangt die Command Line
  Developer Tools.
* **Überall sonst faster-whisper.** Beim ersten Mal holt das Programm
  144 MB Pakete und ein Modell von 1,5 GB. Auf einem gewöhnlichen
  Windows-Rechner ist die Erkennung der teuerste Schritt der ganzen
  Kette.

Die Messungen hinter diesen Zeiten stehen in [What was
measured](../development/measurements.md) (englisch).

Das Programm sieht nach, welchen Weg es hat, und sagt im Protokoll,
welchen es genommen hat. Die Erkennung nimmt die Spracheinstellung des
Laufs. Bleibt sie leer, arbeitet macOS mit der Systemsprache und Whisper
errät sie aus dem Ton. Der Lauf schreibt den Text neben dem
Kameraschnitt mit, nicht davor.

Auf dem macOS-Weg meldet die Erkennung hinterher, wie es ihr ergangen
ist -- in der Fortschrittszeile und im Protokoll: **Erkannt in de-DE:
bereit in 0,1 s, gehört in 25,8 s**. Also womit sie gearbeitet hat, wie
lange sie zum Bereitwerden brauchte und wie lange das Zuhören selbst
gedauert hat. Daran lässt sich ein späterer Lauf gegen diesen halten.
Die Zeile steht in der Sprache des Laufs; früher wurde sie in den
eigenen Schlagworten der Erkennung durchgereicht, Englisch mitten in
einem deutschen Lauf. Sagt die Erkennung etwas anderes, ist es eine
Störung und wird auch als solche ausgegeben.

Die Erkennung läuft auf dem fertigen Mix, nicht auf den Einzelspuren.
Ein leiser Mitschnitt kann für die Sprechertrennung reichen und für
den Text trotzdem nicht taugen.

Was einmal abgehört wurde, wird nicht wieder abgehört, was immer es
gekostet hat. Was aufgehoben wird und was neu gerechnet wird, steht
weiter oben unter „Was aufgehoben wird und was neu gerechnet wird“. Das
Fenster und der Lauf hören verschiedenes ab -- das Fenster die
Aufnahme, der Lauf den Mix, den er daraus gemacht hat -- also zahlt
jeder von beiden einmal.

### Wofür der Text gebraucht wird

Der Text liefert die Satz- und Teilsatzgrenzen für den Kameraschnitt,
beschrieben in [Sprecherstatistik, Kameraschnitt, EDL](camera-cut.de.md).
Ohne Erkennung schneidet das Programm weiter, nur ohne Satzgrenzen;
dasselbe Kapitel sagt, was der Weitwinkel dann tut.

### Wenn etwas klemmt

* **Die Zeile der Aufnahme sagt, was die Trennung meldet.** Aus der
  Installation ist etwas abhandengekommen. Das Programm versucht von
  sich aus einmal, die Pakete über pip zurückzuholen, und fragt danach
  neu nach; klappt das, wird nichts gemeldet und die Trennung läuft
  einfach. Klappt es nicht, steht in der Zeile der Aufnahme der Grund
  selbst — die Zeile, an der der Import gescheitert ist —, und unter
  der Tabelle steht der Befehl, der es wieder hinstellt: derselbe, mit
  dem das Programm installiert wurde, mit `-U`. Im Protokoll steht
  beides, ungekürzt. Bis dahin geht der Lauf ohne sie weiter: mit je
  Person einer Spur kommen die Sprecher aus den Spuren, sonst bleibt
  der Schnitt aus.
* **Die Trennung bricht mit einer Meldung ab.** Das Protokoll sagt, was
  war. Mit je Person einer Spur werden diese Spuren gemessen wie immer,
  und der Schnitt kommt trotzdem, ein Sprecher je Spur; auf einer
  gemeinsamen Aufnahme kommt keiner.
* **Start bleibt gesperrt, und ein Namensfeld steht rot.** Zwei Sprecher
  tragen denselben Namen. Die Zeile unter **Start** sagt, welcher Name
  es ist; gib der Stimme in ihrer Zeile einen eigenen.
* **Auf einem Mac nimmt die Erkennung den langsamen Weg.** Die Command
  Line Developer Tools fehlen. `xcode-select --install` holt sie;
  danach nimmt der Lauf den schnellen Weg.

Die Stimmen haben jetzt Namen, und das Programm hat den Text
mitgeschrieben. Was der Schnitt aus beidem macht, steht in
[Sprecherstatistik, Kameraschnitt, EDL](camera-cut.de.md).

### Weitere Optionen über die Kommandozeile

Diese Optionen gibt es im Fenster nicht.

* `--speakers-local <FILE>` nimmt diese Aufnahme auf diesem Rechner nach
  Stimmen auseinander und schneidet nach dem Ergebnis.
* `--speakers-from <FILE>` holt eine fertige Trennung aus einer
  Projekt- oder Zuordnungsdatei, statt eine zu rechnen.
* `--speakers-count <NUMBER>` gibt an, wie viele Personen zu finden
  sind; ohne die Angabe rechnet das Programm die Zahl selbst aus.
* `--no-speakers-local` nimmt in diesem Lauf keine Aufnahme nach Stimmen
  auseinander, gleich was sonst danach verlangt.
* `--no-speech-recognition` lässt den Text weg.
* `VPM_NO_SPEAKER_SPLIT=1` vor dem Aufruf: keine Spalte **Sprecher**,
  kein Knopf, und die Trennung startet nie von selbst.

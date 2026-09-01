# Sprecherstatistik, Kameraschnitt, EDL

*In English: [camera-cut.md](camera-cut.md). Zurück zum
[Inhalt](README.de.md).*

## Wie der Schnitt entsteht

Der Schnitt braucht zwei Personen mit je einem Namen und einer Kamera.
Eine Person genügt auch, solange es eine zweite Kamera gibt, auf der
niemand ist. Zwei Personen liefern getrennte Aufnahmen, und ebenso die
Stimmen, die auf einer Aufnahme auseinandergehalten wurden, deren
**Sprechername** mit **mehrere Sprecher** beantwortet ist; das Häkchen
**Multitrack** gehört nicht dazu. Beide Wege stehen in [Spracherkennung
und Sprechertrennung](speech.de.md).

**Wer im Schnitt ist, hängt nicht daran, woher er kam.** Eine eigene
Datei mit einer Stimme darauf, der Ton eines Videos mit einer Stimme
darauf, eine Multitrack-Aufnahme oder eine Aufnahme, die in mehrere
Stimmen aufgetrennt wurde — alles zählt gleich, und heraus hält nur
**nicht verwenden**. An drei Personen mit je einer Kamera gemessen: alle
drei sind im Schnitt, und das Bild geht auf alle drei Kameras — die
Person am eigenen Mikrofon darunter, mit 2 Einstellungen.

Damit weiß das Script, wann wer redet, und baut daraus den Schnitt:

* Ein Sprecher allein bekommt seine Kamera, mit Vorlauf.
* Ein kurzes „ja“ nicht: unter **Redet mindestens** bleibt das Bild, wo
  es ist.
* Bei Stille läuft der Weitwinkel: die Kamera, der kein Sprecher
  zugeordnet ist.
* Nach einer langen Einstellung kommt der Weitwinkel an einer
  Satzgrenze.

**Bei mehreren gleichzeitig** gewinnt eine Kamera, die genau diese
Sprecher zeigt, eine auf beide Moderatoren etwa. Passt keine genau, wird
die kleinste genommen, auf der alle Redenden vorkommen. Erst wenn keine
Kamera sie abdeckt, kommt der Weitwinkel. Die Zuordnung sagt, wer auf
welcher Kamera zu sehen ist: zwei Sprecher bei derselben Kamera heißt,
sie zeigt beide.

**Der Name richtet sich nach den Kameras.** Zwischen zwei Kameras
wechselt das Bild, auf einer Kamera nicht. Dort entsteht ein erster
Schnitt an jedem Sprecherwechsel. Drei Fälle, drei Namen, und der Kasten
im Fenster und die Überschrift über dem Abschnitt im Protokoll nennen
denselben:

* **Kameraschnitt**, wenn zwei Personen oder mehr je eine eigene Kamera
  haben;
* **Schnitt mit dem Weitwinkel**, wenn eine Person benannt ist und eine
  zweite Kamera niemanden trägt — ihre Kamera steht, und nur der
  Weitwinkel unterbricht sie;
* **Erster Schnitt nach Sprechern**, wenn alle auf einer Kamera sitzen.

Im Protokoll stehen dieselben drei in Großbuchstaben und auf einer neuen
Zeile: `KAMERASCHNITT`, `SCHNITT MIT DEM WEITWINKEL`,
`ERSTER SCHNITT NACH SPRECHERN`. Solange nichts getrennt ist, heißt der
Kasten **Kameraschnitt**: das Material hat die Frage noch nicht
beantwortet.

Im Ausgabeordner landen `_speakers.csv`, `_speakers.edl`, `_cameracut.csv`
und `_cameracut.edl`, wie der Schnitt auch heißt. Die Köpfe sind
`Speaker,Start TC,End TC,Time from start,Duration s` und
`Shot,Camera,Speaker,Start TC,End TC,Duration s`, die EDL-Titel
`Speakers` und `Camera cut`.

### Die Stellschrauben einstellen

Die Oberfläche nimmt alle Werte entgegen: auf dem Reiter
**Resolve-Schnitt**, im Kasten **Kameraschnitt**. Je Wert ein Feld,
daneben die Einheit und eine kurze Zeile. Den Kasten gibt es, sobald der
Schnitt seine Personen hat — zwei davon, oder eine mit einer zweiten
Kamera, auf der niemand ist; vorher steht an seiner Stelle eine Zeile
und sagt, was fehlt.

![Die Stellschrauben für den Kameraschnitt](images/resolve-cut.de.png)

*Reiter Resolve-Schnitt: links die Werte, rechts die Vorschau. Vier der
Einstellungen stehen grau da, weil noch kein Lauf die Wörter
aufgeschrieben hat.*

Alle acht Felder nehmen Sekunden, und die Zahl in jeder Zeile ist die
Vorgabe. Ein leeres Feld heißt Vorgabe, ein Komma gilt als
Dezimalzeichen, und eine Obergrenze gibt es nicht. Ein negativer Wert
ist nur für **Edit Change Delay** gedacht; die anderen Felder nehmen
ihn an, aber es kommt nichts Gutes dabei heraus.

Drei Felder bestimmen den Rhythmus des Schnitts:

* **Mindestschnittdauer**: 3 s, so lange steht eine Einstellung
  mindestens; höher macht den Schnitt ruhiger (auf der Kommandozeile
  `--min-edit-duration`)
* **Redet mindestens**: 1,5 s, darunter folgt die Kamera nicht; höher
  und sie folgt seltener (auf der Kommandozeile
  `--min-speech-to-switch`)
* **Edit Change Delay**: 0,3 s, so viel später als der Ton wechselt
  das Bild; ein negativer Wert lässt das Bild vorlaufen (auf der
  Kommandozeile `--edit-change-delay`)

Vier formen den Weitwinkel, und die ersten beiden davon gehören
zusammen: eine weiche Grenze und eine harte.

* **Weitwinkel nach**: 70 s, die weiche Grenze. Ab dieser Standzeit
  sucht das Programm eine Satzgrenze und setzt den Weitwinkel dorthin,
  nicht nach der Uhr; kleiner gibt mehr Weitwinkel, 0 schaltet ihn ab
  (auf der Kommandozeile `--wide-after`). An 87 Minuten Interview
  gemessen, in denen einer 59 Minuten redet: bei 40 Sekunden verlässt
  ihn das Bild 77 Mal, alle 39 Sekunden; bei 70 noch 37 Mal, alle 104.
  Beide setzen den Schnitt auf eine Satzgrenze — es geht also um
  Rhythmus, nicht um Richtigkeit.
* **Weitwinkel spätestens**: 120 s, die harte Grenze. Ist seit
  **Weitwinkel nach** keine Satzgrenze gekommen, tritt die längste
  Sprechpause in der Nähe an ihre Stelle, und dort wird geschnitten,
  gleich was gerade gesagt wird; ist auch keine brauchbare Pause da,
  entscheidet die Uhr. Kleiner unterbricht eine stehende Kamera früher
  (auf der Kommandozeile `--wide-latest`)
* **Weitwinkel mindestens**: 5 s, so lange steht der eingeschobene
  Weitwinkel mindestens (auf der Kommandozeile `--wide-length`)
* **Weitwinkel höchstens**: 15 s, und so lange höchstens (auf der
  Kommandozeile `--wide-most`)

Das letzte Feld gehört zur Frage und steht direkt über dem Auswahlfeld,
das über sie entscheidet:

* **Antwort früher im Bild**: 1,5 s, so viel vor dem Ende der Frage
  steht der Antwortende im Bild (auf der Kommandozeile
  `--reaction-lead`). Der Nullpunkt liegt dort, wo der Fragende
  aufhört, nicht dort, wo die Antwort anfängt: die Pause dazwischen
  gehört zur Frage. Gemessen an einer Frage, die bei 10 Sekunden endet,
  und einer Antwort, die bei 12,5 anfängt: mit fünf Sekunden Vorlauf
  liegt der Schnitt bei 5,0 Sekunden, nicht bei 7,5. Die Verzögerung
  aus **Edit Change Delay** kommt nicht noch einmal dazu.

Unter den Feldern stehen vier Auswahlfelder. Sie sagen, was läuft, wenn
die Sprache nicht sagt, wer zu zeigen ist:

* **Nach einer Frage**: **Antwortender** (auf der Kommandozeile
  `--on-question`)
* **Langer Monolog**: **Abwechselnd** (auf der Kommandozeile
  `--on-monologue`)
* **Mehrere reden zugleich**: **Weitwinkel** (auf der Kommandozeile
  `--on-together`)
* **Erkennung unsicher**: **Weitwinkel** (auf der Kommandozeile
  `--on-uncertain`)

Die letzten drei nehmen dieselben vier Werte: **Weitwinkel**,
**Zuhörer**, **Abwechselnd** und **Kein Kamerawechsel**. **Nach einer
Frage** nimmt **nicht vorziehen**, **Antwortender** und **Zuhörer**;
**nicht vorziehen** heißt: kein vorgezogener Kamerawechsel, das Bild
folgt dem Ton hier wie überall sonst.

Unter den Auswahlfeldern hält das Häkchen **Weitwinkel für Begrüßung am
Anfang und Verabschiedung am Ende** Anfang und Ende auf dem Weitwinkel
(auf der Kommandozeile schaltet `--no-wide-edges` es ab). Der Weitwinkel
am Anfang hält, bis das Wort wirklich übergeben wird, nicht bis zum
ersten längeren Block einer Nebenstimme.

**Redet mindestens** erledigt kurze Einwürfe („mhm“, „ja genau“). Eine
Einstellung, die trotzdem zu kurz ausfällt, geht in die folgende, nicht
in die vorherige.

### Die vier Einstellungen, die auf die Wörter warten

**Nach einer Frage**, **Antwort früher im Bild**, **Weitwinkel nach**
und **Weitwinkel höchstens** stehen grau da, solange keine Niederschrift
bekannt ist, und eine Zeile darunter sagt, warum: ohne aufgeschriebene
Sprache wird keine Frage gefunden und keine Satzgrenze, also bewirken
diese vier nichts. Vorher ließen sie sich setzen und taten trotzdem
nichts.

An 200 Sekunden Monolog ohne die Wörter gemessen: **Weitwinkel nach**
liefert denselben einen Einschub, ob dort 40 steht oder 90, und
**Weitwinkel höchstens** dieselben 5,0 Sekunden, ob dort 15 steht oder
40. Mit den Wörtern ergibt dasselbe Material vier Einschübe gegen zwei
und 15 Sekunden gegen 20 bis 30.

**Weitwinkel mindestens** und **Weitwinkel spätestens** bleiben offen,
auch ohne Niederschrift: die beiden zählen nach der Uhr und brauchen
keinen Satz. Offen sind sie, solange es überhaupt einen Weitwinkel gibt
— der nächste Abschnitt handelt vom zweiten Grund, aus dem eine
Einstellung grau dasteht.

Der erste Lauf schreibt die Niederschrift. Von da an sind die vier
offen, und die Vorschau rechnet mit ihnen.

### Wenn keine Kamera frei von Sprechern ist

Der Weitwinkel ist die Kamera, auf der niemand ist. Trägt jede Kamera
einen Sprecher, gibt es keinen, und die fünf Einstellungen, die nichts
anderes sagen als das, was der Weitwinkel tut, stehen grau da:
**Weitwinkel nach**, **Weitwinkel spätestens**, **Weitwinkel
mindestens**, **Weitwinkel höchstens** und das Häkchen für die Ränder.
In den drei unteren Auswahlfeldern wird der Eintrag **Weitwinkel** mit
ihnen grau und lässt sich nicht mehr wählen. Er bleibt aber in der
Liste, statt daraus zu verschwinden, und wer darauf zeigt, erfährt den
Grund: die Antwort auf „warum kann ich das nicht wählen“ gehört dorthin,
wo die Frage aufkommt.

Unter den Einstellungen sagt eine Zeile dasselbe in Worten — keine
Kamera ist frei von Sprechern, also gibt es keinen Weitwinkel, und diese
fünf Einstellungen bewirken nichts. Zwei Personen auf je einer eigenen
Kamera sind genau dieser Fall, und für ein Gespräch, das mit zwei
Kameras aufgenommen wird, ist er der Normalfall.

Die Zeile nennt auch die beiden Auswege; einer von beiden genügt:

* einer Kamera im Feld **Typ** den Wert **Weitwinkel** geben. Das Feld
  steht bei jeder Videodatei in der Liste und in der Kameratabelle auf
  dem Reiter **Zuordnung & Zeitfenster**. Eine so gekennzeichnete Kamera
  nimmt keine Sprecher mehr an, und die Kennzeichnung geht dem vor, was
  das Programm von selbst herausfinden würde;
* oder eine Kamera ohne Sprecher lassen. Jede Kamera, der niemand
  zugeordnet ist, ist ein Weitwinkel.

Mehrere Weitwinkel nebeneinander sind auf beiden Wegen erlaubt. Der
Schnitt nimmt einen davon, und das Protokoll sagt, wie viele es sind und
welchen es genommen hat, statt im Stillen eine Mehrheit auszurechnen.

Eine Zahl, die schon in einem grau gewordenen Feld steht, bleibt
erhalten, und der Lauf richtet sich ebenso wenig nach ihr: ohne
Weitwinkel gilt **Weitwinkel nach** als 0, das Häkchen als
abgeschaltet, und ein Auswahlfeld, in dem noch **Weitwinkel** steht,
wirkt wie **Kein Kamerawechsel**. Das Protokoll sagt es unter der
Überschrift des Schnitts: jede Kamera trägt einen Sprecher, also
bewirken die vier Weitwinkel-Einstellungen und der Haken für die Ränder
hier nichts.

Keines der beiden Graus bleibt für immer. Eine Kamera kennzeichnen oder
einer den Sprecher wegnehmen, und die fünf sind im selben Augenblick
wieder da — so wie die vier, sobald ein Lauf die Wörter aufgeschrieben
hat.

### Wenn die Sprache nicht sagt, wer zu zeigen ist

Vier Fälle, und was jedes der vier Auswahlfelder entscheidet:

* **Nach einer Frage**: das Bild geht zur Antwort, bevor sie anfängt.
  Nur nach einer Frage, die nicht vom Vielredner kommt, wenn sofort ein
  anderer übernimmt und das Wort behält.
* **Langer Monolog**: einer hat über **Weitwinkel nach** hinaus das
  Wort. **Abwechselnd** merkt sich, was die letzte Unterbrechung zeigte.
* **Mehrere reden zugleich**: und keine Kamera zeigt genau sie.
* **Erkennung unsicher**: die Erkennung zerfasert über eine Passage,
  oder von einem Namen bleiben nur Schnipsel.

**Was aus den Fragen geworden ist, steht im Protokoll.** Eine Zeile
nennt, wie viele Fragezeichen im Transkript standen und bei wie vielen
davon das Bild vorgezogen wurde. Dort heißt die Sache
Reaktionsschnitt, und das ist die letzte Stelle, an der das Wort noch
vorkommt: auf dem Bildschirm heißen die beiden Einstellungen **Nach
einer Frage** und **Antwort früher im Bild**. Wo Fragen wegfielen, folgt
eine zweite Zeile mit der Zahl je Grund — der Hauptsprecher fragte,
Fragender und Antwortender auf einer Kamera, niemand antwortete
rechtzeitig, die Antwort behielt das Wort nicht, bei der Frage sprach
niemand. Ohne Niederschrift steht an ihrer Stelle genau das, damit eine
Einstellung, die nichts bewirken kann, nicht wie eine kaputte aussieht.

**Zuhörer** heißt: wer als Nächstes spricht, und nur, wenn auf dieser
Kamera in den letzten 20 Sekunden jemand zu hören war; sonst der
Weitwinkel. Die 20 Sekunden stehen fest; kein Feld und kein Schalter
setzt sie.

**Zuhörer** und **Abwechselnd** zeigen einen Menschen, von dem das
Programm nur weiß, dass er kurz vorher zu hören war. Es sieht das Bild
nicht. **Weitwinkel** einstellen, wo ein falsches Gesicht im Bild teurer
ist als ein ruhiges.

Zwei Sprecher auf einer Kamera zählen für diese Regeln als einer: ein
Sprecherwechsel zwischen ihnen ändert das Bild nicht.

### Was Vorschau und Sprecherkasten zeigen

Der Kasten **Kameraschnitt -- Vorschau** trägt die Länge im Titel und
darunter eine Zeile Zahlen:

* Einstellungen
* mittlere Standzeit
* kürzeste Einstellung
* längste Standzeit einer Kamera
* die Redezeit, geteilt in eigene Kamera, Weitwinkel und fremde Kamera

Die letzte Zahl steht in der Warnfarbe.

Der Kasten **Sprecher** zeigt je Sprecher:

* Redezeit und Anteil
* Zahl der Blöcke und deren mittlere Länge
* eine Zeile Stille

Die Überschrift nennt die Quelle: **Sprecher, nach Stimmen getrennt**
oder **Sprecher, selbst aus den Spuren gemessen**. In der Tabelle kann
beides zugleich stehen — Stimmen aus einer Trennung und Spuren, die aus
ihrem eigenen Mikrofon gemessen wurden, nebeneinander —, und dann heißt
die Überschrift für alle zusammen **Sprecher, nach Stimmen getrennt**.
Das Protokoll hält die beiden auseinander und druckt beide Marken, jede
über den Zeilen, die zu ihr gehören.

Bei zwei gleichzeitig Redenden zählt die Zeit doppelt, bei der Stille
nicht. Deshalb ergeben die Zeilen zusammen mehr als die Laufzeit.

Beides rechnet das Programm aus der Übergabedatei
`<Produktion>_resolve.json` des letzten Laufs, bei jeder Änderung neu
und immer für das gewählte Zeitfenster. Schreiben und Hochladen gehören
zum Lauf, nicht zur Vorschau.

Der Knopf **Sprecher jetzt messen** steht oben im Vorschau-Kasten, unter
dem, was die Vorschau sagt, und nicht unter diesem, solange eine Spur weder von einer Trennung abgedeckt
noch gemessen ist; daneben steht, wer fehlt: **Name noch nicht gemessen
-- im Schnitt, in dieser Vorschau noch nicht**. Diese Leute sind im
Schnitt; ein Druck holt sie auch in die Vorschau. Sind überhaupt keine
Sprecher bekannt, sagt der Vorschau-Kasten das an Stelle seiner Zahlen,
und der Kasten **Sprecher** bleibt leer. Geht die Messung schief, steht
der Grund neben dem Knopf. Sprecher, die später auftauchen, starten die
Vorschau von selbst.

### Schnittband und Legende lesen

Im Kasten **Kameraschnitt -- Vorschau** sitzt das **Schnittband**, an
Stelle der Positionsleiste: der gerechnete Schnitt über die ganze Länge,
je Einstellung ein Balken in der Farbe seiner Kamera. Die Skala trägt
Minuten über das Ganze und Sekunden im Hineingezoomten. Zeigen nennt
Kamera, Von-bis und Dauer, Klicken setzt die Stelle für den Player.
Darunter die **Legende**: je Kamera im Schnitt ein Eintrag, ein Kästchen
in ihrer Farbe und dann wie oft, wer, Anteil und Zeit —
`129 × Gast  50 %  (29:48 Min)`.

**Ein Eintrag ist nach den Personen benannt, nicht nach der Datei.** Ein
Dateiname sagt nichts, was nicht schon bekannt wäre; die Zuordnung sagt
es. Also trägt ein Eintrag:

* den Sprecher dieser Kamera, mit Namen;
* alle Namen mit Pluszeichen verbunden, wenn mehrere auf derselben
  Kamera sind — `41 × Sprecher 1 + Sprecher 2  14 %  (9:37 Min)`;
  keiner fällt weg und keiner wird gekürzt;
* **Weitwinkel** für die Kamera, die als solcher dient;
* den Kurznamen der Kamera, wenn ihr niemand zugeordnet ist und sie
  nicht der Weitwinkel ist, denn sie Weitwinkel zu nennen wäre eine
  Behauptung und keine Ablesung;
* die Kamera neben dem Namen, wenn zwei denselben Namen ergeben — ein
  Sprecher zweimal gefilmt —, sonst wären die Balken nicht
  auseinanderzuhalten.

Die Legende bricht um. In einem schmalen Fenster steht sie auf zwei
Zeilen statt auf einer, und nichts wird gekürzt oder weggelassen, damit
es passt: Die Zeile bricht zwischen zwei Einträgen und an einem Plus,
nie mitten in einem Namen und nie mitten in einer Zahl.

Es sind die Farben der Clips in Resolve, mit einer Ausnahme: der
Weitwinkel wird in blassem Salbeiton angezeigt. In Resolve heißt der Clip
weiterhin Tan. Brown, Chocolate, Cocoa, Navy und Teal werden auf dunklem
Grund aufgehellt, Beige auf hellem abgedunkelt.

Das Band lässt sich zoomen. **+** zeigt halb so viel um die aktuelle
Stelle, **−** doppelt so viel, **▭** wieder die ganze Länge; das Mausrad
über dem Band tut dasselbe, ebenso die Tasten Plus, Minus und 0 nach
einem Klick auf das Band. Hineinzoomen, um zu sehen und zu hören, ob ein
Schnitt in einer Pause oder mitten im Wort sitzt. Beim Abspielen folgt
der Ausschnitt der Position, damit er nicht aus dem Bild läuft.

Am Ende der Zeile stehen der erste und der letzte gezeigte Augenblick
([Die Oberfläche](interface.de.md)). Sobald der Zoom nah genug ist, um
einen einzelnen Schnitt zu beurteilen, sagen die Balken nicht mehr,
welcher Teil der Folge vor einem liegt; die beiden Zeiten sagen es.

### Was das Bild sagt

Das Bild im Vorschaukasten trägt einen eigenen Hinweis, damit ein Blick
beide Fragen zugleich beantwortet: wer spricht, und welche Kamera
gerade läuft.

Unmittelbar unter dem Bild und genau so breit wie dieses liegt eine
Fläche in der Farbe der laufenden Einstellung, und derselbe Ton läuft
als Rahmen um das Bild, so dass beides als ein Block zu lesen ist. Es
sind die Farben des Schnittbands, der Weitwinkel in seinem blassen
Salbeiton. Das Bild behält dabei sein eigenes Seitenverhältnis, und die
Fläche bleibt nur so hoch, wie die Schrift darauf es braucht; die steht
darin mittig. Was beide nicht brauchen — in einem schmalen, hohen
Fenster ist das viel —, bleibt in der Farbe des Kastens dahinter und
nicht in der der Einstellung: Die Farbe soll wie eine Zeile zum Bild
gehören und nicht wie ein zweites Farbfeld darunter stehen. Auf der
Fläche stehen zwei Zeilen:

* **wer spricht**, fett, und bei mehreren alle. Läuft dabei der
  Weitwinkel, steht **(Weitwinkel)** hinter dem Namen: der Weitwinkel
  ist eine Wahl der Kamera und keine Stille, und wer auf ihm spricht,
  behält seinen Namen. Spricht niemand, steht dort **Kein Sprecher**.
  Leer ist die Zeile nie — eine leere Zeile liest sich wie ein Fehler.
* **die Kamera** darunter, mit demselben Namen, den ihr auch das
  Schnittband gibt. Ein Name, der nicht ins Bild passt, wird vorn
  gekürzt, und ein Auslassungszeichen sagt, wo.

Ein Name bleibt **mindestens eine halbe Sekunde** stehen, damit ein
kurzes „Ja“ zwischen zwei langen Antworten ihn nicht aufblitzen lässt.
Der Preis dafür: der Name kann dem Ton um ebenso viel nachhängen.
Nur der Hinweis wartet: das Bild schneidet dort, wo der Schnitt es
sagt, gleich welcher Name gerade noch steht. In den Schnitt, die
Shotlist und die EDLs geht davon nichts ein — es ist Lesestoff und
sonst nichts.

Hat eine Einstellung kein Bild — eine Kamera im Schnitt, deren Datei
nicht da ist —, gibt es nichts, worunter sich die Fläche setzen könnte:
Dann füllt die Farbe den ganzen Kasten, und dieselben zwei Zeilen
stehen darauf. Der Ton läuft weiter, und es bleibt lesbar, wer
spricht und auf welche Kamera der Lauf ihn setzt.

Unter dem Bild stehen links der In-Punkt, in der Mitte die Position und
rechts der Out-Punkt. Die Kamera wird dort nicht wiederholt — sie steht
im Bild.

### Wie die Vorschau-Player Datei und Ton wählen

Zwei Player zeigen das Material, und beide suchen sich ihre Datei
selbst.

Auf dem Reiter **Zuordnung & Zeitfenster** gilt diese Rangfolge:

1. eine Datei, die **In-Punkt und Out-Punkt enthält**, sonst laufen die
   Sprungknöpfe ins Leere
2. sonst eine mit wenigstens einer der Grenzen
3. unter gleich guten die Kamera ohne **zugeordneten Sprecher**
4. darunter die längste
5. nie eine Datei auf „Video ignorieren“, nie Vorspann oder Abspann

Die Projektdatei merkt sich, welche Datei zuletzt im Player stand, und
nimmt sie wieder, solange sie die Grenzen genauso gut abdeckt wie die
beste Alternative. Ohne Timecode oder gemessene Zeitachse behauptet das
Programm nichts über die Grenzen; sobald die Achse da ist, sieht der
Player noch einmal nach. **zu In-Punkt** und **zu Out-Punkt** holen sich
ihre Datei selbst; wenn es gar keine gibt, steht eine Zeile da, warum
nichts passiert ist.

Mit **zugeordneten Ton hören** läuft zum Bild der Ton, der zu dieser
Kamera gehört:

* die **aufbereitete Spur** von auphonic.com (`final_<Name>_<TC>.wav`),
  auf dem unter **Lautheit** gewählten Ziel, oder auf dem des Presets,
  wo nichts gewählt wurde, und mit BWF-Timecode
* sonst die **Rohaufnahme** des zugeordneten Sprechers
* beim Weitwinkel, der Kamera ohne zugeordneten Sprecher, der
  **Full-Mix**, sofern er vorliegt

Rohaufnahmen liegen 16 bis 36 dB unter dem aufbereiteten Ton, und lauter
machen kann die Oberfläche sie nicht. Der Kurzhinweis nennt, was läuft
und in welcher Version.

Auf dem Reiter **Resolve-Schnitt** zeigt der Player im Vorschau-Kasten
immer etwas: wenn ein Schnitt da ist, spielt er ihn und schaltet an jeder
Kante die Kamera um, sonst die Datei ohne zugeordneten Sprecher. Ohne
Schnitt trägt der Hinweis unter dem Bild den Namen dieser Datei und sagt
**Kein Sprecher**, denn wer spricht, ist dann noch gar nicht ermittelt.

Der Ton kommt durchgehend aus einer Datei, am liebsten aus dem
**Full-Mix**, der auf Sendepegel liegt und auch in die Schnitt-Timeline
geht. Solange es ihn nicht gibt, nimmt das Programm die Kameradatei, die
den Mix als erste Tonspur trägt — dieselbe Wahl wie für Perspektive 1
des Multicam-Clips, und deutlich leiser.

`start_s` ist die Uhrzeit, zu der die Programmzeit null ist. Es ist der
früheste Tonanfang, der wirklich bekannt ist, eigener Timecode oder
gemessene Lage; sonst der früheste Kamera-Timecode; sonst nichts.
In-Punkt und Out-Punkt verschieben den Nullpunkt mit. Die Stelle in jeder
Kameradatei ist Programmzeit minus Versatz, derselbe Versatz, mit dem
auch die Schnitt-Timeline gebaut wird.

Das Programm setzt jede Stelle nach, bis sie sitzt;
[Inside the script](../development/internals.md) (englisch) nennt, wie
oft und wie lange.

### Sprecher ohne Auphonic messen

Ohne Auphonic bleibt der Lauf lokal, und das Script misst aus den Spuren,
wer wann redet. Der Weg dahin steht in [Aufbereitung über
auphonic.com](auphonic.de.md) (auf der Kommandozeile
`--without-auphonic`). Im Protokoll steht dieser Abschnitt unter der
Überschrift `SPRECHER -- HIER GEMESSEN`.

So liest das Script die Spuren:

* Es zerlegt jede Spur in Blöcke von 100 Millisekunden.
* Es misst jeden Block gegen den eigenen Grundpegel der Spur, das
  leiseste Fünftel ihrer Blöcke; 10 dB darüber gilt als Sprache.
* Pausen unter 0,35 Sekunden sind kein Sprecherwechsel.
* Passagen unter 0,2 Sekunden zählen nicht. An 31 Minuten
  Dreimikrofon-Material gemessen: darunter sind die Passagen, die
  hinzukommen, im Mittel zwei Zehntelsekunden lang — das ist Atem
  und keine Sprache. Darüber, bei vier Zehnteln, fiel ein kurzes
  „mhm“ weg und die Antwort las sich als Pause: 21 Pausen über zwei
  Sekunden waren in der halben Stunde gar keine.

Davor rechnet das Script das **Übersprechen aus der Messung** heraus,
nicht aus dem Ton. Es sucht die Stellen, an denen genau eine Person
spricht: diese höchstens 10 dB unter ihrem eigenen Sprachpegel, die
anderen mindestens 6 dB unter ihrem. Dort misst es, wie laut diese
Stimme in den anderen Mikrofonen ankommt, und rechnet den eigenen Anteil
aus jeder Spur zurück. Keiner dieser Werte lässt sich einstellen; es
gibt kein Feld und keinen Schalter dafür.

Es geht auch bei Mikrofonen, die enger stehen, als die 3:1-Regel will.
Für ein Paar ohne mindestens drei solche Stellen zieht es nichts ab. Bei
Mikrofonen nebeneinander oder zu ähnlichen Spuren lässt es sich nicht
auflösen: die Pegel bleiben, wie gemessen, und das Protokoll sagt warum
und nennt das schlechteste Paar.

Bis 5 dB Trennung hinunter arbeitet die Erkennung exakt, deutlich unter
den 9,5 dB, die die 3:1-Regel verlangt; die Messreihe dahinter steht in
[What was measured](../development/measurements.md) (englisch).

Das Protokoll sagt, wie stark das Übersprechen war, und darunter je
Sprecher Redezeit und Zahl der Abschnitte. Wenn nichts zu hören war,
gibt es keinen Kameraschnitt.

Der Knopf **Sprecher jetzt messen** tut in der Oberfläche dasselbe, ohne
auf einen Lauf zu warten: gröber als die Trennung nach Stimmen, aber
genug, um den Schnitt einzustellen. Die beiden schließen einander nicht
aus. Stimmen aus einer Trennung und hier gemessene Spuren gehen in ein
und dieselbe Rechnung, und den Knopf gibt es, solange eine Spur weder
von einer Trennung abgedeckt noch gemessen ist — auch dann, wenn schon
getrennt wurde.

### Schneiden, wenn eine Kamera alle zeigt

Bei mehreren Sprechern auf einer Kamera schneidet das Programm am
Sprecherwechsel: jede Einstellung kommt aus demselben Clip, zeigt also
denselben Bildausschnitt, und trägt den Namen dessen, der spricht.
Resolve bekommt eine Spur, die an den richtigen Stellen schon getrennt
ist, und dort lässt sich jedes Stück gruppieren, einfärben und
heranzoomen, so dass aus dem Weitwinkel der Sprecher wird.

Die Schnittliste sagt es mit: bei einer Kamera für alle trägt die EDL
den Sprechernamen an Stelle des Kameranamens. Die Spalte Sprecher in
`_cameracut.csv` steht in jedem Fall da.

**Eine einzige Stimme auf einer Kamera gibt keinen Schnitt.** Niemand
übergibt, also gibt es nichts zu schneiden, und weder Schnittliste noch
EDL entstehen. Die Passagen gehen in die Übergabedatei, und Resolve
setzt sie als Marker auf die Timeline, die es baut: die eine Kamera am
Stück mit dem Mix darunter.

**Mit einer zweiten Kamera gibt eine einzige Stimme sehr wohl einen
Schnitt.** Auf dieser Kamera ist niemand, also steht die Kamera des
Sprechers, und der Weitwinkel unterbricht sie; der Kasten heißt dann
**Schnitt mit dem Weitwinkel**. Fünf Minuten auf zwei Kameras ergaben
15 Einstellungen, davon 7 Weitwinkel, gegen 1 Einstellung auf einer
einzigen Kamera.

### Was die Projektdatei behält

`videopodcast-magic_<Produktion>.json` im Ausgabeordner enthält alles,
was man von Hand eingestellt hat und nicht wieder erraten kann. Das sind
die Dateiliste, Name und Ablageort der Produktion, das Zeitfenster, alle
Werte des Kameraschnitts, wer zu welcher Kamera gehört, das
Auphonic-Preset, die Stereo-Häkchen, die gemessene Lage jeder Datei und
wie schnell ihr Recorder lief; der API Key steht **nicht** darin.

Beim Öffnen prüft das Programm das Format der Datei und weist eine Datei
in einem anderen Format ab. Ältere Projektdateien kann es nicht mehr
öffnen.

Sie entsteht schon, sobald das Programm die Zeitachse gemessen hat, dann
noch neben dem Material, weil es den Ausgabeordner noch nicht gibt. Wenn
er später gewählt oder die Produktion umbenannt wird, **wandert sie
mit**. Es gibt immer genau eine.

**Projekt öffnen ...** auf der Ablegefläche holt sie zurück, solange
keine Dateien in der Liste stehen; bei einem Fehlgriff sucht das Programm
im selben Ordner nach `videopodcast-magic*.json`. Daneben liegt die
Übergabedatei `<Produktion>_resolve.json`. Daraus rechnet die Vorschau,
und daraus baut der Resolve-Teil.

### Wie das Programm den Weitwinkel setzt

Ein Weitwinkel kommt nicht nach der Uhr. Jenseits von **Weitwinkel
nach** steigt er an einer Satzgrenze nahe der gewünschten Stelle ein,
und den genauen Punkt liefert der Ton: die Senke im Pegel um diese
Satzgrenze. Beides ist gemessen, also gibt dasselbe Material denselben
Schnitt.

Er steht so lange, wie **Weitwinkel mindestens** verlangt, dann bis zum
Satzende. Wenn dieses Ende jenseits von **Weitwinkel höchstens** liegt,
beendet ihn die letzte Teilsatzgrenze davor.

**Weitwinkel spätestens** ist die Reißleine. Kommt keine Satzgrenze,
tritt die längste Sprechpause in der Nähe an ihre Stelle, und dort wird
geschnitten, gleich was gerade gesagt wird; ist auch keine brauchbare
Pause da, wird eine Kamera nach der Uhr aufgebrochen, damit kein Stück
von ihr länger als diese Zeit steht. Ohne Niederschrift gibt es
überhaupt keine Satzgrenzen: der Weitwinkel geht dann an die längste
Pause in der Nähe und steht die eingestellte Mindestzeit — deshalb ist
die weiche Grenze gesperrt, solange die Wörter fehlen, und die harte
nicht.

### Was Kennzahlen und Farbvergleich messen

Am Ende jedes Laufs entsteht `<Produktion>_metrics.csv`; das Protokoll
wird beim nächsten Lauf überschrieben, diese Datei nicht. Über Monate
sieht man daran, was in einem einzelnen Lauf nicht auffällt: dass ein
Recorder langsamer wird, dass eine Kamera zunehmend anders aussieht als
die übrigen, dass das Übersprechen mit einem neuen Aufbau zugenommen hat.

Die Spalten sind `Area,Metric,Before,After,Unit`, durch Komma getrennt,
mit Punkt als Dezimalzeichen. `Area` und `Metric` bleiben in jeder
Sprache englisch, damit zwei Läufe vergleichbar bleiben. Vorher ist die
Spur, wie sie hereinkam, nachher, wie sie herausgeht, beides mit
demselben Verfahren gemessen.

Auf einem deutschen System kostet das Komma einen Schritt: Excel öffnet
eine CSV per Doppelklick mit dem Semikolon und legt die ganze Zeile in
eine Spalte. Der Weg hinein ist `Daten > Aus Text/CSV`; dort Trennzeichen
und die Sprache der Zahlen von Hand setzen. LibreOffice fragt beides von
selbst.

| Bereich | Was drinsteht |
|---|---|
| `Audio <Name>` | Lautheit, Spitze, Lautheitsumfang, Uhrengang in ppm, Versatz und Restfehler |
| `Audio` | Verstärkung auf jede Spur, Lautheitsziel |
| `Cut` | Zahl der Einstellungen, Median, kürzeste, längste, Anteil je Kamera |
| `Speech time` | Sekunden je Sprecher |
| `Colour <Name>` | Helligkeit je Kamera, Abstand zum Mittel, Farblage |

**Der Farbvergleich** misst an fünf Stellen jeder Kameradatei Helligkeit
und Farblage, verglichen gegen den Mittelwert aller Kameras statt gegen
eine Vorgabe. Ab etwa zwölf Stufen steht eine Warnung dabei. Beide
Messungen zusammen dauern bei langen Aufnahmen ein paar Minuten: die
Lautheitsmessung läuft je Spur zweimal durch.

### Wenn etwas klemmt

* **Die Vorschau sagt, dass keine Sprecher bekannt sind, und der Kasten
  Sprecher ist leer.** Unten im Vorschau-Kasten **Sprecher jetzt
  messen** drücken. Geht die Messung schief, steht der Grund neben dem
  Knopf.
* **Der Kasten Sprecher zeigt Sprecher, und die Vorschau sagt, dass
  jemand noch nicht gemessen ist.** Diese Person ist im Schnitt; nur die
  Vorschau kann sie nicht zeigen, weil ihre Spur weder getrennt noch
  gemessen ist. **Sprecher jetzt messen** holt sie in die Vorschau.
* **Es kommt kein Schnitt heraus.** Auf den Spuren war nichts zu hören,
  oder die Trennung hat nur eine Stimme gefunden und es gibt nur eine
  Kamera. Das Protokoll sagt es unter `SPRECHER -- HIER GEMESSEN` oder
  `SPRECHER -- NACH STIMMEN GETRENNT`.
* **Auf dem Reiter Resolve-Schnitt fehlt der Kasten für den Schnitt.**
  Niemand trägt Namen und Kamera, oder eine Person tut es und es gibt
  keine zweite Kamera. Auf dem Reiter **Zuordnung & Zeitfenster** jeder
  Stimme einen Namen und eine Kamera geben.
* **Vier Einstellungen sind grau und nehmen nichts an.** Es ist noch
  keine Niederschrift da. **Nach einer Frage**, **Antwort früher im
  Bild**, **Weitwinkel nach** und **Weitwinkel höchstens** brauchen
  eine; der erste Lauf schreibt sie, danach nehmen sie einen Wert an.
* **Fünf Einstellungen sind grau, und der Weitwinkel lässt sich nicht
  wählen.** Jede Kamera trägt einen Sprecher, also gibt es keinen
  Weitwinkel. Einer Kamera im Feld **Typ** den Wert **Weitwinkel**
  geben, oder einer den Sprecher wegnehmen.
* **In einem Auswahlfeld steht Weitwinkel, und der Schnitt hält
  stattdessen das Bild.** Es gibt keinen Weitwinkel, zu dem er gehen
  könnte, also wirkt **Weitwinkel** wie **Kein Kamerawechsel**. Das
  Protokoll nennt es im Abschnitt des Schnitts.
* **Das Bild steht, obwohl der Sprecher wechselt.** Beide Sprecher
  sitzen auf einer Kamera, oder der Block ist kürzer als **Redet
  mindestens**.
* **Die Vorschau zeigt viel Zeit auf einer fremden Kamera.** Auf dem
  Reiter **Zuordnung & Zeitfenster** nachsehen, wer welcher Kamera
  zugeordnet ist.
* **Der Player ist sehr leise.** Den Full-Mix gibt es noch nicht, also
  trägt eine Kameradatei den Ton. Lauter machen kann die Oberfläche ihn
  nicht.
* **Der Schnitt ist unruhig.** **Mindestschnittdauer** oder **Redet
  mindestens** heraufsetzen.

Der Schnitt steht jetzt: eine Einstellungsliste, zwei EDLs und eine
Vorschau, in der er zu prüfen ist. Was Resolve daraus macht, steht in
[DaVinci Resolve](resolve.de.md).

### Weitere Optionen über die Kommandozeile

Im Fenster gibt es dafür keine Entsprechung.

* `--reaction-gap` wie schnell die Antwort auf die Frage folgen muss,
  damit sie überhaupt vorgezogen wird (3 s); größer und das geschieht
  öfter
* `--reaction-hold` welchen Anteil der zehn Sekunden nach der Frage der
  Antwortende halten muss, zwischen 0 und 1 (0,7); höher und er greift
  seltener. Beide gehören zur Frage und wollen eine Niederschrift, wie
  die zwei Einstellungen dafür im Fenster
* `--no-metrics` lässt die Kennzahlendatei und den Farbvergleich weg
* `VPM_PLAYER_DEBUG=1` vor dem Aufruf stellt Uhr, Stand und Sollwert
  aller drei Player unter das Bild und jeden Versuch auf die Konsole

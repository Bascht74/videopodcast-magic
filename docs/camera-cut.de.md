# Sprecherstatistik, Kameraschnitt, EDL

*In English: [Speaker statistics, camera cut, EDL](camera-cut.md). Zurück zum [Inhalt](README.de.md).*

## Sprecherstatistik, Kameraschnitt, EDL

Bei Multitrack weiß das Script, wann wer geredet hat — von auphonic.com
oder hier gemessen (siehe unten). Daraus baut es den Kameraschnitt:

* Wer allein spricht, bekommt seine Kamera, mit Vorlauf.
* Ist es still, läuft der Weitwinkel.
* Steht eine Einstellung lange, kommt der Weitwinkel in eine
  Sprechpause.

**Reden mehrere gleichzeitig**, gewinnt eine Kamera, die genau diese
Sprecher zeigt — eine auf beide Moderatoren etwa. Passt keine genau, wird
die kleinste genommen, auf der alle Redenden vorkommen. Erst wenn keine
Kamera sie abdeckt, kommt der Weitwinkel. Wer auf welcher Kamera zu sehen
ist, steht in der Zuordnung: zwei Sprecher bei derselben Kamera heißt,
sie zeigt beide.

Im Ausgabeordner landen `_speakers.csv`, `_speakers.edl`, `_cameracut.csv`
und `_cameracut.edl`. Die Köpfe sind
`Speaker,Start TC,End TC,Time from start,Duration s` und
`Shot,Camera,Start TC,End TC,Duration s`, die EDL-Titel `Speakers` und
`Camera cut`. Auphonics eigene `<Produktion>_statistics.json` liegt mit
allem anderen vom Dienst in `auphonic-tracks/`.

### Die Stellschrauben

Bei Multitrack lassen sich alle Werte in der Oberfläche eintragen: auf
dem Reiter **3. Resolve-Schnitt**, im Kasten **Kameraschnitt**, je Wert
ein Feld, daneben die Einheit und eine kurze Zeile.

![Die Stellschrauben für den Kameraschnitt](images/resolve-cut.de.png)

*Reiter 3: links die Werte, rechts die Vorschau.*

Die Felder in der Reihenfolge, in der sie stehen:

* **Mindestschnittdauer** -- 3 s, so lange steht eine Einstellung
  mindestens (auf der Kommandozeile `--min-edit-duration`)
* **Edit Change Delay** -- 0,3 s, so viel später als der Ton wechselt
  das Bild (auf der Kommandozeile `--edit-change-delay`)
* **Weitwinkel nach** -- 45 s, ab dieser Standzeit ein kurzer Blick in
  den Weitwinkel (auf der Kommandozeile `--wide-after`)
* **Weitwinkel höchstens** -- 2,5 s, wie lange der Weitwinkel dabei
  höchstens steht (auf der Kommandozeile `--wide-length`)
* **Weitwinkel mindestens** -- 1,5 s, und wie kurz er nicht wird --
  notfalls steht er in die ersten Worte hinein (auf der Kommandozeile
  `--wide-min`)
* **Weitwinkel spätestens** -- 120 s, Obergrenze für eine Kamera am
  Stück (auf der Kommandozeile `--wide-latest`)
* **Weitwinkel im Redefluss** -- 6 s, so lange steht er, wenn mitten im
  Reden geschnitten wird (auf der Kommandozeile `--wide-flow`)

Unter den Feldern hält das Häkchen **Weitwinkel für Begrüßung am Anfang
und Verabschiedung am Ende** Anfang und Ende auf dem Weitwinkel (auf der
Kommandozeile schaltet `--no-wide-edges` es ab).

**Mindestschnittdauer** erledigt kurze Einwürfe mit („mhm", „ja genau"):
ein zu kurzer Blick auf die andere Kamera fällt in die vorherige
Einstellung zurück.

### Vorschau und Sprecherstatistik

Rechts steht der Kasten **Kameraschnitt -- Vorschau**; er trägt die Länge
im Titel und darunter eine Zeile Zahlen: Einstellungen, mittlere
Standzeit, kürzeste Einstellung, längste Standzeit einer Kamera, dazu die
Redezeit, geteilt in eigene Kamera, Weitwinkel und fremde Kamera. Die
letzte Zahl steht in der Warnfarbe.

Links, unter den Stellschrauben, der Kasten **Sprecher**: je Sprecher
Redezeit, Anteil, Zahl der Blöcke und deren mittlere Länge, dazu eine
Zeile Stille. Die Überschrift nennt die Quelle: **Sprecherstatistik von
auphonic.com** oder **Sprecher, selbst aus den Spuren gemessen**. Wo zwei
gleichzeitig reden, zählt die Zeit doppelt, bei der Stille nicht —
deshalb ergeben die Zeilen zusammen mehr als die Laufzeit.

Beides wird aus der Übergabedatei des letzten Laufs gerechnet, bei jeder
Änderung neu und immer für das gewählte Zeitfenster. Geschrieben oder
hochgeladen wird nichts.

Fehlt die Statistik, sagt der Kasten das und bietet den Knopf **Sprecher
jetzt messen**; geht die Rechnung schief, steht an seiner Stelle der
Grund. Ergebnisse, die später auftauchen — auch in
`Ergebnis/auphonic-tracks/` —, starten die Vorschau von selbst.

### Schnittband und Legende

Im Vorschau-Kasten sitzt unter dem Spieler das **Schnittband**, an Stelle
der Positionsleiste: der gerechnete Schnitt über die ganze Länge, je
Einstellung ein Balken in der Farbe seiner Kamera. Die Skala trägt
Minuten über das Ganze und Sekunden im Hineingezoomten. Zeigen nennt
Kamera, Von-bis und Dauer, Klicken setzt die Stelle für den Spieler.
Darunter die **Legende**: je Kamera ein Farbtupfer und
`62 × Kandidat  77 %  (48:19 Min)`.

Es sind die Farben der Clips in Resolve, mit einer Ausnahme: der
Weitwinkel wird in blassem Salbeiton angezeigt. In Resolve heißt der Clip
weiterhin Tan. Brown, Chocolate, Cocoa, Navy und Teal werden auf dunklem
Grund aufgehellt, Beige auf hellem abgedunkelt.

Das Band lässt sich zoomen. **+** zeigt halb so viel um die aktuelle
Stelle, **−** doppelt so viel, der dritte Knopf wieder die ganze Länge;
das Mausrad über dem Band tut dasselbe, ebenso die Tasten Plus, Minus
und 0. Hineingezoomt sieht und hört man, ob ein Schnitt in einer Pause
oder mitten im Wort sitzt. Beim Abspielen folgt der Ausschnitt der
Position, damit er nicht aus dem Bild läuft.

### Die Vorschau-Spieler

Zwei Spieler zeigen das Material, und beide suchen sich ihre Datei
selbst.

**Auf dem Reiter 2. Zuordnung & Zeitfenster** gilt diese Rangfolge:

1. eine Datei, die **In point und Out point enthält**, sonst laufen die
   Sprungknöpfe ins Leere
2. sonst eine mit wenigstens einer der Grenzen
3. unter gleich guten die Kamera ohne **zugeordneten Sprecher**
4. darunter die längste
5. nie eine Datei auf „Video ignorieren", nie Vorspann oder Abspann

Die Projektdatei merkt sich, welche Datei zuletzt im Spieler stand, und
nimmt sie wieder — solange sie die Grenzen genauso gut abdeckt wie die
beste Alternative. Ohne Timecode oder gemessene Zeitachse wird über die
Grenzen nichts behauptet; steht die Achse später da, sieht der Spieler
noch einmal nach. **zu In-Punkt** und **zu Out-Punkt** holen sich ihre
Datei selbst; gibt es gar keine, steht eine Zeile da, warum nichts
passiert ist.

Mit **zugeordneten Ton hören** läuft zum Bild der Ton, der zu dieser
Kamera gehört:

* die **aufbereitete Spur** von auphonic.com (`final_<Name>_<TC>.wav`),
  auf −16 LUFS und mit BWF-Timecode
* sonst die **Rohaufnahme** des zugeordneten Sprechers
* ist kein Sprecher zugeordnet — der Weitwinkel —, der **Full-Mix**,
  sofern er vorliegt

Rohaufnahmen liegen 16 bis 36 dB unter dem aufbereiteten Ton, und lauter
machen kann die Oberfläche sie nicht. Der Tooltip nennt, was läuft und in
welcher Fassung.

**Auf dem Reiter 3. Resolve-Schnitt** zeigt der Spieler im
Vorschau-Kasten immer etwas: gibt es einen Schnitt, spielt er ihn und
schaltet an jeder Kante die Kamera um, sonst die Datei ohne zugeordneten
Sprecher. Gerendert wird nichts.

Der Ton kommt durchgehend aus einer Datei, am liebsten aus dem
**Full-Mix**, der auf Sendepegel liegt und auch in die Schnitt-Timeline
geht. Gibt es ihn noch nicht, bleibt die Kameradatei, die den Mix als
erste Tonspur trägt — dieselbe Wahl wie für Perspektive 1 des
Multicam-Clips, und deutlich leiser.

`start_s` ist die Uhrzeit, zu der die Programmzeit null ist: der früheste
Tonanfang, der wirklich bekannt ist, eigener Timecode oder gemessene
Lage; fehlt der, der früheste Kamera-Timecode; fehlt auch der, steht dort
nichts. In point und Out point verschieben den Nullpunkt mit. Die Stelle
in jeder Kameradatei ist Programmzeit minus Versatz, derselbe Versatz,
mit dem auch die Schnitt-Timeline gebaut wird.

Jede Stelle wird nachgesetzt, bis sie sitzt; wie oft und wie lange, steht
in [Im Inneren des Scripts](internals.de.md).

### Sprecher ohne Auphonic

Auf dem Reiter **2. Zuordnung & Zeitfenster**, im Kasten **Aufbereitung
bei auphonic.com (optional)**, trägt die Preset-Liste den Eintrag **ohne
Auphonic arbeiten** (auf der Kommandozeile `--without-auphonic`). Der
Lauf bleibt dann lokal, und wer wann redet, wird aus den Spuren gemessen.
Im Protokoll steht dieser Abschnitt unter der Überschrift `SPRECHER --
HIER GEMESSEN`.

So werden die Spuren gelesen:

* Jede Spur wird in Blöcke von 100 Millisekunden zerlegt.
* Jeder Block wird gegen den eigenen Grundpegel der Spur gemessen, das
  leiseste Fünftel ihrer Blöcke; 10 dB darüber gilt als Sprache.
* Pausen unter 0,35 Sekunden sind kein Sprecherwechsel.
* Passagen unter 0,4 Sekunden zählen nicht.

Davor wird das **Übersprechen aus der Messung herausgerechnet**, nicht
aus dem Ton. An den Stellen, an denen genau eine Person spricht — diese
höchstens 10 dB unter ihrem eigenen Sprachpegel, die anderen mindestens
6 dB unter ihrem —, misst das Script, wie laut diese Stimme in den
anderen Mikrofonen ankommt, und rechnet den eigenen Anteil aus jeder Spur
zurück.

Die Kopplung wird gemessen, nicht angenommen, also geht es auch bei
Mikrofonen, die enger stehen, als die 3:1-Regel will. Für ein Paar ohne
mindestens drei solche Stellen wird nichts abgezogen. Lässt sie sich
nicht auflösen — Mikrofone nebeneinander, Spuren zu ähnlich —, bleiben
die Pegel, wie gemessen, und das Protokoll sagt warum und nennt das
schlechteste Paar.

Bis 5 dB Trennung hinunter arbeitet die Erkennung exakt, deutlich unter
den 9,5 dB, die die 3:1-Regel verlangt; die Messreihe dahinter steht in
[Im Inneren des Scripts](internals.de.md).

Das Protokoll sagt, wie stark das Übersprechen war, und darunter je
Sprecher Redezeit und Zahl der Abschnitte. War nichts zu hören, gibt es
keinen Kameraschnitt.

Der Knopf **Sprecher jetzt messen** tut in der Oberfläche dasselbe, schon
vor dem ersten Lauf: gröber als auphonic.com, aber genug, um den Schnitt
einzustellen. Sobald die Statistik da ist, hat sie Vorrang, und die
Überschrift über der Tabelle sagt, welche Quelle gerade gilt.

### Eine Kamera für alle

Sitzen mehrere Sprecher auf einer Kamera, wird am Sprecherwechsel
geschnitten: jede Einstellung kommt aus demselben Clip und trägt den
Namen dessen, der spricht. Am Bild ändert sich nichts. Resolve bekommt
eine Spur, die an den richtigen Stellen schon getrennt ist, und dort
lässt sich jedes Stück gruppieren, einfärben und heranzoomen, so dass aus
dem Weitwinkel der Sprecher wird.

Die Schnittliste sagt es mit: `_cameracut.csv` hat eine Spalte Sprecher,
und wo eine Kamera alle zeigt, trägt die EDL den Sprechernamen.

### Projektdatei

`videopodcast-magic_<Produktion>.json` im Ausgabeordner enthält alles,
was man von Hand eingestellt hat und nicht wieder erraten kann: die
Dateiliste, Name und Ablageort der Produktion, das Zeitfenster, alle
Werte des Kameraschnitts, wer zu welcher Kamera gehört, das
Auphonic-Preset, die Stereo-Häkchen und die gemessene Lage jeder Datei.
Der API Key steht **nicht** darin.

Beim Öffnen wird das Format der Datei geprüft; eine Datei in einem
anderen Format wird abgewiesen. Ältere Projektdateien lassen sich nicht
mehr öffnen.

Sie entsteht schon, sobald die Zeitachse gemessen ist — dann noch neben
dem Material, weil es den Ausgabeordner noch nicht gibt. Wird er später
gewählt oder die Produktion umbenannt, **wandert sie mit**. Es gibt immer
genau eine.

**Projekt öffnen ...** oben links holt sie zurück; greift man daneben,
wird im selben Ordner nach `videopodcast-magic*.json` gesucht. Daneben
liegt die Übergabedatei `<Produktion>_resolve.json` — daraus rechnet die
Vorschau, und daraus baut der Resolve-Teil.

### Wie der Weitwinkel gesetzt wird

Ein Weitwinkel kommt nicht nach der Uhr. Er geht dorthin, wo ein Schnitt
ohnehin unauffällig ist: in eine lange Sprechpause, möglichst kurz bevor
jemand anderes einsetzt und nicht zu weit von der Stelle, an der der
Weitwinkel gewünscht war. Gewürfelt wird nichts — dasselbe Material gibt
denselben Schnitt.

`--wide-latest` ist die Reißleine: findet sich keine Pause, wird trotzdem
geschnitten. Der Schnitt fällt dann mitten ins Reden, deshalb steht der
Weitwinkel `--wide-flow` lang statt `--wide-length`; ist der Platz bis
zum nächsten Schnitt knapp, wird er vorgezogen statt gekürzt.

## Kennzahlen und Farbvergleich

Am Ende jedes Laufs entsteht `<Produktion>_metrics.csv`; das Protokoll
wird beim nächsten Lauf überschrieben, diese Datei nicht. Über Monate
sieht man daran, was in einem einzelnen Lauf nicht auffällt: dass ein
Recorder langsamer wird, dass eine Kamera zunehmend anders aussieht als
die übrigen, dass das Übersprechen mit einem neuen Aufbau zugenommen hat.

Aufgebaut ist sie als `Area,Metric,Before,After,Unit` — durch Komma
getrennt, mit Punkt als Dezimalzeichen. `Area` und `Metric` bleiben in
jeder Sprache englisch, damit zwei Läufe vergleichbar bleiben. Vorher ist
die Spur, wie sie hereinkam, nachher, wie sie herausgeht, beides mit
demselben Verfahren gemessen.

Auf einem deutschen System kostet das Komma einen Schritt: Excel öffnet
eine CSV per Doppelklick mit dem Semikolon und legt die ganze Zeile in
eine Spalte. Der Weg hinein ist `Daten > Aus Text/CSV`, dort werden
Trennzeichen und die Sprache der Zahlen von Hand gesetzt. LibreOffice
fragt beides von selbst.

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
Messungen zusammen dauern bei langen Aufnahmen ein paar Minuten — die
Lautheitsmessung läuft je Spur zweimal durch.

## Weitere Optionen über die Kommandozeile

Im Fenster gibt es dafür keine Entsprechung.

* `--no-metrics` lässt die Kennzahlendatei und den Farbvergleich weg
* `VPM_PLAYER_DEBUG=1` vor dem Aufruf stellt Uhr, Stand und Sollwert
  aller drei Abspieler unter das Bild und jeden Versuch auf die Konsole

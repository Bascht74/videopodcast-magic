# DaVinci Resolve

*In English: [resolve.md](resolve.md). Zurück zum
[Inhalt](README.de.md).*

## Der Knopf und die beiden Timelines

Auf dem Reiter **Ausgabe** baut es der Knopf
**Resolve-Projekt anlegen**: erst die Dateien, dann das Projekt. Er legt
das Projekt an, setzt Bildrate, Auflösung und Start-Timecode, importiert
die fertigen Dateien und baut die Timelines. Der Ablauf wird als
`<Produktion>_resolve_log.txt` mitgeschrieben.

Der Knopf arbeitet auf der Übergabedatei und schickt die Werte für den
Kameraschnitt aus den Feldern mit. Die Schnittliste wird also mit dem
gerechnet, was jetzt dort steht. Wer wann spricht, wird dabei nicht neu
gerechnet: das bleibt so, wie der Lauf es gemessen hat, und der Hinweis
am Knopf sagt es. Wenn sich In-Punkt oder Out-Punkt inzwischen geändert
haben, bricht er ab. Der Ton in den Videos gehört dann zum alten
Fenster.

**Zweierlei gibt dem Knopf eine Übergabedatei in die Hand.** Das eine
ist ein Lauf in diesem Fenster: was er geschrieben hat, ist dieses
Material und nichts anderes, und der Knopf ist bedienbar, sobald der
Lauf durch ist. Das andere ist **Projekt öffnen ...** — dabei sucht das
Programm im Ausgabeordner und neben der Projektdatei und nimmt nur eine,
die **genau die Kameras dieses Projekts** nennt. Eine aus einer anderen
Produktion oder aus einer Runde über weniger Kameras übergeht es, als
läge sie nicht da: ein Schnitt daraus sieht genauso aus wie ein frischer
und ist es nicht. Ein Projekt lässt sich also öffnen und
**Resolve-Projekt anlegen** drücken, ohne noch einmal etwas laufen zu
lassen.

Sonst gibt nichts eine her. Dateien hineinziehen und einen
Ausgabeordner wählen, in dem schon eine liegt, genügt nicht: das Wählen
des Ordners nimmt dem Knopf, was er hatte, und niemand sieht dort nach.
Wo der Knopf nicht bedienbar ist, steht der Grund an ihm:

- **Dafür fehlt die Übergabedatei aus einem Lauf.** Kein Lauf in diesem
  Fenster, und kein geöffnetes Projekt, dessen Übergabe passt. Auf
  **Start** drücken.
- **Die Resolve-Schnittstelle liegt nicht da, wo sie sein müsste.**
  Resolve ist nicht dort installiert, wo das Programm nachsieht; der
  Kasten **Verbindung zu Resolve** auf dem Reiter **Resolve-Schnitt**
  sagt mehr dazu.
- **Der Lauf läuft noch.** Abwarten; wenn er durch ist, wird der Knopf
  von selbst wieder frei.

Der Abgleich über die Kameras wird beim Öffnen gefragt und nur dort.
Wird der **Typ** einer Kamera nach einem Lauf auf Vorspann, Abspann oder
**Video ignorieren** gestellt, kostet das also sofort nichts — der Knopf
arbeitet weiter auf der Übergabe des Laufs über alle. Es kostet sie beim
nächsten Öffnen des Projekts: die Datei nennt dann eine Kamera mehr, als
das Projekt hat, und wird übergangen. Dann noch einmal **Start**
drücken, für die Kameras, wie sie jetzt stehen.

Das Programm fragt beim ersten Blick auf den Reiter **Resolve-Schnitt**
von selbst nach, im Hintergrund, ob Resolve antwortet. Dort erscheint
nur ein Nein: der Reiter sagt dann **Resolve antwortet nicht -- siehe
Einstellungen**, und daneben steht der Weg zum Fenster
**Einstellungen ...**, in dem die Prüfung selbst sitzt. Antwortet
Resolve, sagt der Reiter gar nichts -- für Resolve gibt es nichts
einzustellen, und der Weg dorthin ist für den gedacht, der etwas
richten muss.

In dessen Kasten **Verbindung zu Resolve** stehen Produkt und Version,
wenn die Verbindung steht. Wenn nicht, stehen dort die beiden Pfade,
nach denen das Programm gesucht hat, und was im Weg sein kann:

- Resolve läuft nicht.
- Das externe Scripting steht auf „None“ statt „Local“, unter
  Preferences > System > General.
- Es ist die freie Version. Für sie wird berichtet, dass externes
  Scripting seit Version 19.1 der Studio-Version vorbehalten ist. Eine
  offizielle Aussage dazu gibt es nicht.

**Erneut prüfen** und der Rest dieses Fensters stehen in [Die
Oberfläche](interface.de.md).

![Der Reiter Resolve-Schnitt mit der Antwortzeile](images/resolve-cut.de.png)

*Reiter Resolve-Schnitt: die Antwort in Grün, darunter die Werte, die
der Knopf in die Schnittliste nimmt.*

| Fall | Schnitt-Timeline | Multicam-Timeline |
|---|---|---|
| mehrere Kameras, Sprecher getrennt | Bild aus dem Kameraschnitt, Ton am Stück | alle Kameras nebeneinander |
| mehrere Kameras, ein Sprecher mit Kamera | seine Kamera, vom Weitwinkel unterbrochen | alle Kameras nebeneinander |
| mehrere Kameras, niemand mit Namen und Kamera | keine | alle Kameras nebeneinander |
| eine Kamera, Sprecher getrennt | je Sprecherwechsel ein Schnitt, der Mix darunter | keine |
| eine Kamera, eine Stimme oder keine Trennung | die Kamera am Stück, der Mix darunter | keine |

Über die Schnitt-Timeline entscheidet die Sprechertrennung, nicht der
Weg. Zwei Leute mit Namen und Kamera ergeben einen Kameraschnitt, auch
auf dem einfachen Weg, und ebenso eine Person, sobald es eine zweite
Kamera gibt, auf der niemand ist: ihre Kamera steht, und der Weitwinkel
unterbricht sie. Sonst bleibt nur die Multicam-Timeline: alle Kameras an
ihren gemessenen Stellen, und Resolve macht daraus den Multicam-Clip.

Eine Messung, die erkennbar eine Rate von Resolve meint, gilt als diese
Rate: ffprobe misst bei manchen Dateien 29,994 oder 30,001, wo die
Kamera 29,97 oder 30 gemeint hat. Eine Rate, die keine von Resolve ist,
bleibt dagegen die eigene der Datei -- was mit 15 Bildern läuft, zählt
fünfzehn Bilder in der Sekunde, und Timecode und Länge zählen ebenso.
Das Protokoll sagt, welche Rate es genommen hat. Timecodes rechnet es
mit der ganzzahligen Rate und Dauern mit der echten, und Drop-Frame ist
berücksichtigt.

**… Cut**: der fertige Schnitt. Auf V1 (`Camera cut`) liegen die
Bildstücke **ohne ihren Ton**. Darunter läuft auf A1 (`Audio-Full-Mix`)
der Full-Mix in einem Stück durch, damit der Klang an den Schnitten nicht
springt. Der Mix kommt aus der abgelegten Einzeldatei, sonst aus dem
Weitwinkel, wo er die erste Tonspur ist.

Aus dem gemessenen Versatz ergibt sich, welches Stück aus welcher
Kameradatei in die Timeline kommt, nicht aus dem Timecode. Wenn eine
Kamera nicht lief, springt eine andere ein, zuerst der Weitwinkel. Das
Protokoll sagt, wie oft. Bei mehreren Kameras trägt die Timeline keine
Marker.

**… Multicam**: alle Kameras nebeneinander, eine je Bildspur, jede so
lang wie ihre eigene Datei und **ohne Schnitte**, an ihrer gemessenen
Stelle. Die
Spurnamen sind die Sprecher, eine Kamera ohne Sprecher heißt `Wide`, und
die Sprechernamen stehen als Marker. Auf Bildspur 1 kommt die Kamera,
deren erste Tonspur der Full-Mix ist, meist der Weitwinkel; beim
Umwandeln wird er zu Perspektive 1.

**Je Kamera genau eine Tonspur, mit ihrem Bild verknüpft.** Das Script
löscht den überzähligen Ton nach dem Einfügen und benennt die Tonspuren
wie die Bildspuren. Eine Kamera, die nicht gelandet ist, legt es einzeln
nach und meldet es, wenn auch das misslingt.

### Wo jede Kamera sitzt

**Auf beiden Timelines steht eine Kamera dort, wo ihr Ton gemessen
wurde, und nicht dort, wo ihre Uhr es sagt.** Die Messung hält jede
Datei gegen jede andere. Einen Timecode stellt ein Mensch, und ein
Mensch stellt ihn falsch; anzusehen ist es der Datei nicht -- eine
Kamera, die auf der falschen Stunde steht, bringt diese Stunde in die
Timeline mit. Und selbst wenn wirklich jemand alle Kameras auf dieselbe
Uhr gestellt hat, gehen die Uhren noch ein, zwei Bilder auseinander.

**Die Uhr ist der Rückfall, mehr nicht.** War im Ton einer Kamera nichts
zu finden, setzt ihr eigener Timecode sie; hat sie auch den nicht,
landet sie am Anfang der Achse. Beides sagt der Lauf beim Schreiben der
Übergabedatei ausdrücklich, mit Namen:

- *Im Ton war für `WideCam` nichts zu finden -- allein nach Timecode
  gesetzt.*
- *Kein gemessener Versatz für `WideCam` -- liegt am Anfang der Achse.*

Beim ersten lohnt ein Blick. Beim zweiten immer: eine Kamera am Anfang
der Achse ist eine, die niemand platziert hat, und sie sieht genauso aus
wie eine, die mit der Folge beginnt.

Gehen Messung und Uhr um mehr als ein Bild auseinander, druckt der Lauf
für diese Kamera beide Zahlen und sagt dazu, dass er die Messung nimmt.
Ohne diese Zeile geht eine Uhr, die auf einem anderen Tag steht, still
durch, und niemand erfährt davon.

**In der Übergabedatei steht die Antwort je Kamera**, unter `placed_by`
neben dem Versatz: `measured`, `clock` oder `nowhere`. Wer später fragt,
warum eine Kamera dort sitzt, wo sie sitzt, liest es dort nach, statt zu
raten.

### Kameras, die verschieden schnell laufen

Kameras verschiedener Bauart einigen sich selten auf eine Bildrate: die
eine schreibt 24 Bilder in der Sekunde, die nächste 25, der Weitwinkel
30. **Die Timeline bekommt die höchste Rate, die unter den Kameras
vorkommt -- und wenn Resolve für die keine Timeline hat, die nächste
darüber, die es hat.** Nach oben umgerechnet wiederholt Resolve Bilder,
nach unten wirft es welche weg; also gibt die schnellste Kamera den Takt
vor, und kein Bild geht verloren. Über 120 Bildern hat Resolve nichts
Höheres mehr, dort endet die Reihe, und nur dort geht es nach unten.
Intro und Outro zählen nicht mit, denn sie sind fertige Clips und keine
Kameras dieser Folge, und eine Datei auf **Video ignorieren** zählt
ebenso wenig. Wo die Raten auseinandergehen, sagt es der Lauf unter
`VERSCHIEDENE BILDRATEN` und nennt die Rate, auf die er sich festgelegt
hat.

Resolve hat Timelines nur für eine feste Reihe von Raten, und eine
Kamera kann mit einer laufen, die nicht darin steht -- mit 15 Bildern in
der Sekunde etwa. **Eine solche Kamera wird trotzdem verwendet und nicht
weggelassen.** Beim Einlesen nennt der Lauf sie und sagt dazu, dass
Resolve für diese Rate keine Timeline hat und umgerechnet statt
weggelassen wird; derselbe Hinweis steht in der Dateiliste, in der Zeile
**Video** der geöffneten Datei. An Resolve 21.0.4.5 nachgemessen: Eine
Kamera mit 15 Bildern sitzt neben Kameras mit 30 in deren 30er-Timeline
auf ein halbes eigenes Bild genau, ohne Lücke und mit stimmender Länge.
Stünde sie dort allein, bekäme die Timeline 16 -- die nächste Rate, die
Resolve über 15 hat.

Jede Kamera behält dabei ihre eigene Rate, und der Schnitt rechnet in
ihr. Resolve liest Anfang und Ende einer Einstellung als Bilder der
Datei, aus der sie stammt, nicht als Bilder der Timeline. Eine Kamera
mit 24 Bildern lief in einer 30er-Timeline deshalb davon: nach 26,8
Sekunden Programm zeigte sie, was sie erst bei 34,8 Sekunden aufgenommen
hatte, und der Fehler wuchs mit der Länge der Folge. Jetzt sitzt jede
Einstellung da, wo sie hingehört, gleich wie schnell die einzelne Kamera
lief.

Ein Bild bleibt übrig, und das mit Absicht. Eine Kamera mit 24 Bildern
füllt eine 30er-Timeline nur in Schritten von 1,25 Bildern; an etwa
jedem fünften Schnitt geht die Einstellung deshalb nicht bis aufs letzte
Bild auf, und **ein Bild der Timeline bleibt offen** -- eine
Dreißigstelsekunde Schwarz zwischen zwei Einstellungen. Der andere Weg
ist gemessen und verworfen: lässt man die Einstellung ein Bild
überlaufen, schließt sich die Lücke, aber jeder folgende Schnitt rückt
nach hinten, und über eine Stunde summiert sich das auf Sekunden. Eine
Lücke, die ein Bild bleibt, ist besser als ein Wandern ohne Grenze.
Laufen alle Kameras gleich schnell, tritt der Fall gar nicht erst auf.

**Die Multicam-Timeline und die geschriebenen Kameradateien waren davon
nie berührt.** Auf der Multicam-Timeline steht jede Kamera an ihrer
gemessenen Stelle, und die zählt allein in Bildern der Timeline --
nachgemessen und richtig. Die Kameradateien, die das Programm schreibt,
behalten die Bildrate ihrer Quelle und tragen den Augenblick, in dem sie
wirklich anfangen, in dieser Rate gezählt -- aus derselben Messung, die
auch jede Kamera platziert, also stimmen die Dateien untereinander
überein. Nur wo dem Material keine Tageszeit zu entnehmen ist, fällt
jede auf ihre eigene Uhr zurück, verschoben um den Beschnitt vorn.
Falsch war allein die Schnitt-Timeline, und auch die nur dort, wo die
Kameras verschieden schnell liefen.

### Eine Datei, die nirgends hinpasst

In die Übergabedatei kommen nur die Kameras, die der Lauf auf der
gemeinsamen Zeitachse unterbringen konnte. Hat der Ton eines Videos mit
dem übrigen Material nichts gemeinsam, und ordnet auch kein Timecode es
ein, dann lässt der Lauf es weg und sagt beim Schreiben, was er
weggelassen hat und warum: Nichts platziert es, also ist es keine Kamera
dieser Folge.

Das Weglassen hat seinen Grund. Für eine solche Datei ist nichts
aufbereitet worden, und sie trüge die Marke des Weitwinkels: Als Weitwinkel
gilt, wem kein Sprecher zugeordnet ist, und einer Datei, die nirgends
hinpasst, ist niemand zugeordnet. Übergeben stünde ein kurzer Jingle als
Weitwinkel einer ganzen Folge.

Eine Datei, die der Lauf bloß nicht vermessen konnte, ist ein anderer
Fall. Sie wird übergeben, und die Warnung nennt sie: wo sie liegt, sagt
dann ihr eigener Timecode, und hat sie keinen, landet sie am Anfang der
Achse. Beide Zeilen stehen oben unter *Wo jede Kamera sitzt*, und beide
sind einen Blick wert.

### Eine Kamera

Bei einer Kamera entstehen weder Multicam-Timeline noch Multicam-Clip.
Resolve bekommt allein die Timeline **… Cut**, und die Passagen der
Sprecher stehen als Marker darauf, je Person eine Farbe.

Eine einzelne Videodatei mit eigenem Ton ist dieser Fall. Die Trennung
hält die Sprecher auf der einen Spur auseinander, und der Schnitt fällt
an jedem Sprecherwechsel. Das Bild bleibt über die Schnitte hinweg
dasselbe. Eine 360-Grad-Kamera bekommt ihren Bildausschnitt von Hand,
Schnitt für Schnitt, und die Marker sagen, wer dran ist.

### Wenn es das Projekt schon gibt

Das Programm fragt:

- **auf den neuen Stand bringen**: das Script löscht die beiden
  Timelines, die es baut (`… Cut` und `… Multicam`), baut sie neu und
  bringt die Projekteinstellungen auf den neuen Stand. **Der Medienpool,
  eigene Timelines und alles aus früheren Läufen bleiben, wie sie sind.**
- **so lassen und die neuen Timelines danebenlegen**: die vorhandenen
  bleiben.
- **ein neues Projekt daneben anlegen**: Name mit Zusatz.
- **abbrechen.**

In der Oberfläche fragt ein Fenster, im Terminal kommt eine Nummer (auf der
Kommandozeile vorweg `--resolve-project update|keep|new|abort`).

Das Script sieht nach dem Löschen nach, denn Resolve meldet auch dann
Erfolg, wenn nichts geschah. Wenn eine Timeline stehen bleibt, sagt das
Protokoll es, und die neue bekommt einen Zusatz im Namen.

Das Script lässt die Multicam-Timeline stehen, wenn sie schon passt:
dieselben Kameras in derselben Reihenfolge. Für eine neue löscht man die
alte in Resolve. Eine Sicherungskopie legt es nicht an, denn ein Lauf mehr
baut sie wieder auf.

### Den Multicam-Ton wählen

Beim Umwandeln fragt Resolve unter *Multicam Audio Options*, woher der Ton
kommen soll (Handbuch, Kapitel „Multicam Audio Options“):

| Einstellung | wirkt |
|---|---|
| **Source Audio Channels** (Vorgabe) | Zugriff auf die einzelnen Spuren und Kanäle jeder Perspektive |
| **Reference Audio / Angle 1** | die *erste reine Tonperspektive* wird zur Tonspur für alle Winkel; fehlt eine, ist es der erste Winkel |
| **Adaptive Tracks** | alle Spuren und Kanäle einer Perspektive kommen in **eine** Adaptive-Spur |
| **All Angles** | jede Tonspur jeder Perspektive kommt mit — vier plus fünf ergibt neun |

*Source Audio Channels* ist die richtige Wahl: je Kamera ist nur noch eine
Tonspur übrig. Jede Perspektive bringt genau den Sprecher mit, der vor ihr
sitzt. Der Schlusshinweis im Protokoll sagt es auch.

### Welche Farbe jeder Schnitt bekommt

Jeder Schnitt bekommt die Farbe seiner Perspektive, auf beiden Timelines.
Das Script sortiert die Farben nach Unterscheidbarkeit, der Weitwinkel
bekommt `Tan`. Wenn es mehr Perspektiven als Farben gibt, wiederholt sich
die Reihe, und das Protokoll sagt es.

Dazu bekommt jede Kamera eine **Farbgruppe**, beschrieben weiter unten
unter *Eine ganze Kamera auf einmal korrigieren*.

### Was der Renderauftrag setzt

Stehen die Timelines, legt das Script das Renderprofil an und stellt den
Auftrag in die Warteschlange. In Resolve bleibt nur noch **Render All**.

Material und Projekt entscheiden, ob HDR oder SDR herauskommt, nicht der
Geschmack. Das Script liest zuerst den `colr`-Block der Kameradateien.
Drei Sachen gelten als HDR:

- **PQ oder HLG** (Übertragungsfunktion 16 oder 18), die beiden
  HDR-Anzeigekurven,
- **Log** (Apple Log steht als 21 in der Datei) — eine Aufnahmekurve,
  keine Anzeigekurve. **Log ist HDR.**
- **BT.2020** als Farbraum oder als Matrix.

Wenn eine Kamera nichts Brauchbares in den `colr`-Block schreibt, liest
das Script zusätzlich ihre QuickTime-Schlüssel; dort steht bei den
meisten Kameras die Kurve. Gesucht wird nach Wortmarken (`apple log`,
`s-log`, `v-log`, `logc`, …), nicht nach „log“. Sagen die
Projekteinstellungen etwas anderes, sticht das Projekt.

| Einstellung | SDR | HDR |
|---|---|---|
| Codec | H.264, acht Bit | H.265, zehn Bit (Profil Main10) |
| 2160p | 45.000 kbit/s | 56.000 kbit/s |
| 1440p | 16.000 | 20.000 |
| 1080p | 8.000 | 10.000 |
| 720p | 5.000 | 6.500 |

Bei hohen Bildraten von 48, 50 und 60 gelten die höheren Werte: 68.000
bzw. 85.000 kbit/s bei 2160p, entsprechend darunter. Es sind die
Empfehlungen von YouTube für den Upload, jeweils der obere Wert des
Bereichs. Diese Werte sind fest, und kein Schalter des Programms setzt
sie. Bildhöhe, Bildrate und SDR oder HDR wählen den Wert aus. Eine
andere Rate stellt man in Resolve am Renderauftrag selbst ein.

Eine Warnung steht im Protokoll, falls dieses Resolve kein H.265
anbietet. Eine zweite steht dort, falls es das Profil Main10 nicht
annimmt, und das Script setzt den Auftrag dann ohne das Profil.

Das Script muss HDR außerdem kennzeichnen, sonst trägt die fertige Datei
keins, so sauber sie auch gradiert ist. Der Abschnitt *HDR: was in der
Datei stehen muss* nennt, was der Renderauftrag dafür setzt.

Fest bleiben: eine Datei statt eine je Clip, Ziel ist der Ausgabeordner,
Dateiname der Produktionsname, `.mp4`. Der Ton ist AAC bei 48 kHz, 16 Bit,
zwei Kanäle. Die Tonbitrate kennt die Scripting-Schnittstelle von Resolve
nicht als Schlüssel, das Programm kann sie also nicht setzen. Man stellt
sie in Resolve am Renderauftrag selbst ein. Das Protokoll schreibt hin,
dass 384 kbit/s die Empfehlung für Stereo wären. Bei HDR nennt das
Protokoll auch die Prüfung (*HDR: was in der Datei stehen muss*).

Eine Datei statt eine je Clip wird angefordert, und Resolve darf das
ablehnen. Tut es das, steht es im Protokoll unter **Renderauftrag**:
*Eine Datei je Ausgabe wurde abgelehnt; Resolve schreibt eine Datei je
Clip.* Ließ sich die Frage gar nicht erst stellen, steht das dort
stattdessen, mitsamt Grund. So oder so kommt der Auftrag wie sonst in die
Warteschlange — aber **Render All** schreibt dann je Einstellung eine
Datei in den Ausgabeordner, und wer eine Folge sucht, findet einen Ordner
voller Einstellungen. Man stellt die Ausgabe in Resolve am Renderauftrag
wieder auf eine einzige Datei, an derselben Stelle wie Tonbitrate und
eine andere Bildrate, bevor man **Render All** drückt. Steht keine solche
Zeile im Protokoll, wurde nichts abgelehnt.

### Vorspann und Abspann setzen

Jede Videodatei trägt einen **Typ**: *Inhalt*, *Weitwinkel*, *Vorspann*,
*Abspann* oder *Video ignorieren*. Er wird an der Datei gesetzt, in der
Dateiliste auf dem Reiter **Dateien & Produktion**. Andere Stellen im
Programm zeigen denselben Wert.

Vorspann und Abspann sind freiwillig. Eine Datei, die auf Vorspann oder
Abspann steht, richtet das Programm nicht aus, bereitet sie nicht auf
und kopiert sie nicht um. Sie ist ein fertiger Clip und kommt nur in die
Timeline (auf der Kommandozeile `--intro DATEI` und `--outro DATEI`).
Beide landen auf der **zweiten** Bild- und Tonspur, über dem Inhalt
(`Intro / Outro` und `Audio Intro / Outro`).

Eine Folge hat einen Vorspann und einen Abspann. Solange eine Datei eine der
beiden Marken trägt, ist der Eintrag an jeder anderen Datei grau und nennt die
Datei, die ihn hält; nimmt man die Marke dort wieder ab, ist er wieder frei.
Ein Lauf, der trotzdem zwei desselben Typs sieht -- aus einer älteren
Projektdatei etwa --, hält an und nennt beide.

**Beide Clips behalten ihre volle Länge, der Inhalt ebenfalls.** Es
verschiebt sich nur, wo sie liegen, und das richtet sich nach dem **Ton**,
nicht nach der Dateilänge:

- **Vorspann**: das *Ende seines hörbaren Tons* trifft auf das erste Wort.
  Gemeint ist der Jingle, nicht die Datei. Die Schwelle liegt 40 dB unter der
  lautesten Stelle der Datei selbst. Sie liegt fest, und kein Schalter setzt
  sie. Ein Jingle, der leise ausklingt, erreicht die Schwelle vor dem Ende
  seines Tons. Der Rest des Ausklangs liegt dann über den ersten Worten.
- **Abspann**: der *Anfang seines Tons* trifft auf das Ende des letzten Worts.
- Die Sprecherabschnitte der Übergabedatei sagen, wo die Worte liegen.
- Bei einem Clip ohne Ton gilt für den Vorspann sein Ende und für den
  Abspann sein Anfang.

Die weiche Blende zieht man selbst: ein Zug an der oberen Ecke genügt.
Die Scripting-Schnittstelle von Resolve kennt keine Übergänge.

### Die Farbe der Quelle erhalten

Das Script hält die Farbe der Quelle unverändert. Es liest den
`colr`-Block selbst aus der Quelle, gibt die Zahlen ausdrücklich weiter,
erzwingt das Schreiben und prüft nach: Protokollzeile **Farbe**.

iPhone-Aufnahmen aus der Blackmagic Camera App tragen im `colr`-Block
„unbestimmt“ als Kurve. Resolve geht nach den QuickTime-Schlüsseln des
Containers (`com.apple.quicktime.model`, `com.apple.quicktime.software`,
`com.blackmagic-design.camera.*`). Das Script nimmt sie mit und zählt
nach, ob alle Schlüssel ankamen (Protokollzeile **Kameradaten**).

### Wie Apple Log das Umschreiben übersteht

In der Bildbeschreibung liegt ein kleines Atom `logs`, in dem die
Aufnahmekurve als Kennung steht, etwa
`com.apple.apple-wide-gamut.apple-log`. **Das** ist, woran Resolve Apple
Log erkennt — im `colr`-Block steht davon nichts. ffmpeg kann das Atom
nicht erhalten, deshalb trägt das Script es nach dem Schreiben selbst
nach, Byte für Byte aus der Quelle. Danach liest es nach, ob die Datei
noch heil ist.

Im Protokoll steht danach unter **Kameraatome**, ob das Atom nachgetragen
wurde und welche Kurve es nennt. In der Dateiliste steht die Kurve in der
Zeile **Farbe**. Sie trägt einen Klarnamen, wenn einer bekannt ist (Apple
Log, Apple Log 2), sonst die Kennung, wie sie dasteht.

### Eine ganze Kamera auf einmal korrigieren

Das Script legt je Kamera eine **Farbgruppe** an und weist ihr alle Clips
dieser Kamera zu. Eine Korrektur deckt damit eine ganze Kamera ab statt
eines einzelnen Schnitts. Der Node-Editor auf der Farbseite kennt dafür
vier Betriebsarten:

| Betriebsart | wirkt auf |
|---|---|
| **Group Pre-Clip** | „affect every clip in the group simultaneously“ — die ganze Kamera |
| **Clip** | „only affect the specific clip that's selected“ — dieser eine Schnitt |
| **Group Post-Clip** | wieder die ganze Gruppe, aber nach dem Clip gerechnet |
| **Timeline** | alle Clips der Timeline |

Resolve rechnet in dieser Reihenfolge. Also: die Grundkorrektur einer Kamera
in **Group Pre-Clip**, und wenn ein einzelner Schnitt aus der Reihe fällt,
ihn in **Clip** nachziehen. Weitere Clips kommen per Rechtsklick > Group >
Name > Assign to Group in die Gruppe.

### Einen einzelnen Schnitt für sich korrigieren

Das Script setzt **lokale Versionen**, bei jedem Lauf ausdrücklich.
Remote-Grades („Use local version for new clips“ aus) binden alle Clips
derselben Quelldatei an eine Korrektur. Ein einzelner Schnitt ließe sich
dann nicht mehr für sich korrigieren. Ein Schalter zum Wiedereinschalten
fehlt.

Die Einstellung wirkt nur auf Clips, die **danach** in eine Timeline
kommen: `--resolve-project update` baut beide Timelines neu und erledigt
das. Bei `keep` hängen die vorhandenen Clips an ihrem Remote-Grade. Das
Protokoll nennt den Weg: Farbseite, Rechtsklick auf ein Miniaturbild >
**Copy Remote Grades to Local** (nimmt die Korrektur mit) oder **Use
Local Grades**. Das Script sucht den internen Namen der Einstellung aus
der Liste aller Projekteinstellungen heraus und liest ihn nach.

### HDR: was in der Datei stehen muss

Ein HDR-Bild reicht nicht. Es muss auch draufstehen. Drei Zahlen nach
ITU-T H.273 entscheiden, ob ein Abspieler oder YouTube die Datei als HDR
behandelt. Fehlen sie, wird alles als SDR gezeigt, und der Aufwand mit
Apple Log ist verloren.

| Merkmal | HDR10 (PQ) | HLG | Pflicht |
|---|---|---|---|
| Primärfarben | **9** (BT.2020) | **9** | ja |
| Kurve | **16** (SMPTE ST 2084) | **18** (HLG) | ja |
| Matrix | **9** (BT.2020, nicht konstant) | **9** | ja |
| Bittiefe | 10 (oder 12) | 10 | ja |
| Codec | HEVC **Main 10** | dito | bei HEVC |
| `colr`-Atom im Container | vorhanden | vorhanden | ja |
| Mastering-Display (ST 2086) | Werte des Referenzmonitors | entfällt | nein |
| MaxCLL / MaxFALL | z. B. 1000 / 400 | entfällt | nein |

Zwei Fallen stecken in dieser Tabelle. **Die 14 ist keine HDR-Kurve**: Sie
heißt „BT.2020 10 bit“ und ist SDR im großen Farbraum. Und **Tagging ändert
keine Pixel**: ein PQ-Tag auf einem Rec.709-Grade macht daraus falsch
gekennzeichnetes SDR. Die statischen Metadaten sind nur empfohlen; wenn sie
fehlen, setzt YouTube Vorgabewerte an (ein Sony BVM-X300), bei HLG entfallen
sie ganz.

**Was das Script tut.** Beim Anlegen des Renderauftrags liest es den
Ausgabefarbraum aus den Projekteinstellungen. Wenn er PQ oder HLG nennt,
setzt es `ColorSpaceTag`, `GammaTag` und `EncodingProfile` = `Main10`: PQ
bekommt Rec.2020 / ST.2084, HLG bekommt Rec.2020 / HLG.

Nirgends steht, welche Schreibweise diese Resolve-Version annimmt, also
probiert das Script mehrere und schreibt die angenommene ins Protokoll.
Wenn das Projekt keine HDR-Kurve nennt, bleibt es bei „Same as Project“.
Das Protokoll nennt dann die Stelle: Project Settings > Color Management >
Output Color Space.

**Nachsehen an der fertigen Datei:**

```
videopodcast_magic.py --hdr-check Produktion.mp4
```

Das prüft alle Punkte der Tabelle und sagt zu jedem, was zu tun wäre. Es
liest die Datei und lässt sie, wie sie ist. Rückgabewert 0 heißt: die Datei
geht als HDR durch.

„Embed HDR10 Metadata“ und die HDR10+-Analyse kann das Script nicht
ferngesteuert einschalten, denn dafür kennt die Scripting-Schnittstelle
von Resolve keinen Schlüssel. Von Hand:

1. Color Management > HDR10+
2. Farbseite > Analyze All Shots
3. Deliver > Embed HDR10 Metadata

### Position und Zoom für eine ganze Kamera setzen

Position und Zoom gehen über dieselbe Gruppe wie die Farbe, aber nur an einer
Stelle. Die Palette **Sizing** (Farbseite, unten Mitte, zwischen „Key“ und
„Stereo“) kennt fünf Betriebsarten:

| Betriebsart | wirkt |
|---|---|
| Edit Sizing | wie der Inspektor der Schnittseite, je Clip |
| Input Sizing | vor dem Node-Baum, je Clip |
| **Node Sizing** | **im Node-Baum, am ausgewählten Node** |
| Output Sizing | für die ganze Timeline |
| Reference Sizing | nur für den Standbild-Vergleich |

Eine Gruppe teilt den Node-Baum, nicht die Clipeinstellungen; sie nimmt Node
Sizing mit, Edit und Input Sizing nicht. Also, für eine ganze Kamera:

1. Einen Clip dieser Kamera anklicken.
2. Im Node-Editor von „Clip“ auf **Group Pre-Clip** umschalten.
3. Die Sizing-Palette auf **Node Sizing** stellen.
4. Position und Zoom einstellen.

Das gilt rückwirkend für jeden Clip dieser Kamera in beiden Timelines. Eine
Änderung am Media-Pool-Clip greift dagegen nur für Clips, die *danach* in
eine Timeline kommen.

Aus dem Handbuch geschlossen (Kapitel 142 und 152), nicht abgeschrieben.
Das Handbuch sagt nicht, dass Node Sizing im Group-Pre-Clip-Baum auf die
ganze Gruppe wirkt.

### Wenn Resolve selbst schneiden soll

Dafür braucht es einen Multicam-Clip, und den kann das Script nicht
anlegen: die Scripting-Schnittstelle kennt Multicam nicht. Also von Hand:

1. Medienpool, Rechtsklick auf „… Multicam“
2. **Timeline in Multicam-Clip umwandeln** > **Quellaudiokanäle verwenden**

Zum Ton siehe die vier Möglichkeiten weiter oben. Der Spurname wird zum Namen
der Perspektive (Handbuch, Kapitel 49), und deshalb heißen die Bildspuren
nach den Sprechern. Die Umwandlung ist ein Einwegvorgang, und Resolve legt
keine Sicherungskopie an.

### Wenn etwas klemmt

- **Der Knopf bricht ab, bevor er anfängt.** In-Punkt oder Out-Punkt
  passen nicht mehr zu dem Lauf, aus dem die Dateien stammen. Noch einmal
  auf **Start**, mit den alten Werten in den beiden Feldern oder mit dem
  neuen Fenster.
- **Der Reiter sagt, dass Resolve nicht antwortet.** Die drei Ursachen
  stehen oben, im Kasten **Verbindung zu Resolve**. Eine davon beseitigen
  und **Erneut prüfen** drücken.
- **Eine Timeline aus einem früheren Lauf steht noch da, und die neue
  trägt einen Zusatz im Namen.** Resolve hat sie nicht gelöscht. Von Hand
  löschen und den Knopf noch einmal drücken.
- **In Resolve fehlt eine Kamera.** Der Lauf konnte sie nicht
  platzieren und hat sie aus der Übergabedatei herausgelassen; beim
  Schreiben nennt er sie. Der Datei einen Timecode geben, der zu
  den übrigen Aufnahmen passt, und noch einmal laufen lassen -- oder
  sie von Hand nach Resolve holen.
- **Eine Kamera steht neben ihrem Platz oder gleich ganz am Anfang.**
  Der Lauf hat es beim Schreiben der Übergabedatei gesagt: im Ton dieser
  Kamera war nichts zu finden, also ging er allein nach dem Timecode --
  oder er hatte beides nicht und hat sie an den Anfang der Achse gelegt.
  Der Name der Kamera steht in dieser Zeile, und `placed_by` in der
  Übergabedatei sagt dasselbe. Die Kamera in Resolve verschieben, oder
  der Datei einen Timecode geben, der zum übrigen Material passt, und
  noch einmal laufen lassen.
- **Die ganze Folge sitzt weit innen in der Timeline, oder die Timeline
  fängt bei 01:00:00:00 an.** Resolve hat den Anfang nicht übernommen,
  den der Lauf gesetzt hat. Das Protokoll nennt den gewünschten Anfang
  und den, den die Timeline meldet. In Resolve von Hand an der Timeline
  setzen, oder das Projekt noch einmal bauen lassen.
- **Der Knopf ist gleich nach dem Öffnen eines Projekts grau, und im
  Ordner liegt eine Übergabedatei.** Sie nennt andere Kameras, als das
  Projekt hat -- eine andere Produktion, oder eine Runde, bevor eine
  Kamera dazukam oder auf Vorspann gestellt wurde. Noch einmal **Start**
  drücken.
- **Im Ausgabeordner liegt je Einstellung eine Datei statt einer
  Folge.** Resolve hat eine Datei je Ausgabe abgelehnt, und das
  Protokoll sagt es unter **Renderauftrag**. Die Ausgabe in Resolve am
  Renderauftrag wieder auf eine einzige Datei stellen und noch einmal
  rendern.
- **Die fertige Datei läuft als SDR.**
  `videopodcast_magic.py --hdr-check DATEI` aufrufen und tun, was dort
  steht.
- **Eine Perspektive bringt den falschen Ton.** Die Umwandlung lief mit
  einer anderen Einstellung als **Quellaudiokanäle verwenden**. Noch
  einmal umwandeln.

Damit steht der Resolve-Teil: beide Timelines, je Kamera eine Farbgruppe
und der Renderauftrag in der Warteschlange. Das nächste Kapitel,
[Alle Schalter](command-line.de.md), führt jeden Schalter des Programms
an einer Stelle auf.

### Weitere Optionen über die Kommandozeile

Im Fenster gibt es diese Möglichkeiten nicht.

- `--resolve` baut das Projekt als Teil eines ganzen Laufs, gleich nach den
  Dateien.
- `--resolve-json DATEI` holt den Resolve-Teil allein nach; alles Nötige
  steht in `Produktion_resolve.json`. Das ruft auch der Knopf
  **Resolve-Projekt anlegen** auf.
- `--resolve-audio-tracks` sieht nur nach: für das offene Projekt schreibt
  es die Kanalzuordnung jedes Clips und die Spuren jeder Timeline hin.
- `--hdr-check DATEI` sieht nur nach: es misst die fertige Datei gegen die
  Tabelle unter *HDR: was in der Datei stehen muss*.

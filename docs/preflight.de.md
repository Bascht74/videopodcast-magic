# Vorflug

*In English: [preflight.md](preflight.md). Zurück zum
[Inhalt](README.de.md).*

## Was geprüft wird

Das Programm sieht das Material durch, bevor der erste lange Schritt
anfängt. Diesen Durchgang nennt es den Vorflug. Auf dem Reiter **Dateien
& Produktion** geschieht das von selbst, und nach jeder Änderung der
Dateiliste erneut. Ein Satz unter der Liste sagt, was gefunden wurde,
und jede Zeile trägt ein Prüfzeichen ([Die Oberfläche](interface.de.md)).
Der Zeiger auf dem Prüfzeichen oder die aufgeklappte Zeile zeigt, was
dahintersteht.

![Die Dateiliste mit den Prüfzeichen aus dem Vorflug](images/files.de.png)

*Ein Häkchen in jeder Zeile. Drei Aufnahmen sagen in Rot, dass sie zu
keiner der anderen Dateien passen -- Ton nicht erkannt, kein Timecode --,
und zwei Kameras sagen, dass ihr Ton nicht erkannt wurde und ihr Timecode
sie platziert. Der Streifen unter der Liste fasst das Ganze zusammen.*

Der Bericht gilt für beide Betriebsarten.

| Bereich | Was | Was daraus folgt |
|---|---|---|
| Bild | Nennrate gegen tatsächliche Rate, Schwankung der Bildabstände | siehe unten |
| Bild | Bildraten der Kameras untereinander | die Timeline bekommt die höchste davon oder die nächste Rate, die Resolve darüber hat |
| Bild | mehrteilige Kameras: Lücke zwischen den Blöcken | wo Bild fehlt |
| Ton | Abtastrate, Bittiefe, Kanäle, Länge | wird auf 48 kHz gebracht, das steht dann da |
| Ton | Spuren, die deutlich kürzer sind als die längste | Hinweis |
| Ton | Abtastwerte am Anschlag, je Kanal | Hinweis, nur Ganzzahlformate |
| Timecode | die Uhren der Dateien gegeneinander | Hinweis, wo eine Uhr nicht gestellt war |
| Raum | Übersprechen je Sprecherpaar, gegen die 3:1-Regel | Hinweis für die *nächste* Aufnahme |
| System | freier Plattenplatz gegen den geschätzten Bedarf | Hinweis, wenn es knapp wird, **Abbruch**, wenn es nicht reicht |
| Auphonic | Algorithmen des Presets, Lautheitsziel, Spurvorlage | **Abbruch** bei Widerspruch |
| Lautheit | welches Ziel gilt und woher es kommt | — |

Ein Abbruch hält den Lauf an, bevor etwas geschrieben oder hochgeladen
wird.

Laufen die Kameras nicht alle gleich schnell, nennt der Hinweis die
Rate, die die Timeline bekommt: die höchste davon -- oder, wenn Resolve
für diese Rate keine Timeline hat, die nächste darüber, die es hat.

Eine Kamera, für deren eigene Bildrate Resolve keine Timeline hat, wird
trotzdem benutzt. Vorher umzurechnen ist nichts: Umgerechnet wird sie in
die Timeline, weggelassen wird sie nicht. Die aufgeklappte Zeile sagt es
unter **Video**, und beim Einlesen sagt es der Lauf noch einmal bei der
Datei. Jede Kamera behält ihre eigene Rate, und der Schnitt rechnet in
ihr ([Resolve](resolve.de.md), „Kameras, die verschieden schnell
laufen“).

Ein Timecode von der anderen Seite von Mitternacht zählt als eine Nacht,
nicht als ein Tag Abstand. Bei Aufnahmen an wirklich verschiedenen Tagen
gilt der gemessene Versatz.

Das Programm misst nur, was sich geändert hat, und merkt es sich **je
Datei**, nicht je Auswahl. Eine neu hinzugekommene Kamera misst das
Programm allein. Bildraten, Auflösungen und Spuren aus der Reihe fallen
erst im Vergleich auf und rechnen sich aus den gemerkten Daten. Das
Übersprechen gilt für genau diese Menge an Spuren. Plattenplatz und
Lautheitsziel bestimmt das Programm jedes Mal neu.

### Was der Bericht zur variablen Bildrate sagt

Eine Kamera muss nicht alle 1/30 Sekunde ein Bild schreiben. Sie kann zu
jedem Bild einen Zeitstempel ablegen und die Abstände schwanken lassen;
Telefone tun das, wenn es dunkel wird. In der Datei steht trotzdem eine
feste Nennrate. Der Bericht sagt, welcher von zwei Fällen vorliegt:

- **Gleichmäßig daneben.** Die Rate bleibt gleich, sie ist nur nicht
  die, die in der Datei steht. Die Zeile nennt beide -- die gemessene
  gegen die angegebene -- und wie viele Bilder das auf derselben Länge
  ausmacht. Darunter steht, was ein Schnittprogramm daraus macht: es
  legt die Bilder mit der angegebenen Rate ab und lässt dafür alle paar
  Sekunden eines weg, so dass die Datei nicht länger wird und Bild und
  Kameraton zusammenbleiben. Das ist Uhrengang wie beim Ton, und der Ton
  wird beim Ausrichten ohnehin auf das Bild gezogen; der Bericht erwähnt
  es nur.
- **Ungleichmäßig.** Die Bildabstände ändern sich mitten in der
  Aufnahme, und über den Ton lässt sich das *nicht* einfangen. Wenn dann
  auch die Stützstellen beim Ausrichten streuen, hilft nur die Wandlung
  in eine feste Bildrate.

Das Programm liest nur den Container und decodiert nichts. Als
Schwankung zählt nur, was keine ganze Bilddauer ist oder was über die
Datei wandert.

### Wie der Bericht das Übersprechen gegen die 3:1-Regel misst

Bei mehreren Sprechern in einem Raum steht jede Stimme leise auch in den
anderen Mikrofonen. Der Bericht misst, wieviel leiser. Dazu nimmt er
fünf Fenster über die gemeinsame Zeit, je zwanzig Sekunden lang, und
misst darin dort, wo genau einer redet. Fünf und zwanzig stehen fest,
kein Schalter setzt sie. Bei kurzem Material werden die Fenster kürzer,
statt dass die Messung aufgegeben wird.

Der Maßstab ist die 3:1-Regel. Steht das fremde Mikrofon dreimal so weit
vom Sprecher weg wie sein eigenes, ist die Nachbarstimme rund 9,5 dB
leiser. Auch diese Marke steht fest, kein Schalter verschiebt sie: je
weiter ein Paar darunter liegt, desto mehr vom Nachbarn bleibt in der
Spur. Das sagt etwas über den Aufbau im Raum. Es setzt zugleich eine
Grenze für das, was danach kommt: je weniger die Mikrofone getrennt
sind, desto vorsichtiger kann De-Bleed auf auphonic.com arbeiten. Ändern
lässt es sich nur beim nächsten Mal, deshalb hält es den Lauf nicht an.

Bei einer einzigen Spur gibt es nichts zu messen. Dasselbe gilt für
Aufnahmen, die zu wenig überlappen, und für eine Aufnahme ohne Stelle, an
der genau einer spricht. Der Bericht sagt es, und der Lauf geht weiter.

### Wieviel Luft der Bericht verlangt

Bevor der erste lange Schritt anfängt, hält der Bericht den freien Platz
gegen das, was der Lauf schreiben wird. Diese Schätzung ist grob, und
sie sagt das auch von sich: Sie rechnet jede Kamera als kopiert und mit
neuen Tonspuren versehen, dazu die bearbeiteten Spuren und den Mix, und
sie rundet durchweg nach oben auf.

Ein Zeitfenster macht die Kameras kürzer, und die Schätzung geht mit:
Jede Kamera zählt mit ihrem eigenen Anteil am Fenster, eine kurze gibt
also viel weniger von sich her als eine lange
([Multitrack](multitrack.de.md), „Wieviel von jeder Kamera geschrieben
wird“). Das greift nur, wenn In-Punkt und Out-Punkt beide stehen und
beide gleich zählen -- beide als Uhrzeit oder beide als Abstand. Eine
Marke allein, oder ein Out-Punkt, der vom Ende zurückzählt, lässt die
Schätzung beim ganzen Material. Der Lauf schreibt dann weniger, als der
Bericht verlangt hat, nie mehr.

Eine grobe Schätzung, um ein Haar überboten, ist kein Platz. Deshalb
verlangt der Bericht **15 Prozent über seiner eigenen Schätzung**, bevor
er den Platz gutheißt. Dazwischen -- die Zahlen gehen auf, aber knapp --
gibt er einen Hinweis und lässt den Lauf weiterlaufen; darunter bricht
er ab wie zuvor. Dieser Abstand steht fest, kein Schalter verschiebt
ihn.

Dabei sieht der Bericht auf beide Platten. Was der Lauf abliefert,
landet im Ausgabeordner, die Zwischendateien des Laufs aber im
temporären Ordner des Systems, und der liegt noch einmal woanders.
Stehen beide auf derselben Platte, wird derselbe Platz zweimal
gebraucht, und der Bericht zählt ihn zweimal. Auf verschiedenen Platten
ändert sich nichts.

### Welches Lautheitsziel gilt

Der Wert gilt für beides: für die Normalisierung der Spuren und für den
Zielpegel der Lautheitsanzeige im Resolve-Projekt. Er kommt aus
**Lautheit** in der Gruppe **Produktion** auf der ersten Seite des
Fensters oder von `--lufs` auf der Kommandozeile. Das Fenster bietet
fünf Einträge:

- **-16 LUFS (Podcast-Verzeichnisse, stereo)**
- **-19 LUFS (Podcast-Verzeichnisse, mono)**
- **-14 LUFS (YouTube -- regelt nur herunter, nie herauf)**
- **-23 LUFS (EBU R128, Rundfunk)**
- **Aus Quelldateien übernehmen**

Ein neues Projekt beginnt bei −16 LUFS. Das Fenster merkt sich den
zuletzt gewählten Eintrag und beginnt das nächste neue Projekt damit,
und eine geladene Projektdatei sticht diese Erinnerung: ein mit −23 LUFS
gespeichertes Projekt öffnet auf −23 LUFS, auch wenn der Rechner sich
**Aus Quelldateien übernehmen** gemerkt hatte.

**Ohne Ziel wird nichts angepasst.** Kein `--lufs` auf der Kommandozeile
oder **Aus Quelldateien übernehmen** im Fenster, und der Ton geht genau
so hinaus, wie er hereinkam: kein Gewinn auf einer Spur und kein
Limiter. auphonic.com macht weiter, was in seinem Preset steht. Die
Summe wird trotzdem gemessen, und die Messung steht im Protokoll, unter
`Nicht angepasst:` -- aus den Quelldateien übernommen, kein Gewinn und
kein Limiter. Der Vorflug sagt in seiner Zeile Lautheit dasselbe: aus
den Quelldateien übernommen, kein `--lufs` angegeben, es wird nichts
angepasst. Im Resolve-Projekt braucht die Lautheitsanzeige trotzdem eine
Skala, sie wird auf −16 LUFS gesetzt, und die Zeile darüber im Protokoll
sagt, dass das nur der Bezug der Anzeige ist.

**Jeder Lauf wird gemessen und angepasst, und zwar gleich.** Ein Lauf
ohne Multitrack ([Der einfache Weg](simple-path.de.md)) wendet das Ziel
an wie jeder andere, und ein Lauf ganz ohne Bild auch, bei dem die
Blöcke einer Aufnahme zu einer Datei zusammengefügt werden. Im Protokoll
stehen `Ziel:` und `Ergebnis:`; ohne Ziel wird nichts angepasst.

Ein Weg ist die Ausnahme: Multitrack ganz ohne Bild, wo die Spuren
gegeneinander gelegt werden. Dort wird nichts ausgesteuert -- ein Gewinn
je Spur brächte die Stimmen um das Gleichgewicht, für das dieser Weg da
ist --, und der Lauf sagt es in einer Zeile
([Multitrack](multitrack.de.md)).

**Gemischt wird zweikanalig, gemessen auch.** Die Einzelspuren behalten
die Kanäle ihrer Quelle ([Kanäle](channels.de.md)). Jeder *Mix* dagegen,
der `Full-Mix` wie der Mix einer einzelnen Kamera, bekommt dasselbe
Signal auf beide Kanäle, und so misst das Programm ihn. Eine einzige
Aufnahme ist die Ausnahme: Es gibt nichts zu mischen, deshalb bleibt eine
Mono-Aufnahme einkanalig und eine Stereo-Aufnahme zweikanalig.
Einkanalig misst sich derselbe Mix gut drei Dezibel leiser; die Messreihe
dahinter steht in [What was measured](../development/measurements.md)
(englisch). Wer einkanalig misst und zweikanalig abgibt, liegt genau um
diesen Betrag daneben.

Beim Normalisieren steht auch der **Lautheitsumfang** im Protokoll, der
Abstand zwischen leisen und lauten Stellen. Bei Sprache sind 3 bis 7 LU
üblich; unter 2 LU sagt das Protokoll es ausdrücklich, und je tiefer der
Wert, desto flacher das Ergebnis. Dann wurde plattgedrückt, und zwar vom
Leveler, nicht vom Limiter, der nur Spitzen abfängt und höchstens 6 dB
wegnehmen darf. Diese drei Zahlen stehen fest, kein Schalter setzt sie,
und der Leveler wird auf auphonic.com eingestellt.

### Wie der Bericht die Abtastwerte am Anschlag zählt

Das Programm zählt je Kanal, wie viele Abtastwerte auf dem höchsten Wert
liegen, den das Format fassen kann. Drei hintereinander ergeben einen
Fall; einer oder zwei sind Rundung und werden nicht gemeldet. Diese Drei
steht fest, kein Schalter setzt sie. Der Hinweis nennt den Kanal, wie
viele solcher Reihen es gibt, die längste davon in Abtastwerten und in
Millisekunden und wo die erste liegt. Der Hinweis hält nichts auf: eine
übersteuerte Aufnahme ist manchmal die einzige, die es gibt.

Das Programm zählt nur bei Ganzzahlformaten. Ein Ganzzahlformat hat bei
Vollausschlag einen Anschlag, und was darüber lag, ist nie in die Datei
gekommen. Gleitkomma hat keinen Anschlag, und 0 dBFS ist dort eine Marke
auf der Skala, keine Wand. Bei 16 und 24 Bit kommt am Anschlag dasselbe
heraus; [What was measured](../development/measurements.md) (englisch)
zeigt dieselbe übersteuerte Quelle in allen drei Formaten.

Ohne die Zählung bleibt ein übersteuerter Kanal unsichtbar. Das Programm
misst den Master als Summe, und der Limiter zieht ihn unter −1 dBTP. Ein
Ansteckmikrofon, das den ganzen Abend am Anschlag lag, sieht dadurch
sauber aus.

### Wann eine sehr kurze Datei als Vorspann vorgeschlagen wird

Während das Material durchgesehen wird, misst das Fenster auch, wie die
Dateien zueinander liegen ([Die Oberfläche](interface.de.md)). Eine
Datei, die dabei zu nichts passt, wird in der Spalte **Typ** zum
Eintrag **Video ignorieren** vorgeschlagen. Das ist richtig für eine
Kamera, deren Mikrofon nichts vom Raum gehört hat, und falsch für einen
Jingle: Ein Jingle passt zu nichts, weil er keine Kamera ist, und er
soll benutzt werden, nicht weggelassen.

Auseinander hält die beiden die Länge. Von den Dateien, die zu nichts
passen und die auch kein Timecode einordnet, wird die kürzeste als
**Vorspann** vorgeschlagen -- aber nur, wenn sie höchstens ein Zehntel
so lang ist wie die mittlere Länge des übrigen Materials. Maßstab ist
der Dreh selbst und keine aufgeschriebene Länge: Ein Jingle liegt um
Größenordnungen unter dem, wozwischen er steht, während eine Datei, die
zum Dreh gehört und bloß zu nichts passt, ungefähr so lang ist wie alles
andere.

**Vorspann** heißt, dass die Datei an den Anfang gelegt und nie
vermessen wird ([DaVinci Resolve](resolve.de.md)), und davon gibt es
einen. Der Vorschlag trifft deshalb nur eine Datei, die kürzeste, und
gar keine, wenn in der Liste schon irgendwo ein Vorspann steht.

Es ist ein Vorschlag wie die anderen. Er füllt nur einen **Typ**, in dem
noch die eigene Antwort des Programms steht, nie einen, den jemand
gewählt hat, und eine Datei, die eine spätere Messung wieder einordnen
kann, bekommt ihren alten Eintrag zurück. Ein Timecode entscheidet die
Sache schon vorher, sofern noch eine andere Datei einen trägt: Dann hat
die Datei einen Platz, und es wird nichts vorgeschlagen.

### Wenn etwas klemmt

- **Eine sehr kurze Datei steht plötzlich auf Vorspann.** Sie passt zu
  nichts im Material und ist viel kürzer als alles um sie herum, also
  hält das Programm sie für einen Jingle. Einen **Typ** von Hand wählen
  entscheidet die Zeile endgültig.
- **Der Plattenplatz reicht nicht oder gerade eben.** Platz schaffen
  oder im Streifen unter der Dateiliste einen anderen Ausgabeordner
  setzen. Die Zwischendateien des Laufs liegen im temporären Ordner des
  Systems: Liegt der auf derselben Platte wie der Ausgabeordner, braucht
  der Lauf den Platz zweimal, und ein Ausgabeordner auf einer anderen
  Platte hilft dann so viel wie Aufräumen. Wird ohnehin nur ein Stück
  der Aufnahme gebraucht, hilft ein engerer In- und Out-Punkt mehr als
  beides: Die Kameras werden dann nur noch für dieses Fenster
  geschrieben.
- **Das Preset mastert auf eine andere Lautheit.** `--lufs` auf den Wert
  des Presets setzen oder das Lautheitsziel des Presets auf
  auphonic.com ändern. Beides zusammen geht nicht: die Spuren kommen auf
  dem einen Wert zurück, der Mix geht auf den anderen.
- **Das Multitrack-Preset enthält keine Spur.** Auf auphonic.com eine
  Spur im Preset anlegen. Die erste Spur des Presets bestimmt die
  Bearbeitung aller Spuren; ohne sie kommen sie so zurück, wie sie
  hochgeladen wurden.
- **Ein Kanal liegt am Anschlag.** Wenn dieselbe Stimme ein zweites Mal
  aufgenommen wurde, etwa von einer Kamera, diese Aufnahme nehmen. Hier
  lässt sich nichts reparieren, also bei der nächsten Aufnahme niedriger
  aussteuern.

Das Material ist jetzt geprüft, und jede Beanstandung ist entweder
erledigt oder wissentlich hingenommen. Der Bericht nennt die Kanäle jeder
Datei. [Kanäle](channels.de.md) entscheidet, ob eine Datei mit mehr als
einem Kanal eine Spur wird oder zwei.

### Weitere Optionen über die Kommandozeile

Im Fenster gibt es diese Optionen nicht.

`--anyway` läuft trotz eines Abbruchs, `--no-preflight` überspringt die
Prüfung ganz, `--preflight-again` misst alles neu statt nur das Geänderte.

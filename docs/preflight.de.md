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

Der Bericht gilt für beide Betriebsarten.

| Bereich | Was | Was daraus folgt |
|---|---|---|
| Bild | Nennrate gegen tatsächliche Rate, Schwankung der Bildabstände | siehe unten |
| Bild | Bildraten der Kameras untereinander | welche Rate die Timeline bekommt |
| Bild | mehrteilige Kameras: Lücke zwischen den Blöcken | wo Bild fehlt |
| Ton | Abtastrate, Bittiefe, Kanäle, Länge | 44,1 kHz wird umgerechnet, das steht dann da |
| Ton | Spuren, die deutlich kürzer sind als die längste | Hinweis |
| Ton | Abtastwerte am Anschlag, je Kanal | Hinweis, nur Ganzzahlformate |
| Timecode | die Uhren der Dateien gegeneinander | Hinweis, wo eine Uhr nicht gestellt war |
| Raum | Übersprechen je Sprecherpaar, gegen die 3:1-Regel | Hinweis für die *nächste* Aufnahme |
| System | freier Plattenplatz gegen den geschätzten Bedarf | **Abbruch**, wenn es nicht reicht |
| Auphonic | Algorithmen des Presets, Lautheitsziel, Spurvorlage | **Abbruch** bei Widerspruch |
| Lautheit | welches Ziel gilt und woher es kommt | — |

Ein Abbruch hält den Lauf an, bevor etwas geschrieben oder hochgeladen
wird.

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

- **Gleichmäßig daneben.** Die Datei sagt 30, in Wirklichkeit sind es
  konstant 29,98. Das ist Uhrengang wie beim Ton. Der Ton wird beim
  Ausrichten ohnehin auf das Bild gezogen, der Bericht erwähnt es nur.
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
fünf Fenster über die gemeinsame Zeit, jeweils dort, wo genau einer
redet.

Der Maßstab ist die 3:1-Regel. Steht das fremde Mikrofon dreimal so weit
vom Sprecher weg wie sein eigenes, ist die Nachbarstimme rund 9,5 dB
leiser. Das sagt etwas über den Aufbau im Raum. Es setzt zugleich eine
Grenze für das, was danach kommt: je weniger die Mikrofone getrennt
sind, desto vorsichtiger kann De-Bleed auf auphonic.com arbeiten. Ändern
lässt es sich nur beim nächsten Mal, deshalb hält es den Lauf nicht an.

Bei einer einzigen Spur gibt es nichts zu messen. Dasselbe gilt für
Aufnahmen, die zu wenig überlappen, und für eine Aufnahme ohne Stelle, an
der genau einer spricht. Der Bericht sagt es, und der Lauf geht weiter.

### Welches Lautheitsziel gilt

Der Wert gilt für beides: für die Normalisierung der Spuren und für den
Zielpegel der Lautheitsanzeige im Resolve-Projekt. Ohne Angabe sind es
−16 LUFS.

**Gemischt wird zweikanalig, gemessen auch.** Die Einzelspuren behalten
die Kanäle ihrer Quelle ([Kanäle](channels.de.md)). Jeder *Mix* dagegen,
der `Full-Mix` wie der Mix einer einzelnen Kamera, bekommt dasselbe
Signal auf beide Kanäle, und so misst das Programm ihn. Einkanalig misst
sich derselbe Mix gut drei Dezibel leiser; die Messreihe dahinter
steht in [What was measured](../development/measurements.md) (englisch).
Wer einkanalig misst und zweikanalig abgibt, liegt genau um diesen Betrag
daneben.

Beim Normalisieren steht auch der **Lautheitsumfang** im Protokoll, der
Abstand zwischen leisen und lauten Stellen. Bei Sprache sind 3 bis 7 LU
üblich; unter 2 LU sagt das Protokoll es ausdrücklich. Dann wurde
plattgedrückt, und zwar vom Leveler, nicht vom Limiter, der nur Spitzen
abfängt und höchstens 6 dB wegnehmen darf.

### Wie der Bericht die Abtastwerte am Anschlag zählt

Das Programm zählt je Kanal, wie viele Abtastwerte auf dem höchsten Wert
liegen, den das Format fassen kann. Der Hinweis nennt den Kanal, die
Zahl und den Spitzenpegel. Er erscheint ab acht Abtastwerten und nur
dann, wenn die Spitze bis auf 0,1 dB an den Vollausschlag reicht. Der
Hinweis hält nichts auf: eine übersteuerte Aufnahme ist manchmal die
einzige, die es gibt.

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

### Wenn etwas klemmt

- **Der Plattenplatz reicht nicht.** Platz schaffen oder im Streifen
  unter der Dateiliste einen anderen Ausgabeordner setzen. Die
  Zwischendateien des Laufs liegen im temporären Ordner des Systems,
  also woanders.
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

`--lufs` setzt das Ziel als Zahl (Vorgabe −16, näher an null ist lauter),
`--platform` nach Zweck:

| Angabe | Ziel | Wofür |
|---|---|---|
| `podcast` | −16 LUFS | Podcast-Verzeichnisse, stereo |
| `podcast-mono` | −19 LUFS | Podcast-Verzeichnisse, mono |
| `youtube` | −14 LUFS | YouTube regelt nur herunter, nie herauf |
| `broadcast` | −23 LUFS | EBU R128 |

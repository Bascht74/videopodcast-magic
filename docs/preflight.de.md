# Vorflug

*In English: [Preflight](preflight.md). Zurück zum [Inhalt](README.de.md).*

## Vorflug

Das Script sieht das Material durch, bevor der erste lange Schritt
anfängt. Auf dem Reiter **Dateien & Produktion** geschieht das von
selbst, und nach jeder Änderung der Dateiliste erneut. Ein Satz unter der
Liste sagt, was gefunden wurde, und jede Zeile trägt eine Marke. Wer mit
dem Zeiger auf der Marke stehen bleibt oder die Zeile aufklappt, sieht,
was dahintersteht.

Der Bericht gilt für beide Betriebsarten und steht an einer einzigen
Stelle, vor der Weiche. Das Übersprechen fällt bei einer einzigen Spur
weg.

| | Was | Was daraus folgt |
|---|---|---|
| Bild | Nennrate gegen tatsächliche Rate, Schwankung der Bildabstände | siehe unten |
| | Bildraten der Kameras untereinander | welche Rate die Timeline bekommt |
| | mehrteilige Kameras: Lücke zwischen den Blöcken | wo Bild fehlt |
| Ton | Abtastrate, Bittiefe, Kanäle, Länge | 44,1 kHz wird umgerechnet, das steht dann da |
| | Spuren, die deutlich kürzer sind als die längste | Hinweis |
| Raum | Übersprechen je Sprecherpaar, gegen die 3:1-Regel | Hinweis für die *nächste* Aufnahme |
| System | freier Plattenplatz gegen den geschätzten Bedarf | **Abbruch**, wenn es nicht reicht |
| Auphonic | Algorithmen des Presets, Lautheitsziel, Spurvorlage | **Abbruch** bei Widerspruch |
| Lautheit | welches Ziel gilt und woher es kommt | -- |

Ein Abbruch hält den Lauf an, bevor etwas geschrieben oder hochgeladen wird.

Gemessen wird nur, was sich geändert hat, und gemerkt wird **je Datei**,
nicht je Auswahl. Kommt eine Kamera dazu, wird nur diese gemessen.
Bildraten, Auflösungen und Spuren aus der Reihe fallen erst im Vergleich
auf und rechnen sich aus den gemerkten Daten. Das Übersprechen gilt für
genau diese Menge an Spuren. Plattenplatz und Lautheitsziel werden jedes
Mal neu bestimmt.

### Variable Bildrate

Eine Kamera muss nicht alle 1/30 Sekunde ein Bild schreiben. Sie kann zu
jedem Bild einen Zeitstempel ablegen und die Abstände schwanken lassen;
Telefone tun das, wenn es dunkel wird. In der Datei steht trotzdem eine
feste Nennrate. Der Bericht sagt, welcher von zwei Fällen vorliegt:

- **Gleichmäßig daneben.** Die Datei sagt 30, in Wirklichkeit sind es konstant
  29,98 -- Uhrengang wie beim Ton. Der Ton wird beim Ausrichten ohnehin auf
  das Bild gezogen, der Bericht erwähnt es nur.
- **Ungleichmäßig.** Die Bildabstände ändern sich mitten in der Aufnahme, und
  über den Ton lässt sich das *nicht* einfangen. Streuen dann auch die
  Stützstellen beim Ausrichten, hilft nur, die Datei in eine feste Bildrate zu
  wandeln.

Gelesen wird nur der Container -- decodiert wird nichts, es kostet also
keine Zeit. Als Schwankung zählt nur, was keine ganze Bilddauer ist oder
was über die Datei wandert.

### Übersprechen und die 3:1-Regel

Sitzen mehrere Sprecher in einem Raum, steht jede Stimme leise auch in den
anderen Mikrofonen. Der Bericht misst, wieviel leiser -- an fünf Fenstern über
die gemeinsame Zeit, jeweils dort, wo genau einer redet.

Der Maßstab ist die 3:1-Regel: steht das fremde Mikrofon dreimal so weit
vom Sprecher weg wie sein eigenes, ist die Nachbarstimme rund 9,5 dB
leiser. Das sagt etwas über den Aufbau im Raum, nicht über die
Nachbearbeitung. Ändern lässt es sich nur beim nächsten Mal, deshalb hält
es den Lauf nicht an.

### Lautheit

Der Wert gilt für beides: für die Normalisierung der Spuren und für den
Zielpegel der Lautheitsanzeige im Resolve-Projekt. Ohne Angabe sind es
−16 LUFS.

**Gemischt wird zweikanalig, gemessen auch.** Die Einzelspuren behalten
die Kanäle ihrer Quelle ([Kanäle](channels.de.md)). Jeder *Mix* dagegen,
der `Full-Mix` wie der Mix einer einzelnen Kamera, bekommt dasselbe
Signal auf beide Kanäle und wird so gemessen. Einkanalig misst sich
derselbe Mix gut drei Dezibel leiser. Wer einkanalig misst und
zweikanalig abgibt, liegt genau um diesen Betrag daneben.

Beim Normalisieren steht auch der **Lautheitsumfang** im Protokoll, der
Abstand zwischen leisen und lauten Stellen. Bei Sprache sind 3 bis 7 LU
üblich; unter 2 LU sagt das Protokoll es ausdrücklich. Dann wurde
plattgedrückt, und zwar vom Leveler, nicht vom Limiter, der nur Spitzen
abfängt und höchstens 6 dB wegnehmen darf.

### Weitere Optionen über die Kommandozeile

Im Fenster gibt es diese Optionen nicht.

`--anyway` läuft trotz eines Abbruchs, `--no-preflight` überspringt die
Prüfung ganz, `--preflight-again` misst alles neu statt nur das Geänderte.

`--lufs` setzt das Ziel als Zahl, `--platform` nach Zweck:

| Angabe | Ziel | Wofür |
|---|---|---|
| `podcast` | −16 LUFS | Podcast-Verzeichnisse, stereo |
| `podcast-mono` | −19 LUFS | Podcast-Verzeichnisse, mono |
| `youtube` | −14 LUFS | YouTube regelt nur herunter, nie herauf |
| `broadcast` | −23 LUFS | EBU R128 |

# Im Inneren des Scripts

*In English: [Inside the script](internals.md). Zurück zum [Inhalt](README.de.md).*

## Wie das Script aufgebaut ist

Der Kern ist eine einzige Datei — Absicht: kopieren, aufrufen, fertig, ohne
Installation. Darin gilt eine Regel: **Entscheidungen gehören nach draußen,
Fenster nach drinnen.** Alles, was rechnet oder entscheidet, steht als
Funktion auf oberster Ebene und lässt sich ohne Fenster prüfen; `gui()` baut
nur die Oberfläche. Bisher:

| Funktion | was sie entscheidet |
|---|---|
| `run_argv` | die ganze Kommandozeile, samt Prüfungen und Rückfragen |
| `slider_numbers` | die Schnitt-Regler als Zahlen, mit Vorgaben |
| `slider_argv` | dieselben Regler als Schalter |
| `build_handover` | die Übergabe, mit einem Satz zu jedem Nein |
| `choose_zero_point` | wo die Programmzeit anfängt: Ton zuerst, Bild ersatzweise |
| `find_project_file` | die Projektdatei zu dem, worauf gezeigt wurde |
| `format_complaint` | ob eine gespeicherte Datei überhaupt gelesen werden darf |
| `project_files` | was aus dem Projekt noch da ist und was fehlt |
| `metrics_sentence` | der Satz unter der Vorschau: wieviel Redezeit wo landet |
| `speech_heading` | Abschnitte von Auphonic oder selbst gemessen |
| `assignment_rows` | die Zeilen der oberen Tabelle, samt Kameraton |
| `preselected_camera` | auf welche Kamera eine Tonspur vorbelegt wird |
| `camera_output_name` | wie die neue Videodatei heißt, ohne doppelten Namen |
| `measure_time_axis` | wie die Dateien zueinander und zur Uhr liegen |
| `axis_still_valid` | ob eine gemessene Achse für diese Dateien noch gilt |
| `pending_prework` | was an Hüllkurven und Ton noch zu holen ist |
| `window_suggestion` | In point und Out point aus dem, was die Kameras hergeben |
| `recordings_text` | die Kopfzeile der Tongruppe |
| `hdr_findings` | ob eine fertige Datei als HDR durchgeht |
| `copy_mov_atoms` | das `logs`-Atom übertragen und nachlesen |

`choose_zero_point` sind vier Zeilen und war zweimal die Ursache eines falsch
liegenden Schnitts — jetzt steht die Regel an einer Stelle und hat Testfälle.
Umgekehrt bleiben die Bausteine der Oberfläche — `cell`, `table_build`,
`item`, `report`, `mark_red` — in `gui()`: sie werden von über hundert Stellen
gerufen und entscheiden nichts.

`run_argv` gibt keine Dialoge aus, sondern eine Liste `(kind, title, text,
button)` in der vorgesehenen Reihenfolge — `"error"` heißt zeigen und
abbrechen, `"question"` fragen und bei Nein abbrechen. So ist die Reihenfolge
der Rückfragen prüfbar: `argv_test.py` geht achtzehn Fälle durch.

## Wie weit hinunter das Sprecher-Gatter trägt

Gemessen an drei echten Mikrofonspuren, neu gemischt auf eine Trennung,
die wir vorgeben. Die Wahrheit ist damit genau bekannt: 720 Blöcke, in
denen jemand spricht, und die Zahl derer, die die Erkennung trifft.

| Trennung | Mit Gatter | Ohne |
|---|---|---|
| 14 dB | alle 720 richtig, nichts erfunden | 720 richtig, 36 erfunden |
| 10 dB | alle 720 richtig | 528 richtig, 192 verpasst |
| 8 dB | alle 720 richtig | 462 richtig, 258 verpasst |
| 6 dB | alle 720 richtig | 77 richtig, 643 verpasst |
| **5 dB** | **alle 720 richtig** | 30 richtig, 690 verpasst |
| 4 dB | 510 richtig, 480 erfunden, 210 verpasst | 30 richtig, 690 verpasst |

Bis 5 dB hinunter arbeitet das Gatter exakt — deutlich unter den
9,5 dB, die die 3:1-Regel verlangt. Darunter bricht es nicht auf einmal
ab: bei 4 dB gibt es keine Stelle mehr, an der genau eine Person
spricht, also lässt sich die Kopplung überwiegend nicht mehr messen. Die
Trennung läuft dann auf einem halben Modell — immer noch besser als
keins, aber nicht mehr verlässlich. Das Protokoll sagt, wie viele Paare
sich überhaupt messen ließen.

Ohne Gatter sieht der Zusammenbruch unter 6 dB nicht nach „alle reden“
aus, sondern nach „keiner redet“: jede Spur ist durchgehend laut, der
Grundpegel steigt mit, und nichts überschreitet die Schwelle mehr.

## Wie die Spieler eine Stelle anfahren

Eine Stelle anzufahren ist bei Qt keine Anweisung, sondern eine Bitte —
deshalb wird jede Stelle nachgesetzt, bis sie sitzt: alle 120 ms, Toleranz
350 ms, bis zu fünf Sekunden, und immer im Stillstand. Ein `play`, das nicht
ankommt, wird nach 400 ms wiederholt; wechselt das Ausgabegerät, folgt der
Spieler dem neuen Gerät.

## Wie die Kanäle gemessen werden

Welche zwei Kanäle ein Stereopaar sind, entscheidet sich daran, *wann*
beide dasselbe hören, nicht daran, wie ähnlich sie sind. Gemessen an
gebauten Fällen mit absichtlich eingebauter Laufzeit:

| Fall | bei Null | gelesen als |
| --- | --- | --- |
| X-Y, deckungsgleich | 1,00 | ein Paar |
| ORTF, 17 cm | 1,00 | ein Paar |
| Paar mit 30 cm | 1,00 | ein Paar |
| Mono auf beide Seiten | 1,00 | eine Spur |
| zwei Ansteckmics, 0,6 m | 0,16 | zwei Mikrofone |
| zwei Ansteckmics, 1,2 m | 0,10 | zwei Mikrofone |
| zwei Ansteckmics, 2,0 m | 0,10 | zwei Mikrofone |

Pegel und Korrelation versagen hier: bei Übersprechen sind beide
Mikrofone die meiste Zeit gleichzeitig laut.

Die absolute Grenze von −70 dBFS stammt ebenfalls aus einer Messung —
zwei Ausschnitte derselben 32-Kanal-Aufnahme haben dieselben Paare
verschieden beurteilt, weil bei −85 dBFS Dither verglichen wurde.

Beurteilt wird die ganze Aufnahme und nicht Block für Block. Bei einer
Mischer-Aufnahme war der erste Fünf-Minuten-Block der Soundcheck und
ergab ein belegtes Kanalpaar; der zweite war die Aufnahme und ergab
zehn Spuren. Blöcke werden nacheinander gelesen, weil sie nicht alle
gleichzeitig in den Speicher passen.

Ein Block wird in einem Durchgang gelesen und danach zerlegt, statt je
Kanal einmal dekodiert zu werden: eine 32-Kanal-Aufnahme lief früher
32-mal durch ffmpeg. Gemessen an einem 92-MB-Block mit 32 Kanälen:
2,0 s statt 22,9 s, bei gleichen Pegeln und gleichen Paaren; zwei
Blöcke von je 1,8 GB fallen von etwa fünfzehn Minuten auf etwa neunzig
Sekunden.

Beide Kanalumrechnungen werden selbst geschrieben und nicht ffmpeg
überlassen, und das wiegt schwerer, als es aussieht: das Ergebnis von
ffmpeg hängt vom Ausgabeformat ab. Schreibt es Ganzzahlen, skaliert es
die Matrix gegen Übersteuerung herunter und der Pegel stimmt doch,
schreibt es Fließkomma, nicht. Derselbe Aufruf ist an einer Stelle
richtig und an der nächsten 3 dB daneben. Seine eigene Umrechnung
rechnet mit Equal-Power: gemessen an einem Signal bei −24,08 dBFS kommt
ein Kanal auf zwei bei −27,09 heraus und zwei Kanäle auf einen bei
−21,07. Drei Dezibel in die eine oder andere Richtung, beim einmaligen
Hören unhörbar und in jedem Messgerät falsch.

Verglichen werden nur Nachbarn: Kanal 1 gegen 2, 2 gegen 3, und so
weiter. Ein Paar, dessen zwei Kanäle nicht nebeneinander liegen, wird
nicht gefunden.

## Wie die Zeitachse gemessen wird

Die Zeitachse wird mit Stützstellen über die ganze Laufzeit gemessen,
einer Ausgleichsgeraden dadurch und dem Median statt dem Mittelwert. Die
Oberfläche misst im Hintergrund mit demselben Verfahren wie der Lauf
selbst.

Die Schwankung einer Datei wird an fünf Stellen über sie verteilt
gelesen, jeweils zwei Sekunden, an den Zeitstempeln der Pakete im
Container.

## Womit die Lautheit gemessen wurde

| Datei | gemessen |
|---|---|
| Mischung einkanalig | −29,4 LUFS |
| dieselbe Mischung auf beide Kanäle | −26,3 LUFS |
| nach dem Normalisieren, zweikanalig | −16,0 LUFS |

Es dem Schnittprogramm zu überlassen wäre eine unsichtbare Falle: eine
Monospur, mittig auf einen Stereobus gelegt, landet je nach
Panoramagesetz bei 0, −3, −4,5 oder −6 dB.

## Wie viele Prozessoren benutzt werden

Die Hälfte der Prozessoren, die dieser Prozess benutzen **darf**,
höchstens vier, nie mehr als es Dateien gibt. Benutzen darf, nicht hat:
ein Container oder ein taskset kann den Prozess auf zwei von
zweiunddreißig festlegen, und mit allen zweiunddreißig zu rechnen
hieße, dass sich die Threads abwechseln. Python 3.13 und neuer
beantworten diese Frage direkt (`os.process_cpu_count()`); darunter
muss die Zahl der Maschine genügen.

## Wie die Transkription angefordert wird

Die einfache Schnittstelle, die Auphonic für eine einzelne Datei
anbietet, kennt kein Feld für Spracherkennung. Die Produktion wird
deshalb erst angelegt, dann auf Erkennung gestellt, dann gestartet. Ihre
eigenen Ausgabedateien werden gelesen und mit den neuen zusammen
zurückgeschickt, damit der vom Preset gewünschte Ton nicht wegfällt.

Beim Neurechnen kommen auch die Spureinstellungen auf das Preset, jede
über ihre eigene Adresse (`.../multi_input_files/<Name>.json`).

## Spurnamen, und warum das Ziel MOV ist

MOV übernimmt einen eigenen Spurnamen; MP4 verwirft ihn und schreibt
stur „SoundHandler", die Spuren wären dort nicht auseinanderzuhalten.
MP4 kennt außerdem kein PCM im Standard.

## Wie ein Dateiname mit Uhrzeit gelesen wird

Blöcke, deren Namen eine Uhrzeit tragen, werden zusammengefasst, wenn
einer dem anderen innerhalb von zwei Sekunden folgt. Recorder schreiben
ganze Sekunden und ein Block ist selten ganze Sekunden lang — daher der
Spielraum; zwei Blöcke, die wirklich aufeinander folgen, liegen nie
weiter auseinander. Sechs Ziffern für das Datum oder acht, sechs für die
Uhrzeit, und der Kalender muss sie annehmen — `Take_991399_120000` ist
kein Datum und wird auch nicht als eines gelesen. Zwei Namen, die
denselben Moment schreiben — `260808` und `20260808` sind derselbe Tag
—, lassen sich nicht auseinanderhalten, also wird keiner von beiden
genommen, und auch das wird gesagt.

## Wie die Farbkennzeichnung das Kopieren übersteht

Beim Kopieren mit `-c:v copy` schreibt ffmpeg den `colr`-Block aus
seinen eigenen Werten neu und ersetzt, was es nicht kennt: aus Apple Log
(Transferfunktion 21) wird eine 18. Ohne `-movflags +write_colr`
schreibt es gar keinen `colr`-Block, und die Werte stehen nur noch im
Bildstrom, wo Resolve nicht nachsieht. Das Script liest den Block
deshalb selbst aus der Quelle — nicht über ffprobe, das liefert Namen
statt Zahlen und für Unbekanntes einen falschen Namen —, gibt die Zahlen
ausdrücklich weiter (`-color_primaries`, `-color_trc`, `-colorspace`,
`-color_range`), erzwingt das Schreiben und prüft nach: Protokollzeile
**Farbe**.

Die QuickTime-Schlüssel des Containers (`com.apple.quicktime.model`,
`com.apple.quicktime.software`, `com.blackmagic-design.camera.*`) wirft
ffmpeg weg ohne `-map_metadata 0 -movflags +use_metadata_tags`. Das
Script setzt beides.

## Wie das `logs`-Atom übernommen wird

Das Atom liegt in der Bildbeschreibung selbst,
`moov/trak/mdia/minf/stbl/stsd/hvc1`.

ffmpeg kann das Atom nicht erhalten: sein MOV-*Demuxer* kennt den
Boxtyp nicht und liest ihn nie ein, sein *Muxer* schreibt in einem
Bildeintrag nur `colr`, `pasp`, `gama`, `btrt` und den codec-eigenen
Block. Einen Schalter dafür gibt es nicht.

Deshalb trägt das Script das Atom nach dem Schreiben selbst nach, Byte
für Byte aus der Quelle. Das geht nur, weil ffmpeg `moov` ans Dateiende
schreibt: dann verschiebt sein Wachsen die Mediendaten nicht, und die
Chunk-Offsets in `stco`/`co64` bleiben gültig. Es lässt die Finger
davon, wenn

- `moov` nicht als letzte Box am Dateiende liegt (so bei
  `-movflags faststart`),
- eine 64-Bit-Box in der Kette steht,
- die Bildeinträge verschiedener Art sind, `hvc1` gegen `avc1`,
- das Atom über 64 KiB groß ist,
- oder das Atom schon da ist.

Danach wird nachgelesen: die obersten Boxen an denselben Stellen, `moov`
gewachsen und weiter am Dateiende, die Kette bis zur Bildbeschreibung
wieder lesbar, jede Box in ihrer Mutter, das Atom da. Stimmt eines
nicht, kommt das alte `moov` Byte für Byte zurück.

## Was in der Projektdatei steht

| Schlüssel | was |
|---|---|
| `format`, `version` | die Benennung (zurzeit 3) und die schreibende Fassung |
| `files` | die Liste, je Eintrag `{"path": ..., "kind": ...}` |
| `production`, `out_folder` | Name und Ablageort |
| `multitrack` | das Häkchen, und mit ihm die hinteren Reiter |
| `in_point`, `out_point` | das Zeitfenster |
| `camera_cut`, `wide_at_edges` | alle Werte des Kameraschnitts |
| `assignment` | wer zu welcher Kamera gehört, wie die neuen Dateien heißen, „eigener Ton", dazu die zuletzt gespielte Datei (`player_file`, `player_spot`) |
| `preset` | das gewählte Auphonic-Preset, oder `no-auphonic` |
| `transcript`, `speech_language` | das Transkript-Häkchen und der Sprach-Tag |
| `apart`, `together` | von Hand herausgenommene und zusammengelegte Blöcke |
| `channels` | die Stereo-Häkchen, je Datei und Channel |
| `timeline`, `timeline_absolute` | die gemessene Lage jeder Datei |
| `call` | die Kommandozeile des letzten Laufs |

Die `assignment` lässt sich nicht erraten. Die `timeline` spart beim
nächsten Start die Messung.

## Wie eine Stelle für den Weitwinkel bewertet wird

Jeder Kandidat bekommt eine gewichtete Summe aus drei Kriterien — Länge
der Pause (bei 2 s gedeckelt, x3), Nähe zum nächsten Einsatz eines
anderen Sprechers (Rampe über 6 s, x4), Abstand zum Wunschpunkt (x1,5
negativ).

## Woher die Vorschau ihre Versätze nimmt

Eine Übergabedatei trägt je Kamera `offset`, eine Vorschau aus der
Sprecherstatistik je Kamera `start_s`, und beides wird gelesen.

## Deutsch und Englisch: was wo steht

Der ganze Quelltext ist englisch — Namen, Meldungen, Kommentare. Deutsch gibt
es nur als Übersetzungstexte, in `CATALOGUE["de"]` am Dateiende, geschlüsselt
mit dem englischen Text. `T()` schlägt sie nach; ein fehlender Eintrag
erscheint englisch statt gar nicht.

`--lang de` oder `--lang en` legt die Sprache eines Laufs fest; ohne den
Schalter entscheidet `system_locale()` über `LANGUAGE`, `LC_ALL`,
`LC_MESSAGES`, `LANG`, unter macOS `AppleLocale`, unter Windows
`GetUserDefaultLocaleName`. Ein Lauf spricht eine Sprache. Ausnahme ist
`--help`: die Hilfe bleibt englisch, denn diese Texte laufen nicht durch
`T()`.

Nicht übersetzt wird, was Maschinen lesen — Dateinamen, Ordnernamen,
Spurnamen, die Schlüssel in Projekt- und Übergabedatei, die Spaltenköpfe der
CSV-Dateien. Die Schlüssel sind englisch (`speakers`, `cameras`, `length_s`,
`start_s`, `timeline`, `offset`), die Dateien tragen `"format": 3`, und
`format_complaint()` weist ältere Stände ab, statt in alte Namen eine neue
Bedeutung zu lesen.

Zahlen sind geteilt: auf dem Bildschirm folgen sie der Sprache (25.000 gegen
25,000, 1,2 s gegen 1.2 s — `group_text`, `decimal_text`), in Dateien gehen
sie immer englisch. Die CSV-Dateien sind kommagetrennt mit Punkt als
Dezimalzeichen, in jeder Sprache: zwei Läufe müssen vergleichbar bleiben.

Eine weitere Sprache kostet keinen Code: den Block `CATALOGUE["de"]` kopieren,
auf das neue Kürzel taufen, die rechten Seiten übersetzen. `--lang` bietet sie
danach an, und ein darauf eingestelltes System nimmt sie von selbst.

Die Testsuite ist durchweg englisch, und `style_test.py` wacht über den
Quelltext: deutsche Kommentare, erzählende Kommentare, Textzeilen über 79
Zeichen, zu lange Blöcke, Docstring-Kopfzeilen ohne Punkt. Alle Zähler stehen
auf null.

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

Steht ein Name im Feld, bietet die Zelle **Sprecher** an, es sich
anders zu überlegen: **Nur ein Sprecher -- Spur auftrennen?**, oder,
wenn die Stimmen schon da sind, sie zu zeigen. Ein Klick, und sie
stehen in ihren Zeilen. Einem Feld, das niemand beantwortet hat, wird
nichts angeboten.

Ist eine Aufnahme getrennt, steht **Getrennt: 4 Sprecher** in ihrer
Zelle **Sprecher**. Das Programm behält eine Trennung. Wird eine
zweite Aufnahme getrennt, tritt deren Ergebnis an die Stelle der
ersten.

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
einzigen Kamera. Mit einem eigenen Mikrofon je Person sind die Spuren
die Wahrheit, und es muss nichts getrennt werden. Die Trennung sagt,
wer wann spricht; sie macht aus einer Aufnahme keine Spur je Sprecher.

Die Einrichtung lädt beim ersten Mal rund 218 MB, das Modell danach
etwa 33 MB. [Was gebraucht wird](requirements.de.md#das-programm-holen)
sagt, woher das Modell kommt, und die Messungen hinter den 218 MB
stehen in [What was measured](../development/measurements.md)
(englisch).

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

### Die Stimmen benennen

Die Stimmen haben keine eigene Tabelle. Sie hängen unter der Aufnahme,
in der sie gehört wurden, als eingerückte Zeilen derselben Liste: in
der ersten Spalte steht **Stimme**, damit die Stufe überhaupt zu sehen
ist, daneben stehen der **Sprechername** und unter **gehört zu** die
Kamera. Die Namen sind mit Sprecher 1, Sprecher 2 und so fort vorbelegt,
nach Sprechzeit, die längste zuerst. Keine Zeit steht in der Zeile: um
welche Aufnahme es geht, sagt die Zeile darüber, und wie lange jemand
redet, entscheidet hier niemand.

Eine Aufnahme, die Stimmen zeigt, kommt aufgeklappt hoch, mit einem
Dreieck davor, das sie zuklappt. Aufgeklappt bleibt ihr eigenes
**gehört zu** leer, und die Zeilen darunter tragen die Zuordnung;
zugeklappt steht dort, was das Zuklappen vom Schirm nimmt -- die
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

### Wann das Programm neu rechnet

Das Programm rechnet die Trennung nur neu, wenn die Quelldatei wechselt,
wenn sie sich ändert oder wenn jemand eine Sprecherzahl von Hand setzt.
Ein verschobenes Zeitfenster, ein neuer In-Punkt, ein geänderter Versatz
oder ein umbenannter Sprecher laufen mit der vorhandenen Trennung
weiter. Die Trennung aus dem Fenster reist mit dem Lauf mit, und das
Programm rechnet sie nur noch auf dessen Zeitachse um.

Eine von Hand gesetzte Sprecherzahl gehört zu der Aufnahme, für die sie
gesetzt wurde. Der Knopf in einer anderen Zeile verwirft sie und zählt
neu.

### Woher die Sprecher kamen

Das Protokoll sagt es. Zwei Marken zum Suchen:
`SPRECHER -- NACH STIMMEN GETRENNT` und `SPRECHER -- HIER GEMESSEN`.
Zuerst zählt die örtliche Trennung. Die Messung unter der zweiten Marke
braucht je Person eine Spur. Passt die Trennung nicht zum Lauf, sagt
das Protokoll warum, und der Lauf geht weiter – mit der Messung aus den
Spuren oder ohne Schnitt nach Sprechern.

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

Die Erkennung läuft auf dem fertigen Mix, nicht auf den Einzelspuren.
Ein leiser Mitschnitt kann für die Sprechertrennung reichen und für
den Text trotzdem nicht taugen.

### Wofür der Text gebraucht wird

Der Text liefert die Satz- und Teilsatzgrenzen für den Kameraschnitt,
beschrieben in [Sprecherstatistik, Kameraschnitt, EDL](camera-cut.de.md).
Ohne Erkennung schneidet das Programm weiter, nur ohne Satzgrenzen;
dasselbe Kapitel sagt, was der Weitwinkel dann tut.

### Wenn etwas klemmt

* **Die Zeile der Aufnahme sagt, die Trennung ist nicht eingerichtet.**
  Beim ersten Lauf holt sie sich, was sie braucht. Misslingt das, geht
  der Lauf weiter: mit je Person einer Spur kommen die Sprecher aus den
  Spuren, sonst bleibt der Schnitt aus.
* **Die Trennung bricht mit einer Meldung ab.** Das Protokoll sagt, was
  war. Mit je Person einer Spur misst das Programm stattdessen aus den
  Spuren, und der Schnitt kommt trotzdem; auf einer gemeinsamen Aufnahme
  kommt keiner.
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

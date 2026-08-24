# Spracherkennung und Sprechertrennung

*In English: [speech.md](speech.md). Zurück zum
[Inhalt](README.de.md).*

## Die Zeile im Player-Kasten

Das Programm schreibt mit, was gesprochen wird, und es trennt die
Stimmen einer Aufnahme. Beides läuft auf diesem Rechner, ohne Konto und
ohne Hochladen, und bevor irgendetwas zu auphonic.com geht.

### Die Sprecher trennen

Auf dem Reiter **Zuordnung & Zeitfenster** steht im Kasten **Vorschau
Player** eine Zeile unter der gemessenen Zeitachse. Sie sagt, ob sich
die Stimmen einer Aufnahme hier trennen lassen. Sie sagt außerdem, wie
weit das gediehen ist: bereit, läuft, fertig oder für dieses Projekt
abgeschaltet. Die Zeile bleibt leer, wenn nichts zu trennen ist.

Der Knopf **Sprecher trennen** startet die Trennung, **Abbrechen**
hält einen laufenden Durchgang an. Auf einem Rechner, der kein Mac ist,
steht beim ersten Mal **Auf diesem Rechner nicht** daneben. Das Projekt
merkt sich die Antwort, und **Sprecher trennen** verschwindet mit ihr:
ein Projekt, das nein gesagt hat, fragt nicht wieder. Auf einem Mac
läuft die Trennung von selbst, sobald die Dateien da sind.

Die Trennung ist der Weg für **eine gemeinsame Aufnahme**, auf der alle
zu hören sind. Sie braucht das Häkchen **Multitrack (je Sprecher eine
Spur)** nicht: Zeile und Knopf stehen auf beiden Wegen da, auch bei
einer einzigen Kamera. Mit einem eigenen Mikrofon je Person sind die
Spuren die Wahrheit, und die Zeile bleibt weg. Die Trennung sagt, wer
wann spricht; sie macht aus einer Aufnahme keine Spur je Sprecher.

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

Eine Stimme in der Tabelle heißt kein Schnitt: niemand übergibt, also
gibt es keinen Wechsel, an dem geschnitten wird. Die Passagen gehen in
die Übergabedatei, und der Lauf geht bis zum Ende durch.

### Die Stimmen benennen

Auf demselben Reiter steht unter den Zuordnungstabellen eine Tabelle:
**Stimme**, **Sprechername**, **gehört zu**, **Anhören**. Sie hat je
erkannter Stimme eine Zeile, vorbelegt mit Sprecher 1, Sprecher 2 und
so fort nach Sprechzeit, die längste zuerst. Die Zelle **Stimme** nennt
die Aufnahme, wie lange diese Stimme darin redet und wo ihre längste
Stelle anfängt.

1. **Sprecher trennen** drücken. Auf einem Mac ist das schon gelaufen.
2. In einer Zeile **Anhören** drücken. Der Knopf spielt die längste
   Strecke ab, die diese Stimme spricht.
3. **Sprechername** mit dem Namen der Person überschreiben.
4. Bei einer fehlenden Stimme unter der Tabelle **Ein Sprecher mehr in
   `<Datei>`** drücken. Der Knopf hört dieselbe Aufnahme noch einmal
   ab, mit einem Sprecher mehr, als der letzte Durchgang gefunden hat.
   Dann zurück zu Schritt 2. Bei mehr als einer Aufnahme wandert der
   Name vom Knopf in ein Auswahlfeld daneben.

Eine gesetzte Zahl schärft die Trennung. Eine falsche Zahl vervierfacht
die Bildzeit auf der falschen Person. Deshalb wird sie nur gesetzt,
wenn die Zahl bekannt ist. Die Messungen stehen in [What was
measured](../development/measurements.md) (englisch).

![Die Stimmen einer Aufnahme](images/voices.de.png)

*Reiter Zuordnung & Zeitfenster: die Stimmentabelle unter der
Zuordnung, und der Stand der Trennung neben dem Player.*

### Wann das Programm neu rechnet

Das Programm rechnet die Trennung nur neu, wenn die Quelldatei wechselt,
wenn sie sich ändert oder wenn jemand eine Sprecherzahl von Hand setzt.
Ein verschobenes Zeitfenster, ein neuer In-Punkt, ein geänderter Versatz
oder ein umbenannter Sprecher laufen mit der vorhandenen Trennung
weiter. Die Trennung aus dem Fenster reist mit dem Lauf mit, und das
Programm rechnet sie nur noch auf dessen Zeitachse um.

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

* **Die Zeile sagt, die Trennung ist nicht eingerichtet.** Beim ersten
  Lauf holt sie sich, was sie braucht. Misslingt das, geht der Lauf
  weiter: mit je Person einer Spur kommen die Sprecher aus den Spuren,
  sonst bleibt der Schnitt aus.
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
* `VPM_NO_SPEAKER_SPLIT=1` vor dem Aufruf: die Trennung startet nie von
  selbst. Der Knopf startet sie weiterhin.

# Kanäle: eine Spur oder zwei?

*In English: [Channels: one track or two?](channels.md). Zurück zum [Inhalt](README.de.md).*

## Kanäle: eine Spur oder zwei?

Eine Datei mit zwei Kanälen kann zweierlei sein: ein Mikrofonpaar, oder
zwei Personen, die ein Recorder in eine Datei geschrieben hat. Der
Unterschied zählt — als Paar gelesen landen beide Sprecher in einer Spur,
und der Kameraschnitt hat nichts mehr zu wechseln.

In der Dateiliste auf dem Reiter **1. Dateien & Produktion** wird eine
Datei mit mehr als einem Kanal in eine Zeile je Kanal aufgeklappt:
**Kanal 1**, **Kanal 2** und so fort. Auf jeder Zeile bietet ein Häkchen
**mit Channel 3 zusammenlegen** an, und was gemessen wurde, steht
daneben. Gefragt wird jeder Nachbar, nicht jeder zweite. Ein Channel
kann nur zu einem Paar gehören: sind 2 und 3 zusammengelegt, hat die
Zeile von Channel 3 kein eigenes Häkchen mehr und sagt **mit Channel 2
eine Stereospur** — der ist dann vergeben. Sehen zwei Nachbarn beide
nach einem Paar aus, gewinnt der linke, bis jemand etwas anderes sagt.

Die Messung schlägt einmal vor, und ein Häkchen berichtigt diesen
Vorschlag, statt ihn neu zu starten: ein Paar auseinanderzunehmen nimmt
genau dieses auseinander und legt nichts anderes zusammen, eines
zusammenzulegen macht seine beiden Nachbarn frei. Ein Häkchen, das
dasselbe sagt wie die Messung, ist keine Übersteuerung und wird auch
nicht als eine gemerkt; nur eine Zeile, die etwas anderes sagt, steht
als **manuell gesetzt -- übersteuert die Messung** da. Bis die Messung
da ist, sagt die Zeile das, statt zu raten; lässt sich die Kanalzahl
einer Datei gar nicht lesen, sagt der Lauf das, statt die Zeile warten
zu lassen.

Die Spuren heißen nach ihren Channels: `Channel 1`, `Channel 2+3`. Die
Dateien, in die sie geschnitten werden, ebenso — zusammengeschrieben und
mit einem kurzen Fingerabdruck des Quellordners dazwischen:
`Mixer_3f9a1c02_Channel1+2.wav`. Das Wort „Channel" bleibt in jeder
Sprache englisch.

Es entscheidet, *wann* die beiden Kanäle dasselbe hören, nicht wie
ähnlich sie sind. Ein
Mikrofonpaar hört alles praktisch gleichzeitig; zwei Ansteckmikrofone auf
zwei Personen hören einander verspätet, und zwar genau um ihren Abstand.

Der genannte Abstand stimmt auf einen Zehntelmeter, und es trägt auch
dann noch, wenn das Übersprechen 26 dB unter dem Sprecher liegt.

Zwei Grenzen, beide in der Zeile benannt. Ein Paar mit mehr als etwa
35 cm Abstand wird als zwei Mikrofone gelesen. Und eine Datei, deren
beide Kanäle vor dem Zusammenlegen auf eine gemeinsame Zeitachse gebracht
wurden, sieht aus wie ein Paar. Wo die beiden Kanäle zu wenig
gemeinsamen Ton haben, wird nichts behauptet — die Trennung wird
vorgeschlagen.

Jede Spur, die dabei herauskommt, ist eine Spur wie jede andere: eine
Zeile in der Zuordnung, ein Name, eine Kamera, und einzeln anhörbar.
Stumme Kanäle werden keine Spur. Der Haken übersteuert die Messung
jederzeit, und eine Übersteuerung steht im Projekt.

Ob ein Kanal als belegt gilt, entscheiden zwei Regeln, und eine genügt.
Relativ: 45 dB unter dem lautesten Kanal ist ein Eingang, in den niemand
etwas gesteckt hat. Absolut: unter −70 dBFS liegt nur noch der
Rauschteppich des Wandlers. Die absolute Regel stammt aus einer Messung,
nicht aus einer Annahme. Sie greift nur, wenn wenigstens ein Kanal
darüber liegt; eine durchweg leise Aufnahme wird weiter nach der
relativen Regel beurteilt.

Beurteilt wird die ganze Aufnahme, nicht ihr erster Block. Jeder Block
wird für sich gemessen, und die Antworten werden zusammengeführt: ein
Kanal gilt als belegt, wenn er in irgendeinem Block etwas trägt, und
jedes Paar wird in dem Block beurteilt, in dem es am lautesten ist.

### Stereo bleibt Stereo

Eine Spur behält die Kanäle ihrer Quelle. Wo die Messung oben zwei
Kanäle als Paar liest — oder das Häkchen es sagt — bleibt dieses Paar
den ganzen Weg zweikanalig: auf die Zeitachse, durch die
Lautheitsmessung, als eigene Tonspur in die Kameradatei und in den Mix.
Eine zweikanalige Datei, die gar nicht getrennt wurde, verhält sich
genauso; ein zusätzliches Kennzeichen braucht es nicht.

Der Mix ist ohnehin zweikanalig, für eine Stereospur muss also kein
Platz geschaffen werden; was das für die Lautheitsmessung heißt, steht
im [Vorflug](preflight.de.md). Monospuren werden vor der Summe auf beide
Seiten kopiert, nicht danach.

Bei auphonic.com wird der fertige Mixdown zweikanalig angefordert,
sobald eine Spur Stereo ist. Auf dem einfachen Weg wird die Mono-Faltung
bei jeder Ausgabe abgeschaltet, die das Preset verlangt: was ein Preset
faltet, lässt sich hinterher nicht entfalten.

Was auphonic.com mit einer Stereospur innerhalb einer
Multitrack-Produktion macht, habe ich nicht am echten Dienst gemessen.
Kommt eine Spur, die als Stereo hochging, einkanalig zurück, sagt der
Lauf das und macht weiter — der Mix bleibt zweikanalig, weg ist der
Unterschied zwischen den beiden Mikrofonen dieser einen Spur.

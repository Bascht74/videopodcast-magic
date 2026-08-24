# Überblick

*In English: [overview.md](overview.md). Zurück zum
[Inhalt](README.de.md).*

Aus dem Rohmaterial eines Videopodcasts wird eine geschnittene Folge: der
gute Ton in den Videodateien, die Kameras auf einer Zeitachse und ein
erster Kameraschnitt in DaVinci Resolve. Ein Fenster, oder ein Aufruf.

## Was es einem abnimmt

Ein Interview ist im Kasten. Zwei Kameras liefen mit, und weil ein
Kameramikrofon nie gut klingt, stand ein Recorder daneben. Auf der Platte
liegen jetzt zwei Sorten Dateien: großes Bild mit mäßigem Ton, guter Ton
ohne Bild. Es müsste doch reichen, das eine auf das andere zu legen.

Tut es nicht. Der Recorder hat die Aufnahme bei zwei Gigabyte geteilt,
aus einem Interview sind drei Dateien geworden. Ton und Bild fangen nicht
gleichzeitig an. Und nach einer Stunde Schnitt stimmen die Lippen nicht
mehr, ein Zehntel vielleicht. Kamera und Recorder haben je einen eigenen
Quarz, und der eine tickt ein paar Millionstel schneller. Dafür gäbe es
den Timecode, wenn jemand beide Geräte auf dieselbe Uhr gestellt hätte.

Also hört das Programm hin. Es vergleicht, wann der gute Ton laut wird
und wann das Kameramikrofon, schiebt beides übereinander und rechnet den
Uhrengang über die Länge heraus. Wenn die Messung dafür zu wackelig ist,
lässt es die Finger davon und sagt das auch.

Dieser Vergleich lebt von Sprechpausen, und Musik hat keine. Wenn er
nichts findet, sucht das Programm weiter über die Phase, die einen Raum
und ein zweites Mikrofon übersteht. Im Protokoll steht, dass es
umgeschaltet hat, und wie sicher der Fund war. Die Phase sagt, wo der
Ton liegt. Der Uhrengang bleibt unbekannt, und auf diesem Weg rechnet ihn
das Programm nicht heraus.

## Was herauskommt

Je Kamera eine neue Videodatei. Das Bild wird umkopiert, nicht neu
gerechnet. Darin liegt der gute Ton als erste Tonspur, das
Kameramikrofon als zweite, beide mit Namen. Im Schnittprogramm sagt man
„Ton von Spur eins“ und ist fertig. Danach misst das Programm nach, wie
weit die beiden Spuren auseinanderliegen, und schreibt es hin. Bei einem
Recorder und einer Kamera ist das der ganze Lauf: [der einfache
Weg](simple-path.de.md).

Vor dem ersten langen Schritt sieht das Programm das Material durch;
diese Prüfung heißt der Vorflug ([Vorflug](preflight.de.md)). Am Ende
landet jeder Messwert in einer CSV, die der nächste Lauf nicht
überschreibt. Über ein paar Monate sieht man daran, dass ein Recorder
langsamer wird oder eine Kamera den anderen farblich davonläuft.

## Mehrere Sprecher auf eine Zeitachse legen

Drei Leute am Tisch heißt drei Mikrofone, und auf jedem sind alle drei zu
hören. Dieses Übersprechen ist es, was Podcastton billig klingen lässt.
auphonic.com kann es herausrechnen, wenn alle Spuren exakt gleich lang
sind, auf die Millisekunde ([Aufbereitung](auphonic.de.md)). Also legt
das Programm zuerst jede Kamera und jede Spur auf eine gemeinsame
Zeitachse.

Dann ordnet man zu, wer zu welcher Kamera gehört, in einer Tabelle mit
einem Player daneben. Jede Kameradatei trägt danach als erste Tonspur den
Mix genau der Sprecher, die in ihrem Bild zu sehen sind, und die einzelnen
Stimmen dahinter. Wer sie allein abspielt, hört das Passende; wer
schneidet, hat alles einzeln zur Hand ([Multitrack](multitrack.de.md)).

Der Dienst ist freiwillig. Ohne ihn fehlen drei Schritte: De-Bleed,
Leveler und Rauschentfernung. Das Programm findet selbst heraus, wer wann
spricht, und den Abstand der Mikrofone misst es, statt ihn anzunehmen.

## Nach Sprechern schneiden

Ein Sprecher allein bekommt seine Kamera, mit ein wenig Vorlauf, damit
der Schnitt vor dem ersten Wort sitzt. Bei mehreren gleichzeitig Redenden
schlägt eine Kamera, die genau diese Leute zeigt, den Weitwinkel: die
eine Kamera, die alle im Bild hat. Der Weitwinkel selbst kommt nicht nach
der Uhr, sondern an einer langen Sprechpause, kurz bevor jemand anderes
einsetzt.

Acht Zahlenfelder und vier Auswahlfelder legen fest, wie fein der Schnitt
ausfällt, und das Fenster zeigt ihre Wirkung sofort, ohne etwas zu
schreiben. Heraus kommen eine Tabelle, eine EDL und die Sprechzeiten: wer
wie lange geredet hat, in Prozent ([Kameraschnitt](camera-cut.de.md)).

## Das Resolve-Projekt anlegen

Auf Wunsch legt das Programm das Projekt an und baut zwei Timelines
([DaVinci Resolve](resolve.de.md)). Die eine ist der fertige Schnitt:
oben die Bildstücke aus den Kameras, ohne ihren Ton, darunter der
Gesamt-Mix in einem Stück, damit der Klang an den Schnitten nicht
springt. Die andere hat jede Kamera auf einer eigenen Bildspur,
ungeschnitten, bereit für einen Multicam-Clip, wenn Resolve lieber selbst
schneiden soll.

Die Umwandlung ist ein Rechtsklick und das Einzige, was das Programm
nicht abnimmt. Die Scripting-Schnittstelle von Resolve kennt Multicam
nicht, also sagt es genau, was zu klicken ist. Farbkennzeichnung, eine
Farbgruppe je Kamera und der Renderauftrag stehen; in Resolve bleibt ein
Klick auf **Render All**.

## Was es nicht entscheidet

Der Kameraschnitt ist ein Vorschlag, der einem die erste stumpfe Stunde
abnimmt. Was die Folge werden soll, bleibt die eigene Sache: welche
Passage bleibt, wo es sich zieht, wie das Bild gegradet wird, wo die
Blende im Intro sitzt. Das Programm sorgt dafür, dass am Anfang der
eigentlichen Arbeit alles da ist, wo es hingehört. Es sagt einem, wenn
etwas nicht zusammenpasst, bevor man eine Stunde in den falschen Schnitt
gesteckt hat.

[Was gebraucht wird](requirements.de.md) nennt, was zuerst zu
installieren ist. [Die Oberfläche](interface.de.md) zeigt das Fenster
selbst.

# Das Handbuch

*In English: [README.md](README.md). Zurück zum
[Projekt](../README.de.md).*

Elf Kapitel, in der Reihenfolge, in der das Programm arbeitet. Jedes steht
für sich; nichts davon muss von vorn bis hinten gelesen werden.

## Inhalt

* **[Was gebraucht wird](requirements.de.md)** -- Python, ffmpeg, die beiden Pakete, und was sich je Plattform unterscheidet.
* **[Die Oberfläche](interface.de.md)** -- Das Fenster, Reiter für Reiter — und was zu tun ist, wenn es keinen Timecode gibt.
* **[Vorflug](preflight.de.md)** -- Was vor einem Lauf geprüft wird, und was jede Beanstandung bedeutet.
* **[Kanäle: eine Spur oder zwei?](channels.de.md)** -- Wie ein Stereopaar von zwei einzelnen Mikrofonen unterschieden wird. Gemessen, nicht geraten.
* **[Der einfache Fall](simple-path.de.md)** -- Eine Tondatei, eine Kamera: der kürzeste Weg hindurch.
* **[Aufbereitung über auphonic.com](auphonic.de.md)** -- Pegeln, Übersprechen, Transkription — und wo der Schlüssel liegt.
* **[Multitrack: mehrere Sprecher, mehrere Kameras](multitrack.de.md)** -- Eine Spur je Sprecher, mehrere Kameras, eine Zeitachse.
* **[Spracherkennung und Sprechertrennung](speech.de.md)** -- Was gesagt wird und wer es sagt, auf diesem Rechner ermittelt.
* **[Sprecherstatistik, Kameraschnitt, EDL](camera-cut.de.md)** -- Wie der erste Schnitt vorgeschlagen wird, und die Zahlen, an denen er gemessen wird.
* **[DaVinci Resolve](resolve.de.md)** -- Das Projekt, das herauskommt: Timelines, Spuren, Farbe, Ausgabe.
* **[Alle Schalter](command-line.de.md)** -- Jeder Schalter der Kommandozeile, mit dem, was er tut.

Der [Überblick](overview.de.md) ist kein Kapitel: er zeigt dasselbe Feld
auf wenigen Seiten, für alle, die erst entscheiden wollen, ob dieses
Programm für sie ist.

## Weitere Informationen und technische Details

Neben dem Handbuch stehen die Dokumente für alle, die das Programm
ändern statt es zu benutzen. Sie sind alle englisch.

Sie liegen in `development/`, neben diesem Ordner. [Inside the
script](../development/internals.md) sagt, wie die eine Datei aufgebaut
ist und wie jeder Schritt arbeitet. [What was
measured](../development/measurements.md) hält die Belege hinter den
Zahlen: Trefferquoten, Laufzeiten, Verteilungen, Vergleiche. [Coding
guidelines](../development/coding_guidelines.md) sagt, wie der Code
geschrieben ist, und warum.

[CHANGELOG.md](../CHANGELOG.md) sagt, was sich in jeder Fassung geändert
hat, von 0.1.0 an. [THIRD-PARTY.md](../THIRD-PARTY.md) führt auf, worauf
sich das Programm zur Laufzeit stützt und unter welchen Bedingungen,
samt dem mitgelieferten Sprechermodell. [CLAUDE.md](../CLAUDE.md) hält
die Projektregeln, darunter die, über die nicht verhandelt wird; Claude
Code liest die Datei zu Beginn einer Sitzung von selbst.

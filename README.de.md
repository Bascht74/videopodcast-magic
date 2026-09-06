# Video Podcast Magic

*In English: [README.md](README.md)*

![Das Hauptfenster: die Dateien einer Produktion](docs/images/files.de.png)

*Das Hauptfenster. Was gefunden wurde, was zusammengehört und was nicht
zusammenpasst — bevor irgendetwas geschrieben wird.*

*Am Programm arbeiten oder einen Pull Request stellen? [CONTRIBUTING.md](CONTRIBUTING.md) sagt wie: die Tests, der Gegenbeweis, den jede Prüfung schuldet, und was ein Pull Request tragen muss.*

**Version 3.0.0b6.** Es macht die Arbeit, für die es geschrieben wurde,
jede Woche, an echtem Material. Der Schritt auf 3 ist ein Bruch und
kein Haufen neuer Funktionen: das Programm wird jetzt installiert, mit
pip3, und ist danach ein Befehl namens `videopodcast-magic`. Wer es
irgendwo noch als Datei startet, schreibt das einmal um. Das Format
der Projektdatei kann sich weiterhin ändern, und eine ältere Datei
wird mit einer klaren Meldung abgewiesen statt halb gelesen.

`videopodcast-magic` — aufbereiteten Ton als erste Tonspur in
Videodateien legen und daraus alles bauen, was der Schnitt danach braucht:
die Kameras auf einer Zeitachse, einen ersten Schnitt nach Sprecher und ein
DaVinci-Resolve-Projekt.

Ein Python-Programm, und zu bauen ist daran nichts: pip macht ein Paket
daraus und legt den Befehl in den Suchpfad.

## Warum es das gibt

Vor jeder Folge stand dieselbe Stunde Handarbeit. Der Rekorder trennt
eine Aufnahme bei zwei Gigabyte, aus einem Interview werden drei
Dateien. Ton und Bild fangen nicht zusammen an, und nach einer Stunde
sind die Lippen um eine Zehntelsekunde daneben, weil Kamera und
Rekorder jeweils ihren eigenen Quarz haben. Dann muss der gute Ton in
jede Kameradatei, jeder Sprecher muss von den anderen getrennt werden,
und jemand muss entscheiden, welche Kamera zu sehen ist, während wer
spricht.

Nichts davon ist Schnitt. Es ist die Arbeit vor dem Schnitt, es ist
jede Woche dieselbe, und eine Maschine kann sie messen, wo ein Mensch
sie schätzen müsste — also macht es die Maschine, und die Stunde geht
in den Schnitt.

Geschrieben wurde es für einen Podcast, und dort tut es diese Arbeit
jede Woche. Es entscheidet nicht: der Kameraschnitt ist ein Vorschlag,
der Schnitt bleibt deiner. Die Geschichte eines Laufs, von den Dateien
auf der Platte bis zum fertigen Resolve-Projekt, steht in
**[docs/overview.de.md](docs/overview.de.md)**.

## Installieren

Ein Befehl, und einen zweiten Weg hinein gibt es nicht:

```
pip3 install git+https://github.com/Bascht74/videopodcast-magic
videopodcast-magic
```

Die neuere Fassung kommt über dieselbe Adresse und tritt an die Stelle
der installierten:

```
pip3 install -U git+https://github.com/Bascht74/videopodcast-magic
```

**Beim ersten Befehl heißt es warten. Er dauert Minuten, und das soll
er.** Alles, was das Programm an Python braucht, kommt in diesem einen
Zug mit — das Fenster, die Messungen, die Zertifikate, die
Spracherkennung. Danach wird nichts mehr hinter dem Rücken nachgeholt,
und beim ersten Öffnen des Fensters fehlt nichts. Gemessen am
4. September 2026 auf einem Mac: fünf Minuten, 498 MB über die
Leitung, 1,4 GB auf der Platte. Fast alles davon ist das Fenster:
`PySide6` allein kommt in einem Stück von 332 MB, und genau so sieht
eine erste Installation aus, wenn man denkt, sie hänge. Jedes `-U`
danach ist eine Sache von Sekunden — zwölf, gemessen, als sich die
Versionsnummer nicht bewegt hatte —, denn pip liest die Ablage,
vergleicht die Nummer und hört auf, wo dort schon die installierte
steht.

**Verweigert `pip3 install` den Dienst** mit dem Hinweis, diese
Umgebung werde von außen verwaltet, dann gehört dieses Python einem
Paketverwalter — dem von Homebrew oder dem der Linux-Distribution —,
der pip aus dem heraushält, was er selbst pflegt, und die Meldung
nennt den Weg daran vorbei:
`pipx install git+https://github.com/Bascht74/videopodcast-magic` legt
das Programm in eine eigene Umgebung und den Befehl in den Suchpfad.

Zweierlei kann pip nicht mitbringen, weil beides kein Python ist:
**Python selbst**, 3.10 oder neuer, und **`ffmpeg` 9.0.1 oder neuer,
samt `ffprobe`**. Die beiden Werkzeuge sucht das Programm im Suchpfad,
bietet die Paketverwaltung der Maschine an und fragt, bevor es sie
ausführt, und sonst sagt es, woher man sie bekommt. Unter 9.0.1 geht
das Fenster auf und bleibt leer: erst diese Fassung reicht neben dem
Bild auch die Angaben der Kamera unverändert durch — Farbkasten,
Aufnahmekurve, Dolby Vision, Zeitcode.

**Eine Falle, am 4. September 2026 gemessen.** Ein pip, das die
Projektdatei liest, hört unterhalb von Python 3.10 auf und sagt,
welche Version es erwartet hätte. Das pip, das macOS mit seinem
eigenen Python 3.9 mitbringt — `/usr/bin/pip3` —, liest sie nicht: es
antwortet `Successfully installed UNKNOWN-0.0.0` und hinterlässt einen
leeren Ordner dieses Namens, keinen Befehl und keine Fehlermeldung.
Wer `UNKNOWN` liest, hat das falsche pip erwischt; dann Python 3.10
oder neuer installieren und dessen `pip3` nehmen.

Später, und nur wenn jemand will, wofür sie da sind, holt es noch
zwei Dinge: die Umgebung, in der die Sprechertrennung läuft, und ihr
Modell.

**Zum Modell.** Die Trennung liest es aus einem Ordner neben dem
Programm — ohne Konto, ohne Zugangsschlüssel, und nach dem einen
Download ohne Netz. Das Programm holt es aus seinem eigenen
Repository, hält jede Datei gegen ihre Prüfsumme und legt es dorthin.
Es holt das Modell nur beim ersten Mal.

## Loslegen

```
videopodcast-magic                          Oberfläche
videopodcast-magic TON.wav VIDEO.mov
videopodcast-magic TON.wav                  nur zusammensetzen
videopodcast-magic TON.wav *.mov --out Fertig
videopodcast-magic VIDEO.mov                nimmt den Kameraton
videopodcast-magic --lang fr                Sprache der Meldungen
videopodcast-magic --help                   alle Schalter
```

Hat pip den Befehl in einen Ordner gelegt, den der Suchpfad nicht
erreicht, nennt pips eigene Warnung diesen Ordner: ihn in den Suchpfad
aufnehmen und ein neues Terminal öffnen. Einen zweiten Weg hinein gibt
es nicht.

Ohne Argumente öffnet sich die Oberfläche. Die Dateien werden an der Endung
erkannt, die Reihenfolge ist egal. `--lang` legt die Sprache fest -- dreizehn
stehen zur Wahl, `docs/command-line.de.md` nennt sie; ohne den Schalter
entscheidet die Systemsprache. Nur `--help` bleibt englisch.

![Der Reiter Zuordnung](docs/images/assignment.de.png)

*Welche Aufnahme zu welcher Kamera gehört, und was aus jeder Kamera
wird.*

## Was gebraucht wird

Python 3.10 oder neuer, dazu `ffmpeg` 9.0.1 oder neuer samt `ffprobe`
im Suchpfad. Mehr steht nicht auf der Liste: alles andere ist ein
Python-Paket, jedes davon steht auf der Liste, die pip liest, und die
Installation bringt sie alle mit. ffmpeg ist die Ausnahme, die es nicht
sein kann, denn es ist kein Python — ein eigenes bringt das Programm
nicht mit, es bietet den Paketverwalter des Systems an und fragt
vorher, und sonst sagt es, woher man es bekommt. Benutzt wird das Ganze
auf macOS und Windows; Linux läuft mit zwei Einschränkungen.

Die Einzelheiten — warum diese ffmpeg-Fassung, welches Python empfohlen
wird und was sich je Plattform unterscheidet — stehen in
**[docs/requirements.de.md](docs/requirements.de.md)**.

## Das Handbuch

* **[Was gebraucht wird](docs/requirements.de.md)**: der eine Befehl,
  der es installiert, Python, welches ffmpeg und warum, und was sich je
  Plattform unterscheidet.
* **[Die Oberfläche](docs/interface.de.md)**: das Fenster, Reiter für
  Reiter — und was zu tun ist, wenn es keinen Timecode gibt.
* **[Vorflug](docs/preflight.de.md)**: was vor einem Lauf geprüft wird,
  und was jede Beanstandung bedeutet.
* **[Kanäle: eine Spur oder zwei?](docs/channels.de.md)**: wie ein
  Stereopaar von zwei einzelnen Mikrofonen unterschieden wird. Gemessen,
  nicht geraten.
* **[Der einfache Weg](docs/simple-path.de.md)**: eine Tondatei, eine
  Kamera — der kürzeste Weg hindurch.
* **[Aufbereitung über auphonic.com](docs/auphonic.de.md)**: Pegeln,
  Übersprechen, Transkription — und wo der Schlüssel liegt.
* **[Multitrack: mehrere Sprecher, mehrere Kameras](docs/multitrack.de.md)**:
  eine Spur je Sprecher, mehrere Kameras, eine Zeitachse.
* **[Spracherkennung und Sprechertrennung](docs/speech.de.md)**: was
  gesagt wird und wer es sagt, auf diesem Rechner ermittelt.
* **[Sprecherstatistik, Kameraschnitt, EDL](docs/camera-cut.de.md)**: wie
  der erste Schnitt vorgeschlagen wird, und die Zahlen, an denen er
  gemessen wird.
* **[DaVinci Resolve](docs/resolve.de.md)**: das Projekt, das herauskommt
  — Timelines, Spuren, Farbe, Ausgabe.
* **[Alle Schalter](docs/command-line.de.md)**: jeder Schalter der
  Kommandozeile, mit dem, was er tut.

Das ganze Verzeichnis: **[docs/README.de.md](docs/README.de.md)**.

## Weitere Informationen und technische Details

Neben dem Handbuch stehen die Dokumente für alle, die das Programm
ändern statt es zu benutzen. Sie sind alle englisch.

**[Inside the script](development/internals.md)** sagt, wie das
Programm aufgebaut ist und wie jeder Schritt arbeitet. **[What was
measured](development/measurements.md)** hält die Belege hinter den
Zahlen: Trefferquoten, Laufzeiten, Verteilungen, Vergleiche. **[Coding
guidelines](development/coding_guidelines.md)** sagt, wie der Code
geschrieben ist, und warum. Alle drei liegen in `development/`.

**[CHANGELOG.md](CHANGELOG.md)** sagt, was sich in jeder Version
geändert hat, von 0.1.0 an. **[THIRD-PARTY.md](THIRD-PARTY.md)** führt
auf, worauf sich das Programm zur Laufzeit stützt und unter welchen
Bedingungen, samt dem mitgelieferten Sprechermodell.
**[CLAUDE.md](CLAUDE.md)** hält die Projektregeln, darunter die, über
die nicht verhandelt wird; Claude Code liest die Datei zu Beginn einer
Sitzung von selbst.

## Was das Script nicht tut

Es schneidet nicht und entscheidet nichts. Der Kameraschnitt ist ein
Vorschlag. Das Script sorgt dafür, dass am Anfang der eigentlichen Arbeit
alles da ist, wo es hingehört — und sagt Bescheid, wenn etwas nicht
zusammenpasst, bevor man eine Stunde in den falschen Schnitt gesteckt hat.

## Lizenz

MIT — siehe `LICENSE`. Benutzen, ändern, weitergeben; der Urhebervermerk
bleibt dabei. Worauf sich das Programm stützt und unter welchen Bedingungen,
steht in `THIRD-PARTY.md`.

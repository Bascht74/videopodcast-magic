# Video Podcast Magic

*In English: [README.md](README.md)*

**Fassung 1.0.0-beta.** Es macht die Arbeit, für die es geschrieben
wurde, jede Woche, an echtem Material. Beta heißt es, weil es nicht
fertig geprüft ist: das Format der Projektdatei kann sich noch ändern,
und eine ältere Datei wird mit einer klaren Meldung abgewiesen statt
halb gelesen.

`videopodcast-magic.py` -- aufbereiteten Ton als erste Tonspur in
Videodateien legen und daraus alles bauen, was der Schnitt danach braucht:
die Kameras auf einer Zeitachse, einen ersten Schnitt nach Sprecher und ein
DaVinci-Resolve-Projekt.

Eine Python-Datei, rund 24000 Zeilen. Kein Paket, kein Bauschritt.

## Loslegen

```
python3 videopodcast-magic.py                          Oberfläche
python3 videopodcast-magic.py TON.wav VIDEO.mov
python3 videopodcast-magic.py TON.wav                  nur zusammensetzen
python3 videopodcast-magic.py TON.wav *.mov --out Fertig
python3 videopodcast-magic.py VIDEO.mov                nimmt den Kameraton
python3 videopodcast-magic.py --lang de|en             Sprache der Meldungen
python3 videopodcast-magic.py --help                   alle Schalter
```

Ohne Argumente öffnet sich die Oberfläche. Die Dateien werden an der Endung
erkannt, die Reihenfolge ist egal. `--lang de` oder `--lang en` legt die
Sprache fest; ohne den Schalter entscheidet die Systemsprache. Nur `--help`
bleibt englisch.

## Was gebraucht wird

Python 3.10 oder neuer, `ffmpeg` und `ffprobe` im Suchpfad und zwei Pakete
— `PySide6` für das Fenster, `numpy` für die Messungen. Was fehlt, wird
beim Start über pip nachinstalliert. Benutzt wird das Ganze auf macOS und
Windows; Linux läuft mit zwei Einschränkungen.

Die Einzelheiten, samt empfohlener Python-Fassung und den Unterschieden je
Plattform, stehen in
**[docs/requirements.de.md](docs/requirements.de.md)**.

## Das Handbuch

* **[Was gebraucht wird](docs/requirements.de.md)** -- Python, ffmpeg, die beiden Pakete, und was sich je Plattform unterscheidet.
* **[Die Oberfläche](docs/interface.de.md)** -- Das Fenster, Reiter für Reiter — und was zu tun ist, wenn es keinen Timecode gibt.
* **[Vorflug](docs/preflight.de.md)** -- Was vor einem Lauf geprüft wird, und was jede Beanstandung bedeutet.
* **[Kanäle: eine Spur oder zwei?](docs/channels.de.md)** -- Wie ein Stereopaar von zwei einzelnen Mikrofonen unterschieden wird. Gemessen, nicht geraten.
* **[Der einfache Fall](docs/simple-path.de.md)** -- Eine Tondatei, eine Kamera: der kürzeste Weg hindurch.
* **[Aufbereitung über auphonic.com](docs/auphonic.de.md)** -- Pegeln, Übersprechen, Transkription — und wo der Schlüssel liegt.
* **[Multitrack: mehrere Sprecher, mehrere Kameras](docs/multitrack.de.md)** -- Eine Spur je Sprecher, mehrere Kameras, eine Zeitachse.
* **[Sprecherstatistik, Kameraschnitt, EDL](docs/camera-cut.de.md)** -- Wie der erste Schnitt vorgeschlagen wird, und die Zahlen, an denen er gemessen wird.
* **[DaVinci Resolve](docs/resolve.de.md)** -- Das Projekt, das herauskommt: Timelines, Spuren, Farbe, Ausgabe.
* **[Alle Schalter](docs/command-line.de.md)** -- Jeder Schalter der Befehlszeile, mit dem, was er tut.
* **[Im Inneren des Scripts](docs/internals.de.md)** -- Wie die eine Datei aufgebaut ist, und wo das Deutsche steht.

Das ganze Verzeichnis: **[docs/README.de.md](docs/README.de.md)**.

## Was das Script nicht tut

Es schneidet nicht und entscheidet nichts. Der Kameraschnitt ist ein
Vorschlag. Das Script sorgt dafür, dass am Anfang der eigentlichen Arbeit
alles da ist, wo es hingehört — und sagt Bescheid, wenn etwas nicht
zusammenpasst, bevor man eine Stunde in den falschen Schnitt gesteckt hat.

## Lizenz

MIT — siehe `LICENSE`. Benutzen, ändern, weitergeben; der Urhebervermerk
bleibt dabei. Worauf sich das Programm stützt und unter welchen Bedingungen,
steht in `THIRD-PARTY.md`.

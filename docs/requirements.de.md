# Was gebraucht wird

*In English: [requirements.md](requirements.md). Zurück zum [Inhalt](README.de.md).*

## Das Programm holen

Eine Datei, und sonst ist nichts zu installieren:
`videopodcast-magic.py` holen und starten. Der Befehl steht in der
[README](../README.de.md#installieren). Python 3.10 oder neuer muss
vorher da sein — das eine kann das Programm nicht mitbringen.

Alles andere holt sich das Programm, wenn es gebraucht wird, und sagt
dabei, was es tut:

* `numpy` und `PySide6` beim ersten Start, über pip.
* `ffmpeg` und `ffprobe`, wenn sie fehlen, über die Paketverwaltung.
  Wie, steht im Abschnitt darunter.
* Die Umgebung, in der die Sprechertrennung läuft, etwa 218 MB, beim
  ersten Trennen.
* Das Modell für die Trennung, etwa 33 MB, gleich danach.
* Die Nummer der neuesten Fassung, von github.com, kurz nachdem das
  Fenster steht. Gesendet wird nichts, ungefragt geholt auch nichts;
  [Die Oberfläche](interface.de.md#sich-selbst-aktuell-halten) sagt,
  was dann kommt.

**Zum Modell.** Stimmen auseinanderzuhalten braucht ein trainiertes
Modell. Das Programm holt es aus seinem eigenen Repository in den
Ordner `models/` neben dem Programm und hält jede Datei gegen ihre
SHA-256-Prüfsumme; was nicht übereinstimmt, wird nicht geschrieben. Die
Trennung liest es danach von dort, ohne Konto, ohne Zugangsschlüssel
und ohne Netz. Wo der Ordner schon liegt, wird nichts noch einmal
geholt.

## Python

Python: 3.10 oder neuer, darunter sagt das Programm es und hört auf. Die
Untergrenze ist das, was die Oberfläche braucht — PySide6 baut unterhalb
von 3.10 nicht, die Kommandozeile allein käme also tiefer, das Fenster
nicht. Die Testsuite läuft auf 3.14.7, der Fassung, die hier täglich
benutzt wird. `--version`, die Kopfzeile des Protokolls und die erste
Zeile jedes Laufs sagen, welches Python läuft, und nennen die empfohlene
Fassung, wenn es eine andere ist:
`Python 3.11.15  (recommended version 3.14.7)`. `--help` und `--version`
brauchen keines der beiden Pakete und antworten auf jeder Fassung.

## ffmpeg, PySide6, numpy

Gebraucht werden `ffmpeg` und `ffprobe`: zuerst im Suchpfad, dann neben
dem Programm. Fehlen beide, nennt das Programm die Paketverwaltung
dieser Maschine und fragt, bevor es sie ausführt — `brew` unter macOS,
`apt-get`, `dnf`, `zypper` oder `pacman` unter Linux, dort mit `sudo`
davor. Unter Windows gibt es keine zu fragen, also bietet es an,
ffmpeg.org zu öffnen; der Ordner mit `ffmpeg.exe` gehört danach in PATH
oder die Dateien neben das Programm. Nur wo es keine Paketverwaltung
gibt, wird `static-ffmpeg` geholt, eine Fassung in diesem Python.

Für die Oberfläche `PySide6` (Qt), für die Messungen `numpy`. Was fehlt,
wird beim Start über pip nachinstalliert — installiert sein muss nur
Python. In `requirements.txt` stehen die beiden Pakete für alle, die
sie lieber vorher oder in einer virtuellen Umgebung installieren.

## Plattformen

Plattformen: benutzt wird das Ganze auf macOS und Windows. Linux läuft, mit
zwei Einschränkungen — der Schlüssel lässt sich nicht ablegen (kein
Schlüsselbund, keine Registry), er muss also jedes Mal aus `AUPHONIC_TOKEN`
kommen, und der Zwischenspeicher liegt unter `XDG_CACHE_HOME`. Wo die
Paketverwaltung die Python-Installation als extern verwaltet kennzeichnet,
installiert man die beiden Pakete selbst, in einer virtuellen Umgebung oder
über die Pakete der Distribution.

# Was gebraucht wird

*In English: [requirements.md](requirements.md). Zurück zum [Inhalt](README.de.md).*

## Python

Python: 3.10 oder neuer, darunter sagt das Programm es und hört auf. Die
Untergrenze ist das, was die Oberfläche braucht — PySide6 baut unterhalb
von 3.10 nicht, die Befehlszeile allein käme also tiefer, das Fenster
nicht. Die Testsuite läuft auf 3.14.7, der Fassung, die hier täglich
benutzt wird. `--version`, die Kopfzeile des Protokolls und die erste
Zeile jedes Laufs sagen, welches Python läuft, und nennen die empfohlene
Fassung, wenn es eine andere ist:
`Python 3.11.15  (recommended version 3.14.7)`. `--help` und `--version`
brauchen keines der beiden Pakete und antworten auf jeder Fassung.

## ffmpeg, PySide6, numpy

Gebraucht werden `ffmpeg` und `ffprobe`: zuerst im Suchpfad, dann neben dem
Script; fehlen beide, holt sich das Script `static-ffmpeg`. Für die
Oberfläche `PySide6` (Qt), für die Messungen `numpy`. Was fehlt, wird beim
Start über pip nachinstalliert -- installiert sein muss nur Python. In
`requirements.txt` stehen die beiden Pakete für alle, die sie lieber vorher
oder in einer virtuellen Umgebung installieren.

## Plattformen

Plattformen: benutzt wird das Ganze auf macOS und Windows. Linux läuft, mit
zwei Einschränkungen — der Schlüssel lässt sich nicht ablegen (kein
Schlüsselbund, keine Registry), er muss also jedes Mal aus `AUPHONIC_TOKEN`
kommen, und der Zwischenspeicher liegt unter `XDG_CACHE_HOME`. Wo die
Paketverwaltung die Python-Installation als extern verwaltet kennzeichnet,
installiert man die beiden Pakete selbst, in einer virtuellen Umgebung oder
über die Pakete der Distribution.

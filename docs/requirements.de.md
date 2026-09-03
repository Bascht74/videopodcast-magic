# Was gebraucht wird

*In English: [requirements.md](requirements.md). Zurück zum
[Inhalt](README.de.md).*

## Das Programm holen

Es führen zwei Wege hinein, und die
[README](../README.de.md#installieren) hält zu jedem den Befehl.

**Geholt**: die eine Datei `videopodcast_magic.py` nehmen, mit
`python3` starten, sonst ist nichts zu installieren. Gut zum
Hineinschauen, für eine Maschine, an der man einmal sitzt, und für
eine Fassung, die neben ihrem Material liegen bleibt.

**Installiert**: der Befehl
`pip3 install git+https://github.com/Bascht74/videopodcast-magic`
legt das Programm in dieses Python und hinterlässt den Befehl
`videopodcast-magic`, aufrufbar aus jedem Ordner. Derselbe Befehl mit
`-U` holt die neuere Fassung. Gut, wo das Programm jede Woche
gebraucht wird.

Verweigert `pip3 install` den Dienst mit dem Hinweis, diese Umgebung
werde von außen verwaltet, dann gehört dieses Python einem
Paketverwalter — dem von Homebrew oder dem der Linux-Distribution —,
und die Meldung nennt `pipx`. Das ist der richtige Rat: `pipx` auf
dieselbe Adresse legt das Programm in eine eigene Umgebung und den
Befehl in den Suchpfad.

So oder so muss Python 3.10 oder neuer vorher da sein. Das eine kann
das Programm nicht mitbringen.

Alles andere holt sich das Programm, wenn es gebraucht wird, und sagt
dabei, was es tut:

* `numpy` und `PySide6` beim ersten Start, über pip. Das meiste davon
  ist `PySide6`: etwa 250 MB unter Windows und Linux, etwa 440 MB
  unter macOS.
* `ffmpeg` und `ffprobe`, wenn sie fehlen -- über die Paketverwaltung
  dieses Systems, und nur dann, wenn das erlaubt wird. Auf einem
  anderen Weg holt das Programm sie nicht. Der Abschnitt darunter
  sagt, wie.
* Die Umgebung, in der die Sprechertrennung läuft, etwa 218 MB, beim
  ersten Trennen.
* Das Modell für die Trennung, etwa 33 MB, gleich danach.
* Die Nummer der neuesten Version, von github.com, kurz nachdem das
  Fenster steht. Das Programm sendet dabei nichts und holt diese
  Version erst, wenn jemand es verlangt.
  [Die Oberfläche](interface.de.md#sich-selbst-aktuell-halten) sagt,
  was dann kommt.

**Zum Modell.** Die Stimmen einer Aufnahme auseinanderzuhalten ist die
Sprechertrennung, und sie braucht ein trainiertes Modell. Das Programm
holt es aus seinem eigenen Repository in den Ordner `models/` neben
dem Programm. Es hält jede Datei gegen ihre SHA-256-Prüfsumme und
schreibt nur, was übereinstimmt.

Die Trennung liest das Modell danach aus diesem Ordner, ohne Konto,
ohne Zugangsschlüssel und ohne Netz. Das Programm holt es nur beim
ersten Mal.

## Welches Python das Programm braucht

3.10 oder neuer, darunter sagt das Programm es und hört auf. Die
Untergrenze ist das, was die Oberfläche braucht: PySide6 baut
unterhalb von 3.10 nicht. Die Testsuite läuft auf 3.14.7, der Version,
die hier täglich benutzt wird. Sie deckt nur 3.14.7 ab; was zwischen
3.10 und 3.14.7 liegt, ist nicht gemessen.

`--version`, die Kopfzeile des Protokolls und die erste Zeile jedes
Laufs sagen, welches Python läuft. Sie nennen die empfohlene Version,
wenn es eine andere ist: `Python 3.11.15  (recommended version 3.14.7)`.
`--help` und `--version` antworten ohne `numpy`, `PySide6` und
`ffmpeg`.

![Ein Lauf im Terminal](images/terminal.de.png)

*Die erste Zeile nennt Version und Python, darunter steht der Pfad der
laufenden Datei. Dieses Python ist das empfohlene, also folgt keine
Klammer.*

## Woher ffmpeg, PySide6 und numpy kommen

Das Programm sucht `ffmpeg` und `ffprobe` zuerst im Suchpfad, dann
neben sich. Fehlen sie danach immer noch, nennt es die Paketverwaltung
dieser Maschine und fragt, bevor es sie ausführt -- ungefragt tut es
das nie, denn eine Paketverwaltung schreibt außerhalb des Programms,
in das hinein, was dem Besitzer der Maschine gehört:

* **macOS:** `brew`.
* **Linux:** `apt-get`, `dnf`, `zypper` oder `pacman`, mit `sudo`
  davor.
* **Windows:** Windows bringt keine Paketverwaltung mit, also bietet
  das Programm an, ffmpeg.org zu öffnen. Der Ordner mit `ffmpeg.exe`
  gehört danach in PATH oder die Dateien neben das Programm.
* **Wenn nichts installiert wird:** Das Programm hört auf und sagt,
  was auf dieser Maschine zu tun ist -- unter macOS
  `brew install ffmpeg`, unter Windows die Version von ffmpeg.org und
  ihr Ordner in PATH, unter Linux die Paketverwaltung der
  Distribution. Die Frage mit nein zu beantworten beendet den Lauf
  auf demselben Weg. Ein eigenes ffmpeg bringt das Programm nicht
  mit: was es braucht, muss auf der Maschine liegen, und wer es nicht
  hat, holt es sich einmal von Hand.

Eine Frage braucht jemanden, der sie beantwortet, und wird deshalb nur
dort gestellt, wo der Lauf ein Terminal vor sich hat. Ohne eines fragt
das Programm nichts, sondern hört so auf, wie es der letzte Punkt oben
beschreibt.

Für die Oberfläche `PySide6` (Qt), für die Messungen `numpy`. Das
Programm installiert das Fehlende beim Start über pip nach. Nur Python
muss schon da sein. In `requirements.txt` stehen die beiden Pakete für
alle, die sie lieber vorher oder in einer virtuellen Umgebung
installieren.

Wenn eine Paketverwaltung die Python-Installation als extern verwaltet
kennzeichnet, installiert das Programm die beiden Pakete daran vorbei
und sagt es. Um der Paketverwaltung aus dem Weg zu gehen: die beiden
Pakete vorher selbst installieren, in einer virtuellen Umgebung oder
über die Pakete der Distribution.

## Was sich je Plattform unterscheidet

Im Alltag läuft das Programm auf macOS und Windows. Unter Linux läuft
es ebenfalls, mit zwei Einschränkungen:

* Der Schlüssel lässt sich nicht ablegen (kein Schlüsselbund, keine
  Registry), er muss also jedes Mal aus `AUPHONIC_TOKEN` kommen.
* Der Zwischenspeicher liegt unter `XDG_CACHE_HOME`.

## Wenn etwas klemmt

* **Das Programm hört auf und nennt die Python-Version.** Dieses
  Python ist älter als 3.10. Eine neuere installieren und neu starten.
* **pip bekommt `numpy` oder `PySide6` nicht installiert.** Die
  letzten Zeilen von pip sagen, woran es liegt. Beide selbst
  installieren, mit `pip install numpy PySide6`, am besten in einer
  virtuellen Umgebung.
* **`ffmpeg` wird auch nach der Installation nicht gefunden.** Der
  Ordner mit `ffmpeg` steht nicht im Suchpfad. Die beiden Dateien
  stattdessen neben `videopodcast_magic.py` legen.
* **`videopodcast-magic` ist nach der Installation kein bekannter
  Befehl.** pip hat den Befehl in einen Ordner gelegt, der nicht im
  Suchpfad steht. Entweder diesen Ordner in den Suchpfad aufnehmen
  oder das Programm über Python erreichen:
  `python3 -m videopodcast_magic` braucht keinen eigenen Befehl und
  nimmt dieselben Schalter.

Mehr braucht das Programm nicht. Was das Fenster danach zeigt, Reiter
für Reiter, steht in [Die Oberfläche](interface.de.md).

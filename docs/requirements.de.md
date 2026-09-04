# Was gebraucht wird

*In English: [requirements.md](requirements.md). Zurück zum
[Inhalt](README.de.md).*

## Das Programm installieren

Ein Befehl installiert es, und einen zweiten Weg hinein gibt es nicht:

```
pip3 install git+https://github.com/Bascht74/videopodcast-magic
```

Zurück bleibt der Befehl `videopodcast-magic`, aufrufbar aus jedem
Ordner. Alles, was das Programm an Python braucht, kommt in diesem
einen Zug mit: `PySide6` für das Fenster, `numpy` für die Messungen,
`certifi` für die Stellen, gegen die eine https-Verbindung geprüft
wird, `faster-whisper` für die Spracherkennung auf einem System, das
selbst keine mitbringt. Danach wird nichts mehr hinter jemandes Rücken
nachgeholt, und beim ersten Öffnen des Fensters fehlt nichts.

**Dieser erste Befehl dauert Minuten, und die Wartezeit sind diese
Pakete.** Gemessen am 4. September 2026, auf einem Mac mit leerem
Zwischenspeicher: fünf Minuten, 498 MB geholt und danach 1,4 GB auf
der Platte. Fast alles davon ist das Fenster — `PySide6` allein macht
443 MB des Downloads aus, in zwei Stücken von 332 und 111 MB, und
1,2 GB ausgepackt. An einer schnellen Leitung ist es früher vorbei; an
einer langsamen hängt nichts, sondern es lädt gerade das Stück von
332 MB.

**Die neuere Fassung kommt über dieselbe Adresse, und die ist eine
Sache von Sekunden:**

```
pip3 install -U git+https://github.com/Bascht74/videopodcast-magic
```

Dazwischen steht kein Paketverzeichnis: die Adresse ist die Ablage
selbst. pip liest sie jedes Mal neu, vergleicht die Versionsnummer
dort mit der installierten und lässt alles liegen, wo beide dieselbe
ist. Am selben Tag gemessen: zwölf Sekunden für ein `-U`, das nichts
Neueres fand, und kein einziges Paket angefasst.

Verweigert `pip3 install` den Dienst mit dem Hinweis, diese Umgebung
werde von außen verwaltet, dann gehört dieses Python einem
Paketverwalter — dem von Homebrew oder dem der Linux-Distribution —,
der pip aus dem heraushält, was er selbst pflegt, und die Meldung
nennt den Weg daran vorbei: `pipx install` auf dieselbe Adresse legt
das Programm in eine eigene Umgebung und den Befehl in den Suchpfad.

Zweierlei muss vor diesem Befehl auf der Maschine liegen, denn beides
kann pip nicht mitbringen:

* **Python 3.10 oder neuer, und dessen pip.** Ein pip, das die
  Projektdatei liest, hört unterhalb von 3.10 auf und nennt die
  Version, die es erwartet hätte. **Das pip, das macOS mit seinem
  eigenen Python 3.9 mitbringt, liest sie gar nicht und meldet keinen
  Fehler**: am 4. September 2026 gemessen, antwortete `/usr/bin/pip3`
  — pip 21.2.4 — mit `Successfully installed UNKNOWN-0.0.0` und ließ
  einen leeren Ordner dieses Namens zurück. Kein Modul, kein Befehl,
  keine Fehlermeldung. **Wer `UNKNOWN` liest, hat das falsche pip
  erwischt**, und die Antwort darauf ist, Python 3.10 oder neuer zu
  installieren und dessen `pip3` zu nehmen.
* **`ffmpeg` und `ffprobe`.** Sie sind kein Python, und keine Liste,
  die pip liest, hat einen Platz für sie. [Woher ffmpeg
  kommt](#woher-ffmpeg-kommt) sagt, was das Programm tut, wenn sie
  fehlen.

Zweierlei holt das Programm später nach, und nur, wenn jemand will,
wofür es da ist:

* Die Umgebung, in der die Sprechertrennung läuft, etwa 218 MB, beim
  ersten Trennen.
* Das Modell für die Trennung, etwa 33 MB, gleich danach.

Und nach einem fragt es bloß: nach der Nummer der neuesten Version,
bei github.com, kurz nachdem das Fenster steht. Das Programm sendet
dabei nichts und holt diese Version erst, wenn jemand es verlangt.
[Die Oberfläche](interface.de.md#sich-selbst-aktuell-halten) sagt, was
dann kommt.

**Zum Modell.** Die Stimmen einer Aufnahme auseinanderzuhalten ist die
Sprechertrennung, und sie braucht ein trainiertes Modell. Das Programm
holt es aus seinem eigenen Repository in den Ordner `models/` neben
dem Programm. Es hält jede Datei gegen ihre SHA-256-Prüfsumme und
schreibt nur, was übereinstimmt.

Die Trennung liest das Modell danach aus diesem Ordner, ohne Konto,
ohne Zugangsschlüssel und ohne Netz. Das Programm holt es nur beim
ersten Mal.

## Welches Python das Programm braucht

3.10 oder neuer, darunter lehnt pip die Installation ab. Die
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

## Woher ffmpeg kommt

**`ffmpeg` und `ffprobe` sind das eine, was pip nicht mitbringen
kann**, denn sie sind kein Python, und keine Liste, die pip liest, hat
einen Platz für sie. Jedes andere Stück kam mit der Installation; diese
beiden müssen auf der Maschine liegen.

Das Programm sucht sie zuerst im Suchpfad, dann
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

In `requirements.txt` stehen dieselben Python-Pakete, die pip aus
`pyproject.toml` liest, für alle, die sie lieber vor der Installation
in einer virtuellen Umgebung haben.

## Was sich je Plattform unterscheidet

Im Alltag läuft das Programm auf macOS und Windows. Unter Linux läuft
es ebenfalls, mit zwei Einschränkungen:

* Der Schlüssel lässt sich nicht ablegen (kein Schlüsselbund, keine
  Registry), er muss also jedes Mal aus `AUPHONIC_TOKEN` kommen.
* Der Zwischenspeicher liegt unter `XDG_CACHE_HOME`.

## Wenn etwas klemmt

* **pip lehnt ab und nennt eine Python-Version.** Dieses Python ist
  älter als 3.10. Eine neuere installieren und denselben Befehl dieser
  geben.
* **pip antwortet `Successfully installed UNKNOWN-0.0.0`.**
  Installiert wurde nichts. Dieses pip ist zu alt, um die Projektdatei
  zu lesen; auf einem Mac ist das `/usr/bin/pip3`, und es gehört zu
  Python 3.9. Python 3.10 oder neuer installieren und den Befehl
  dessen `pip3` geben.
* **pip sagt, die Umgebung werde von außen verwaltet.** Dieses Python
  gehört einem Paketverwalter. `pipx install` auf dieselbe Adresse ist
  der Weg daran vorbei.
* **Die Installation bricht mittendrin ab.** Die letzten Zeilen von
  pip sagen, woran es liegt. Fast immer ist es der Download von
  `PySide6`, das Stück von 332 MB: denselben Befehl noch einmal geben.
* **`videopodcast-magic` ist danach kein bekannter Befehl.** pip hat
  ihn in einen Ordner gelegt, der nicht im Suchpfad steht. Entweder
  diesen Ordner in den Suchpfad aufnehmen oder das Programm über
  Python erreichen: `python3 -m videopodcast_magic` braucht keinen
  eigenen Befehl und nimmt dieselben Schalter.
* **`ffmpeg` wird auch nach der Installation nicht gefunden.** Der
  Ordner, in dem es liegt, steht nicht im Suchpfad. Ihn dort
  aufnehmen und neu starten.

Mehr braucht das Programm nicht. Was das Fenster danach zeigt, Reiter
für Reiter, steht in [Die Oberfläche](interface.de.md).

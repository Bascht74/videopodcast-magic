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
einen Zug mit: das Fenster, das Messen, die Stellen, gegen die eine
https-Verbindung geprüft wird, die Spracherkennung für ein System, das
selbst keine mitbringt — und die Sprechertrennung, die die Stimmen
einer Aufnahme auseinanderhält und von allem das mit Abstand größte
Stück ist. Danach wird nichts mehr hinter jemandes Rücken nachgeholt,
und beim ersten Öffnen des Fensters fehlt nichts.

**Dieser erste Befehl dauert Minuten, und die Wartezeit sind diese
Pakete.** Auf einem Mac gemessen: etwa hundert Sekunden und danach rund
2565 MB auf der Platte. Das meiste davon sind zwei Brocken — das
Fenster, ein Download von 443 MB in zwei Stücken und 1,2 GB ausgepackt,
und der Unterbau, auf dem die Sprechertrennung rechnet, 536 MB in einem
Stück. An einer schnellen Leitung ist es früher vorbei; an einer
langsamen hängt nichts, sondern es lädt gerade an einem der beiden.

**Die Sprechertrennung gehört zur Installation, und das mit Absicht.**
Sie hat sich früher beim ersten Gebrauch eine eigene Umgebung
eingerichtet, und eine Umgebung neben der Installation liegt außerhalb
dessen, woran pip herankommt: Wer daraus von Hand ein Paket entfernt,
dem fehlt es weiter, und der Befehl zum Aktualisieren merkt nichts
davon. Jetzt setzt ein Befehl alles wieder instand, die Trennung
eingeschlossen.

**Die neuere Fassung kommt über dieselbe Adresse, und die ist eine
Sache von Sekunden:**

```
pip3 install -U git+https://github.com/Bascht74/videopodcast-magic
```

Dazwischen steht kein Paketverzeichnis: die Adresse ist die Ablage
selbst. pip liest sie jedes Mal neu, vergleicht die Versionsnummer
dort mit der installierten und lässt alles liegen, wo beide dieselbe
ist. Gemessen: zwölf Sekunden für ein `-U`, das nichts Neueres fand,
und kein einziges Paket angefasst.

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
* **`ffmpeg` 9.0.1 oder neuer, samt `ffprobe`.** Sie sind kein Python,
  und keine Liste, die pip liest, hat einen Platz für sie. Das Programm
  bietet an, sie zu holen, auf allen drei Systemen. [Woher
  ffmpeg kommt](#woher-ffmpeg-kommt) sagt, warum diese Fassung, was das
  Programm darunter tut, und warum der angebotene Bau soxr mitbringt,
  obwohl er nicht darauf besteht.

Eines holt das Programm später nach, und nur, wenn jemand will, wofür
es da ist: das Modell für die Sprechertrennung, etwa 33 MB, beim ersten
Trennen. Danach fragt es nicht — worauf die Trennung rechnet, kam mit
der Installation, und das Modell ist das letzte kleine Stück von etwas,
das längst bezahlt ist.

Und nach einem fragt es bloß: nach der Nummer der neuesten Version,
bei github.com, kurz nachdem das Fenster steht. Das Programm sendet
dabei nichts und holt diese Version erst, wenn jemand es verlangt.
[Die Oberfläche](interface.de.md#sich-selbst-aktuell-halten) sagt, was
dann kommt.

**Zum Modell.** Die Stimmen einer Aufnahme auseinanderzuhalten ist die
Sprechertrennung, und sie braucht ein trainiertes Modell. Das Programm
holt es aus seinem eigenen Repository in den Ordner `models/` im Ordner
des Programms selbst. Es hält jede Datei gegen ihre SHA-256-Prüfsumme und
schreibt nur, was übereinstimmt.

Die Trennung liest das Modell danach aus diesem Ordner, ohne Konto,
ohne Zugangsschlüssel und ohne Netz. Das Programm holt es nur beim
ersten Mal.

## Wo es nach dem ersten Start auftaucht

Die Installation hinterlässt einen Befehl, und ein Befehl will getippt
werden. **Beim allerersten Start legt sich das Programm daher selbst
einen Platz dort an, wo dieses System seine Programme zeigt** — von da
an startet es wie jedes andere auch:

* **macOS**: ein eigenes Programm im Ordner **Programme** des eigenen
  Benutzers, nicht in dem, der der ganzen Maschine gehört. Es startet
  von dort und lässt sich ins Dock legen wie jedes andere Programm.
* **Windows**: ein Eintrag im eigenen Startmenü, unter dem Namen des
  Programms.
* **Linux**: ein Eintrag, den die Arbeitsumgebung liest, und daneben
  das Bild in dem Ordner, in dem ein Symbolthema danach sucht — so
  behält der Eintrag sein Bild auch dann, wenn die Arbeitsumgebung
  Thema oder Größe wechselt. Wann eine Arbeitsumgebung einen neuen
  Eintrag aufnimmt, bleibt ihre eigene Sache: die eine zeigt ihn
  sofort, die andere erst nach der nächsten Anmeldung.

Installiert wird dabei nichts. Was angelegt wird, zeigt auf den Befehl,
den pip längst auf die Maschine gelegt hat: Wer den Eintrag löscht,
rührt das Programm nicht an, und wer das Programm mit pip entfernt,
behält den Eintrag, bis er ihn wie jedes andere Symbol wegwirft.

**Dabei schreibt es eine Zeile ins Protokoll:**

```
Eine Verknüpfung zu diesem Programm wurde angelegt: <Pfad>
```

Auf dem Bildschirm steht sie nicht: vor dem Fenster sagt das Programm
nichts. Jeder Start danach schreibt auch nichts mehr.

**Der Start hängt davon nicht ab.** Lässt sich der Platz nicht
beschreiben — ein Ordner, in den nicht geschrieben werden darf, ein
System, das keine Antwort gibt —, schreibt das Programm den Grund in eine
zweite Protokollzeile und geht wie gewohnt weiter ins Fenster:

```
Es wurde keine Verknüpfung zu diesem Programm angelegt: <Grund>
```

Beide Zeilen stehen nur dort, zu lesen unter **Hilfe > Protokoll dieses
Laufs anzeigen**.

**Von Hand gelöscht, bleibt gelöscht.** Das Programm schreibt sich den
Platz auf, den es angelegt hat. Ist dieser Platz später leer, während
der Ordner darum herum noch steht, versteht es das als Antwort: Es legt
nichts ein zweites Mal an und sagt auch nichts mehr dazu. Wer den
Eintrag nicht haben will, löscht ihn also genau einmal.

**Zurück kommt er nur, wenn er nicht mehr funktioniert.** Der Eintrag
zeigt auf den installierten Befehl, und der zieht um, sobald das Python
darunter ausgetauscht wird — danach steht das Symbol noch da und
startet nichts mehr. Zeigt der Eintrag auf etwas, das es nicht mehr
gibt, schreibt das Programm ihn neu und dieselbe Zeile noch
einmal ins Protokoll. Das ist der einzige Start nach dem ersten, der
überhaupt etwas schreibt.

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

**9.0.1 ist die Untergrenze, und darunter läuft nichts.** Das Bild aus
einer Kameradatei wird unverändert durchkopiert, und was daneben steht,
soll genauso unverändert ankommen: der Farbkasten, die Aufnahmekurve,
die Dolby-Vision-Angaben, der Zeitcode, die Schlüssel der Kamera. Was
eine ältere Fassung davon fallen lässt, hängt davon ab, wie sie gebaut
wurde: Das Ergebnis sähe richtig aus und wäre falsch, und zwar an genau
der Stelle, an der niemand nachsieht.

Eine Untergrenze sagt, wofür das Programm geradesteht; sie behauptet
nicht, alles darunter sei kaputt. Gegen 9.0.1 wird hier gemessen, und
9.0.1 ist zugleich die Fassung, die das Programm auf allen drei
Systemen selbst besorgen kann — eine Untergrenze, die niemand erreicht,
gehört damit nicht zu den Dingen, die hier schiefgehen können.

**soxr ist keine zweite Bedingung, sondern ein Unterschied in der
Genauigkeit.** Die Kameras kommen auf eine Zeitachse, und ihre Uhren
laufen auseinander — ein paar Millionstel, was über eine Stunde Bilder
sind. Das herauszurechnen heißt, Ton um einen Faktor dicht bei eins zu
dehnen, und der einfache Rechenweg kann nur auf ganze Abtastraten
runden: bei 48 kHz sind das Schritte von 21 ppm. Mit soxr ist der
Schritt 0,21 ppm, also hundertmal feiner. Ein Bau ohne soxr läuft
deshalb, rechnet den Uhrengang gröber heraus und sagt das einmal in den
Meldungen des Laufs. Darum trägt soxr, was das Programm holt oder baut,
obwohl es einen Bau ohne annimmt.

Ist dieses ffmpeg neu genug, hat aber kein soxr, sagt das Fenster es
einmal und bietet den feineren Bau gleich daneben an. Es ist keine
Schranke: **Weiter** behält den vorhandenen, und alles funktioniert.
Gefragt wird einmal je Version, danach nicht wieder — ein Kasten, der
bei jedem Start wegen einer Sache aufgeht, die nicht kaputt ist, ist
ein Kasten, den man wegzuklicken lernt. Wo diese Maschine ohnehin
keinen besseren Bau bekommen kann, wird gar nicht gefragt.

**Fehlt eines oder ist es zu alt, geht das Fenster auf und bleibt
leer.** Gesperrt ist alles, was die beiden Werkzeuge braucht, und nicht
erst der Lauf — Dateien hinzufügen, ein Projekt öffnen, die Zeitachse
messen. Die Meldung nennt das Gefundene und das, was gebraucht wird,
und daneben steht ein Knopf, der es holt.

**Gesagt wird es dort, wo jemand es lesen kann**: in einem Kasten auf
dem Fenster, wenn eines da ist, und im Terminal, wenn das Programm mit
Schaltern gestartet wurde. Wo niemand antworten kann, wird nichts
gefragt und nichts geholt — der Grund steht im Protokoll, und der Lauf
endet. Vor dem Fenster sagt das Programm nie eine Zeile.

**Das Holen dauert Minuten, und jede Zeile davon ist lesbar.** Der
Kasten sagt das, bevor der Knopf gedrückt wird. Was die Paketverwaltung
oder der Download dann von sich gibt, läuft Zeile für Zeile in den
vierten Reiter **Ausgabe** und ins Protokoll dazu — ein Fehlschlag ist
hinterher also nachzulesen und nicht zu erraten. Das Fenster bleibt
dabei bedienbar, und wenn es geklappt hat, sagen die letzten Zeilen das
und bitten um einen Neustart, damit der neue Bau greift.

Das Programm sieht an drei Stellen nach: in dem Ordner, in den es einen
eigenen Bau legt und der allem anderen vorgeht, dann im Suchpfad, dann
neben sich. Fehlen sie danach immer noch, geht es den Weg, den diese
Maschine hat:

* **macOS: Es baut eines.** Für Macs dieser Bauart gibt es keinen
  fertigen Bau zu holen, also übersetzt Homebrew einen aus dem Tap, der
  soxr hat: `brew install --yes homebrew-ffmpeg/ffmpeg/ffmpeg
  --with-libsoxr`. Das dauert zwei bis drei Minuten. Es ist mit Absicht
  **nicht** `brew install ffmpeg`: Homebrews eigenes ffmpeg wird in
  keiner angebotenen Fassung mit soxr gebaut, dieser Befehl
  installierte also eines, das den Uhrengang hundertmal gröber
  herausrechnen muss. Fehlt Homebrew auf der Maschine, gibt es nichts
  zu drücken; dann steht dort, man solle es von brew.sh installieren
  und wiederkommen.
* **Windows: Es holt eines.** Windows bringt keine Paketverwaltung mit,
  also lädt das Programm einen Bau mit soxr und legt `ffmpeg.exe` und
  `ffprobe.exe` in einen eigenen Ordner unter den lokalen Daten des
  Benutzers. Von Hand muss dafür nichts in PATH. Schlägt der Download
  fehl, bietet es stattdessen an, ffmpeg.org zu öffnen.
* **Linux: erst die Paketverwaltung, dann ein Download.** `apt-get`,
  `dnf`, `zypper` oder `pacman`, mit `sudo` davor, wo der Lauf nicht
  ohnehin als root läuft — weil eine Paketverwaltung außerhalb des
  Programms schreibt, in das hinein, was dem Besitzer der Maschine
  gehört, wird vorher gefragt. Danach werden die Werkzeuge noch einmal
  befragt statt geglaubt: Eine Distribution kann Erfolg melden und eine
  Fassung hingelegt haben, die Jahre unter der Untergrenze liegt. Wo
  das so ist, holt das Programm einen eigenen Bau, genau wie unter
  Windows.
* **Wo ein geholter Bau landet, wird er auch benutzt.** Er kommt in den
  eigenen Ordner des Programms für solche Dinge — nicht in den
  Zwischenspeicher, den einzigen Ordner, von dem allen gesagt wird, sie
  dürften ihn löschen — und vor den Suchpfad, damit er antwortet und
  nicht der ältere, den das System hatte.
* **Ist eines da und zu alt**, muss es neu gebaut und nicht ein zweites
  Mal installiert werden: Auf die Aufforderung, etwas zu installieren,
  was schon da ist, antwortet eine Paketverwaltung „ist schon
  installiert“ und tut nichts. Das Programm kennt den Unterschied und
  nimmt den anderen Befehl — unter macOS `brew reinstall --yes
  homebrew-ffmpeg/ffmpeg/ffmpeg --with-libsoxr`.
* **Wenn nichts installiert wird**, bleibt das Fenster leer und sagt,
  was auf dieser Maschine zu tun ist. Die Frage mit nein zu beantworten
  lässt es genauso stehen.

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
  pip sagen, woran es liegt. Fast immer ist es einer der beiden großen
  Downloads, das Fenster oder der Unterbau der Sprechertrennung:
  denselben Befehl noch einmal geben. Verloren ist nichts — was schon
  angekommen war, liegt in pips Zwischenspeicher.
* **`videopodcast-magic` ist danach kein bekannter Befehl.** pip hat
  ihn in einen Ordner gelegt, der nicht im Suchpfad steht, und die
  eigene Warnung von pip nennt diesen Ordner. Ihn in den Suchpfad
  aufnehmen und ein neues Terminal öffnen. Einen zweiten Weg hinein
  gibt es nicht: **`python3 -m videopodcast_magic` hat das Programm
  früher gestartet und tut es nicht mehr.**
* **Das Symbol oder der Startmenü-Eintrag ist weg und kommt nicht
  wieder.** So ist es gedacht: Was von Hand weggeräumt wurde, wird
  kein zweites Mal angelegt. Der installierte Befehl startet das
  Programm weiterhin aus dem Terminal, und ein Alias, eine Verknüpfung
  oder ein selbst gebauter Starter darf darauf zeigen.
* **`ffmpeg` wird auch nach der Installation nicht gefunden.** Der
  Ordner, in dem es liegt, steht nicht im Suchpfad. Ihn dort
  aufnehmen und neu starten.
* **Das Fenster geht auf und bleibt leer, und die Meldung nennt eine
  ffmpeg-Fassung.** Dieses ffmpeg ist älter als 9.0.1. Der Knopf in
  diesem Kasten holt ein neues; was er dabei tut, erscheint unter
  **Ausgabe**. Von Hand heißt das unter macOS `brew reinstall --yes
  homebrew-ffmpeg/ffmpeg/ffmpeg --with-libsoxr`, sonst ein Bau von
  ffmpeg.org und sein Ordner in den Suchpfad. `ffmpeg -version` in
  einem Terminal sagt, welche Fassung gerade im Suchpfad steht.
* **Das Fenster bietet ein feineres ffmpeg an, und kaputt ist nichts.**
  Diesem fehlt soxr. Gesperrt ist damit nichts: Der Uhrengang wird dann
  in Schritten von 21 ppm statt 0,21 herausgerechnet. **Weiter** behält
  das vorhandene, und in dieser Version kommt die Frage nicht wieder.
  `ffmpeg -version` führt `--enable-libsoxr` unter den Bauoptionen auf,
  wo es da ist.

Mehr braucht das Programm nicht. Was das Fenster danach zeigt, Reiter
für Reiter, steht in [Die Oberfläche](interface.de.md).

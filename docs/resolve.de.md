# DaVinci Resolve

*In English: [DaVinci Resolve](resolve.md). Zurück zum [Inhalt](README.de.md).*

## DaVinci Resolve

Auf dem Reiter **Ausgabe** baut es der Knopf
**Resolve-Projekt anlegen**: erst die Dateien, dann das Projekt. Er legt das
Projekt an, setzt Bildrate, Auflösung und Start-Timecode, importiert die
fertigen Dateien und baut die Timelines; der Ablauf wird als
`<Produktion>_resolve_log.txt` mitgeschrieben.

Der Knopf arbeitet auf der Übergabedatei und schickt die Werte für den
Kameraschnitt aus den Feldern mit; die Schnittliste wird also mit dem
gerechnet, was jetzt dort steht. Haben sich In-Punkt oder Out-Punkt
inzwischen geändert, bricht er ab — der Ton in den Videos gehört dann zum
alten Fenster.

Ob Resolve antwortet, wird beim ersten Blick auf den Reiter
**Resolve-Schnitt** von selbst gefragt, im Hintergrund. Der Reiter sagt
die Antwort in einer Zeile, und daneben steht der Weg zum Fenster
**Einstellungen ...**, in dem die Prüfung selbst sitzt. In dessen Kasten
**Verbindung zu Resolve** stehen Produkt und Fassung, wenn es geht, und
wenn nicht, die beiden Pfade, nach denen gesucht wurde, und was im Weg
sein kann:

- Resolve läuft nicht.
- Das externe Scripting steht auf „None" statt „Local", unter
  Preferences > System > General.
- Die freie Fassung, für die berichtet wird, dass externes Scripting seit
  Fassung 19.1 der Studio-Fassung vorbehalten ist. Eine offizielle Aussage
  dazu gibt es nicht.

In diesem Kasten fragt **Erneut prüfen** noch einmal, und das Öffnen des
Fensters ebenso.

| | Schnitt-Timeline | Multicam-Timeline |
|---|---|---|
| Multitrack, mehrere Kameras | Bild aus dem Kameraschnitt, Ton am Stück | alle Kameras nebeneinander |
| einfacher Weg, mehrere Kameras | — keine getrennten Sprecher, also keine | alle Kameras nebeneinander |
| eine Kamera | die Kamera am Stück, der Mix darunter | — wäre sinnlos |

Der einfache Weg legt ebenfalls ein Projekt an. Einen Kameraschnitt kann er
nicht liefern — dafür bräuchte es Multitrack und die Sprecherzuordnung —,
wohl aber die Timeline mit allen Kameras an ihren gemessenen Stellen; daraus
macht Resolve den Multicam-Clip.

Die Bildrate wird auf eine gebracht, die Resolve kennt — ffprobe misst bei
manchen Dateien 29,994 oder 30,001 —, und das Protokoll sagt, welche.
Timecodes werden mit der ganzzahligen Rate gerechnet, Dauern mit der echten;
Drop-Frame ist berücksichtigt.

**… Cut** — der fertige Kameraschnitt. Auf V1 (`Camera cut`) liegen die
Bildstücke **ohne ihren Ton**; darunter läuft auf A1 (`Audio-Full-Mix`)
der Full-Mix in einem Stück durch, damit der Klang an den Schnitten nicht
springt. Der Mix kommt aus der abgelegten Einzeldatei, sonst aus dem
Weitwinkel, wo er die erste Tonspur ist.

Welches Stück aus welcher Kameradatei genommen wird, ergibt sich aus dem
gemessenen Versatz, nicht aus dem Timecode. Lief eine Kamera nicht,
springt eine andere ein, zuerst der Weitwinkel; das Protokoll sagt, wie
oft. Marker gibt es hier keine — der Schnitt ist gemacht.

**… Multicam** — alle Kameras nebeneinander, eine je Bildspur, in voller
Länge und **ohne Schnitte**, jede an ihrer gemessenen Stelle, Spurnamen =
Sprecher (eine Kamera ohne Sprecher heißt `Wide`), dazu die Sprechernamen
als Marker. Auf Bildspur 1 kommt die Kamera, deren erste Tonspur der
Full-Mix ist, meist der Weitwinkel; beim Umwandeln wird er zu
Perspektive 1.

**Je Kamera genau eine Tonspur, mit ihrem Bild verknüpft.** Der
überzählige Ton wird nach dem Einfügen gelöscht und die Tonspuren werden
wie die Bildspuren benannt. Eine Kamera, die nicht gelandet ist, wird
einzeln nachgelegt und andernfalls gemeldet.

### Wenn es das Projekt schon gibt

Es wird gefragt:

- **auf den neuen Stand bringen** — die beiden Timelines, die dieses Script
  baut (`… Cut` und `… Multicam`), werden gelöscht und neu gebaut, die
  Projekteinstellungen kommen auf den neuen Stand. **Alles andere bleibt
  unangetastet:** der Medienpool, eigene Timelines, alles aus früheren Läufen.
- **so lassen und die neuen Timelines danebenlegen** — die vorhandenen
  bleiben.
- **ein neues Projekt daneben anlegen** — Name mit Zusatz.
- **abbrechen.**

In der Oberfläche fragt ein Fenster, im Terminal kommt eine Nummer (auf der
Kommandozeile vorweg `--resolve-project update|keep|new|abort`).

Nach dem Löschen wird nachgesehen — Resolve meldet auch dann Erfolg, wenn
nichts geschah. Bleibt eine Timeline stehen, sagt das Protokoll es, und die
neue bekommt einen Zusatz im Namen.

Die Multicam-Timeline bleibt verschont, wenn sie schon passt — dieselben
Kameras in derselben Reihenfolge. Wer eine neue will, löscht sie in Resolve.
Eine Sicherungskopie wird nicht angelegt: ein Lauf mehr baut sie wieder auf.

### Multicam-Ton: die vier Möglichkeiten

Beim Umwandeln fragt Resolve unter *Multicam Audio Options*, woher der Ton
kommen soll (Handbuch, Kapitel „Multicam Audio Options"):

| Einstellung | wirkt |
|---|---|
| **Source Audio Channels** (Vorgabe) | Zugriff auf die einzelnen Spuren und Kanäle jeder Perspektive |
| **Reference Audio / Angle 1** | die *erste reine Tonperspektive* wird zur Tonspur für alle Winkel; fehlt eine, ist es der erste Winkel |
| **Adaptive Tracks** | alle Spuren und Kanäle einer Perspektive kommen in **eine** Adaptive-Spur |
| **All Angles** | jede Tonspur jeder Perspektive kommt mit — vier plus fünf ergibt neun |

*Source Audio Channels* ist die richtige Wahl: je Kamera ist nur noch eine
Tonspur übrig, und jede Perspektive bringt genau den Sprecher mit, der vor
ihr sitzt. Der Schlusshinweis im Protokoll sagt es auch.

### Clipfarben

Jeder Schnitt bekommt die Farbe seiner Perspektive, auf beiden Timelines.
Die Farben sind nach Unterscheidbarkeit sortiert, der Weitwinkel bekommt
`Tan`. Gibt es mehr Perspektiven als Farben, wiederholt sich die Reihe,
und das Protokoll sagt es.

Dazu bekommt jede Kamera eine **Farbgruppe** — siehe *Farbgruppen* weiter
unten.

### Der Renderauftrag

Stehen die Timelines, legt das Script das Renderprofil an und stellt den
Auftrag in die Warteschlange. In Resolve bleibt nur noch „Render All".

Ob HDR oder SDR herauskommt, entscheiden Material und Projekt, nicht der
Geschmack. Gelesen wird zuerst der `colr`-Block der Kameradateien. Als HDR
gilt:

- **PQ oder HLG** (Übertragungsfunktion 16 oder 18), die beiden
  HDR-Anzeigekurven,
- **Log** (Apple Log steht als 21 in der Datei) — eine Aufnahmekurve,
  keine Anzeigekurve. **Log ist HDR.**
- **BT.2020** als Farbraum oder als Matrix.

Schreibt eine Kamera nichts Brauchbares in den `colr`-Block, werden
zusätzlich ihre QuickTime-Schlüssel gelesen; dort steht bei den meisten
Kameras die Kurve. Gesucht wird nach Wortmarken (`apple log`, `s-log`,
`v-log`, `logc`, …), nicht nach „log". Sagen die Projekteinstellungen
etwas anderes, sticht das Projekt.

| | SDR | HDR |
|---|---|---|
| Codec | H.264, acht Bit | H.265, zehn Bit (Profil Main10) |
| 2160p | 45.000 kbit/s | 56.000 kbit/s |
| 1440p | 16.000 | 20.000 |
| 1080p | 8.000 | 10.000 |
| 720p | 5.000 | 6.500 |

Bei hohen Bildraten — 48, 50, 60 — gelten die höheren Werte: 68.000 bzw.
85.000 kbit/s bei 2160p, entsprechend darunter. Es sind die Empfehlungen von
YouTube für den Upload, jeweils der obere Wert des Bereichs.

Eine Warnung steht im Protokoll, falls dieses Resolve kein H.265 anbietet, und
eine zweite, falls es das Profil Main10 nicht annimmt — dann wird es ohne
gesetzt.

Gekennzeichnet werden muss HDR außerdem, sonst trägt die fertige Datei keins,
so sauber sie auch gradiert ist. Die Kurve kommt aus dem Ausgabefarbraum des
Projekts: PQ bekommt Rec.2020 / ST.2084, HLG bekommt Rec.2020 / HLG. Nennt das
Projekt keine HDR-Kurve, bleibt der Render auf „Same as Project".

Fest sind: eine Datei statt eine je Clip, Ziel ist der Ausgabeordner,
Dateiname der Produktionsname, `.mp4`, Ton AAC bei 48 kHz, 16 Bit, zwei
Kanäle. Die Tonbitrate kennt die Scripting-Schnittstelle von Resolve nicht
als Schlüssel; das Protokoll schreibt hin, dass 384 kbit/s die Empfehlung
für Stereo wären. Bei HDR nennt es auch die Prüfung:
`videopodcast-magic.py --hdr-check DATEI`.

### Vorspann und Abspann

In der Kameratabelle auf dem Reiter **Zuordnung & Zeitfenster** hat jede
Zeile eine Spalte **Typ**: *Inhalt*, *Vorspann*, *Abspann* oder
*Video ignorieren*. Vorspann und Abspann sind freiwillig. Eine Datei, die
kein Inhalt ist, wird nicht ausgerichtet, nicht aufbereitet und nicht
umkopiert — sie ist ein fertiger Clip und kommt nur in die Timeline (auf der
Kommandozeile `--intro DATEI` und `--outro DATEI`). Beide landen auf der
**zweiten** Bild- und Tonspur, über dem Inhalt (`Intro / Outro` und
`Audio Intro / Outro`).

Es gibt einen Vorspann und einen Abspann. Stellt man eine zweite Datei auf
denselben Typ, geht die erste zurück auf Inhalt. Ein Lauf, der trotzdem zwei
desselben Typs sieht, hält an und nennt sie.

**Gekürzt wird nichts.** Beide Clips behalten ihre volle Länge, und auch der
Inhalt wird nicht angeschnitten. Es verschiebt sich nur, wo sie liegen, und
das richtet sich nach dem **Ton**, nicht nach der Dateilänge:

- **Vorspann**: das *Ende seines hörbaren Tons* trifft auf das erste Wort.
  Gemeint ist der Jingle, nicht die Datei. Die Schwelle liegt 40 dB unter der
  lautesten Stelle der Datei selbst.
- **Abspann**: der *Anfang seines Tons* trifft auf das Ende des letzten Worts.
- Wo die Worte liegen, steht in den Sprecherabschnitten der Übergabedatei.
- Hat ein Clip keinen Ton, gilt beim Vorspann sein Ende, beim Abspann sein
  Anfang.

Die weiche Blende zieht man selbst, und genau dafür liegen die Clips
*über* dem Inhalt statt daneben: so genügt ein Zug an der oberen Ecke. Die
Scripting-Schnittstelle von Resolve kennt keine Übergänge.

### Farbe

Die Farbe der Quelle bleibt unverändert erhalten. Das Script liest den
`colr`-Block selbst aus der Quelle, gibt die Zahlen ausdrücklich weiter,
erzwingt das Schreiben und prüft nach: Protokollzeile **Farbe**.

iPhone-Aufnahmen aus der Blackmagic Camera App tragen im `colr`-Block
„unbestimmt" als Kurve; Resolve geht nach den QuickTime-Schlüsseln des
Containers (`com.apple.quicktime.model`, `com.apple.quicktime.software`,
`com.blackmagic-design.camera.*`). Das Script nimmt sie mit und zählt
nach, ob alle Schlüssel ankamen (Protokollzeile **Kameradaten**).

#### Das `logs`-Atom

In der Bildbeschreibung liegt ein kleines Atom `logs`, in dem die
Aufnahmekurve als Kennung steht, etwa
`com.apple.apple-wide-gamut.apple-log`. **Das** ist, woran Resolve Apple
Log erkennt — im `colr`-Block steht davon nichts. ffmpeg kann das Atom
nicht erhalten, deshalb trägt das Script es nach dem Schreiben selbst
nach, Byte für Byte aus der Quelle, und liest danach nach, ob die Datei
noch heil ist.

Im Protokoll steht danach unter **Kameraatome**, ob das Atom nachgetragen
wurde und welche Kurve es nennt, in der Dateiliste die Kurve in der Zeile
**Farbe** — mit Klarnamen, wo einer bekannt ist (Apple Log, Apple Log 2),
sonst mit der Kennung, wie sie dasteht.

### Farbgruppen

Das Script legt je Kamera eine **Farbgruppe** an und weist ihr alle Clips
dieser Kamera zu, korrigiert wird also einmal je Kamera statt einmal je
Schnitt. Der Node-Editor auf der Farbseite kennt dafür vier Betriebsarten:

| Betriebsart | wirkt auf |
|---|---|
| **Group Pre-Clip** | „affect every clip in the group simultaneously" — die ganze Kamera |
| **Clip** | „only affect the specific clip that's selected" — dieser eine Schnitt |
| **Group Post-Clip** | wieder die ganze Gruppe, aber nach dem Clip gerechnet |
| **Timeline** | alle Clips der Timeline |

Gerechnet wird in dieser Reihenfolge. Also: die Grundkorrektur einer Kamera in
**Group Pre-Clip**, und fällt ein einzelner Schnitt aus der Reihe, ihn in
**Clip** nachziehen. Weitere Clips kommen per Rechtsklick > Group > Name >
Assign to Group in die Gruppe.

### Lokale statt Remote-Grades

Das Script setzt **lokale Versionen**, bei jedem Lauf ausdrücklich.
Remote-Grades („Use local version for new clips" aus) binden alle Clips
derselben Quelldatei an eine Korrektur, ein einzelner Schnitt ließe sich
dann nicht mehr für sich korrigieren. Einen Schalter zum Wiedereinschalten
gibt es nicht.

Die Einstellung wirkt nur auf Clips, die **danach** in eine Timeline
kommen: `--resolve-project update` baut beide Timelines neu und erledigt
das. Bei `keep` hängen die vorhandenen Clips an ihrem Remote-Grade, und
das Protokoll nennt den Weg — Farbseite, Rechtsklick auf ein Miniaturbild
> **Copy Remote Grades to Local** (nimmt die Korrektur mit) oder **Use
Local Grades**. Wie die Einstellung intern heißt, wird aus der Liste aller
Projekteinstellungen herausgesucht und nachgelesen.

### HDR: was in der Datei stehen muss

Ein HDR-Bild reicht nicht — es muss auch draufstehen. Drei Zahlen nach
ITU-T H.273 entscheiden, ob ein Abspieler oder YouTube die Datei als HDR
behandelt; fehlen sie, wird alles als SDR gezeigt, und der Aufwand mit Apple
Log ist verloren.

| Merkmal | HDR10 (PQ) | HLG | Pflicht |
|---|---|---|---|
| Primärfarben | **9** (BT.2020) | **9** | ja |
| Kurve | **16** (SMPTE ST 2084) | **18** (HLG) | ja |
| Matrix | **9** (BT.2020, nicht konstant) | **9** | ja |
| Bittiefe | 10 (oder 12) | 10 | ja |
| Codec | HEVC **Main 10** | dito | bei HEVC |
| `colr`-Atom im Container | vorhanden | vorhanden | ja |
| Mastering-Display (ST 2086) | Werte des Referenzmonitors | entfällt | nein |
| MaxCLL / MaxFALL | z. B. 1000 / 400 | entfällt | nein |

Zwei Fallen: **die 14 ist keine HDR-Kurve** — sie heißt „BT.2020 10 bit" und
ist SDR im großen Farbraum. Und **Tagging ändert keine Pixel**: ein PQ-Tag auf
einem Rec.709-Grade macht daraus falsch gekennzeichnetes SDR. Die statischen
Metadaten sind nur empfohlen; fehlen sie, setzt YouTube Vorgabewerte an (ein
Sony BVM-X300), bei HLG entfallen sie ganz.

**Was das Script tut.** Beim Anlegen des Renderauftrags liest es den
Ausgabefarbraum aus den Projekteinstellungen. Nennt er PQ oder HLG, setzt es
`ColorSpaceTag`, `GammaTag` und `EncodingProfile` = `Main10`; welche
Schreibweise diese Resolve-Fassung annimmt, steht nirgends, also werden
mehrere probiert und die angenommene protokolliert. Sonst bleibt es bei „Same
as Project", und das Protokoll nennt die Stelle: Project Settings > Color
Management > Output Color Space.

**Nachsehen an der fertigen Datei:**

```
videopodcast-magic.py --hdr-check Produktion.mp4
```

Das prüft alle Punkte der Tabelle, sagt zu jedem, was zu tun wäre, und ändert
nichts. Rückgabewert 0 heißt: die Datei geht als HDR durch.

„Embed HDR10 Metadata" und die HDR10+-Analyse kann das Script nicht
ferngesteuert einschalten — dafür kennt die Scripting-Schnittstelle von
Resolve keinen Schlüssel. Von Hand: Color Management > HDR10+, Farbseite >
Analyze All Shots, Deliver > Embed HDR10 Metadata.

### Bildausschnitt

Position und Zoom gehen über dieselbe Gruppe wie die Farbe, aber nur an einer
Stelle. Die Palette **Sizing** (Farbseite, unten Mitte, zwischen „Key" und
„Stereo") kennt fünf Betriebsarten:

| Betriebsart | wirkt |
|---|---|
| Edit Sizing | wie der Inspektor der Schnittseite, je Clip |
| Input Sizing | vor dem Node-Baum, je Clip |
| **Node Sizing** | **im Node-Baum, am ausgewählten Node** |
| Output Sizing | für die ganze Timeline |
| Reference Sizing | nur für den Standbild-Vergleich |

Eine Gruppe teilt den Node-Baum, nicht die Clipeinstellungen; sie nimmt Node
Sizing mit, Edit und Input Sizing nicht. Also: Clip der Kamera anklicken, im
Node-Editor von „Clip" auf **Group Pre-Clip** umschalten, Sizing-Palette auf
**Node Sizing**, einstellen — gilt rückwirkend für jeden Clip dieser Kamera in
beiden Timelines. Was am Media-Pool-Clip geändert wird, greift dagegen nur für
Clips, die *danach* in eine Timeline kommen.

Aus dem Handbuch geschlossen (Kapitel 142 und 152), nicht abgeschrieben: dass
Node Sizing im Group-Pre-Clip-Baum auf die ganze Gruppe wirkt, steht dort
nicht.

### Wenn Resolve selbst schneiden soll

Dafür braucht es einen Multicam-Clip, und den kann das Script nicht
anlegen: die Scripting-Schnittstelle kennt Multicam nicht. Also von Hand:

1. Medienpool, Rechtsklick auf „… Multicam"
2. **Timeline in Multicam-Clip umwandeln** > **Quellaudiokanäle verwenden**

Zum Ton siehe die vier Möglichkeiten weiter oben. Der Spurname wird zum Namen
der Perspektive (Handbuch, Kapitel 49) — deshalb heißen die Bildspuren nach
den Sprechern. Die Umwandlung ist ein Einwegvorgang, und eine
Sicherungskopie gibt es nicht.

### Weitere Optionen über die Kommandozeile

Im Fenster gibt es diese Möglichkeiten nicht.

- `--resolve` baut das Projekt als Teil eines ganzen Laufs, gleich nach den
  Dateien.
- `--resolve-json DATEI` holt den Resolve-Teil allein nach; alles Nötige
  steht in `Produktion_resolve.json`. Das ruft auch der Knopf
  **Resolve-Projekt anlegen** auf.
- `--resolve-audio-tracks` sieht nur nach: für das offene Projekt schreibt
  es die Kanalzuordnung jedes Clips und die Spuren jeder Timeline hin.


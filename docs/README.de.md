# Das Handbuch

*In English: [README.md](README.md). Zurück zum
[Projekt](../README.de.md).*

Elf Kapitel, in der Reihenfolge, in der das Programm arbeitet. Jedes steht
für sich; nichts davon muss von vorn bis hinten gelesen werden.

## Inhalt

* **[Was gebraucht wird](requirements.de.md)**: Python, ffmpeg, die
  beiden Pakete, und was sich je Plattform unterscheidet.
* **[Die Oberfläche](interface.de.md)**: das Fenster, Reiter für
  Reiter — und was zu tun ist, wenn es keinen Timecode gibt.
* **[Vorflug](preflight.de.md)**: was vor einem Lauf geprüft wird, und
  was jede Beanstandung bedeutet.
* **[Kanäle: eine Spur oder zwei?](channels.de.md)**: wie ein
  Stereopaar von zwei einzelnen Mikrofonen unterschieden wird.
  Gemessen, nicht geraten.
* **[Der einfache Weg](simple-path.de.md)**: eine Tondatei, eine
  Kamera — der kürzeste Weg hindurch.
* **[Aufbereitung über auphonic.com](auphonic.de.md)**: Pegeln,
  Übersprechen, Transkription — und wo der Schlüssel liegt.
* **[Multitrack: mehrere Sprecher, mehrere Kameras](multitrack.de.md)**:
  eine Spur je Sprecher, mehrere Kameras, eine Zeitachse.
* **[Spracherkennung und Sprechertrennung](speech.de.md)**: was gesagt
  wird und wer es sagt, auf diesem Rechner ermittelt.
* **[Sprecherstatistik, Kameraschnitt, EDL](camera-cut.de.md)**: wie
  der erste Schnitt vorgeschlagen wird, und die Zahlen, an denen er
  gemessen wird.
* **[DaVinci Resolve](resolve.de.md)**: das Projekt, das herauskommt —
  Timelines, Spuren, Farbe, Ausgabe.
* **[Alle Schalter](command-line.de.md)**: jeder Schalter der
  Kommandozeile, mit dem, was er tut.

Der [Überblick](overview.de.md) ist kein Kapitel: er zeigt dasselbe Feld
auf wenigen Seiten, für alle, die erst entscheiden wollen, ob dieses
Programm für sie ist.

## Stichwortverzeichnis

Jeder Eintrag nennt sein Kapitel und den Abschnitt darin. Der Abschnitt,
der das Wort erklärt, steht vorn.

* **3:1-Regel**: `preflight`, „Wie der Bericht das Übersprechen gegen die
  3:1-Regel misst“
* **Abspann**: `resolve`, „Vorspann und Abspann setzen“; `multitrack`, „Die
  Zuordnung setzen“
* **Abtastwerte am Anschlag**: `preflight`, „Wie der Bericht die Abtastwerte
  am Anschlag zählt“
* **als Spur (Häkchen)**: `multitrack`, „Kameraton zur Spur machen“
* **Anschlag**: siehe Abtastwerte am Anschlag
* **Ansteckmikrofon**: `channels`, „Eine Spur oder zwei“; `multitrack`,
  „Kameraton zur Spur machen“
* **API Key**: `auphonic`, „Der Schlüssel und das Preset“; `interface`, „Was
  hinter Einstellungen ... steht“
* **Apple Log**: `resolve`, „Wie Apple Log das Umschreiben übersteht“
* **Bildrate, variable**: `preflight`, „Was der Bericht zur variablen
  Bildrate sagt“
* **Block**: `simple-path`, „Was neben dem Mix ins Video kommt“;
  `simple-path`, „Blöcke von Hand zusammenlegen“
* **`colr`**: `resolve`, „Die Farbe der Quelle erhalten“
* **De-Bleed**: `auphonic`, „Ohne Auphonic arbeiten“; `preflight`, „Wie der
  Bericht das Übersprechen gegen die 3:1-Regel misst“
* **Drop-Frame**: `resolve`, „Der Knopf und die beiden Timelines“
* **Edit Change Delay**: `camera-cut`, „Die Stellschrauben einstellen“
* **EDL**: `camera-cut`, „Wie der Schnitt entsteht“
* **Einstellungen ...**: `interface`, „Was hinter Einstellungen ... steht“
* **Entfernen (Knopf)**: `simple-path`, „Blöcke von Hand zusammenlegen“;
  `multitrack`, „Mehrere Dateien gleichzeitig laufen lassen“
* **Farbgruppe**: `resolve`, „Eine ganze Kamera auf einmal korrigieren“
* **Farbvergleich**: `camera-cut`, „Was Kennzahlen und Farbvergleich messen“
* **faster-whisper**: `speech`, „Wie das Programm den Text mitschreibt“
* **ffmpeg**: `requirements`, „Woher ffmpeg, PySide6 und numpy kommen“
* **ffplay**: `interface`, „Die vier Reiter“
* **Fortsetzungsdatei**: `simple-path`, „Was neben dem Mix ins Video kommt“;
  `interface`, „Die vier Reiter“
* **Full-Mix**: `multitrack`, „Was in die Kameradateien kommt“; `resolve`,
  „Der Knopf und die beiden Timelines“
* **gehört zu (Auswahlfeld)**: `multitrack`, „Die Zuordnung setzen“;
  `simple-path`, „Blöcke von Hand zusammenlegen“
* **Guthaben**: `auphonic`, „Wenn es die Produktion schon gibt“
* **HDR**: `resolve`, „HDR: was in der Datei stehen muss“; `resolve`, „Was
  der Renderauftrag setzt“
* **`--hdr-check`**: `resolve`, „HDR: was in der Datei stehen muss“
* **Hüllkurve**: `interface`, „Die vier Reiter“; `multitrack`, „Mehrere
  Dateien gleichzeitig laufen lassen“
* **In-Punkt**: `multitrack`, „Das Zeitfenster setzen“; `interface`, „Die
  vier Reiter“
* **Kameraton**: `multitrack`, „Kameraton zur Spur machen“; `simple-path`,
  „Was je Videodatei zurückkommt“
* **Kanal, belegt oder nicht**: `channels`, „Welche Kanäle überhaupt eine
  Spur werden“
* **Kennzahlen (`_metrics.csv`)**: `camera-cut`, „Was Kennzahlen und
  Farbvergleich messen“
* **Lautheitsumfang**: `preflight`, „Welches Lautheitsziel gilt“
* **Lautheitsziel (LUFS)**: `preflight`, „Welches Lautheitsziel gilt“;
  `command-line`, „Grundlagen“
* **Legende**: `camera-cut`, „Schnittband und Legende lesen“
* **Leveler**: `preflight`, „Welches Lautheitsziel gilt“; `auphonic`, „Ohne
  Auphonic arbeiten“
* **Mindestschnittdauer**: `camera-cut`, „Die Stellschrauben einstellen“
* **Modell (Sprechertrennung)**: `requirements`, „Das Programm holen“;
  `speech`, „Die Sprecher trennen“
* **Mono-Faltung**: `channels`, „Stereo bleibt Stereo“
* **MOV**: `simple-path`, „Warum das Ziel immer MOV ist“
* **Multicam-Clip**: `resolve`, „Wenn Resolve selbst schneiden soll“;
  `resolve`, „Den Multicam-Ton wählen“
* **Node Sizing**: `resolve`, „Position und Zoom für eine ganze Kamera
  setzen“
* **ohne Auphonic arbeiten**: `auphonic`, „Ohne Auphonic arbeiten“
* **Out-Punkt**: siehe In-Punkt
* **Paketverwaltung**: `requirements`, „Woher ffmpeg, PySide6 und numpy
  kommen“
* **Player, Vorschau**: `interface`, „Die vier Reiter“; `camera-cut`, „Wie
  die Vorschau-Player Datei und Ton wählen“
* **Preset**: `auphonic`, „Der Schlüssel und das Preset“; `preflight`, „Was
  geprüft wird“
* **Probelauf**: `interface`, „Die vier Reiter“
* **Projektdatei**: `camera-cut`, „Was die Projektdatei behält“;
  `interface`, „Wie die Zeitachse ohne Timecode entsteht“
* **Protokoll (`videopodcast-magic.log`)**: `interface`, „Die vier Reiter“
* **Prüfzeichen ✓ ! ✕**: `interface`, „Die vier Reiter“; `preflight`, „Was
  geprüft wird“
* **PySide6**: `requirements`, „Woher ffmpeg, PySide6 und numpy kommen“
* **Reaktionsschnitt**: `camera-cut`, „Die Stellschrauben einstellen“
* **Redet mindestens**: `camera-cut`, „Die Stellschrauben einstellen“
* **Renderauftrag**: `resolve`, „Was der Renderauftrag setzt“
* **Rohaufnahme (Pegel)**: `camera-cut`, „Wie die Vorschau-Player Datei und
  Ton wählen“
* **Satzgrenze**: `camera-cut`, „Wie das Programm den Weitwinkel setzt“;
  `speech`, „Wofür der Text gebraucht wird“
* **Schlüsselbund**: `auphonic`, „Der Schlüssel und das Preset“;
  `requirements`, „Was sich je Plattform unterscheidet“
* **Schnittband**: `camera-cut`, „Schnittband und Legende lesen“
* **Source Audio Channels**: `resolve`, „Den Multicam-Ton wählen“
* **Sprecher jetzt messen (Knopf)**: `camera-cut`, „Sprecher ohne Auphonic
  messen“
* **Sprechername**: `multitrack`, „Die Zuordnung setzen“; `speech`, „Die
  Stimmen benennen“
* **Sprechertrennung**: `speech`, „Die Sprecher trennen“
* **`start_s`**: `camera-cut`, „Wie die Vorschau-Player Datei und Ton
  wählen“
* **static-ffmpeg**: `requirements`, „Woher ffmpeg, PySide6 und numpy
  kommen“
* **Stereospur**: `channels`, „Stereo bleibt Stereo“; `preflight`, „Welches
  Lautheitsziel gilt“
* **Stimme**: `speech`, „Die Stimmen benennen“
* **Tasten**: `interface`, „Alles über Menü oder Taste erreichen“
* **Timecode, virtueller**: `interface`, „Wie die Zeitachse ohne Timecode
  entsteht“
* **Transkription**: `auphonic`, „Transkription holen“; `speech`, „Wie das
  Programm den Text mitschreibt“
* **Übergabedatei (`_resolve.json`)**: `camera-cut`, „Was die Projektdatei
  behält“
* **Übersprechen**: `preflight`, „Wie der Bericht das Übersprechen gegen die
  3:1-Regel misst“; `camera-cut`, „Sprecher ohne Auphonic messen“
* **Uhrengang**: `overview`, „Was es einem abnimmt“; `command-line`, „Was
  mit Ton und Bild geschieht“
* **Update**: `interface`, „Sich selbst aktuell halten“
* **Versatz**: `camera-cut`, „Wie die Vorschau-Player Datei und Ton wählen“;
  `simple-path`, „Was neben dem Mix ins Video kommt“
* **Vorflug**: `preflight`, „Was geprüft wird“
* **Vorspann**: `resolve`, „Vorspann und Abspann setzen“
* **Weitwinkel**: `camera-cut`, „Wie das Programm den Weitwinkel setzt“;
  `camera-cut`, „Wie der Schnitt entsteht“
* **Zeitachse**: `interface`, „Wie die Zeitachse ohne Timecode entsteht“;
  `multitrack`, „Was Multitrack tut“
* **Zeitfenster**: `multitrack`, „Das Zeitfenster setzen“
* **Zuordnung**: siehe gehört zu

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

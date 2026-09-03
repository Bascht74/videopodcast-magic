# Changelog

All notable changes to this project are documented in this file. The
format is based on [Keep a Changelog][kac], and the numbers are given
out under [Semantic Versioning][semver].

Every version says everything twice: the English part first, then a
line reading **Deutsch**, then the same in German. The program shows
only the language it is running in.

The versions below 1.0.0-beta carry no date. They were numbered after
the fact, and no reliable release date for them survives.

**Deutsch**

Alle nennenswerten Änderungen an diesem Programm stehen in dieser
Datei. Der Aufbau folgt [Keep a Changelog][kac], die Nummern folgen
[Semantic Versioning][semver].

Jede Version sagt alles zweimal: zuerst der englische Teil, dann eine
Zeile **Deutsch**, dann dasselbe auf Deutsch. Das Programm zeigt nur
die Sprache, in der es läuft.

Die Versionen unter 1.0.0-beta tragen kein Datum. Sie wurden im
Nachhinein nummeriert, ein verlässliches Freigabedatum gibt es zu ihnen
nicht.

## [3.0.0b0] - 2026-09-03

The program file is called `videopodcast_magic.py` from here on, where
it was `videopodcast-magic.py`. There is no second name and no way
back: whoever has the old file fetches the new one or installs it as
below, and whatever calls the file by name -- a shortcut, a script, a
job on a timer -- is written once more.

### Added

- `pip3 install git+https://github.com/Bascht74/videopodcast-magic`
  installs the program now, and the same line with `-U` puts a newer
  one in its place. `videopodcast-magic` then starts it from any
  folder. Fetching the single file by hand works as it did.
- A `SHA256SUMS.txt` hangs beside the program on every release now.
  Whoever downloads the file holds it against that sum and sees that
  what arrived is what was sent.

### Changed

- Nothing is installed unasked any more. Where `PySide6` or `numpy` is
  missing, the program names the Python it would install into and asks
  first; whoever says no gets the line to type by hand.
- The program's own update leaves an installed copy alone. It names the
  folder that copy sits in and says to update it the way it was
  installed.
- In the coloured note over the picture in **Preview player** the
  camera stands on top now and who speaks under it. A speaker's name
  too long for the line is cut at the end rather than at the front, so
  the beginning of the name stays readable.

### Removed

- The program fetches no ffmpeg of its own over pip any more. It looks
  on the search path and beside its own file, offers the package
  manager of the system, and otherwise says where ffmpeg is to be had.
- The program no longer installs past a system's guard over its own
  Python. Where the system refuses, it stops and says so, rather than
  writing into that Python anyway.

### Fixed

- The check for a newer version now says when it could not look at all.
  No network, or a certificate store this Python cannot read, gave the
  same answer as a look that found nothing: no newer version. The
  reason stands on the command line and in the window now.

**Deutsch**

Die Programmdatei heißt ab jetzt `videopodcast_magic.py`, vorher
`videopodcast-magic.py`. Einen zweiten Namen gibt es nicht und einen
Weg zurück auch nicht: Wer die alte Datei hat, holt sich die neue oder
installiert sie wie unten, und was die Datei beim Namen ruft -- eine
Verknüpfung, ein Skript, ein nächtlicher Lauf -- wird einmal
umgeschrieben.

### Hinzugefügt

- `pip3 install git+https://github.com/Bascht74/videopodcast-magic`
  installiert das Programm, dieselbe Zeile mit `-U` holt eine neuere
  Fassung. `videopodcast-magic` startet es danach aus jedem Ordner.
  Die eine Datei von Hand zu holen, geht wie bisher.
- Bei jeder Freigabe hängt ab jetzt eine `SHA256SUMS.txt` neben dem
  Programm. Wer die Datei herunterlädt, hält sie gegen diese Summe und
  sieht, dass angekommen ist, was abgeschickt wurde.

### Geändert

- Ungefragt installiert das Programm nichts mehr. Fehlt `PySide6` oder
  `numpy`, nennt es das Python, in das es installieren würde, und fragt
  vorher; wer nein sagt, bekommt die Zeile zum Selbertippen.
- Die eigene Aktualisierung rührt eine installierte Fassung nicht an.
  Sie nennt den Ordner, in dem die Fassung liegt, und sagt, sie auf
  demselben Weg zu aktualisieren, auf dem sie installiert wurde.
- Im farbigen Feld über dem Bild im **Vorschau Player** steht ab jetzt
  oben die Kamera und darunter, wer spricht. Ein Sprechername, der
  nicht in die Zeile passt, wird hinten gekürzt statt vorn, damit sein
  Anfang lesbar bleibt.

### Entfernt

- Das Programm holt sich kein eigenes ffmpeg mehr über pip. Es sucht im
  Suchpfad und neben der eigenen Datei, bietet die Paketverwaltung des
  Systems an und sagt sonst, woher ffmpeg zu bekommen ist.
- Das Programm installiert nicht mehr an der Sperre vorbei, mit der ein
  System sein eigenes Python schützt. Wehrt sich das System, hält es an
  und sagt das, statt trotzdem hineinzuschreiben.

### Behoben

- Die Prüfung auf eine neuere Fassung sagt jetzt, wenn sie gar nicht
  nachsehen konnte. Ohne Netz, oder wenn Python den Zertifikatsspeicher
  nicht lesen kann, hieß die Antwort bisher: keine neuere Fassung.
  Jetzt steht der Grund dabei, im Fenster wie auf der Kommandozeile.

## [2.32.0-beta] - 2026-09-03

### Added

- The log `videopodcast-magic.log` now says what the program does
  outside itself: every call to ffmpeg and ffprobe with the file it is
  about and how long it took, and the speech recognition and the
  separation the same way. Where a measurement was there already and
  nothing had to be called, that stands in its place.
- The same call repeated stands as one line, with the count and the
  total. The fine measurement after auphonic.com asks for nine short
  stretches out of two files, which used to be twenty lines saying the
  same thing.
- All of it goes into the file only, never into what a run prints. There
  it would land between two progress bars and tear them apart.
- What the window shows in red now stands in the log as well, with the
  time of day: a warning box, a red line under a box, a red mark on a row
  of the file list. A red mark is gone the moment that row is drawn
  again, and the complaint about it arrives hours later.

### Changed

- The channels of a recording are measured once now, and what was
  measured outlives the program. Reading every channel of a file right
  through takes 20 to 50 seconds on an hour of material, and until now
  every start did it again -- opening the same project a second time cost
  the same wait as the first. A file that has changed is measured afresh.
- The heading over the speaker figures on the **Resolve cut** tab now
  carries the speech time and, behind it, the note that people talking at
  once are counted twice. The line that said so under the table is gone,
  and the table has that row back.
- The line about Resolve on the **Resolve cut** tab now shows only where
  Resolve does not answer, and it names the way to the settings. Where
  Resolve answers there is nothing to set up, and the row goes to the
  rest of the tab.

### Fixed

- An intro or an outro now plays its own sound in the preview, with
  **hear assigned audio** ticked as well. No speaker is assigned to it,
  so the rule for the wide shot took hold and the full mix of the episode
  ran under it, laid on an axis it is not on: an intro stands before the
  episode and an outro after it, not inside it.
- The warning about a weak match now names the file it is about. With
  several recordings the log held a heap of warnings nobody could put
  back against a file -- and each of them says two files may not belong
  together.
- A camera whose sound gives nothing to read no longer ends the run. One
  reporting a track with nothing in it stopped it on the first line, and
  where it was the longest every other camera was measured against it.
  The reference is now the longest that can be measured against; the
  silent one is placed by its clock and named.

### Tests

- A test holds the log to what it promises: that every call is written
  down, that repeated ones are summed up, that none of it reaches the
  output of a run, and that the channel measurement really is read back
  in a second process instead of measured again.
- Another prints the table of the program's own sections at every run
  -- how long each is, how many names it takes from elsewhere and how
  many it hands out. It holds one of them: the ground section takes
  nothing from above it.

**Deutsch**

### Hinzugefügt

- Das Protokoll `videopodcast-magic.log` sagt jetzt, was das Programm
  ausserhalb von sich tut: jeden Aufruf von ffmpeg und ffprobe mit der
  Datei, um die es geht, und mit seiner Dauer -- Spracherkennung und
  Sprechertrennung ebenso. Wo eine Messung schon vorlag und nichts
  aufgerufen werden musste, steht das an ihrer Stelle.
- Derselbe Aufruf mehrfach steht als eine Zeile, mit Anzahl und Summe.
  Die feine Nachmessung nach auphonic.com holt neun kurze Stellen aus
  zwei Dateien -- das waren zwanzig Zeilen mit demselben Inhalt.
- Das alles steht nur in der Datei, nie in dem, was ein Lauf ausgibt.
  Dort landete es zwischen zwei Fortschrittsbalken und zerriss sie.
- Was das Fenster rot zeigt, steht jetzt auch im Protokoll, mit der
  Uhrzeit: ein Warnfenster, eine rote Zeile unter einem Kasten, eine rote
  Marke an einer Zeile der Dateiliste. Eine rote Marke ist weg, sobald
  die Zeile neu gezeichnet wird, und die Beschwerde darüber kommt Stunden
  später.

### Geändert

- Die Messung, die die Kanäle einer Aufnahme beurteilt, läuft jetzt
  einmal und überdauert das Programm. Sie liest jeden Kanal einer Datei
  ganz durch; bei einer Stunde Material sind das 20 bis 50 Sekunden, und
  bisher fielen die bei jedem Start wieder an -- auch beim zweiten Öffnen
  desselben Projekts. Eine geänderte Datei wird neu gemessen.
- Die Überschrift über den Sprecherzahlen auf dem Reiter
  **Resolve-Schnitt** trägt jetzt die Sprechzeit und dahinter den
  Hinweis, dass gleichzeitig Redende doppelt zählen. Die Zeile, die das
  unter der Tabelle sagte, ist weggefallen, und die Tabelle hat die Zeile
  wieder.
- Die Zeile über Resolve auf dem Reiter **Resolve-Schnitt** erscheint nur
  noch, wenn Resolve nicht antwortet, und nennt dann den Weg zu den
  Einstellungen. Antwortet Resolve, ist ohnehin nichts einzustellen, und
  die Zeile gehört dem übrigen Reiter.

### Behoben

- Ein Vorspann oder ein Abspann spielt in der Vorschau jetzt seinen
  eigenen Ton, auch bei gesetztem Häkchen **zugeordneten Ton hören**. Ihm
  ist kein Sprecher zugeordnet, also griff die Regel für den Weitwinkel
  und die Gesamtmischung der Folge lief darunter -- auf einer Zeitachse,
  auf der er nicht steht: Ein Vorspann steht vor der Folge, ein Abspann
  dahinter, nicht darin.
- Die Warnung über eine schwache Übereinstimmung nennt jetzt die Datei,
  um die es geht. Bei mehreren Aufnahmen stand im Protokoll ein Haufen
  Warnungen, den niemand einer Datei zuordnen konnte -- und jede davon
  sagt, dass zwei Dateien womöglich nicht zusammengehören.
- Eine Kamera, deren Ton nichts hergibt, beendet den Lauf nicht mehr.
  Eine, die eine Tonspur meldet und nichts herausgibt, brach ihn in der
  ersten Zeile ab -- und war sie die längste, wurde an ihr gemessen.
  Bezugskamera ist jetzt die längste, an der sich messen lässt; die
  stumme wird nach ihrer Uhr eingeordnet und genannt.

### Tests

- Eine Pruefung haelt das Protokoll an sein Versprechen: dass jeder
  Aufruf aufgeschrieben wird, dass sich wiederholende zusammengefasst
  werden, dass nichts davon in die Ausgabe eines Laufs gelangt, und
  dass die Kanalmessung im zweiten Prozess wirklich gelesen statt neu
  gemessen wird.
- Eine zweite druckt bei jedem Lauf die Tabelle der Abschnitte des
  Programms: wie lang jeder ist, wie viele Namen er von anderswo holt
  und wie viele er hinausgibt. Einen Punkt haelt sie fest -- der
  Unterbau holt sich nichts von oberhalb.

## [2.31.1-beta] - 2026-09-03

### Changed

- The summary before **Start** now says what follows where nobody has a
  camera of their own: every shot then goes to the same camera. It named
  those speakers already; what would become of the cut it did not say,
  and that is worth knowing before the hours of computing.

### Fixed

- Changing the camera while the picture runs now holds the moment. A
  freshly opened file falls back to its front after it has reported
  itself loaded -- 18 to 88 milliseconds later, never twice the same --
  and the one jump to the moment had been made before that, so the
  switch landed at the beginning of the file instead. It is asked for
  again until it sits.
- A file the player refuses no longer costs the picture. The refusal
  stopped the player, the player loaded again and played again, and that
  raised the refusal again -- 2590 times in two seconds, the surface
  black throughout. It is said once per file now, and the picture stays.
- Which camera a recording belongs to now follows the name the run works
  with. Only the name field was asked, and a name merely offered in grey
  leaves it empty, so whoever did not type over the suggestion got **no
  camera of its own** on every recording -- no camera then carried a
  speaker, and a whole episode was cut on a single one.
- A speaker finds their camera where the file name carries the number a
  device counted it with. `Presenter00018` was held against the camera's
  name with that number still on it and matched nothing. The
  digits a recorder or a camera counts its files with are left out of
  the comparison now.
- The name of a written camera file no longer says a name twice, and no
  longer tears a camera's name in half. The speakers go in front of the
  number the camera counts its files with; where there is no such
  number the camera's name stays whole and the speakers go behind it,
  and where the camera already carries those names they are not said
  again.
- The three speech-time shares under **Camera cut -- preview** now count
  every speaker, with a camera of their own or without. Only those who
  had one were counted, so where nobody had one the line read 0.0 %
  three times -- which reads as a quiet episode and is the loudest case
  there is.
- The Timeline start is read back now. Where DaVinci Resolve did not
  take it, the Timeline kept the 01:00:00:00 a new one is born with and
  a whole episode sat fifteen hours inside it, without a word. The run
  prints the start it set, and says so where the Timeline answers with
  another one.
- The timecode written into a camera file comes out of the measurement
  now. It was the camera's own clock moved by what had been cut off the
  front -- half the one reckoning, half the other -- so two cameras
  ended up sixteen frames away from the place the handover gives them.
  All of them are counted from one moment now, so the files agree.
- The preview of the camera cut now shows the shots the run makes. Where
  one camera shows everybody, the run cuts again at every change of
  speaker; the preview did not, and reported a single shot over a whole
  programme where the run made 237.
- A project carrying an Auphonic preset now fetches the preset list when
  it is opened. The list was fetched only when somebody opened the box,
  so the preset had no list to stand in and the box fell back to **work
  without Auphonic**. Until the answer is there the box names the preset
  with **being checked** behind it, and a run before that spends nothing.

### Tests

- The checks that build a real project in DaVinci Resolve run after a
  plain start of Resolve now. All four used to stand aside while Resolve
  was on the untitled project it opens with, which is the state after
  every start. Three of them run there now; the fourth needs a project
  of somebody's own, since what it checks is that a run gives it back.

**Deutsch**

### Geändert

- Die Zusammenfassung vor **Start** sagt jetzt auch, was folgt, wenn
  niemand eine eigene Kamera hat: dann geht jede Einstellung auf
  dieselbe Kamera. Die Namen standen schon da; was daraus für den
  Schnitt wird, stand nicht dabei -- und das will man wissen, bevor die
  Stunden Rechenzeit anfangen.

### Behoben

- Der Kamerawechsel bei laufendem Bild hält jetzt die Stelle. Eine
  frisch geöffnete Datei fällt auf ihren Anfang zurück, nachdem sie sich
  als geladen gemeldet hat -- 18 bis 88 Millisekunden später und nie
  zweimal gleich --, und der eine Sprung war da schon getan: der
  Wechsel landete also am Anfang der Datei. Er wird jetzt so lange
  nachgefragt, bis er sitzt.
- Eine Datei, die der Abspieler ablehnt, kostet nicht mehr das Bild. Die
  Absage hielt ihn an, er lud neu und spielte wieder, und das löste die
  Absage erneut aus -- 2590 Mal in zwei Sekunden, und die Fläche blieb
  schwarz. Gesagt wird es jetzt einmal je Datei, und das Bild bleibt.
- Zu welcher Kamera eine Aufnahme gehört, richtet sich jetzt nach dem
  Namen, mit dem der Lauf arbeitet. Gefragt war nur das Namensfeld, und
  ein bloß grau angebotener Name lässt es leer: wer den Vorschlag nicht
  übertippte, bekam bei jeder Aufnahme **ohne eigene Kamera** -- dann
  trug keine Kamera einen Sprecher, und eine ganze Folge saß im Schnitt
  auf einer einzigen.
- Ein Sprecher findet seine Kamera jetzt auch dort, wo der Dateiname
  die Zählnummer des Geräts trägt. `Presenter00018` wurde mitsamt dieser
  Nummer gegen den Kameranamen gehalten und traf nichts. Die Ziffern,
  mit denen ein Aufnahmegerät oder eine Kamera ihre Dateien durchzählt,
  bleiben beim Vergleich außen vor.
- Der Name einer geschriebenen Kameradatei nennt jetzt keinen Namen
  mehr doppelt und zerreißt keinen Kameranamen mehr. Die Sprecher
  kommen vor die Zählnummer der Kamera; gibt es keine, bleibt der
  Kameraname ganz und die Sprecher stehen dahinter, und heißt die
  Kamera ohnehin nach ihnen, werden sie kein zweites Mal genannt.
- Die drei Anteile der Redezeit unter **Kameraschnitt -- Vorschau**
  zählen jetzt jeden Sprecher, mit eigener Kamera wie ohne. Gezählt
  wurden nur die mit einer, also stand dort dreimal 0,0 %, wo niemand
  eine hatte -- das liest sich wie eine stille Folge und ist der
  lauteste Fall, den es gibt.
- Der Anfang der Timeline wird jetzt nachgelesen. Nahm DaVinci Resolve
  ihn nicht an, blieb die Timeline bei den 01:00:00:00, mit denen eine
  neue anfängt, und eine ganze Folge saß fünfzehn Stunden darin, ohne
  ein Wort. Der Lauf schreibt den gesetzten Anfang jetzt auf und sagt
  es, wenn die Timeline einen anderen nennt.
- Der Timecode, der in eine Kameradatei geschrieben wird, kommt jetzt
  aus der Messung. Bisher war es die Uhr der Kamera, verschoben um den
  Beschnitt vorn -- halb die eine Rechnung, halb die andere --, und zwei
  Kameras lagen dadurch sechzehn Bilder neben dem Platz, den die
  Übergabe für sie nennt. Jetzt wird jeder von einem einzigen
  Augenblick aus gezählt, und die Dateien stimmen untereinander.
- Die Vorschau des Kameraschnitts zeigt jetzt die Einstellungen, die der
  Lauf macht. Zeigt eine Kamera alle, schneidet der Lauf noch einmal an
  jedem Sprecherwechsel; die Vorschau tat das nicht und meldete eine
  einzige Einstellung über eine ganze Sendung, wo der Lauf 237 machte.
- Ein Projekt, das ein Auphonic-Preset mitbringt, holt die Presetliste
  jetzt beim Öffnen selbst. Bisher kam sie nur, wenn jemand den Kasten
  aufklappte -- das Preset fand also nichts, worin es hätte stehen
  können, und der Kasten fiel auf **ohne Auphonic arbeiten** zurück. Bis
  die Antwort da ist, nennt der Kasten das Preset mit **wird geprüft**
  dahinter, und ein Lauf davor kostet nichts.

### Tests

- Die Prüfungen, die ein echtes Projekt in DaVinci Resolve bauen, laufen
  jetzt auch nach einem frischen Start von Resolve. Alle vier ließen
  sich aus, solange Resolve auf dem unbenannten Projekt stand, mit dem
  es aufmacht -- also nach jedem Start. Drei laufen dort jetzt; die
  vierte braucht ein eigenes Projekt, denn sie prüft, dass ein Lauf es
  zurückgibt.

## [2.31.0-beta] - 2026-09-03

### Added

- Both players now write down what they do in
  `videopodcast-magic.log`, on lines marked `[GUI]`: which file was
  loaded and at what point, every play and every pause, and which
  recording was laid under which picture, out of which of the two
  reckonings. Those are the lines to send along with a complaint about
  the preview.

### Changed

- A camera now reaches DaVinci Resolve at the place its sound was
  measured, and at its own timecode only where nothing could be found in
  the sound. Cameras run on a shared clock only if somebody set them to
  one, and even that is a frame or two out. The run names every camera
  it had to place by the clock alone.
- The time axis is now measured as soon as two files are in the list,
  with a timecode or without. It used to be left out where every file
  carried a clock, and the preview then showed a different film from the
  one the run made. Material that used to skip the measurement now waits
  for it once.
- An episode has one intro and one outro, so while a file holds either
  mark, that entry is greyed out on every other file and names the file
  holding it. Choosing it a second time used to take the mark off the
  first file without a word.
- The full mix is called `Full-Mix` in the plan the run prints, the same
  name the written track carries. It used to be listed with its
  ingredients in brackets behind it, so the plan and Resolve named one
  track two ways.

### Removed

- The button "Measure speakers now" is gone. The speakers are worked out
  as soon as the "Resolve cut" tab is opened, which is the moment they
  are wanted -- and not a second time while one reading is running, nor
  after one failed, nor where a finished run already knows them.

### Fixed

- The assigned recording now runs with the picture in the preview
  player. Where the picture stood came out of one clock and where the
  recording began out of another, and the difference between the two
  stayed in the answer: on real material the sound ran 2.35 seconds
  ahead of the picture. Both ends of that sum come out of one reckoning
  now.
- The column "Timecode" now shows the same thing at every file: the
  measured place, with "computed" behind it. A file with a clock of its
  own showed that clock while all the others showed the measurement, so
  one column carried two reckonings and its numbers could not be
  compared.
- A recording written in two files now plays through in the preview
  player. The player knew only the first file and went silent at the
  boundary with no word; it moves on to the next part now, and keeps quiet
  where the recording is not due yet rather than sounding its beginning
  under a picture it does not belong to.
- A recording written in two files is no longer thrown out of the run
  because of its second part. Every part was placed on the time axis on
  its own, so a tail of seven minutes that fitted nowhere refused a
  recording of over an hour whose first part sat on the axis to the
  millisecond. Both parts are one recording now.
- The window no longer measures the whole material over and over on its
  own. Two files that fit nowhere pushed each other back and forth
  between "Intro" and "Wide shot", and every turn set the measurement
  going again -- 170 full measurements in twenty seconds. The measuring
  now starts only where the material has changed.
- A file the player cannot open no longer costs the picture of every
  file after it. The refusal hid the picture and nothing ever brought it
  back, so the next file played its sound with nothing to see. The
  refusal is taken back as soon as frames arrive.
- A camera now keeps its name and its measured place where the same file
  reaches the run written two ways. The lookup settled the folder and
  not the spelling, so the camera rendered under the bare file name and
  its offset fell back to the start of the axis. On Windows a single
  capital letter was enough, and the picture then stood 7.5 seconds
  beside its place.
- The preset now stands in the box again after a project is reopened. It
  was written into the project file correctly but applied before
  "Multitrack" was switched on, and a multitrack preset is not in the
  list in the other mode -- so the box fell back to "work without
  Auphonic".
- Opening a second project no longer brings the speakers of the first
  one along. They stayed in hand across the change, so the cut preview
  of the new material was built out of the old material's voices. They
  are worked out again now.

**Deutsch**

### Hinzugefügt

- Beide Abspieler schreiben jetzt in `videopodcast-magic.log`
  mit, was sie tun; ihre Zeilen tragen vorn `[GUI]`. Darin steht, welche
  Datei geladen wurde und an welcher Stelle, jedes Abspielen und jede
  Pause, und welche Aufnahme aus welcher Rechnung unter welches Bild
  gelegt wurde. Wer sich über die Vorschau beschwert, schickt diese
  Zeilen mit.

### Geändert

- Eine Kamera kommt jetzt an der Stelle nach DaVinci Resolve, an der ihr
  Ton gemessen wurde; ihr eigener Timecode zählt nur noch dort, wo im
  Ton nichts zu finden war. Kameras laufen nur auf einer gemeinsamen
  Uhr, wenn jemand sie darauf gestellt hat, und auch die geht ein, zwei
  Bilder daneben. Der Lauf nennt jede Kamera, die er allein nach der Uhr
  setzen musste.
- Die Zeitachse wird jetzt gemessen, sobald zwei Dateien in der Liste
  stehen -- mit Timecode wie ohne. Bisher unterblieb die Messung, wenn
  jede Datei eine Uhr trug; die Vorschau zeigte einen anderen Film als
  den, den der Lauf machte. Material, das die Messung bisher übersprang,
  wartet jetzt einmal darauf.
- Vorspann und Abspann gibt es in einer Folge je einmal. Solange eine
  Datei die Marke hält, ist der Eintrag bei jeder anderen grau und nennt
  die Datei, die ihn hält. Bisher nahm die zweite Wahl der ersten Datei
  die Marke stillschweigend wieder ab.
- Die Gesamtmischung heißt im Laufplan `Full-Mix`, genau wie die
  geschriebene Spur. Bisher standen ihre Zutaten in Klammern dahinter,
  und Laufplan und Resolve nannten dieselbe Spur verschieden.

### Entfernt

- Der Schalter „Sprecher jetzt messen“ ist fort. Die Sprecher werden
  ermittelt, sobald der Reiter „Resolve-Schnitt“ aufgeht -- in dem
  Augenblick also, in dem man sie braucht. Nicht ein zweites Mal,
  während eine Messung läuft, nicht nach einer gescheiterten, und nicht
  dort, wo ein fertiger Lauf sie schon kennt.

### Behoben

- Die zugeordnete Aufnahme läuft im Vorschau-Abspieler jetzt mit dem
  Bild. Wo das Bild stand, kam aus der einen Uhr, wo die Aufnahme
  anfing, aus einer anderen, und ihr Unterschied blieb im Ergebnis
  stehen: an echtem Material lief der Ton dem Bild um 2,35 Sekunden
  voraus. Beide Enden dieser Rechnung kommen jetzt aus derselben Quelle.
- In der Spalte „Timecode“ steht jetzt bei jeder Datei dasselbe: der
  gemessene Platz, mit „errechnet“ dahinter. Eine Datei mit eigener Uhr
  zeigte deren Wert, alle übrigen den gemessenen -- zwei Zeitrechnungen
  in einer Spalte, deren Zahlen sich nicht vergleichen ließen.
- Eine Aufnahme aus zwei Dateien läuft im Vorschau-Abspieler jetzt
  durch. Der Abspieler kannte nur die erste Datei und verstummte an der
  Grenze, ohne ein Wort; jetzt schaltet er weiter -- und er
  schweigt, wo die Aufnahme noch gar nicht dran ist, statt ihren Anfang
  unter ein Bild zu legen, zu dem er nicht gehört.
- Eine Aufnahme aus zwei Dateien fliegt nicht mehr wegen ihres zweiten
  Teils aus dem Lauf. Jeder Teil kam einzeln auf die Zeitachse, also
  verwarf ein Schwanz von sieben Minuten, für den sich kein Platz fand,
  eine Aufnahme von über einer Stunde, deren erster Teil auf die
  Millisekunde genau lag. Beide Teile sind jetzt eine Aufnahme.
- Das Fenster misst das ganze Material nicht mehr von selbst immer
  wieder neu. Zwei Dateien ohne Platz schoben einander hin und her
  zwischen „Vorspann“ und „Weitwinkel“, und jede Runde stieß die Messung
  erneut an -- 170 vollständige Messungen in zwanzig Sekunden. Gemessen
  wird jetzt nur noch, wo sich das Material geändert hat.
- Eine Datei, die der Abspieler nicht öffnen kann, kostet nicht mehr das
  Bild aller folgenden. Die Absage verdeckte das Bild, und nichts holte
  es je zurück -- die nächste Datei spielte dann ihren Ton, ohne dass
  etwas zu sehen war. Die Absage wird jetzt zurückgenommen, sobald
  Bilder ankommen.
- Eine Kamera behält jetzt ihren Namen und ihren gemessenen Platz, auch
  wenn derselbe Pfad den Lauf in zwei Schreibweisen erreicht. Das
  Nachschlagen klärte den Ordner, nicht die Schreibweise: die Kamera
  wurde unter dem nackten Dateinamen gerendert, und ihr Versatz fiel auf
  den Anfang der Achse zurück. Unter Windows genügte dafür ein einziger
  Großbuchstabe, und das Bild stand 7,5 Sekunden neben seinem Platz.
- Nach dem Wiederöffnen eines Projekts steht das Preset jetzt wieder im
  Kasten. Es kam richtig in die Projektdatei, wurde aber angewandt,
  bevor „Multitrack“ eingeschaltet war -- und im anderen Modus steht ein
  Multitrack-Preset gar nicht in der Liste, also fiel der Kasten auf
  „ohne Auphonic arbeiten“ zurück.
- Öffnet man ein zweites Projekt, kommen die Sprecher des ersten nicht
  mehr mit. Sie blieben über den Wechsel hinweg stehen, und so entstand
  die Schnittvorschau des neuen Materials aus den Stimmen des alten. Sie
  werden jetzt neu ermittelt.

## [2.30.0-beta] - 2026-09-02

### Added

- Where the microphones hear each other too well to be told apart, the
  speaker separation now listens to all of them at once and names each
  voice after its microphone. On material whose speakers are known to
  the millisecond, the speech under the right name went from 72.5 to
  92.7 per cent. Only on a run without auphonic.com, where the tracks
  still bleed.
- A recording with a steady tone over it -- a hum, an air conditioner --
  now finds its place on the time axis. Where the shape of the sound
  says nothing, the run compares it once more on the frequency bands
  that do move: with a hum 40 dB over the material the old way missed by
  more than half an hour, the new one finds it to three hundredths of a
  second.

### Changed

- Every speaker separation already stored on this machine is measured
  again on the first run after this version. How the voices are worked
  out has changed, so a stored answer no longer belongs to the way it
  would be worked out now. It costs minutes of the graphics unit per
  recording, once.

### Fixed

- A run started from the window now reaches the joined recording too. It
  took over whatever separation the window had already made, so the
  case that joining was built for never arose there and the speech under
  the right name stayed at 37.5 per cent.
- A handover trimmed after it was written now moves its timecode along
  with the seconds. Only the seconds moved, and DaVinci Resolve places from
  the timecode alone -- every picture landed off by the trimmed head,
  measured ten seconds.
- Two shots merged into one now name every speaker heard in them. The
  survivor kept its own names, so somebody who spoke for ten seconds on
  the same camera vanished from the "Speaker" column of the cut list and
  from the clip name in the EDL.
- Two names at one camera now stand in the same order everywhere. The
  preview sorted them and the run put the recordings first, and it is
  the run that writes the track name in Resolve.
- The log now says which of the three ways placed a recording, and how
  sharp
  a find by phase was. On the run with no picture it named no way at
  all, and a track placed by phase showed a drift of "+0.00 ppm" where
  the drift is in truth unknown.
- The buttons under the run now stand on one line, and "Dry run" shows
  what it is for while it is still switched off.

**Deutsch**

### Hinzugefügt

- Hören die Mikrofone einander zu gut, um die Stimmen auseinanderhalten
  zu können, hört die Sprechertrennung jetzt allen Mikrofonen zugleich zu
  und benennt jede Stimme nach ihrem Mikrofon. Bei Material, dessen
  Sprecher auf die Millisekunde bekannt sind, stieg die richtig benannte
  Rede von 72,5 auf 92,7 Prozent. Das gilt nur für einen Lauf ohne
  auphonic.com, bei dem die Spuren noch ineinanderlaufen.
- Eine Aufnahme, über der ein gleichbleibender Ton liegt -- ein Brummen,
  eine Klimaanlage --, findet jetzt ihren Platz auf der Zeitachse. Wo die
  Form des Klangs nichts hergibt, vergleicht der Lauf noch einmal, nur
  auf den Frequenzbändern, die sich bewegen: bei einem Brummen 40 dB über
  dem Material verfehlte der alte Weg den Platz um mehr als eine halbe
  Stunde, der neue trifft ihn auf drei Hundertstelsekunden genau.

### Geändert

- Jede Sprechertrennung, die schon auf diesem Rechner liegt, wird beim
  ersten Lauf nach dieser Fassung neu gemessen. Wie die Stimmen ermittelt
  werden, hat sich geändert; ein gespeichertes Ergebnis passt deshalb
  nicht mehr zu dem, was jetzt herauskäme. Das kostet einmalig einige
  Minuten Rechenzeit auf der Grafikkarte je Aufnahme.

### Behoben

- Auch ein Lauf, der aus dem Fenster gestartet wird, kommt jetzt zur
  zusammengelegten Aufnahme. Bisher übernahm er die Trennung, die das
  Fenster schon gemacht hatte; der Fall, für den das Zusammenlegen gebaut
  ist, trat dort also nie ein, und die richtig benannte Rede blieb bei
  37,5 Prozent.
- Eine Übergabedatei, die nachträglich beschnitten wird, zieht jetzt
  ihren Timecode mit. Bisher wanderten nur die Sekunden, und DaVinci
  Resolve richtet sich allein nach dem Timecode -- jedes Bild landete um
  den abgeschnittenen Kopf versetzt, gemessen zehn Sekunden.
- Zwei Einstellungen, die zu einer zusammengelegt werden, nennen jetzt
  jeden, der darin zu hören ist. Bisher behielt die verbleibende nur ihre
  eigenen Namen, und wer zehn Sekunden auf derselben Kamera sprach, fehlte
  in der Spalte „Speaker" der Schnittliste und im Clipnamen der EDL.
- Zwei Namen an einer Kamera stehen jetzt überall in derselben
  Reihenfolge. Die Vorschau sortierte sie, der Lauf stellte die Aufnahmen
  nach vorn -- und der Lauf ist es, der den Spurnamen in Resolve schreibt.
- Das Protokoll sagt jetzt, auf welchem der drei Wege eine Aufnahme
  gesetzt wurde und wie sicher ein Fund über die Phase war. Beim Lauf
  ohne Bild nannte es gar keinen Weg, und eine über die Phase gesetzte
  Spur zeigte eine Drift von „+0,00 ppm", obwohl die Drift dort
  unbekannt ist.
- Die Schalter unter dem Lauf stehen jetzt in einer Zeile, und
  „Probelauf" sagt auch im abgeschalteten Zustand, wofür er da ist.

## [2.29.0-beta] - 2026-09-02

### Added

- A selector "Nobody speaks" beside "Recognition uncertain", with the
  field "Short gap up to" at one second. Silence went to the wide shot
  with no choice. The default stays the wide shot.

### Fixed

- A file added while the time axis is being measured is now measured
  too. The request used to be dropped and nobody picked it up.
- Removing a file now reaches the saved project. The recording stayed in
  it, and one added again later was silently "Intro" once more.
- Where auphonic.com refuses the key, "work without Auphonic" is no
  longer written into the project as a decision. It came back at every
  opening, long after the key was good again.
- The key that was checked is now the key that is stored. The field was
  read a second time when the answer arrived.
- The complaint about a refused key now names where the value came from,
  the environment or the store. It blamed the store either way.
- Three notes that broke off in the middle of a word now break into
  lines: in the file column, at the colour hint, under the player.
- The name of the camera file now takes the speaker even where the name
  was only proposed and never typed. It went to Resolve without it.
- The reference camera no longer reports a measurement it cannot make.
  It is the reference; there is nothing to measure against.
- The speech recognition now says what it did in a sentence, in the
  language of the run and with that language's decimal mark.

**Deutsch**

### Hinzugefügt

- Ein Auswahlfeld „Niemand redet" neben „Erkennung unsicher", dazu das
  Feld „Kurze Lücke bis" mit einer Sekunde. Bei Stille ging der Schnitt
  bisher in den Weitwinkel, und man hatte keine Wahl. Vorgabe bleibt der
  Weitwinkel.

### Behoben

- Eine Datei, die während der Messung der Zeitachse dazukommt, wird jetzt
  mitgemessen. Bisher wurde die Anfrage fallengelassen, und niemand holte
  sie nach.
- Wird eine Datei entfernt, verschwindet sie jetzt auch aus der
  gespeicherten Projektdatei. Bisher blieb sie darin stehen, und eine
  später wieder hinzugefügte hieß wortlos erneut „Vorspann".
- Lehnt auphonic.com den Schlüssel ab, wird „ohne Auphonic arbeiten"
  nicht mehr als Entscheidung ins Projekt geschrieben. Sie kam bei jedem
  Öffnen zurück, lange nachdem der Schlüssel wieder gut war.
- Geprüft und gespeichert wird jetzt derselbe Schlüssel. Bisher wurde das
  Feld ein zweites Mal gelesen, sobald die Antwort eintraf.
- Die Meldung über einen abgelehnten Schlüssel nennt jetzt, woher der
  Wert kam: aus der Umgebung oder aus dem Speicher. Bisher schob sie es
  immer auf den Speicher.
- Drei Hinweise, die mitten im Wort abbrachen, brechen jetzt um: in der
  Dateispalte, bei der Farbkennung, unter dem Player.
- Der Name der Kameradatei trägt den Sprecher jetzt auch dort, wo dieser
  Name nur vorgeschlagen und nie getippt wurde. Bisher ging die Datei
  ohne ihn nach Resolve.
- Die Referenzkamera meldet keine Messung mehr, die es bei ihr gar nicht
  gibt. Sie ist die Referenz; es gibt nichts, wogegen sie zu messen
  wäre.
- Die Spracherkennung sagt jetzt in einem Satz, was sie getan hat -- in
  der Sprache des Laufs und mit deren Dezimalzeichen.

## [2.28.0-beta] - 2026-09-02

### Added

- A Timecode as In point or Out point works even where the reference
  camera carries no clock of its own. The axis is hung on the clocks of
  the files that do have one, and the run says which those were and what
  the reference camera's first frame reads. Before, such a project could
  not be started at all.
- "Create Resolve project" can be pressed after opening a project whose
  output folder holds the handover of an earlier run. The note on that
  sheet had been offering this way for a while; now the button follows.

### Changed

- The column "belongs to" is there with and without "Multitrack". Which
  camera a recording belongs to decides the cut, not the number of
  delivered tracks, and the run has never needed the tick for it.
- After a run, the cut preview shows the speakers the run measured and
  says so in its heading. It used to work them out again from the raw
  recordings and could arrive at a different film.

### Removed

- The button "Measure speakers now" is gone where a run's measurement is
  in hand. There it could change nothing, because the run's result wins
  anyway.

### Fixed

- A click on "Multitrack" cleared every camera assignment made by hand,
  in both directions, and wrote "no camera of its own" into the project.
  From then on no camera had a speaker, so every camera was the wide shot
  and "Content" could not be chosen any more. The tick now leaves the
  assignment alone.
- Where saving the API key failed, the box stayed ticked, the button went
  green, and the key was gone at the next start -- the refusal deleted the
  key that was already there. The box now takes itself back and says what
  the store answered.
- The cut preview counted more minutes than the timeline is long: 1080
  seconds over a window of 600. It counts once per moment of the timeline
  now, not once per speaker.
- The note on a file whose frame count and track duration disagree said
  picture and camera sound drift apart. Measured, they do not. It now
  names the rate, and that an editing program leaves out about one frame
  every so many seconds.
- The camera sound was read from a different moment than its picture
  begins, where a file says its audio track starts late. The cut then
  carried the sound ahead of the picture -- measured, 1.4 frames on one
  camera. The track's own start is read out of the file now.

**Deutsch**

### Hinzugefügt

- Ein Timecode als In- oder Out-Punkt geht auch dort, wo die
  Referenzkamera keine eigene Uhr trägt. Die Achse hängt dann an den
  Uhren der Dateien, die eine haben, und der Lauf nennt sie und sagt,
  worauf das erste Bild der Referenzkamera steht. Vorher ließ sich ein
  solches Projekt gar nicht starten.
- „Resolve-Projekt anlegen" lässt sich drücken, nachdem ein Projekt
  geöffnet wurde, in dessen Ausgabeordner die Übergabedatei eines
  früheren Laufs liegt. Der Hinweis auf diesem Reiter bot den Weg schon
  an; jetzt folgt ihm der Knopf.

### Geändert

- Die Spalte „gehört zu" gibt es jetzt mit und ohne „Multitrack". Über
  den Schnitt entscheidet, zu welcher Kamera eine Aufnahme gehört, und
  nicht die Zahl der abgelieferten Spuren; den Haken hat der Lauf dafür
  nie gebraucht.
- Nach einem Lauf zeigt die Schnittvorschau die Sprecher, die der Lauf
  gemessen hat, und sagt das in ihrer Überschrift. Vorher rechnete sie
  die Sprecher aus den Rohaufnahmen neu und kam dabei auf einen anderen
  Film.

### Entfernt

- Den Knopf „Sprecher jetzt messen" gibt es nicht mehr, wo die Messung
  eines Laufs vorliegt. Dort konnte er nichts ändern, weil ohnehin das
  Ergebnis des Laufs gilt.

### Behoben

- Ein Klick auf „Multitrack" löschte jede von Hand gesetzte
  Kamerazuordnung, in beide Richtungen, und schrieb „ohne eigene Kamera"
  ins Projekt. Danach hatte keine Kamera mehr einen Sprecher, also war
  jede Kamera Weitwinkel und „Inhalt" nicht mehr wählbar. Der Haken lässt
  die Zuordnung jetzt stehen.
- Wo das Speichern des API-Schlüssels fehlschlug, blieb der Haken
  gesetzt, der Knopf wurde grün, und beim nächsten Start war der
  Schlüssel weg -- die Ablehnung löschte den, der schon da war. Der Haken
  nimmt sich jetzt selbst zurück und sagt, was der Speicher geantwortet
  hat.
- Die Schnittvorschau zählte mehr Minuten, als die Zeitleiste lang ist:
  1080 Sekunden in einem Fenster von 600. Sie zählt jetzt je Augenblick
  der Zeitleiste, nicht je Sprecher.
- Der Hinweis zu einer Datei, deren Bildzahl und Spurdauer auseinander
  liegen, sagte, Bild und Kameraton liefen auseinander. Gemessen tun sie
  das nicht. Er nennt jetzt die Rate und sagt, in welchem Abstand ein
  Schnittprogramm ein Bild weglässt.
- Sagt eine Datei, dass ihre Tonspur später anfängt, wurde der Kameraton
  von einer anderen Stelle an gelesen als der, an der sein Bild beginnt.
  Der Ton lief dem Bild dann voraus -- gemessen 1,4 Bilder bei einer
  Kamera. Der eigene Anfang der Spur wird jetzt aus der Datei gelesen.

## [2.27.0-beta] - 2026-09-02

### Added

- A camera whose frame rate Resolve has no timeline for is used all the
  same: the timeline takes the next rate Resolve does have, and the
  camera keeps its own. Measured, a 15 fps file sits in a 30 fps timeline
  to within half a frame.
- The chooser "belongs to" greys out a recording whose clock is hours
  away from the one it would join, and says how far apart they are.
  Joined by hand, that difference went into the file as silence: 40
  seconds of sound became 5.95 GB and the speaker was gone.

### Changed

- Where the sound of a file could not be matched, the note used to say
  only that it does not fit the others. It now says which of the two
  ways to a place still holds: "sound not recognised; placed by its
  timecode", or that neither does and the sound cannot be used.

### Fixed

- A camera could be marked as fitting none of the others although the
  measurement had found it. The test for a trustworthy reading now uses
  two numbers that were already measured and thrown away, and those
  separate every one of 378 pairs correctly.
- The preview dropped files the run kept, so the cut band showed one
  camera fewer than the finished project. Both now ask the same
  question.
- A camera whose sound was not recognised is allowed to be the source of
  the speaker separation now, as long as its timecode places it.
- A file whose frame rate is not one of Resolve's had its timecode
  counted at the wrong rate. It is counted at its own now.
- German headings wrote OE and UE where they meant Ö and Ü. They no
  longer do, in twelve places.
- The reason beside a channel tick was cut off where it was longer than
  its column -- in German the sentence lost its point, "matching at 120
  of " and then nothing. It wraps now.
- Curves the program keeps to save re-reading a file carried no mark of
  how they were worked out. They carry one now, so a changed reckoning
  throws the old ones away instead of mixing them in.

**Deutsch**

### Hinzugefügt

- Eine Kamera, für deren Bildrate Resolve keine Zeitleiste hat, wird
  trotzdem verwendet: die Zeitleiste bekommt die nächste Rate, die
  Resolve kennt, und die Kamera behält ihre eigene. Gemessen sitzt eine
  Datei mit 15 Bildern je Sekunde in einer Zeitleiste mit 30 auf ein
  halbes Bild genau.
- Die Auswahl „gehört zu" graut eine Aufnahme aus, deren Uhr Stunden von
  der Aufnahme entfernt liegt, mit der sie zusammengelegt werden soll,
  und sagt, wie weit. Wurden die beiden von Hand verbunden, ging der
  Unterschied als Stille in die Datei: aus 40 Sekunden Ton wurden
  5,95 GB, und der Sprecher war weg.

### Geändert

- Wo der Ton einer Datei sich nicht zuordnen ließ, stand bisher nur, sie
  passe nicht zu den anderen. Jetzt steht da, welcher der beiden Wege zu
  einem Platz noch offen ist: „Ton nicht erkannt; über den Timecode
  platziert" -- oder dass keiner mehr offen ist und der Ton nicht
  verwendet werden kann.

### Behoben

- Eine Kamera konnte als unpassend markiert werden, obwohl die Messung
  sie gefunden hatte. Die Prüfung auf eine brauchbare Ablesung nimmt
  jetzt zwei Zahlen, die ohnehin gemessen wurden; diese beiden trennen
  alle 378 Paare richtig.
- Die Vorschau ließ Dateien weg, die der Lauf behielt -- im Schnittband
  stand eine Kamera weniger als im fertigen Projekt. Beide fragen jetzt
  dasselbe.
- Eine Kamera, deren Ton nicht erkannt wurde, darf jetzt Quelle der
  Sprechertrennung sein, solange ihr Timecode sie platziert.
- Bei einer Datei, deren Bildrate keine von Resolves ist, wurde der
  Timecode mit der falschen Rate gezählt. Er wird jetzt mit ihrer
  eigenen gezählt.
- Deutsche Überschriften schrieben OE und UE, wo Ö und Ü gemeint war.
  Sie tun es nicht mehr, an zwölf Stellen.
- Der Hinweis neben einem Kanal-Häkchen war abgeschnitten, wo er länger
  war als seine Spalte -- auf Deutsch fehlte die Aussage selbst,
  „an 120 von " und dann nichts. Er bricht jetzt um.
- Die Kurven, die das Programm aufhebt, um eine Datei nicht zweimal lesen
  zu müssen, trugen kein Zeichen dafür, wie sie berechnet wurden. Jetzt
  tragen sie eines, und nach einer geänderten Rechnung werden die alten
  weggeworfen, statt sich unter die neuen zu mischen.

## [2.26.1-beta] - 2026-09-01

### Fixed

- Where the cameras did not all run at the same speed, the cut in the
  Resolve timeline sat in the wrong place, and further out the longer the
  episode ran. A shot due at 26.8 seconds showed what its camera had
  recorded at 34.8. Every camera now counts its frames in its own rate,
  and the cut read back out of Resolve matches the list the program
  wrote.
- The timeline now gets the highest rate found among the cameras, where
  it used to get the rate of the longest recording. Converted upwards
  Resolve repeats frames, downwards it throws them away. Intro and outro
  do not count, nor does a file set to "ignore this video".
- Between two shots from cameras of different speeds a frame of the
  timeline could stay black, because the outgoing camera's frames did not
  reach that far. A shot now begins where the one before it really
  stopped. Measured over 400 shots for every pair of rates the program
  knows: no gap anywhere, and no shot running into the next.
- The cut list written beside the project named frames that were one out
  from the ones in the timeline. Both now count from the same place.
- A camera's own timecode was read at another camera's rate, which put
  it out by a fraction of a second before anything was cut. It is read
  at its own rate now.
- The note before a run said the timeline would get the rate of the
  first file, and the run said different rates did not matter. Both were
  the opposite of the truth. They now name the rate the timeline gets.

### Documentation

- The Resolve chapter says in both languages what happens when cameras
  run at different speeds -- which rate the timeline gets, why one frame
  of it can stay open at a cut, and that the multicam timeline and the
  written camera files were never part of this.

**Deutsch**

### Behoben

- Liefen die Kameras nicht alle gleich schnell, saß der Schnitt in der
  Resolve-Timeline an der falschen Stelle, und umso weiter daneben, je
  länger die Folge lief. Eine Einstellung, die bei 26,8 Sekunden fällig
  war, zeigte, was ihre Kamera bei 34,8 aufgenommen hatte. Jede Kamera
  zählt ihre Bilder jetzt in ihrer eigenen Rate, und der aus Resolve
  zurückgelesene Schnitt deckt sich mit der Liste des Programms.
- Die Timeline bekommt jetzt die höchste Rate, die unter den Kameras
  vorkommt; bisher war es die der längsten Aufnahme. Rechnet Resolve
  nach oben um, wiederholt es Bilder, nach unten wirft es welche weg.
  Intro und Outro zählen nicht mit, eine Datei auf „dieses Video
  ignorieren" ebenso wenig.
- Zwischen zwei Einstellungen von verschieden schnellen Kameras konnte
  ein Bild der Timeline schwarz bleiben, weil die Bilder der abgehenden
  Kamera nicht so weit reichten. Eine Einstellung beginnt jetzt dort, wo
  die vorige wirklich aufgehört hat. Über 400 Einstellungen für jedes
  Ratenpaar gemessen, das das Programm kennt: nirgends eine Lücke, und
  keine Einstellung, die in die nächste läuft.
- Die Schnittliste neben dem Projekt nannte Bilder, die um eins neben
  denen der Timeline lagen. Beide zählen jetzt von derselben Stelle.
- Der Timecode einer Kamera wurde mit der Rate einer anderen gelesen und
  saß dadurch um Bruchteile einer Sekunde daneben, bevor überhaupt
  geschnitten war. Er wird jetzt mit ihrer eigenen Rate gelesen.
- Der Hinweis vor dem Lauf sagte, die Timeline bekomme die Rate der
  ersten Datei, und der Lauf selbst sagte, verschiedene Raten störten
  hier nicht. Beides war das Gegenteil der Wahrheit. Sie nennen jetzt
  die Rate, die die Timeline bekommt, und was Resolve mit den anderen
  macht.

### Dokumentation

- Das Resolve-Kapitel sagt in beiden Sprachen, was geschieht, wenn
  Kameras verschieden schnell laufen -- welche Rate die Timeline
  bekommt, warum an einem Schnitt ein Bild von ihr offen bleiben kann,
  und dass die Multicam-Timeline und die geschriebenen Kameradateien
  davon nie berührt waren.

## [2.26.0-beta] - 2026-09-01

### Added

- Under the preview on the third tab a line now says what the cut rests
  on: "measured from the recordings", in the colour of a warning, before
  a run; "from the finished run" or "from the processed Auphonic tracks"
  in the good colour once one is done. Turn the knobs after that and
  "Create Resolve project" works out the Resolve cut afresh from the
  values standing there and that same result.

### Changed

- The preview takes the clock drift of the recorders out, as the run has
  always done. Its edit points ran some 143 milliseconds -- three to four
  frames -- away from the run's over an hour; they now stay inside a
  single frame. Which camera is cut to never changed. The project file
  keeps how fast each recorder ran; one written before that still opens.
- The coloured plate under the picture in the cut player keeps to the two
  lines it carries, centred in it, and the height neither of them uses
  goes to the ground of the box. In a narrow, tall window that plate was
  a third of the height. A shot with no picture keeps the whole box.

### Fixed

- A speaker who says little was counted as speaking whenever a neighbour
  did, because the bleed was removed from the measurement only for
  somebody speaking in more than a tenth of the recording. Below that it
  now works too. On test material, half of what was heard used to be put
  on the wrong person; a twentieth is now.
- The line saying how many speakers were measured was hidden again 400
  milliseconds later by the preview. It now stays.
- A test that talks to DaVinci Resolve destroyed an open project that
  had never been saved. Those tests now leave themselves out instead and
  say what to do.
- The dry run now gives the separated voices the heading the real run
  gives them, and German no longer counts "in 1 Abschnitten".

### Tests

- The run says at the end that the Resolve tests exist, did not run here
  and how to start them -- and says it more sharply where the Resolve
  branch has been worked on. The 74 checks under those tests are now held
  against their register by name; until now they fell out of it unseen.

**Deutsch**

### Hinzugefügt

- Unter der Vorschau auf dem dritten Reiter steht jetzt, worauf der
  Schnitt beruht: „gemessen aus den Aufnahmen" in der Warnfarbe, solange
  kein Lauf durch ist; „aus dem fertigen Lauf" oder „aus den bearbeiteten
  Auphonic Spuren" in der guten Farbe, sobald einer durch ist. Verstellt
  man danach die Regler, rechnet „Resolve-Projekt anlegen" den Schnitt
  aus den jetzt dort stehenden Werten und eben diesem Ergebnis neu.

### Geändert

- Die Vorschau rechnet den Uhrengang der Recorder heraus, wie der Lauf
  es immer getan hat. Ihre Schnittpunkte wichen über eine Stunde um rund
  143 Millisekunden von denen des Laufs ab, also um drei bis vier Bilder;
  jetzt bleiben sie innerhalb eines einzigen Bildes. Welche Kamera
  geschnitten wird, hat sich nie geändert. Die Projektdatei hält jetzt
  fest, wie schnell jeder Recorder lief; eine ältere lässt sich
  weiterhin öffnen.
- Die farbige Fläche unter dem Bild im Schnitt-Player ist nur noch so
  hoch, wie ihre zwei mittig stehenden Zeilen es brauchen; die Höhe, die
  sie nicht brauchen, füllt der Hintergrund des Kastens. In einem
  schmalen, hohen Fenster war diese Fläche ein Drittel der Höhe. Eine
  Einstellung ohne Bild behält den ganzen Kasten.

### Behoben

- Wer wenig sagt, galt als sprechend, sobald ein Nachbar sprach: das
  Übersprechen wurde nur für jemanden herausgerechnet, der in mehr als
  einem Zehntel der Aufnahme redet. Darunter geschieht es jetzt auch. Am
  Prüfmaterial landete bisher die Hälfte des Gehörten bei der falschen
  Person, jetzt ein Zwanzigstel.
- Die Zeile, die sagt, wie viele Sprecher gemessen wurden, wurde 400
  Millisekunden später von der Vorschau wieder ausgeblendet, so dass sie
  niemand je gesehen hat. Sie bleibt jetzt stehen.
- Ein Test, der mit DaVinci Resolve spricht, hat ein offenes, nie
  gespeichertes Projekt vernichtet. Diese Tests laufen jetzt nicht mehr
  von selbst mit und sagen stattdessen, was zu tun ist.
- Der Probelauf gibt den getrennten Stimmen jetzt die Überschrift, die
  der richtige Lauf ihnen gibt, und auf Deutsch steht nicht mehr „in 1
  Abschnitten".

### Tests

- Der Lauf sagt am Ende, dass es die Resolve-Tests gibt, dass sie hier
  nicht mitgelaufen sind, und wie man sie startet -- deutlicher dort, wo
  am Resolve-Zweig gearbeitet wurde. Die 74 Prüfungen dieser Tests werden
  jetzt namentlich gegen ihr Register gehalten; bisher fielen sie
  ungesehen heraus.

## [2.25.1-beta] - 2026-09-01

### Removed

- The switches `--update-check` and `--no-update-check` are gone. They
  belonged to a remembered no that the window has not offered for a
  version. `VPM_NO_UPDATE_CHECK` in the environment still switches the
  looking off for everybody on a machine, and `--update` is what fetches.

### Fixed

- Two cameras whose file names begin alike were drawn as one in the
  preview: one of them never played, both shots carried one colour, and
  the legend counted them once. Worse, the preview showed one standing
  shot where the run cut twice. Cameras are told apart by their whole
  file name there now, so the picture the sliders are set against is the
  cut that comes out.
- The summary that opens on "Start" named the same amount of disc space
  whatever time window was set. It was wrong in both directions -- 96 GB
  for a run that writes 6, and 115 MB for one that writes a gigabyte, and
  that second number is the one somebody checks their free space against.
  The summary and the report before the run now come from one reckoning.
- Where the key frames of a camera could not be read, the log said the
  whole camera was written and then cut its tail anyway. It says now that
  the copy starts at the beginning of the file, which is what happens.
- Keeping the transcript saved nothing: the words were filed under the
  name of a mix that is built in a new folder every time, so they were
  never found again. They are filed under what the recording holds now,
  and a second run of the same material skips the recogniser -- the 27
  seconds in the window, and the eleven to thirty minutes Whisper takes
  on Windows.
- The program had stopped saying that a newer version was out. A no given
  once in passing had been kept in the cache and could only be taken back
  with a switch that nothing in the window mentions. No answer is remembered
  now; "Skip this version" skips one version and asks again at the
  next.

**Deutsch**

### Entfernt

- Die Schalter `--update-check` und `--no-update-check` gibt es nicht
  mehr. Sie gehörten zu einem gemerkten Nein, das im Fenster seit einer
  Fassung gar nicht mehr angeboten wird. `VPM_NO_UPDATE_CHECK` in der
  Umgebung schaltet das Nachsehen weiterhin für alle auf einem Rechner
  ab, geholt wird mit `--update`.

### Behoben

- Zwei Kameras, deren Dateinamen gleich anfangen, waren in der Vorschau
  ein und dieselbe: eine davon lief nie, beide Einstellungen hatten
  dieselbe Farbe, und die Legende zählte sie einmal. Schlimmer noch: die
  Vorschau zeigte eine durchgehende Einstellung, wo der Lauf zweimal
  schnitt. Kameras werden dort jetzt am ganzen Dateinamen
  auseinandergehalten, so dass das Bild, nach dem die Regler gestellt
  werden, den Schnitt zeigt, der herauskommt.
- Die Übersicht, die bei „Start" aufgeht, nannte denselben Platzbedarf,
  gleich welches Zeitfenster gesetzt war -- und zwar in beide Richtungen
  falsch: 96 GB für einen Lauf, der 6 schreibt, und 115 MB für einen, der
  ein Gigabyte schreibt. Die zweite Zahl ist die gefährliche, denn an ihr
  misst jemand seinen freien Platz. Übersicht und Bericht vor dem Lauf
  rechnen jetzt dasselbe.
- Wo die Schlüsselbilder einer Kamera nicht zu lesen waren, schrieb das
  Protokoll, die ganze Kamera werde geschrieben, und schnitt ihr Ende
  dann doch ab. Es steht jetzt da, dass die Kopie am Anfang der Datei
  beginnt -- und so geschieht es auch.
- Die Niederschrift aufzuheben brachte nichts: die Wörter lagen unter dem
  Namen einer Mischung, die bei jedem Lauf in einem neuen Ordner entsteht,
  und waren deshalb nie wiederzufinden. Sie liegen jetzt unter dem, was
  die Aufnahme enthält, und ein zweiter Lauf über dasselbe Material spart
  sich die Erkennung -- die 27 Sekunden im Fenster, und die elf bis
  dreißig Minuten, die Whisper unter Windows braucht.
- Das Programm sagte nicht mehr, dass eine neuere Fassung da ist. Ein
  einmal nebenbei gegebenes Nein lag im Zwischenspeicher und war nur mit
  einem Schalter zurückzunehmen, von dem im Fenster nichts steht. Gemerkt
  wird jetzt nichts mehr; „Diese Version überspringen" überspringt genau
  diese eine und fragt bei der nächsten wieder.

## [2.25.0-beta] - 2026-09-01

**English**

### Added

- The picture in **Camera cut -- preview** carries a note of its own:
  who is speaking, in bold, and the camera under it, on a plate in the
  colour of the running shot with a frame of that colour round the
  picture. Where a shot has no picture, the colour fills the whole box
  and the same two lines stand on it.
- The player on the **Resolve cut** tab has a fast forward of its own,
  at the end of the transport and on the `L` key. Every press doubles
  the speed, up to eight times, and the speed stands on the button.

### Changed

- Where a time window is marked, each camera is written only for that
  window, plus a second at each end. One mark is enough: an In point on
  its own takes the head off every camera. On a five-minute window of a real
  interview that is 6.09 GB of output rather than 83.57 GB, and the cut
  it produces is the same to the millisecond.
- Pressing **Measure speakers now** and then **Start** worked the same
  recording out twice. The run reads the store the window fills now, so
  a separation already in it comes back in 0.0008 s rather than 201 s,
  and the log says it was read back.
- The speech recognition waited for the speaker separation to finish.
  It starts beside it now, which takes 27 seconds off the 201 seconds
  an 87-minute recording waits. It runs on the consent that started the
  separation, so nothing is asked twice.
- Checking a camera the program has just written walks the file once,
  not once per audio track. On a 36 GB camera file off a 150 MB/s drive
  that saves about four minutes a camera, and the two progress lines
  become one, **Check: Full-Mix and camera track**.

### Removed

- The flat button **Only one speaker -- separate the track?** in the
  **Speakers** column is gone. What it did is an answer in the name
  field of the same row: **several speakers** rather than a name.
- A double click on the preview picture used to blow it up to the whole
  screen, and Escape brought it back. Both are gone; the picture stays
  in the box it is given, on every tab.

### Fixed

- Where two recordings had been taken apart, only one of them reached
  the cut, and its people were placed on the other one's cameras: 2 of
  4 speakers arrived, on the wrong two. All four are in the cut now,
  each on their own camera.
- Every separation started its stand-in names at **Speaker 1** again,
  so five people shared three names. A stand-in takes the first number
  nobody has now, over all recordings; typing a name another voice
  already carries turns both fields red and holds the start.
- Separating a second recording wiped the first one's voices off the
  screen, and names typed under the first were written onto the
  second's. Every recording keeps its own now, they stand side by side,
  and reopening a project brings them all back.
- A voice reached the cut only where a separation had found it, so
  somebody measured from their own microphone dropped out as soon as any
  recording was taken apart. Voices out of a separation and tracks
  measured here go into one reckoning now, and only **do not use** keeps
  somebody out.
- Where somebody on **no camera of its own** spoke beside somebody who
  has a camera, the picture went to the wide shot. Such a voice counts
  now for the speaking shares and among who is heard in a shot, but the
  camera is chosen among those who have one.
- With nothing loaded, **Save project**, **Close project**, **Start**
  and **Dry run** stood black over an empty list while the buttons for
  the same four were grey. Each entry follows its button now, and so
  does every entry of the **Player** menu.
- The transport entries drove the preview player of the second tab
  whatever tab was showing, the **Resolve cut** tab included. Each
  drives the player of the tab in front now, and stays grey where that
  tab shows none.
- Storing the key while the keychain was locked stood for twenty
  seconds and then failed, with a reason that was not the real one.
  **Save in Keychain** is grey now, a line under it says the keychain is
  locked, and **Open Keychain Access** beside it opens the program that
  unlocks it.
- Where the camera's own audio track was missing from the written file,
  the run reported that the two tracks cannot be compared, which reads
  like a bad take. It says now that the track is not in the file and
  that nothing was measured.
- The **Speakers** column hung off the right edge of the window: its
  message was cut to two half lines and the button beside it showed the
  single letter "e". The column is 132 px wide now, and the sideways
  scrollbar under the table is gone.

### Security

- Where the macOS keychain did not take the key, the program handed it
  over a second way: as an argument on a command line, where everybody
  on the machine can read it. That way is gone -- nothing is stored
  where the keychain refuses, and a line says why.

**Deutsch**

### Hinzugefügt

- Das Bild in **Kameraschnitt -- Vorschau** trägt eine eigene Auskunft:
  wer spricht, fett, darunter die Kamera, auf einer Fläche in der Farbe
  der laufenden Einstellung und in einem Rahmen derselben Farbe. Wo eine
  Einstellung kein Bild hat, füllt die Farbe den ganzen Kasten, und die
  zwei Zeilen stehen darauf.
- Der Player auf dem Reiter **Resolve-Schnitt** hat einen eigenen
  **Vorlauf**, am Ende der Bedienleiste und auf der Taste `L`. Jeder
  Druck verdoppelt das Tempo, bis achtfach, und das Tempo steht auf dem
  Knopf.

### Geändert

- Wo ein Zeitfenster gesetzt ist, wird jede Kamera nur für dieses
  Fenster geschrieben, dazu je eine Sekunde davor und danach. Eine
  Marke genügt: ein In-Punkt allein schneidet jeder Kamera den Kopf ab. Bei
  fünf Minuten aus einem echten Interview sind das 6,09 GB statt
  83,57 GB, und der Schnitt bleibt auf die Millisekunde derselbe.
- Wer **Sprecher jetzt messen** drückte und danach **Start**, ließ
  dieselbe Aufnahme zweimal durchrechnen. Der Lauf liest jetzt zurück,
  was das Fenster abgelegt hat: eine schon gemessene Trennung kommt in
  0,0008 s statt in 201 s, und das Protokoll sagt, dass sie
  zurückgelesen wurde.
- Die Spracherkennung wartete, bis die Sprechertrennung fertig war. Sie
  läuft jetzt daneben und spart 27 der 201 Sekunden, die eine Aufnahme
  von 87 Minuten braucht. Die Einwilligung bleibt dieselbe: sie stammt
  vom Start der Trennung, gefragt wird nichts zweimal.
- Die Kontrolle einer eben geschriebenen Kamera geht einmal durch die
  Datei, nicht einmal je Tonspur. Bei 36 GB auf einer Platte mit
  150 MB/s sind das rund vier Minuten je Kamera, und aus zwei
  Fortschrittszeilen wird eine: **Kontrolle: Full-Mix und Kameraspur**.

### Entfernt

- Der flache Knopf **Nur ein Sprecher -- Spur auftrennen?** in der
  Spalte **Sprecher** ist weg. Was er tat, ist eine Antwort im
  Namensfeld derselben Zeile: **mehrere Sprecher** statt eines Namens.
- Ein Doppelklick auf das Vorschaubild machte es bildschirmfüllend,
  Escape holte es zurück. Beides gibt es nicht mehr; das Bild bleibt in
  dem Kasten, den es bekommt, auf jedem Reiter.

### Behoben

- Waren zwei Aufnahmen aufgetrennt, kam nur eine davon in den Schnitt,
  und ihre Leute wurden den Kameras der anderen zugeordnet: 2 von 4
  Sprechern kamen an, auf den falschen zwei. Jetzt sind alle vier im
  Schnitt, jeder auf seiner eigenen Kamera.
- Jede Trennung fing ihre Ersatznamen wieder bei **Sprecher 1** an,
  fünf Leute teilten sich drei Namen. Ein Ersatzname nimmt jetzt die
  erste freie Nummer über alle Aufnahmen hinweg; wer einen Namen tippt,
  den eine andere Stimme trägt, färbt beide Felder rot und hält den
  Start an.
- Eine zweite Trennung wischte die Stimmen der ersten vom Bildschirm,
  und die unter der ersten getippten Namen landeten auf den Stimmen der
  zweiten. Jede Aufnahme behält jetzt ihre eigenen, sie stehen
  nebeneinander, und ein wieder geöffnetes Projekt bringt alle zurück.
- Eine Stimme kam nur in den Schnitt, wenn eine Trennung sie gefunden
  hatte; wer über sein eigenes Mikrofon gemessen wurde, fiel heraus,
  sobald irgendeine Aufnahme aufgetrennt wurde. Stimmen aus einer
  Trennung und hier gemessene Spuren gehen jetzt in dieselbe Rechnung,
  und nur **nicht verwenden** hält jemanden heraus.
- Sprach jemand, der auf **ohne eigene Kamera** steht, neben jemandem
  mit eigener Kamera, ging das Bild auf den Weitwinkel. Eine solche
  Stimme zählt jetzt für die Sprechanteile und dafür, wer in einer
  Einstellung zu hören ist -- die Kamera wird unter denen gewählt, die
  eine haben.
- Ohne geladenes Projekt standen die Einträge **Projekt speichern**,
  **Projekt schließen**, **Start** und **Probelauf** schwarz über einer
  leeren Liste, während die Knöpfe dafür grau waren. Jeder Eintrag folgt
  jetzt seinem Knopf, und die Einträge des Menüs **Wiedergabe** ebenso.
- Die Wiedergabe-Einträge im Menü steuerten den Vorschau-Player des
  zweiten Reiters, gleich welcher Reiter vorn stand, den
  **Resolve-Schnitt** eingeschlossen. Jetzt steuern sie den Player des
  Reiters, der vorn steht, und bleiben grau, wo dort keiner ist.
- Den Schlüssel bei zugesperrtem Schlüsselbund abzulegen, hing zwanzig
  Sekunden lang und scheiterte dann mit einer Begründung, die nicht die
  richtige war. **Im Schlüsselbund speichern** ist jetzt grau, eine
  Zeile darunter sagt, dass der Schlüsselbund zugesperrt ist, und
  **Schlüsselbundverwaltung öffnen** daneben öffnet das Programm, das
  ihn aufsperrt.
- Fehlte die Kameraspur in der geschriebenen Datei, meldete der Lauf,
  die beiden Spuren ließen sich nicht vergleichen -- das liest sich wie
  eine schlechte Aufnahme. Jetzt sagt er, dass die Spur nicht in der
  Datei ist und nichts gemessen wurde.
- Die Spalte **Sprecher** hing über den rechten Fensterrand hinaus: ihre
  Meldung war auf zwei halbe Zeilen beschnitten, und der Knopf daneben
  zeigte nur den Buchstaben „e". Die Spalte ist jetzt 132 px breit, und
  der waagerechte Rollbalken unter der Tabelle ist weg.

### Sicherheit

- Nahm der Schlüsselbund den Schlüssel nicht, reichte das Programm ihn
  auf einem zweiten Weg weiter: als Argument einer Kommandozeile, wo ihn
  jeder am Rechner lesen kann. Diesen Weg gibt es nicht mehr -- wo der
  Schlüsselbund ablehnt, wird nichts abgelegt, und eine Zeile sagt,
  warum.

## [2.24.1-beta] - 2026-08-31

**English**

### Changed

- Above a recording it had just placed, the run printed nothing but a
  weak match, which read as a verdict it was overruling. The line names
  the comparison that placed the file -- "placed by phase" -- beside
  the block count.

### Fixed

- None of the keys Ctrl+1 to Ctrl+4 did anything at all. All four reach
  their tab now.
- Every camera arrived in Resolve as a wide shot carrying nobody
  wherever the voices were told apart under one shared recording. The
  handover reads the assignment too now, so a camera comes over with
  its speaker and its clips are keyed by the person.
- "This produces:" promised two audio tracks per camera; the run wrote
  five -- the mix, one per recording, and the camera original. The plan
  counts them as the writer does now, and says two where
  "--no-single-tracks" or a single recording makes two.
- A finished cut paused the player and rewound it, so anybody who
  pressed play shortly after opening a project was stopped. The picture
  still follows the new cut, but the place and the playing now stay
  with whoever is watching.
- A recording nothing could place was laid down at whatever number came
  out, where it looks exactly like one that fits. It is refused now,
  with the sentence the program keeps for it, as a camera without a
  place already was.
- A camera whose file was never written stood in the handover with an
  empty path, counted as the wide shot, and Resolve then quietly
  imported the untouched source in its place. Such a camera is named
  among the ones left out now.
- The tracks coming back from auphonic.com were matched on the whole
  file name, so an episode title carrying the speakers' names drew a
  track to the wrong file. What all the names share is cut away now,
  before they are compared.
- Every upload to auphonic.com and every download left an empty file
  lying in the temp folder, one per transfer. The folder stays clean
  now.

### Tests

- 431 checks that had been green for months are now known to catch
  something. A third of the suite stands on that evidence.
- The check that the Auphonic key never leaves the machine in the clear
  read the command line only, and a key written into the request body
  left it green. Every argument and every file handed to curl is
  searched now.

### Documentation

- The interface chapter said the "Language" field tells auphonic.com
  what to expect when transcribing. It sets the tag of the written
  audio track and tells the recognition on this machine which language
  to expect, and the chapter says so.
- The key table gave K as "Pause, back to 1x". K pauses; the speed goes
  back to 1x on the next press of L.
- The roadmap described 2.23.0-beta: a transcript ordered at
  auphonic.com, a contributing guide and a pull request template under
  what is not planned although both exist. It describes 2.24.0-beta.

**Deutsch**

### Geändert

- Über einer Aufnahme, die der Lauf gerade platziert hatte, stand nur
  „schwache Übereinstimmung" -- als setze er sich über sein eigenes
  Urteil hinweg. Neben der Blockzahl sagt die Zeile, welcher Vergleich
  die Datei gesetzt hat: „per Phase platziert".

### Behoben

- Keine der Tasten Strg+1 bis Strg+4 tat überhaupt etwas. Alle vier
  erreichen jetzt ihren Reiter.
- Jede Kamera kam in Resolve als Weitwinkel ohne Sprecher an, sobald
  die Stimmen unter einer gemeinsamen Aufnahme auseinandergehalten
  wurden. Die Übergabe liest jetzt auch die Zuordnung: jede Kamera
  trägt ihren Sprecher, und ihre Clips heißen nach der Person.
- „Daraus werden:" versprach zwei Tonspuren je Kamera, geschrieben
  wurden fünf: die Mischung, eine je Aufnahme, dazu die Kameraspur. Der
  Plan zählt jetzt nach derselben Regel, nach der das Programm die
  Spuren schreibt -- mit „--no-single-tracks" oder einer einzigen
  Aufnahme sind es zwei.
- Ein fertiger Schnitt hielt den Player an und spulte an den Anfang;
  wer kurz nach dem Öffnen eines Projekts auf Wiedergabe drückte, wurde
  gestoppt. Das Bild folgt weiter dem neuen Schnitt, Stelle und
  Wiedergabe bleiben jetzt beim Zuschauer.
- Eine Aufnahme, die nirgends hinpasste, wurde bei der Zahl abgelegt,
  die gerade herauskam -- und sah dort aus wie eine, die passt. Sie wird
  jetzt zurückgewiesen, mit dem Satz, den das Programm dafür bereithält
  -- so wie eine Kamera ohne Platz schon länger.
- Eine Kamera, deren Datei nie geschrieben wurde, stand mit leerem Pfad
  in der Übergabe, galt dort als Weitwinkel, und Resolve holte sich
  still die unbearbeitete Quelle. Eine solche Kamera steht jetzt unter
  den ausgelassenen.
- Die Tonspuren von auphonic.com wurden am ganzen Dateinamen
  zugeordnet: trug der Episodentitel die Sprechernamen, landete eine
  Spur bei der falschen Datei. Verglichen wird jetzt nur, was die Namen
  unterscheidet.
- Jede Übertragung zu auphonic.com und zurück ließ eine leere Datei im
  Temp-Ordner liegen, eine je Vorgang. Der Ordner bleibt jetzt sauber.

### Tests

- Für 431 Prüfungen, die monatelang grün waren, ist jetzt belegt, dass
  sie überhaupt etwas prüfen. Ein Drittel der Testreihe steht auf
  solchen Belegen.
- Die Prüfung, dass der Auphonic-Schlüssel nirgends im Klartext
  auftaucht, sah nur in die Kommandozeile; stand der Schlüssel im Text
  der Anfrage, blieb sie grün. Durchsucht wird jetzt jedes Argument und
  jede Datei, die curl gereicht bekommt.

### Dokumentation

- Das Kapitel zur Oberfläche schrieb dem Feld „Sprache" zu, es sage
  auphonic.com, was beim Abtippen zu erwarten sei. Es setzt die
  Kennzeichnung der Tonspur und sagt der Erkennung auf diesem Rechner,
  welche Sprache kommt; so steht es jetzt da.
- Die Tastentabelle gab K als „Pause, zurück auf 1x" an. K hält an; auf
  1x geht es beim nächsten Druck auf L.
- Die Roadmap beschrieb noch 2.23.0-beta: die Niederschrift wurde dort
  bei auphonic.com bestellt, und ein Beitragsleitfaden und eine Vorlage
  für Pull Requests standen unter dem, was nicht geplant ist, obwohl es
  beides längst gibt. Jetzt beschreibt sie 2.24.0-beta.


## [2.24.0-beta] - 2026-08-31

**English**

### Added

- The three tabs can be reached from the "View" menu and with Ctrl+1 to
  Ctrl+3. Until now the only way to a tab was its own label, and a tab
  that had not been built yet had none.

### Changed

- The preflight said there was room when the numbers only just fitted,
  and it looked at the output folder alone. It wants a margin over its
  own estimate now, and counts the system temp folder too -- on one
  disk that space is used twice.
- The two settings that belong to a question stood at opposite ends of
  the tab, in words that did not meet. "Answer on screen earlier" now
  stands directly above "After a question", and its seconds say what
  they are counted from.
- Asking auphonic.com to write down the speech is gone: the tick
  "Fetch transcript" and the switch "--transcript" with it. The
  transcript is made here, as it already was on every run without a
  preset, and it no longer depends on the service.
- Four settings are greyed while no transcript is known, with the
  reason under them: both of the question, and "Wide shot after" and
  "Wide shot at most", which place themselves on a sentence boundary.
  Measured: without one, "after 40" gives what "after 90" gives.
- "Wide shot holds" is called "Wide shot at least" now, so it and "at
  most" read as the pair they are, and the four wide shot settings
  stand in the order they take effect.
- "Wide shot after" and "Wide shot at the latest" said much the same
  thing. The first is the soft limit -- from there a sentence boundary
  is looked for -- and the second the hard one, where the cut happens
  without one. Both lines now say which is which.

### Fixed

- The "Language" field steered nothing but the tag on the audio track.
  The recognition wanted a two-letter code and got three, so the
  setting was dropped without a word: asked for English on a German
  Mac, the recognition ran in German. It reaches the recognition now.
- "Rebuild cut list" read the stored call only in part and fell back
  to the defaults for the rest: the camera marked as the wide shot,
  "Reaction gap", "Reaction hold" and the file saying which voice was
  heard on which camera all fell out, so every separately heard voice
  landed on one camera. The button keeps them now.
- The colour comparison counted a file the run could not place as a
  camera. An 18-second jingle raised a caution about 357 steps of
  brightness against three cameras it is never cut against. Only the
  cameras of the episode are compared now.
- The preview shows no reaction cut until a run has written a
  transcript, and it did not say so. The two settings of the question
  stood there taking answers that changed nothing. They are greyed with
  the reason under them now.
- The lead of the reaction cut counted from the start of the answer, so
  the pause between question and answer swallowed it. Zero is the end
  of the question now: five seconds means five seconds before the asker
  stops.
- "Save project" opened the folder chooser without a word, and the
  sentence saying why came only for whoever cancelled. The sentence
  comes first now.
- A jingle became the wide shot of the episode: an 18-second clip took
  42 shots and 5:15 of an hour. A file nothing can place is proposed as
  "Intro" now, and "Content" and "Wide shot" are barred for it --
  whoever set them, and wherever they came from.
- The camera a speaker is filmed by stopped following the name: the
  window wrote its own first guess into the project as though somebody
  had chosen it. Only an answer that differs from the suggestion is
  written down now, and the suggestion is worked out at every rebuild.
- "--apart" and the "Remove" button separated a block and got it back
  joined one step later, because two blocks of one recorder are given
  the same name. A block taken out stays out of the plan now.
- The handover to Resolve named a camera the run had refused, with an
  empty file name and the mark of the wide shot on it. Such a file is
  left out of the handover now, and the run says which one and why.
- The Timecode column showed "no timecode" for times the program had
  just worked out: the times were stored under one spelling of the path
  and looked up under another. Both go through one shape now.
- A recording reached under two spellings of its path had its sound
  curve measured twice, which cost 2.88 MB an hour and a second pass
  over the file. It is measured once now.

### Tests

- A test whose checking part died quietly printed nothing and stayed
  green. The number of judgements is now read out of every test and
  held against a floor, so a test that stops judging turns red even
  when every judgement left in it passed.

**Deutsch**

### Hinzugefügt

- Die drei Reiter lassen sich über das Menü „Ansicht" und mit Strg+1
  bis Strg+3 erreichen. Bisher führte zu einem Reiter nur seine eigene
  Beschriftung, und ein Reiter, den es noch nicht gab, hatte keine.

### Geändert

- Der Vorflug sagte „genug Platz", wenn die Zahlen gerade eben aufgingen,
  und sah nur in den Ausgabeordner. Er will jetzt einen Abstand über
  seine Schätzung hinaus und zählt den Temp-Ordner mit -- auf einer
  Platte wird dieser Platz zweimal gebraucht.
- Die zwei Einstellungen, die zu einer Frage gehören, standen an
  entgegengesetzten Enden des Reiters, und ihre Beschriftungen passten
  nicht zueinander. „Antwort früher im Bild" steht jetzt direkt über
  „Nach einer Frage", und die Sekunden sagen, wovon sie zählen.
- Die Niederschrift bei auphonic.com zu bestellen, ist weggefallen, und
  mit dieser Möglichkeit auch der Haken „Transkription holen" und der
  Schalter „--transcript". Die Niederschrift entsteht hier, wie schon
  bisher bei jedem Lauf ohne Voreinstellung, und hängt an keinem Dienst
  mehr.
- Vier Einstellungen sind gesperrt, solange keine Niederschrift
  bekannt ist, mit dem Grund darunter: die beiden der Frage sowie
  „Weitwinkel nach" und „Weitwinkel höchstens", die sich auf
  Satzgrenzen setzen. Gemessen: ohne sie gibt „nach 40" dasselbe wie
  „nach 90".
- „Weitwinkel steht" heißt jetzt „Weitwinkel mindestens", damit es mit
  „höchstens" das Paar bildet, das es ist; die vier Weitwinkelfelder
  stehen in der Reihenfolge, in der sie greifen.
- „Weitwinkel nach" und „Weitwinkel spätestens" sagten fast dasselbe.
  Das erste ist die weiche Grenze -- ab dort wird eine Satzgrenze
  gesucht --, das zweite die harte, an der auch ohne eine geschnitten
  wird. Beide Zeilen sagen das jetzt.

### Behoben

- Das Feld „Sprache" steuerte nur die Kennzeichnung der Tonspur. Die
  Erkennung wollte zwei Buchstaben und bekam drei, also fiel die
  Einstellung wortlos heraus: auf einem deutschen Mac lief die
  Erkennung deutsch, auch wenn Englisch dastand. Jetzt erreicht das Feld
  die Erkennung.
- „Schnittliste neu bauen" las den gespeicherten Aufruf nur zur Hälfte
  und nahm für den Rest die Vorgabewerte: die als Weitwinkel markierte
  Kamera, „Reaktionsabstand", „Reaktionshaltezeit" und die Datei, die
  sagt, welche Stimme auf welcher Kamera zu sehen ist, fielen heraus --
  jede einzeln gehörte Stimme landete dann auf derselben Kamera. Der
  Knopf behält sie jetzt.
- Der Farbvergleich zählte eine Datei mit, die der Lauf nicht platzieren
  konnte. So kam wegen eines 18-Sekunden-Jingles eine Warnung über 357
  Helligkeitsstufen Unterschied zu drei Kameras, gegen die er nie
  geschnitten wird. Verglichen werden jetzt nur die Kameras der Folge.
- Die Vorschau zeigt keinen Reaktionsschnitt, solange kein Lauf eine
  Niederschrift geschrieben hat, und sagte es nicht. Die zwei
  Einstellungen der Frage nahmen Antworten entgegen, die nichts
  bewirkten. Sie sind jetzt gesperrt, mit dem Grund darunter.
- Der Vorlauf des Reaktionsschnitts zählte ab dem Beginn der Antwort,
  und die Pause zwischen Frage und Antwort verschluckte ihn. Null ist
  jetzt das Ende der Frage: fünf Sekunden heißt fünf Sekunden, bevor
  der Fragende aufhört.
- „Projekt speichern" öffnete die Ordnerauswahl wortlos, und der Satz,
  warum sie kommt, erschien nur für den, der abbrach. Der Satz kommt
  jetzt zuerst.
- Ein Jingle wurde zum Weitwinkel der Folge: ein 18-Sekunden-Clip bekam
  42 Einstellungen und 5:15 Minuten einer Stunde. Eine Datei, die sich
  nirgends platzieren lässt, wird jetzt als „Vorspann" vorgeschlagen,
  und „Inhalt" und „Weitwinkel" sind für sie gesperrt.
- Die Kamera eines Sprechers folgte dem Namen nicht mehr: das Fenster
  schrieb seine eigene erste Vermutung ins Projekt, als hätte jemand
  sie gewählt. Aufgeschrieben wird jetzt nur, was vom Vorschlag
  abweicht, und der Vorschlag wird bei jedem Neuaufbau neu gerechnet.
- „--apart" und der Knopf „Entfernen" trennten einen Block ab, und einen
  Schritt später war er wieder zusammengefügt, weil zwei Blöcke
  desselben Aufnahmegeräts denselben Namen bekommen. Ein herausgenommener
  Block bleibt jetzt auch im Plan draußen.
- Die Übergabe an Resolve nannte eine Kamera, die der Lauf
  zurückgewiesen hatte -- ohne Datei und mit der Marke des Weitwinkels.
  Eine solche Datei bleibt jetzt aus der Übergabe heraus, und der Lauf
  sagt, welche und warum.
- Die Timecode-Spalte zeigte „kein Timecode" für Zeiten, die das
  Programm gerade selbst ausgerechnet hatte: die Zeiten lagen unter der
  einen Schreibweise des Pfades und wurden unter einer anderen gesucht.
  Beide bringen den Pfad jetzt in dieselbe Schreibweise.
- Bei einer Aufnahme, die unter zwei Schreibweisen ihres Pfades erreicht
  wurde, wurde die Klangkurve zweimal vermessen -- 2,88 MB je Stunde und
  ein zweiter Gang über die Datei. Sie wird jetzt einmal vermessen.

### Tests

- Ein Test, dessen prüfender Teil still starb, druckte nichts und blieb
  grün. Die Zahl der Urteile wird jetzt aus jedem Test gelesen und
  gegen eine Untergrenze gehalten -- ein Test, der aufhört zu urteilen,
  wird rot, auch wenn jedes verbliebene Urteil zutrifft.


## [2.23.0-beta] - 2026-08-30

**English**

### Added

- A run with "--multitrack" and no video file was turned away. The
  recordings are laid against each other now -- equally long, one
  starting point, the longest as the reference -- and each becomes
  `<name>_aligned.wav`.
- With an Auphonic key those aligned recordings go up together as one
  multitrack production, the way the tracks of a shoot with cameras do.
- "--lufs" adjusts nothing on that path, and says so where no Auphonic
  preset is in play. The recordings go out as they were taken, so the
  balance between the voices is the one the room had; the loudness is
  set where they are mixed.

### Changed

- A file that fits nothing in the material was proposed for "ignore
  this video". One that is far shorter than the rest is proposed as
  "Intro": a jingle is meant to be used, put at the front rather than
  measured.
- The "Kind" field offered "Wide shot" for a file the run cannot place
  in the material at all. That entry is barred now, with the reason on
  it: the wide shot is the camera that runs through and steps in when
  no other fits, which a file nobody can place in time cannot be.
- A project file lying with the material was offered only after
  everything had been measured, and opening it replaced the list, so
  the measuring had been for nothing. It is offered as the files come
  in.

### Fixed

- "Close project" emptied the file list but left the measuring running,
  so the bar went on naming files that had gone. It now calls off the
  prework, the time axis and the speaker separation.
- The stretch on show beside the cut band stayed empty until somebody
  pressed "+" or "−". It stands there from the start now, in typewriter
  digits, so the columns hold still as it counts.
- In the "Kind" field a camera the program had made the wide shot
  showed all its words in grey, as if nothing could be answered. Only
  the barred entry "Content" is grey now, and the field stands in black.
- Resolve refusing "one file per delivery" left the render writing one
  file per clip, and the log said nothing. The refusal stands in the log
  now, so a folder full of single shots has a reason beside it.

---

**Deutsch**

### Hinzugefügt

- Ein Lauf mit „--multitrack" ohne Videodatei wurde abgewiesen. Die
  Aufnahmen werden jetzt gegeneinander ausgerichtet -- gleich lang, ein
  Anfang für alle, die längste als Bezug -- und aus jeder wird
  `<Name>_aligned.wav`.
- Mit Auphonic-Schlüssel gehen diese ausgerichteten Aufnahmen zusammen
  als eine Multitrack-Produktion hoch, so wie die Spuren eines Drehs
  mit Kameras.
- „--lufs" regelt auf diesem Weg nichts und sagt das auch, wo keine
  Auphonic-Voreinstellung im Spiel ist. Die Aufnahmen gehen so heraus,
  wie sie aufgenommen wurden -- das Verhältnis der Stimmen ist also das
  des Raumes; die Lautheit wird beim Mischen gesetzt.

### Geändert

- Eine Datei, die zu nichts im Material passt, wurde als „Video
  ignorieren" vorgeschlagen. Ist sie zugleich viel kürzer als der Rest,
  lautet der Vorschlag jetzt „Vorspann": ein Jingle soll verwendet und
  vorn angesetzt werden, nicht vermessen.
- Das Feld „Typ" bot „Weitwinkel" auch für eine Datei an, die sich im
  Material nirgends einordnen lässt. Dieser Eintrag ist jetzt gesperrt,
  und der Grund steht dabei: der Weitwinkel ist die Kamera, die
  durchläuft und einspringt, wenn keine andere passt -- das kann eine
  Datei nicht sein, die sich zeitlich nirgends einordnen lässt.
- Eine Projektdatei neben dem Material wurde erst nach dem Vermessen
  angeboten, und beim Öffnen ersetzte ihre Dateiliste die gerade
  vermessene -- das Vermessen war umsonst. Angeboten wird sie jetzt,
  sobald die Dateien hereinkommen.

### Behoben

- „Projekt schließen" leerte die Dateiliste, ließ die Messungen aber
  weiterlaufen; der Balken nannte Dateien, die es im Fenster nicht mehr
  gab. Jetzt brechen Vorarbeit, Zeitachse und Sprechertrennung ab.
- Die Zeitspanne neben dem Schnittband blieb leer, bis jemand „+" oder
  „−" drückte. Sie steht jetzt von Anfang an da, in
  Schreibmaschinenziffern, damit die Spalten beim Zählen ruhig stehen.
- Im Feld „Typ" zeigte eine Kamera, die das Programm zum Weitwinkel
  gemacht hatte, alle Wörter grau, als gäbe es nichts zu beantworten.
  Grau ist jetzt nur der gesperrte Eintrag „Inhalt", das Feld selbst
  steht in Schwarz.
- Lehnte Resolve „eine Datei je Ausgabe" ab, entstand still eine Datei
  je Clip, und im Protokoll stand nichts. Die Ablehnung wird jetzt
  gemeldet, damit ein Ordner voller Einzelclips einen Grund neben sich
  hat.

## [2.22.0-beta] - 2026-08-30

**English**

### Fixed

- The buttons "−", "+" and "▭" under the cut band moved 104 pixels at
  the first press, so a second press landed beside the button. The
  reading beside them is now held at its widest, and they stay put.
- Several recordings and no picture were joined into one file, one
  voice after the other. Each recording now becomes a file of its own,
  named after itself.
- A run with a single mono recording wrote its finished sound track
  with two channels. The track now has as many channels as the
  recording has.
- The update window showed the release notes in English to somebody
  running the program in German. It was the half that comes first, and
  only the window in the Help menu cut the text. Both show one language
  now, the one the program is running in.
- A loudness target given with "--lufs" was applied on a run with a
  picture and only reported on a run without one. It is applied on every
  run now, and the joined file keeps the clock of its source.
- What auphonic.com sends back on a run with no picture was never held
  against what went up. It is checked now, as on any other run.

---

**Deutsch**

### Behoben

- Die Schalter „−", „+" und „▭" unter dem Schnittband rückten beim
  ersten Druck um 104 Pixel weiter, der zweite Druck traf daneben. Die
  Anzeige daneben hat jetzt eine feste Breite, und die Schalter bleiben
  stehen.
- Mehrere Aufnahmen ohne Bild wurden zu einer Datei zusammengefügt,
  eine Stimme nach der anderen. Jetzt entsteht aus jeder Aufnahme eine
  eigene Datei, nach ihr benannt.
- Ein Lauf mit einer einzelnen Mono-Aufnahme schrieb die fertige
  Tonspur mit zwei Kanälen. Die Spur hat jetzt so viele Kanäle wie die
  Aufnahme.
- Das Update-Fenster zeigte die Versionshinweise auf Englisch, obwohl
  das Programm auf Deutsch lief: gezeigt wurde immer die obere, die
  englische Hälfte des Abschnitts. Nur das Fenster im Hilfe-Menü kürzte
  den Text. Jetzt zeigen beide eine Sprache, die des laufenden
  Programms.
- Ein Lautheitsziel aus „--lufs" wurde bei einem Lauf mit Bild
  angewendet und bei einem ohne nur gemeldet. Jetzt wird es bei jedem
  Lauf angewendet, und die zusammengefügte Datei behält die Uhr ihrer
  Quelle.
- Was auphonic.com bei einem Lauf ohne Bild zurückschickte, wurde nie
  gegen das Hochgeladene gehalten. Jetzt wird es geprüft wie bei jedem
  anderen Lauf.

## [2.21.0-beta] - 2026-08-30

**English**

### Changed

- A run without "--multitrack" now writes what a multitrack run
  writes: the metrics, the transcript, the cut lists, the saved tracks
  and the project file. On the same material: two files before, eleven
  now.
- "--multitrack" now says only how the recordings are grouped into
  productions. The time axis, the placing of the cameras and the files
  that come out are the same with the switch and without it.
- Five switches did nothing on a run without "--multitrack":
  "--parallel", "--no-metrics", "--no-transcript-file",
  "--no-speech-recognition" and "--auphonic-done". They work on every
  run now.

### Removed

- The switch "--name", which gave the new audio track a name of its
  own, is gone. The track is called "Full-Mix" everywhere: that name
  reaches Resolve, and an older handover is found again by it.
- The switch "--no-trim", which kept the sound at its full length, is
  gone. What falls away follows from the window every camera saw, so
  there is nothing left to switch off.

### Fixed

- A time window set with "--in-point" and "--out-point" meant a
  different moment for each camera on a run without "--multitrack". It
  now means one moment for all of them, as it did with the switch.
- Sound and picture with less than thirty seconds in common stopped
  the run, and 26 seconds of picture that come out exact were turned
  away. What counts now is how many sample points the alignment found
  in the window, and the message names the number.
- A camera was refused where the alignment could set no sample point
  inside it: they stand thirty seconds apart, so a 21-second camera
  had none. What counts now is how alike the two recordings sound.
- What a recording loses to the time window is now written in the log,
  at the front and at the back. A run that quietly cut seconds off a
  recording looked exactly like one that cut nothing.
- A recording that comes in several blocks was joined without a word
  under "--multitrack", so a ten-second hole in it went through
  unmentioned. Both ways now say how many blocks were joined, where
  the gaps are and whether two of them overlap.
- "--multitrack" stopped where only one recording could be aligned and
  said multitrack was not worth it. That recording now goes through
  like any other, and only a run that can align nothing stops.

---

**Deutsch**

### Geändert

- Ein Lauf ohne „--multitrack" schreibt jetzt dasselbe wie ein
  Multitrack-Lauf: die Kennzahlen, das Transkript, die Schnittlisten,
  die gesicherten Tonspuren und die Projektdatei. Am selben Material:
  vorher zwei Dateien, jetzt elf.
- „--multitrack" sagt jetzt nur noch, wie die Aufnahmen zu Produktionen
  zusammengefasst werden. Die Zeitachse, die Lage der Kameras und die
  Dateien am Ende sind mit dem Schalter dieselben wie ohne ihn.
- Fünf Schalter taten ohne „--multitrack" gar nichts: „--parallel",
  „--no-metrics", „--no-transcript-file", „--no-speech-recognition" und
  „--auphonic-done". Sie wirken jetzt bei jedem Lauf.

### Entfernt

- Der Schalter „--name", der die neue Tonspur eigens benannte, ist
  entfernt. Die Spur heißt überall „Full-Mix": dieser Name reicht bis
  Resolve, und eine ältere Übergabe wird darüber wiedergefunden.
- Der Schalter „--no-trim", der den Ton in voller Länge ließ, ist
  entfernt. Was wegfällt, ergibt sich aus dem Fenster, das jede Kamera
  gesehen hat; es gibt also nichts mehr abzuschalten.

### Behoben

- Ein Zeitfenster aus „--in-point" und „--out-point" meinte ohne
  „--multitrack" für jede Kamera einen anderen Moment. Jetzt meint es
  für alle denselben, so wie mit dem Schalter.
- Hatten Ton und Bild weniger als dreißig Sekunden gemeinsam, hielt der
  Lauf an, und 26 Sekunden Bild, die exakt liegen, wurden abgewiesen.
  Jetzt zählt, wie viele Stützpunkte die Ausrichtung im Fenster
  gefunden hat, und die Meldung nennt die Zahl.
- Eine Kamera wurde abgewiesen, wenn die Ausrichtung darin keinen
  Stützpunkt setzen konnte: die Stützpunkte liegen dreißig Sekunden
  auseinander, eine 21 Sekunden lange Kamera hatte also keinen. Jetzt
  zählt, wie ähnlich die beiden Aufnahmen klingen.
- Was eine Aufnahme durch das Zeitfenster verliert, steht jetzt im
  Protokoll, vorne wie hinten. Ein Lauf, der stillschweigend Sekunden
  abschnitt, sah aus wie einer, der nichts abschnitt.
- Eine Aufnahme aus mehreren Blöcken wurde unter „--multitrack"
  stillschweigend zusammengefügt; ein zehn Sekunden langes Loch darin
  fiel niemandem auf. Jetzt sagen beide Wege, wie viele Blöcke
  zusammenkamen, wo die Lücken liegen und ob zwei sich überlappen.
- „--multitrack" hielt an, wenn sich nur eine Aufnahme ausrichten ließ,
  und sagte, Multitrack lohne nicht. Diese Aufnahme läuft jetzt durch
  wie jede andere, und nur ein Lauf, der nichts ausrichten kann, hält
  an.

## [2.20.0-beta] - 2026-08-30

**English**

### Added

- "What changed in this version" in the Help menu shows the text in a
  window. It used to open the project's whole changelog in a browser.
- The loudness of the sound is now measured on the single-track path
  too and named in the log. The level is not changed there, and
  "--lufs" says so instead of keeping quiet about it.

### Changed

- Release notes are written in English and German. The program shows
  the language it runs in.
- The tick in the update window, "Do not ask again", used to stop the
  search for new versions for good. It is now called "Skip this
  version", and later versions are reported again.
- The audio track is called "Full-Mix" on both paths. The single-track
  path called it "Processed audio"; that name reaches Resolve, which
  names its audio track after it.

### Removed

- The switches "--head" and "--tail", which cut a fixed amount off the
  front and the back of a recording by hand, are gone. What carries no
  picture is still measured and cut.

### Fixed

- Two outputs of one name were both fetched into one file, so the
  second overwrote the first. Only one is fetched now.
- A time window moved the sound out of step on the simple path, by as
  much as the gap between the start of a recording and the start of its
  picture. Sound and picture now hold together.
- A time window that meets none of the material wrote a video of pure
  silence and reported it as a result. It now stops and says so.
- The line "Check: new track against the camera track" gave a number
  even where the two could not be compared at all. It now says that no
  comparison is possible.
- A video whose sound has nothing in common with the recording and
  carries no timecode was laid down at a guess. It is now refused, and
  the window proposes it for "ignore this video".
- Two cameras on the single-track path were handed to Resolve at the
  same spot and had to be pulled apart by hand. Each now stands where
  the alignment measured it.
- A recording taken through the single-track path lost the marker that
  tells Resolve which curve it was shot on, Apple Log among them.
  Colour and metadata are checked there now as well.
- The progress bar reported not one stage on the single-track path and
  crept from end to end over a run of many minutes. It now names the
  same six stages the other path names.
- A run without an assignment file wrote camera files under the name of
  the source and no handover for Resolve at all. Each video is now a
  camera of its own, and the handover is written.
- A fourteen-second jingle among three cameras stopped the whole run. A
  file that cannot be placed against the others is now named and left
  out, and the run goes through.
- Multitrack without a single video complained about files that were
  never given. It now says instead that the tracks are laid against the
  cameras, and that there are none to lay them on.

### Documentation

- Every version in this changelog, back to 0.1.0, now stands in English
  and in German, with the same points in the same order.

---

**Deutsch**

### Hinzugefügt

- „Was sich in dieser Version geändert hat" im Hilfe-Menü zeigt den
  Text in einem Fenster. Bisher öffnete es den ganzen Änderungsbericht
  des Projekts im Browser.
- Die Lautheit des Tons wird jetzt auch auf dem Einspur-Weg gemessen
  und im Protokoll genannt. Der Pegel wird dort nicht verändert, und
  „--lufs" sagt das jetzt, statt zu schweigen.

### Geändert

- Versionshinweise stehen auf Englisch und Deutsch. Das Programm zeigt
  sie in der Sprache, in der es läuft.
- Der Haken „Nicht mehr nachfragen" im Update-Fenster stellte die Suche
  nach neuen Versionen für immer ab. Er heißt jetzt „Diese Version
  überspringen", und spätere Versionen werden wieder gemeldet.
- Die Tonspur heißt auf beiden Wegen „Full-Mix". Der Einspur-Weg nannte
  sie „Processed audio"; dieser Name reicht bis Resolve, das seine
  Tonspur danach benennt.

### Entfernt

- Die Schalter „--head" und „--tail", die von Hand ein festes Stück vom
  Anfang und vom Ende einer Aufnahme abschnitten, sind entfernt. Was
  kein Bild trägt, wird weiter gemessen und geschnitten.

### Behoben

- Zwei gleichnamige Ausgaben landeten beide in derselben Datei; die
  zweite überschrieb die erste. Jetzt wird nur noch eine geholt.
- Ein Zeitfenster verschob auf dem Einspur-Weg den Ton gegen das Bild,
  und zwar um den Abstand vom Beginn der Aufnahme zum Beginn des
  Bildes. Jetzt liegen Ton und Bild aufeinander.
- Ein Zeitfenster, das kein Material trifft, schrieb ein Video aus
  reiner Stille und meldete es als Ergebnis. Jetzt hält der Lauf an und
  sagt das auch.
- Die Zeile „Prüfung: neue Spur gegen den Kameraton" nannte auch dann
  eine Zahl, wenn sich die beiden gar nicht vergleichen ließen. Jetzt
  sagt sie, dass kein Vergleich möglich ist.
- Ein Video, dessen Ton nichts mit der Aufnahme gemein hat und keinen
  Timecode trägt, wurde auf Verdacht abgelegt. Es wird jetzt abgelehnt,
  und das Fenster schlägt „dieses Video ignorieren" vor.
- Zwei Kameras lagen auf dem Einspur-Weg in der Resolve-Übergabe an
  derselben Stelle und mussten von Hand auseinandergezogen werden.
  Jetzt steht jede dort, wo sie gemessen wurde.
- Eine Aufnahme über den Einspur-Weg verlor die Marke, die Resolve
  sagt, auf welche Kurve gedreht wurde -- Apple Log zum Beispiel. Farbe
  und Metadaten werden dort jetzt ebenso geprüft.
- Der Fortschrittsbalken meldete auf dem Einspur-Weg keine einzige
  Stufe und kroch minutenlang von Anfang bis Ende. Er nennt jetzt
  dieselben sechs Stufen wie der andere Weg.
- Ein Lauf ohne Zuordnungsdatei schrieb Kameradateien unter dem Namen
  der Quelle und gar keine Übergabe für Resolve. Jedes Video wird
  jetzt eine eigene Kamera, und die Übergabe wird geschrieben.
- Ein vierzehn Sekunden langer Jingle unter drei Kameras brachte den
  ganzen Lauf zu Fall. Eine Datei, die sich nicht einordnen lässt, wird
  jetzt benannt und ausgelassen, und der Lauf läuft durch.
- Ein Multitrack-Lauf ohne ein einziges Video beklagte Dateien, die nie
  übergeben wurden. Jetzt sagt das Programm stattdessen, dass die Spuren
  an die Kameras gelegt werden und keine Kamera da ist.

### Dokumentation

- Jede Version in diesem Änderungsbericht, zurück bis 0.1.0, steht
  jetzt auf Englisch und auf Deutsch, mit denselben Punkten in
  derselben Reihenfolge.

## [2.19.0-beta] - 2026-08-30

**English**

### Added

- Where every person has a microphone of their own, the program says
  which voice belongs to which track. Where two microphones pick up too
  much of the same speech it proposes nothing.

### Changed

- The window proposed "Speaker 1" to "Speaker n" for the voices. It now
  ranks them by who does the asking and proposes "Guest" and "Host" --
  only ever over a name it made up itself.
- A voice that gathers too few sentences inside the chosen time window
  is proposed for "do not use". Widen the window and the voice comes
  back to its camera and takes a name from the new ranking.
- "Do not use" on a voice took its camera away and greyed its name, and
  no more: it still became a track, a speaker at auphonic.com and a line
  in the transcript. Its passages are left out now.
- Writing down the speech costs about half a minute for an hour and a
  half. It runs once per recording, in the background, once a separation
  exists. Nothing is installed, nothing downloaded.
- A moved In or Out point changes the proposed names at once, rather
  than on the next visit to another tab.
- The buttons at the foot of the window -- "Settings ...", "Start", "Dry
  run" and the one that breaks a run off -- are now the same height.
  "Settings ..." stood four pixels shorter and centred.
- What was measured of a file is found again under any other path
  leading to it. A folder reachable by two names had every file in it
  measured twice.

### Tests

- Reading a file that is not there put 54 error lines into the error
  output of every run, on every machine. It is quiet now.
- The reading of the builder's times matched no name holding a digit, so
  one test fell out of every reading and kept a stale number. It is read
  with the rest now.
- A failure report keeps what the test itself printed. Twenty-five lines
  about a window that did not build matched no pattern, so not one of
  them reached the builder's log.
- The scripts that take the pictures judge by their own checks, no
  longer by what the window system gives back. On Linux that was 1 even
  where every step had been reached.
- The test for the bar at the foot of the window keeps measurements of
  its own. Warm runs were instant, the bar never appeared, and a bar
  that was right looked wrong.
- A test that comes back red is run once more by itself. One that is
  green alone lands under "unsteady" with what it said the first time --
  neither counted red nor quietly counted green.
- Every window script prints one last line: whether it reached its last
  step, how much it found wanting, and what the window system gave back.
  A missing line is itself the first finding.
- Each window script gets a runtime folder of its own. Six of them start
  at the same moment on one machine, and until now they shared one
  folder.

### Documentation

- The chapter on speech says what the names propose, when a voice is
  proposed for "do not use", and where the writing down of the words
  runs and what it costs.

---

**Deutsch**

### Hinzugefügt

- Hat jede Person ein eigenes Mikrofon, sagt das Programm, welche Stimme
  zu welcher Spur gehört. Nehmen zwei Mikrofone zu viel derselben Rede
  auf, schlägt es nichts vor.

### Geändert

- Das Fenster schlug für die Stimmen „Sprecher 1" bis „Sprecher n" vor.
  Jetzt ordnet es sie danach, wer fragt, und schlägt „Gast" und
  „Moderation" vor -- aber nur dort, wo der Name von ihm selbst stammt.
- Sammelt eine Stimme im Zeitfenster zu wenige Sätze, wird sie für
  „nicht verwenden" vorgeschlagen. Weitet man das Fenster, kehrt sie zur
  Kamera zurück und bekommt einen Namen aus der neuen Reihenfolge.
- „Nicht verwenden" nahm einer Stimme die Kamera und graute den Namen,
  mehr nicht: Sie wurde weiter zur Spur, zum Sprecher bei auphonic.com,
  zur Zeile im Transkript. Ihre Passagen entfallen jetzt.
- Das Niederschreiben der Rede kostet etwa eine halbe Minute je
  anderthalb Stunden. Es läuft einmal je Aufnahme im Hintergrund, sobald
  eine Trennung vorliegt. Nichts wird installiert oder geladen.
- Ein verschobener In- oder Out-Punkt ändert die vorgeschlagenen Namen
  sofort, nicht erst beim nächsten Besuch eines anderen Reiters.
- Die Knöpfe am Fuß des Fensters -- „Einstellungen ...", „Start",
  „Probelauf" und der zum Abbrechen -- sind jetzt gleich hoch.
  „Einstellungen ..." war vier Pixel niedriger und mittig gesetzt.
- Was an einer Datei gemessen wurde, wird auch unter jedem anderen Pfad
  dahin wiedergefunden. War ein Ordner über zwei Namen erreichbar, wurde
  jede Datei darin zweimal gemessen.

### Tests

- Das Lesen einer fehlenden Datei schrieb in jedem Lauf auf jedem
  Rechner 54 Fehlerzeilen in die Fehlerausgabe. Jetzt bleibt es still.
- Das Ablesen der Zeiten des Baurechners erfasste keinen Namen mit
  Ziffer, sodass ein Test aus jeder Ablesung fiel und eine veraltete
  Zahl behielt. Jetzt wird er mitgelesen.
- Ein Fehlerbericht behält, was der Test selbst ausgab. Fünfundzwanzig
  Zeilen über ein misslungenes Fenster passten auf kein Muster; keine
  einzige erreichte das Protokoll des Baurechners.
- Die Skripte für die Bilder urteilen nach eigenen Prüfungen, nicht mehr
  danach, was das Fenstersystem zurückgibt. Unter Linux war das 1,
  obwohl jeder Schritt erreicht war.
- Der Test für den Balken am Fuß des Fensters hält eigene Messungen.
  Warme Läufe waren sofort fertig, der Balken erschien nie, und ein
  richtiger Balken sah falsch aus.
- Ein Test, der rot zurückkommt, läuft noch einmal allein. Ist er dabei
  grün, steht er unter „unstet" mit seiner ersten Meldung -- weder rot
  gezählt noch stillschweigend grün.
- Jedes Fensterskript gibt eine letzte Zeile aus: ob es seinen letzten
  Schritt erreichte, wie viel es bemängelte und was das Fenstersystem
  zurückgab. Fehlt sie, ist das der erste Befund.
- Jedes Fensterskript bekommt einen eigenen Laufzeitordner. Sechs von
  ihnen starten auf einem Rechner im selben Augenblick; bisher teilten
  sie sich einen.

### Dokumentation

- Das Kapitel über die Rede sagt, welche Namen vorgeschlagen werden,
  wann eine Stimme für „nicht verwenden" vorgeschlagen wird und wo das
  Niederschreiben der Worte läuft und was es kostet.

## [2.18.0-beta] - 2026-08-30

**English**

### Changed

- The wide shot comes after 70 seconds on one camera instead of 40. Over
  87 minutes of interview the picture left a long-speaking guest 77
  times; it leaves them 37 times now.

### Fixed

- The count of processes a test starts stood about 1.7 times too high:
  every run of the program was counted twice. One test now reports 49
  starts in place of 85.
- The chooser of recordings beside "One more speaker in" cut every
  recording name: its width hung on a count of twelve characters. It now
  asks for the room its widest entry needs.
- Where the room is not enough, a recording name is now shortened in the
  middle instead of at the end -- the recordings of one session differ
  at the end. The whole name stands as a tooltip.

### Tests

- A test builds its two camera files in one ffmpeg call in place of two,
  one process start fewer.

---

**Deutsch**

### Geändert

- Der Weitwinkel kommt nach 70 Sekunden auf einer Kamera statt nach 40.
  Über 87 Minuten Interview verließ das Bild einen lange redenden Gast
  77-mal, jetzt noch 37-mal.

### Behoben

- Die Zahl der Prozesse, die ein Test startet, stand etwa 1,7-mal zu
  hoch: Jeder Lauf des Programms wurde doppelt gezählt. Ein Test meldet
  jetzt 49 Starts statt 85.
- Die Auswahl der Aufnahmen neben „Ein Sprecher mehr in" beschnitt jeden
  Aufnahmenamen: Ihre Breite hing an zwölf Zeichen. Jetzt fordert sie
  den Platz, den ihr breitester Eintrag braucht.
- Reicht der Platz nicht, wird ein Aufnahmename jetzt in der Mitte
  gekürzt statt am Ende -- die Aufnahmen einer Sitzung unterscheiden sich
  am Ende. Der ganze Name steht als Tooltip.

### Tests

- Ein Test baut seine zwei Kameradateien in einem ffmpeg-Aufruf statt in
  zweien; das ist ein Prozessstart weniger.

## [2.17.0-beta] - 2026-08-30

**English**

### Added

- After a run the log says who does the asking, with the sentences and
  the questions behind it. It is an order and never a threshold, and
  nothing in the program is set from it.
- That ranking takes one voice per track. Where two people share a
  microphone it says nothing useful, and it says so.
- The test suite counts the processes each test starts and prints the
  number beside the verdict, with the run's total and the five that
  start most.

### Changed

- Sounds shorter than 0.4 seconds were dropped before the pause search,
  and an "mhm" is shorter than that, so a reply read as a pause. The
  floor stands at 0.2 seconds now.
- What was measured of a video file is kept from one run to the next, by
  its size and its time of change. Opening the same project twice asked
  the same question about the same file again.
- The key store is asked once per run in place of once per question.
  Drawing the settings sheet asked it several times over. The key goes
  into no file and onto no command line, as before.
- Two places that started five processes start one: the frame timing of
  a video is taken in a single call, and short samples of the bleed
  among microphones are cut out of one reading.
- The whole test job on the Windows builder went from 208 seconds to
  161, its longest test from 126 to 107.

---

**Deutsch**

### Hinzugefügt

- Nach einem Lauf sagt das Protokoll, wer fragt, mit den Sätzen und
  Fragen dahinter. Es ist eine Reihenfolge, nie ein Schwellenwert, und
  im Programm wird daraus nichts gesetzt.
- Diese Reihenfolge setzt eine Stimme je Spur voraus. Teilen sich zwei
  Personen ein Mikrofon, sagt sie nichts Brauchbares -- und sagt das.
- Die Testsuite zählt die Prozesse jedes Tests und nennt die Zahl neben
  dem Urteil, dazu die Summe des Laufs und die fünf mit den meisten
  Starts.

### Geändert

- Vor der Pausensuche entfielen Laute unter 0,4 Sekunden, und ein „Mhm"
  ist kürzer, sodass eine Antwort als Pause gelesen wurde. Die Grenze
  liegt jetzt bei 0,2 Sekunden.
- Was an einer Videodatei gemessen wurde, bleibt von Lauf zu Lauf
  erhalten, nach Größe und Änderungszeit. Dasselbe Projekt zweimal zu
  öffnen stellte dieselbe Frage zu derselben Datei erneut.
- Der Schlüsselspeicher wird einmal je Lauf befragt statt einmal je
  Frage. Das Zeichnen des Einstellungsfensters fragte ihn gleich
  mehrfach ab. Der Schlüssel kommt in keine Datei und auf keine
  Befehlszeile, wie bisher.
- Zwei Stellen, die fünf Prozesse starteten, starten nur noch einen: die
  Bildtaktung eines Videos wird in einem Aufruf geholt, und kurze Proben
  des Übersprechens werden aus einem einzigen Durchgang geschnitten.
- Der ganze Testauftrag auf dem Windows-Baurechner fiel von 208 auf 161
  Sekunden, sein längster Test von 126 auf 107.

## [2.16.0-beta] - 2026-08-30

**English**

### Added

- A project can be opened, saved and closed from the "File" menu, which
  is grouped: the project first, the material, then the run. A second
  production used to mean starting the program over.
- Saving a project no longer waits for a run. The file was written when
  a run started and when the program was quitted, and nowhere else.
- The "View" menu names the tabs in place of numbering them, so an entry
  says which tab it leads to. The names are read off the tabs
  themselves.
- The title bar names the open project, in front, the way a document
  window does. A window with a project open and one without looked
  exactly alike.

### Changed

- A name too long for its column is shown from the front, with the whole
  name as a tooltip. The field showed its end, and the new names end
  with the camera, so which row it is was cut off.
- A column holding a field or a drop down is measured by what that
  holds. Such a column counted as empty and came out at its minimum --
  the drop down beside the name showed half a word.

### Tests

- A test that crashed is run again before the whole run is called red,
  up to three goes. Only a crash: a check that said FAIL will say it
  again.
- A test that crashed and then went green is not folded into the green
  count. It is named on a line of its own, with how many goes fell and
  what the first one said.
- A new test takes the whole circle: everything settable is set through
  the widget a person would use, the file is written, a second window
  opens it, and every answer is asked after by name.
- The same test walks the second circle: closing the project empties the
  window, and the file it came from is untouched.
- `bash run.sh <name> ...` runs only the tests named, through the same
  machinery.
- The crash report is found on a Mac now. It was looked for with a
  pattern a BSD tool does not know, so it matched nothing, silently, and
  a crashed test fell back to sampled lines.

---

**Deutsch**

### Hinzugefügt

- Ein Projekt lässt sich über das Menü „Datei" öffnen, speichern und
  schließen; das Menü ist gruppiert: erst das Projekt, das Material,
  dann der Lauf. Eine zweite Produktion hieß bisher Neustart.
- Ein Projekt zu speichern wartet nicht mehr auf einen Lauf. Die Datei
  wurde geschrieben, wenn ein Lauf begann und wenn das Programm beendet
  wurde, sonst nirgends.
- Das Menü „Ansicht" nennt die Reiter, statt sie zu nummerieren, sodass
  ein Eintrag sagt, zu welchem Reiter er führt. Die Namen stammen von
  den Reitern selbst.
- Die Titelzeile nennt das offene Projekt vorn, wie es ein
  Dokumentfenster tut. Ein Fenster mit offenem Projekt sah genauso aus
  wie eines ohne.

### Geändert

- Ein für seine Spalte zu langer Name wird von vorn gezeigt und steht
  ganz als Tooltip. Das Feld zeigte bisher sein Ende, und die neuen Namen
  enden mit der Kamera -- weg war gerade der Teil, der die Zeile benennt.
- Eine Spalte mit einem Feld oder Klappmenü wird nach dessen Inhalt
  bemessen. Solch eine Spalte galt als leer und kam auf ihr Mindestmaß
  -- das Klappmenü neben dem Namen zeigte ein halbes Wort.

### Tests

- Ein abgestürzter Test läuft erneut, bis zu drei Anläufe, bevor der
  ganze Lauf rot heißt. Nur ein Absturz: Eine Prüfung, die FAIL sagte,
  sagt es wieder.
- Ein Test, der abstürzte und dann grün wurde, geht nicht in der grünen
  Zahl auf. Er steht auf einer eigenen Zeile, mit der Zahl gefallener
  Anläufe und der ersten Meldung.
- Ein neuer Test geht den ganzen Kreis: Alles Einstellbare wird über das
  Bedienelement gesetzt, das auch eine Person benutzen würde, die Datei
  wird geschrieben, ein zweites Fenster öffnet sie, und jede Antwort wird
  namentlich abgefragt.
- Derselbe Test geht den zweiten Kreis: Das Schließen des Projekts leert
  das Fenster, und die Datei, aus der es kam, bleibt unberührt.
- `bash run.sh <name> ...` lässt nur die genannten Tests laufen, über
  dieselbe Maschinerie.
- Der Absturzbericht wird auf einem Mac gefunden. Gesucht wurde mit
  einem Muster, das ein BSD-Werkzeug nicht kennt: Es traf still nichts,
  und ein abgestürzter Test fiel auf Stichzeilen zurück.

## [2.15.0-beta] - 2026-08-30

**English**

### Added

- A project file lying beside the material is offered when files are
  added. The material's folder and one below it are searched. One find
  comes with its date, several are offered to choose from.

### Changed

- Adding material no longer reads the output folder and the production
  name out of an old handover file. The name comes from the material's
  own folder; the output folder stays empty until chosen.
- On a Mac the first menu bar entry read "Python". It carries the
  program's name now.
- "Preferences", "Quit", "Services" and the buttons in the file dialog
  come in the chosen language on a Mac. They had stayed English in a
  German window.
- "Fetch transcript" is grey while the preset is "work without
  Auphonic". It had been offering a file that could not arrive.

### Tests

- The test that runs a whole episode on this machine alone costs a
  third less processor time, all nineteen checks unchanged. Its
  material runs 34 seconds instead of 40.
- The crosstalk test builds its material in one pass and no longer
  works out the same two voices forty-eight times. It takes 4 seconds
  instead of 19.
- The suite starts the long tests first. They used to be handed out in
  alphabetical order, so a slow test named late in it ran last and the
  whole run grew by its length.
- The order of that queue comes from the builder's own times, fetched
  with `bash builder_times.sh`. This Mac is the wrong machine to ask:
  `crosstalk` takes four seconds here and 118 there.
- The suite says where it is while it runs: the time, the place in the
  queue and the verdict, one line per test as it finishes, instead of
  two silent minutes and everything at once.
- 33 checks over where a project file is looked for, what is offered
  for one and for several, that nothing is offered where there is no
  project file, and that an open project stays silent.

---

**Deutsch**

### Hinzugefügt

- Eine Projektdatei beim Material wird angeboten, sobald Dateien
  hinzukommen. Gesucht wird im Ordner des Materials und in einem
  darunter. Ein Fund kommt mit seinem Datum, mehrere zur Auswahl.

### Geändert

- Beim Hinzufügen von Material kommen Ausgabeordner und
  Produktionsname nicht mehr aus einer alten Übergabedatei. Der Name
  stammt aus dem Ordner des Materials; der Ausgabeordner bleibt leer,
  bis er gewählt wird.
- Auf dem Mac trug der erste Eintrag der Menüleiste den Namen „Python".
  Er trägt jetzt den Namen des Programms.
- „Einstellungen", „Beenden", „Dienste" und die Knöpfe im Dateidialog
  erscheinen auf dem Mac in der gewählten Sprache. Im deutschen Fenster
  waren sie bisher englisch geblieben.
- „Transkription holen" ist grau, solange die Voreinstellung „ohne
  Auphonic arbeiten" gilt. Der Knopf bot bisher eine Datei an, die gar
  nicht kommen konnte.

### Tests

- Der Test, der eine ganze Folge allein auf diesem Rechner
  durchspielt, braucht ein Drittel weniger Rechenzeit, alle neunzehn
  Prüfungen unverändert. Sein Material dauert 34 statt 40 Sekunden.
- Der Crosstalk-Test erzeugt sein Material in einem Zug und rechnet
  dieselben zwei Stimmen nicht mehr achtundvierzigmal aus. Er dauert 4
  statt 19 Sekunden.
- Die Suite startet die langen Tests zuerst. Bisher kamen sie in
  alphabetischer Reihenfolge an die Reihe: Ein langsamer Test am Ende
  des Alphabets lief zuletzt, und der Lauf wuchs um seine Dauer.
- Die Reihenfolge dieser Schlange stammt von den Zeiten des
  Baurechners, geholt über `bash builder_times.sh`. Dieser Mac taugt
  dafür nicht: `crosstalk` dauert hier vier Sekunden, dort 118.
- Die Suite sagt beim Laufen, wo sie ist: Uhrzeit, Platz in der
  Schlange und Urteil, eine Zeile je Test, sobald er fertig ist, statt
  zwei stummer Minuten und alles auf einmal.
- 33 Prüfungen darüber, wo nach einer Projektdatei gesucht wird, was
  bei einer und bei mehreren angeboten wird, dass ohne Projektdatei
  nichts angeboten wird und dass ein offenes Projekt schweigt.

## [2.14.0-beta] - 2026-08-30

**English**

### Added

- Where "Wide shot holds" is set below the "Minimum Edit Duration",
  the preview says so. Set that way, every wide shot put into a long
  monologue is merged away again and is not in the episode.

### Changed

- A handover file counts only for the window that wrote it. One lying
  in the result folder may be days old, from another measurement.
  After a restart the cut is worked out again from the project.
- A dry run no longer says a result is there: it writes nothing, and
  "Open result folder" had pointed at an earlier run. Building a
  Resolve project now names the run its cut comes from.
- The line saying why the run cannot start stands above the buttons
  instead of under them.

### Fixed

- The picture ran 80 ms ahead of the sound wherever the cut was built
  in the window and not by a run: no frame rate travelled with it, so
  the player took 30. It is measured on a camera now.
- A typed speaker name did not reach the preview: it went on showing
  the old name at the old camera until something else was touched. The
  preview follows the typing now.

### Tests

- A foreign handover file lies in the result folder throughout one
  test: three cameras of its own, ten minutes long. The cut has to
  come out on the cameras of the project.
- Putting a whole production together had no test. It has 70 checks
  now against a stand-in for auphonic.com: a dry run sends nothing,
  and the key stands in no argument list.

---

**Deutsch**

### Hinzugefügt

- Steht „Weitwinkel steht" unter der „Mindestschnittdauer", weist die
  Vorschau darauf hin. So gesetzt, wird jeder Weitwinkel in einem langen
  Monolog wieder zusammengelegt und fehlt in der Folge ganz.

### Geändert

- Eine Übergabedatei gilt nur für das Fenster, das sie schrieb. Eine
  im Ergebnis-Ordner kann Tage alt sein, aus einer anderen Messung.
  Nach einem Neustart entsteht der Schnitt neu aus dem Projekt.
- Ein Probelauf meldet kein Ergebnis mehr: Er schreibt nichts, und
  „Ergebnis-Ordner öffnen" zeigte auf einen alten Lauf.
  „Resolve-Projekt anlegen" nennt jetzt den Lauf, aus dem sein Schnitt
  stammt.
- Die Zeile, die sagt, warum der Lauf nicht starten kann, steht über
  den Knöpfen statt darunter.

### Behoben

- Das Bild lief 80 ms vor dem Ton, wo der Schnitt im Fenster entstand
  statt in einem Lauf: Es reiste keine Bildrate mit, und der Player
  nahm 30 an. Sie stammt jetzt von einer Kamera.
- Ein getippter Sprechername erreichte die Vorschau nicht: Sie zeigte
  weiter den alten Namen an der alten Kamera, bis etwas anderes
  berührt wurde. Jetzt folgt sie dem Tippen.

### Tests

- Eine fremde Übergabedatei liegt während eines Tests im
  Ergebnis-Ordner: drei eigene Kameras, zehn Minuten lang. Der Schnitt
  muss auf den Kameras des Projekts entstehen.
- Das Zusammensetzen einer Produktion hatte keinen Test. Jetzt sind es
  70 Prüfungen gegen einen Ersatz für auphonic.com: Ein Probelauf
  sendet nichts, und der Schlüssel steht in keiner Argumentliste.

## [2.13.0-beta] - 2026-08-30

**English**

### Added

- A run can be broken off. "Break off" stands beside Start while a run
  is going. It stops only where nothing is left half written, so a
  wait follows the press, and the log says so.
- What was written before a break is whole, what comes after is
  missing. The run names the finished files and says the folder holds
  a part, not a result. A running ffmpeg is ended with it.

### Changed

- The progress bar neither falls back nor stands still. Pressing Start
  while the measuring after a project was opened was still going left
  it holding one figure through two whole stages.
- In the camera table nothing stands behind the answer. Where no
  speaker is assigned to a camera, only "Content" is barred, and it
  says on itself why. The other answers stay open.

### Fixed

- A shot could arrive under the "Minimum Edit Duration": at 8 s, with
  "Wide shot holds" at 5, shots of 5.00 s reached the cut. Wide shots
  inside a long monologue are merged now.
- The preview and the run took different stand-ins where no camera is
  a wide shot: 15 shots in the run against 12 in the preview. Both
  take the same one now.

### Tests

- Eight window tests deleted their folder while the window still
  stood, four of them still holding three players each. They let go
  first now, and the wait for the release is itself the measurement.

### Documentation

- Nineteen numbers in the manual say what they are: whether they are a
  default, which switch sets them, and what a larger or a smaller
  value does.
- Two were wrong. The report of samples at the ceiling was said to
  appear from eight on, where the program says three, and to need a
  peak near full scale. That condition does not exist.

---

**Deutsch**

### Hinzugefügt

- Ein Lauf lässt sich abbrechen. „Abbrechen" steht neben Start,
  solange er läuft. Er hält erst dort, wo nichts halb geschrieben
  bleibt: Auf den Druck folgt eine Wartezeit, und das Protokoll sagt
  das auch.
- Was vor einem Abbruch geschrieben wurde, ist ganz; was danach käme,
  fehlt. Der Lauf nennt die fertigen Dateien und sagt, dass im Ordner
  ein Teilstück liegt und kein Ergebnis. Ein laufendes ffmpeg wird mit
  abgebrochen.

### Geändert

- Der Fortschrittsbalken fällt weder zurück noch bleibt er stehen.
  Start zu drücken, während die Messung nach dem Öffnen eines Projekts
  noch lief, ließ ihn zwei Stufen lang auf einer Zahl stehen.
- In der Kameratabelle steht nichts hinter der Antwort. Wo einer
  Kamera kein Sprecher zugewiesen ist, ist nur „Inhalt" gesperrt und
  sagt selbst, warum. Die übrigen Antworten bleiben offen.

### Behoben

- Eine Einstellung konnte kürzer werden als die gesetzte
  „Mindestschnittdauer": Bei 8 s und „Weitwinkel steht" auf 5 kamen
  5,00 s durch. Weitwinkel im Monolog werden jetzt zusammengelegt.
- Wo keine Kamera Weitwinkel ist, griffen Vorschau und Lauf zu
  verschiedenen Ersatzkameras: 15 Einstellungen im Lauf gegen 12 in
  der Vorschau. Jetzt nehmen beide dieselbe.

### Tests

- Acht Fenster-Tests löschten ihren Ordner, während das Fenster noch
  stand, und vier von ihnen hielten dabei je drei Player. Sie lassen
  jetzt zuerst los, und das Warten auf die Freigabe ist selbst die
  Messung.

### Dokumentation

- Neunzehn Zahlen im Handbuch sagen, was sie sind: ob sie eine
  Vorbelegung sind, welcher Schalter sie setzt und was ein größerer
  oder kleinerer Wert bewirkt.
- Zwei stimmten nicht. Laut Handbuch sollte die Meldung über Samples an
  der Decke erst ab acht kommen -- das Programm nennt drei -- und
  außerdem einen Spitzenwert nahe Vollaussteuerung verlangen; diese
  Bedingung gibt es gar nicht.

## [2.12.0-beta] - 2026-08-29

**English**

### Changed

- The window a run works out for itself is the stretch every camera
  saw, not the one any of them saw. It begins where the last camera
  came on and ends where the first one stopped.
- Whoever wants a wider stretch than that sets an In point of their
  own. It is untouched by the rule above.
- The line beside the progress bar is shortened in the middle where it
  is too wide for its field. The whole of it stands as a tooltip. How
  wide it turns out is decided by the material.
- No In point or Out point while an intro, an outro or a file marked
  "ignore this video" is in the player. The four buttons are grey and
  say why: such a file goes before or after the material.

### Tests

- The cut itself is held against numbers: 64 checks over a
  conversation built for the purpose, so the right answer is known
  beforehand. Every setting that is a number is read back out of it.
- The window a run works out had no test at all. Its arithmetic stands
  on its own now: three cameras that do not begin together, one camera
  alone, cameras that do, and two that never overlap.

---

**Deutsch**

### Geändert

- Das Fenster, das ein Lauf selbst ermittelt, ist die Strecke, die
  jede Kamera sah, nicht die, die irgendeine sah. Es beginnt, wo die
  letzte Kamera ansprang, und endet, wo die erste aufhörte.
- Wer eine längere Strecke will, setzt einen eigenen In-Punkt. Von der
  Regel darüber bleibt er unberührt.
- Die Zeile neben dem Fortschrittsbalken wird in der Mitte gekürzt, wo
  sie für ihr Feld zu breit ist. Der ganze Text steht als Tooltip. Wie
  breit sie wird, entscheidet das Material.
- Kein In- und kein Out-Punkt bei Vorspann, Abspann oder einer als
  „Video ignorieren" markierten Datei im Player. Die vier Knöpfe sind
  grau und sagen, warum: So etwas steht vor oder hinter dem Material.

### Tests

- Der Schnitt wird gegen Zahlen gehalten: 64 Prüfungen über ein eigens
  gebautes Gespräch, bei dem die richtige Antwort vorher bekannt ist.
  Jede Einstellung, die eine Zahl ist, wird zurückgelesen.
- Das ermittelte Fenster hatte keinen Test. Die Rechnung steht jetzt
  für sich: drei Kameras, die nicht zugleich beginnen,
  eine allein, gemeinsam beginnende und zwei ohne Überschneidung.

## [2.11.1-beta] - 2026-08-28

**English**

### Added

- Where a camera's timecode and the measured alignment disagree by more
  than one frame, the log names both numbers. The timecode still decides
  where the camera sits.

### Changed

- The length of the time window stands on a line of its own in the preview
  player, under "In point" and "Out point". The note that a file begins
  later or ends earlier fits again.
- The two players in the window stop each other: starting one pauses the
  other, so only ever one picture runs.
- An answer given in the window reaches the preview at once, with no run in
  between. Marking a camera as "Wide shot", or giving a voice a camera,
  moves the band underneath straight away.

### Fixed

- The window could stop answering for good. It happened where a player that
  had never started was told to pause; such a player is now left alone.
- The Resolve project put the cameras where the alignment measurement had
  them, up to 78 s from the cut that had been approved. Each camera's own
  timecode decides now.
- The timecode is read at the frame rate of the material, no longer at a
  fixed 30 frames. At 25 fps a camera stood up to 0.160 s -- four frames --
  away from its place.
- A time window set by hand stopped the Resolve project from being made at
  all. A run now writes down the window it was made with, and the check
  against older files asks for that.
- The handover file did not say which speaker sits at which camera. Every
  camera counted as "Wide shot" and the whole episode fell into one single
  shot. It now says so.
- The camera table said "Wide shot" for a camera a speaker had been given.
  Both tables and the file list are now redrawn the moment a voice is given
  a name or a camera.
- Saved at any moment other than the one the answer was picked in, a project
  came back calling everybody "Speaker 1". Speaker names and the answer
  "several speakers" are now kept at every saving.
- Switching the "Kind" of a file no longer makes the assignment sheet
  flash.

### Tests

- A test that skipped the part its machine cannot do and then fell over the
  rest was written down as skipped. Such a failure is shown and counted now,
  and it reaches the result of the suite.
- The builder writes down which ffmpeg it ran against, holds the speech
  model against the checksums shipped beside it, and stops a run on macOS
  that outstays its time limit.
- The gate test builds three windows at a time in place of six. A child
  that has said nothing for a hundred seconds is stopped, built once more
  on its own, and named in the log.
- Four new checks over the time axes: a time window shifts nothing, points
  counted from the end give a sensible length, every camera sits at its own
  timecode, and an answer reaches the cut.

---

**Deutsch**

### Hinzugefügt

- Wo der Timecode einer Kamera und die gemessene Ausrichtung um mehr als
  ein Bild auseinanderliegen, nennt das Protokoll beide Zahlen. Der
  Timecode bestimmt weiterhin, wo die Kamera sitzt.

### Geändert

- Die Länge des Zeitfensters steht im Vorschau-Player auf einer eigenen
  Zeile, unter „In-Punkt" und „Out-Punkt". Der Zusatz, dass eine Datei
  später beginnt oder früher endet, passt wieder.
- Die beiden Player im Fenster halten einander an: Wer den einen startet,
  pausiert den anderen, so läuft immer nur ein Bild.
- Eine Antwort im Fenster erreicht die Vorschau sofort, ohne Lauf. Eine
  Kamera als „Weitwinkel" zu markieren oder einer Stimme eine Kamera zu
  geben, verschiebt das Band darunter sogleich.

### Behoben

- Das Fenster konnte endgültig aufhören zu reagieren. Es geschah, wo ein
  Player pausiert werden sollte, der nie gestartet war; ein solcher
  Player wird jetzt in Ruhe gelassen.
- Das Resolve-Projekt setzte die Kameras dorthin, wo die
  Ausrichtungsmessung sie hatte, bis zu 78 s neben den freigegebenen
  Schnitt. Jetzt entscheidet der eigene Timecode jeder Kamera.
- Der Timecode wird jetzt mit der Bildrate des Materials gelesen, nicht
  mehr mit festen 30 Bildern. Bei 25 fps stand eine Kamera bis zu 0,160 s
  -- vier Bilder -- neben ihrem Platz.
- Ein von Hand gesetztes Zeitfenster verhinderte das Resolve-Projekt
  vollständig. Ein Lauf schreibt sein Zeitfenster jetzt mit, und die
  Prüfung gegen ältere Dateien fragt danach.
- Die Übergabedatei nannte nicht, welcher Sprecher an welcher Kamera
  sitzt. Jede Kamera galt als „Weitwinkel", und die ganze Folge fiel zu
  einer einzigen Einstellung zusammen. Jetzt steht es darin.
- Die Kameratabelle sagte „Weitwinkel" für eine Kamera, der ein Sprecher
  gegeben war. Beide Tabellen und die Dateiliste werden jetzt neu
  gezeichnet, sobald eine Stimme Namen oder Kamera bekommt.
- Wurde ein Projekt zu einem anderen Zeitpunkt gesichert als dem, in dem
  die Antwort gewählt wurde, hieß danach jeder „Sprecher 1". Sprechername
  und Antwort bleiben jetzt bei jedem Sichern erhalten.
- Der Wechsel des „Typs" einer Datei lässt das Zuordnungsblatt nicht mehr
  flackern.

### Tests

- Ein Test, der den unmöglichen Teil übersprang und am Rest abstürzte,
  galt als übersprungen. Solch ein Fehler wird nun gezeigt und gezählt und
  erreicht das Ergebnis der Suite.
- Der Baurechner schreibt mit, gegen welches ffmpeg er lief, hält das
  Sprachmodell gegen die mitgelieferten Prüfsummen und bricht einen Lauf
  auf macOS ab, der seine Zeit überschreitet.
- Der Gate-Test baut drei Fenster gleichzeitig statt sechs. Ein
  Kindprozess, der hundert Sekunden lang nichts gesagt hat, wird
  gestoppt, allein noch einmal gebaut und im Protokoll benannt.
- Vier neue Prüfungen der Zeitachsen: Ein Zeitfenster verschiebt nichts, vom
  Ende gezählte Punkte ergeben sinnvolle Längen, jede Kamera sitzt auf ihrem
  Timecode, eine Antwort erreicht den Schnitt.

## [2.11.0-beta] - 2026-08-26

**English**

### Added

- One speaker is enough for a cut; it took two before. With one person named
  and two or more cameras released, the box says "Cut with the wide shot".
  Five minutes give 15 shots.
- "Kind" carries "Wide shot" as a value, in the file list and beside the
  player, and `--wide-shot` says the same on the command line. A camera
  marked that way takes no speaker.
- The loudness of the finished episode is set in the window: five entries
  in the "Production" box, among them "Take from source files", which
  adjusts nothing. It starts at -16 LUFS.

### Changed

- The assignment is a tree. A recording is a row with a triangle, and the
  voices found in it fold in underneath. A click on a voice row plays that
  voice at its longest passage.
- The name field no longer picks "several speakers" by itself; it carries a
  given answer only. Where one speaker is all there is, the offer stands
  beside it.
- Picking a camera for a voice makes that row the current one, so whoever
  picks hears what they are picking. Opening the camera list and clicking
  into the name field both move the player.
- The camera table on the assignment tab drops the hints and the red. The
  file list on the first tab still says all of it, at full length.
- The legend under the cut band says who is in the picture, in place of the
  file it came out of, and it wraps: on a 1512 px window there is nothing
  left to scroll.
- The speaker table has a lid. From the fourth speaker on it scrolls inside
  itself in place of stretching the whole sheet taller.
- A guessed speaker name counts where nobody typed one, but only where it
  begins with a letter. A file called `0008A.wav` gives nothing, the field
  stays empty, and Multitrack refuses to start.
- The log entry about the reaction cut says how many questions stood in the
  transcript, how many became a cut, and why the rest did not.

### Removed

- `--platform` is gone, and with no `--lufs` nothing is adjusted any more. A
  stored call that leaned on the old -16 LUFS comes out untouched now;
  `--lufs -16` asks for the old behaviour.

### Fixed

- The name field could not be typed into where it read "several speakers":
  the first keystroke tore down the very field being typed into. It waits
  for the end of the typing now.
- The "Resolve cut" tab did not reach the run where neither "Multitrack"
  was ticked nor a separation had run: the run took the default values.
  What is typed in now reaches it.
- An In point set afterwards moved everything except the cameras: picture
  and sound stood 60 seconds apart. The gap is 0.0 now, and with no In
  point the counter-check comes out unchanged.
- Camera sound was unpacked at a fixed bit depth, wrong in both directions:
  a 24-bit camera squeezed into 16, a 16-bit camera blown up to 24. The
  depth follows the source now.
- Where there is no wide shot at all, its four numbers and its tick still
  broke a monologue with a look at somebody else's camera. They do nothing
  now, greyed out with the reason.
- The camera assignment was lost when a project was opened: recordings with
  no typed name came back without a camera. They now come back with the
  camera they were given.
- The output tab kept the colours it had started with. Started light and put
  on dark, the running text stood at a contrast of 1.00. Lines already
  written follow the appearance now.
- A camera whose speaker name is only guessed was played with the raw
  recording while its prepared track lay ready. The guess counts here as
  well now.

### Documentation

- The manual follows this in both languages: the assignment as a tree, the
  button that is gone, the cut for one speaker, `--wide-shot`, and the
  loudness field.

---

**Deutsch**

### Hinzugefügt

- Ein Sprecher genügt für einen Schnitt, zuvor waren es zwei. Bei einem
  Namen und mindestens zwei freigegebenen Kameras sagt das Feld „Schnitt mit
  dem Weitwinkel": 15 Einstellungen in fünf Minuten.
- „Typ" trägt „Weitwinkel" als Wert, in der Dateiliste wie neben dem
  Player, und `--wide-shot` sagt dasselbe auf der Kommandozeile. Eine so
  markierte Kamera nimmt keinen Sprecher an.
- Die Lautheit der fertigen Folge stellt man im Fenster ein: fünf Einträge
  im Feld „Produktion", darunter „Aus Quelldateien übernehmen", das nichts
  angleicht. Es beginnt bei -16 LUFS.

### Geändert

- Die Zuordnung ist ein Baum. Eine Aufnahme ist eine Zeile mit Dreieck, die
  darin gefundenen Stimmen klappen darunter auf. Ein Klick auf eine
  Stimmzeile spielt ihre längste Passage.
- Das Namensfeld wählt „mehrere Sprecher" nicht mehr von selbst; es trägt
  nur eine gegebene Antwort. Gibt es nur einen Sprecher, steht das Angebot
  daneben.
- Eine Kamera für eine Stimme zu wählen, macht deren Zeile zur aktuellen;
  wer wählt, hört also, was er gerade wählt. Beides bewegt den Player: die
  Kameraliste zu öffnen und ins Namensfeld zu klicken.
- Die Kameratabelle im Zuordnungsreiter lässt Hinweise und Rot weg. Die
  Dateiliste im ersten Reiter sagt weiterhin alles, in voller Länge.
- Die Legende unter dem Schnittband nennt, wer im Bild ist, statt der Datei,
  aus der es stammt, und sie bricht um: auf einem 1512 px breiten Fenster
  bleibt nichts zu rollen.
- Die Sprechertabelle hat einen Deckel. Ab dem vierten Sprecher rollt sie
  in sich selbst, statt den ganzen Reiter höher zu ziehen.
- Ein geratener Sprechername zählt, wo niemand einen tippte, aber nur wenn
  er mit einem Buchstaben beginnt. `0008A.wav` ergibt nichts, das Feld
  bleibt leer, und Multitrack verweigert den Start.
- Der Protokolleintrag zum Reaktionsschnitt nennt, wie viele Fragen im
  Transkript standen, wie viele ein Schnitt wurden, und warum die übrigen
  es nicht wurden.

### Entfernt

- `--platform` ist fort, und ohne `--lufs` wird nichts mehr angeglichen. Ein
  Aufruf, der sich auf die alten -16 LUFS verließ, bleibt nun unangetastet;
  `--lufs -16` fordert das alte Verhalten.

### Behoben

- Ins Namensfeld ließ sich nicht tippen, wo „mehrere Sprecher" darin stand:
  Der erste Anschlag zerstörte genau das Feld, in das getippt wurde. Es
  wartet jetzt das Tippen ab.
- Der Reiter „Resolve-Schnitt" erreichte den Lauf nicht, wenn weder
  „Multitrack" angehakt war noch eine Trennung gelaufen: Der Lauf nahm die
  Vorgabewerte. Jetzt kommt das Getippte an.
- Ein nachträglich gesetzter In-Punkt verschob alles außer den Kameras:
  Bild und Ton lagen 60 Sekunden auseinander. Jetzt sind es 0,0, und ohne
  In-Punkt bleibt die Gegenprobe unverändert.
- Kameraton wurde mit fester Bittiefe entpackt, in beide Richtungen falsch:
  eine 24-Bit-Kamera auf 16 gequetscht, eine 16-Bit-Kamera auf 24
  aufgeblasen. Die Tiefe folgt jetzt der Quelle.
- Wo es keinen Weitwinkel gab, unterbrachen seine vier Zahlen und sein
  Haken einen Monolog weiterhin mit dem Blick auf eine fremde Kamera. Sie
  bewirken jetzt nichts mehr und sind mit Begründung ausgegraut.
- Die Kamerazuordnung ging verloren, sobald ein Projekt geöffnet wurde:
  Aufnahmen ohne getippten Namen kamen ohne Kamera zurück. Jetzt kommen sie
  mit ihrer Kamera zurück.
- Der Ausgabereiter behielt die Farben, mit denen er begann. Startete das
  Fenster hell und wurde danach auf dunkel gestellt, stand der laufende
  Text bei einem Kontrast von 1,00. Geschriebene Zeilen folgen jetzt dem
  Aussehen.
- Eine Kamera, deren Sprechername nur geraten ist, wurde mit der rohen
  Aufnahme gespielt, obwohl ihre fertige Spur bereitlag. Der geratene Name
  zählt hier jetzt auch.

### Dokumentation

- Das Handbuch folgt dem in beiden Sprachen: Zuordnung als Baum,
  verschwundener Knopf, Schnitt für einen Sprecher, `--wide-shot`
  und das Lautheitsfeld.

## [2.10.1-beta] - 2026-08-25

**English**

### Fixed

- A recorder whose clock was never set carries a timecode of 48 seconds. The
  program said so on the first tab and used it anyway: no cut came out. The
  same material gives 218 shots now.
- The guard against a time window shorter than five seconds sat before the
  trimming, so a window outside the material slipped past and came out
  negative. It sits behind the trimming now.
- A time window that cannot work gave a length of minus 56788 seconds and no
  complaint at all. It now says where it lies and how long the material
  runs.
- The hint about an unset clock, the audio origin and the zero point judge
  such a clock by one and the same rule now.
- Where no cut comes out, the reason is now given: no speaker, no camera, no
  length, no voice with a camera, or no shot left standing once the rules
  have been applied.

---

**Deutsch**

### Behoben

- Ein Gerät, dessen Uhr nie gestellt wurde, trägt einen Timecode von 48
  Sekunden. Das Programm sagte es im ersten Reiter und nahm ihn doch: kein
  Schnitt kam heraus. Jetzt sind es 218 Einstellungen.
- Die Sperre gegen ein Zeitfenster unter fünf Sekunden griff vor dem
  Beschneiden, so dass ein Fenster außerhalb des Materials durchrutschte
  und negativ wurde. Sie greift jetzt hinter dem Beschneiden.
- Ein Zeitfenster, das so gar nicht aufgehen kann, ergab eine Länge von
  minus 56788 Sekunden, ganz ohne Klage. Es sagt jetzt, wo es liegt und
  wie lang das Material läuft.
- Der Hinweis auf eine ungestellte Uhr, der Tonursprung und der Nullpunkt
  beurteilen eine solche Uhr jetzt nach ein und derselben Regel.
- Wo kein Schnitt herauskommt, wird jetzt der Grund genannt: kein Sprecher,
  keine Kamera, keine Länge, keine Stimme mit Kamera, oder keine
  Einstellung, die nach den Regeln stehen bleibt.

## [2.10.0-beta] - 2026-08-25

**English**

### Changed

- The assignment tab carries one table where it carried two. A recording is
  a row, the voices heard in it are rows directly underneath, and the
  assignment stands on exactly one level.
- The button "Separate speakers" is gone. It is an answer in the name field
  now: type a name, or pick "several speakers". One question, with answers
  in place of a button.
- Setting a name again hides the voice rows, and picking "several speakers"
  brings them straight back, with the names and cameras that were given and
  computing nothing again.
- The "Listen" button is gone. A click on the row does the same, and lands
  in the middle of that voice's longest passage.
- The voice row no longer prints how long somebody speaks and where their
  longest passage is. Both are still worked out -- the click takes the
  player there -- and the row is a third as wide.
- "Kind" stands on both tabs with one value: what is known at import is said
  in the file list, what is noticed while watching can be changed beside the
  player.
- Where a voice is set to "do not use", its name field is greyed out. The
  name is kept and the row still plays, so the tool for deciding stays.
- The separation starts by itself only where there is exactly one candidate.
  With two cameras released it used to start on the longer of them and spend
  three minutes unasked.
- The line under the table saying that who speaks when can be worked out on
  this machine only speaks where this machine does not do the separation at
  all.
- Before a run, the box says who gets no camera of their own.

### Fixed

- Closing the window saved nothing. Two names typed, two cameras picked,
  window closed, and the project file lay unmoved. It is written when the
  window closes now.
- The dry run did not write the project either. It now writes it, so the
  hand work that stands before it is not lost.

### Documentation

- The pictures in the manual are stale and are taken again before the next
  release, no longer after every change.

---

**Deutsch**

### Geändert

- Der Zuordnungsreiter trägt eine Tabelle, wo er zwei trug. Eine Aufnahme
  ist eine Zeile, die darin gehörten Stimmen sind Zeilen direkt darunter,
  und die Zuordnung steht auf genau einer Ebene.
- Der Knopf „Sprecher trennen" ist fort. Er ist jetzt eine Antwort im
  Namensfeld: einen Namen tippen oder „mehrere Sprecher" wählen. Eine Frage,
  Antworten statt Knopf.
- Wird wieder ein Name gesetzt, verschwinden die Stimmzeilen, und „mehrere
  Sprecher" holt sie umgehend zurück, mit den vergebenen Namen und Kameras
  und ohne erneutes Rechnen.
- Der Knopf „Anhören" ist fort. Ein Klick auf die Zeile tut dasselbe und
  landet mitten in der längsten Passage dieser Stimme.
- Die Stimmzeile nennt nicht mehr, wie lange jemand spricht und wo seine
  längste Passage liegt. Beides wird weiterhin ermittelt -- der Klick führt dorthin --
  und die Zeile ist ein Drittel so breit.
- „Typ" steht in beiden Reitern mit einem Wert: Was beim Einlesen bekannt
  ist, sagt die Dateiliste; was beim Ansehen auffällt, lässt sich neben dem
  Player ändern.
- Ist eine Stimme auf „nicht verwenden" gesetzt, ist ihr Namensfeld
  ausgegraut. Der Name bleibt erhalten, die Zeile spielt weiterhin, das
  Werkzeug zum Entscheiden bleibt also.
- Die Trennung startet nur von selbst, wo es genau einen Kandidaten gibt.
  Bei zwei freigegebenen Kameras nahm sie bisher die längere von beiden und
  rechnete drei Minuten ungefragt.
- Die Zeile unter der Tabelle, nach der sich auf diesem Rechner ermitteln
  lässt, wer wann spricht, erscheint nur noch dort, wo dieser Rechner die
  Trennung gar nicht ausführt.
- Vor einem Lauf sagt das Feld, wer keine eigene Kamera bekommt.

### Behoben

- Das Schließen des Fensters sicherte nichts. Zwei Namen getippt, zwei
  Kameras gewählt, Fenster geschlossen, Projektdatei unberührt. Sie wird
  jetzt beim Schließen geschrieben.
- Der Probelauf schrieb das Projekt ebenso wenig. Er schreibt es jetzt,
  so dass die Handarbeit davor nicht verloren geht.

### Dokumentation

- Die Bilder im Handbuch sind veraltet und werden vor der nächsten Freigabe
  neu gemacht, nicht mehr nach jeder Änderung.

## [2.9.0-beta] - 2026-08-25

**English**

### Changed

- Whether a video file's audio is used is decided on the file sheet now, at
  every video, as a drop-down reading "do not use the audio". It sat on the
  assignment tab as a tick.
- Once the audio is taken, it goes through the same machinery as a
  recording read in on its own: channels measured, the stereo verdict,
  silent channels dropped, cut into tracks.
- The same field stands on the assignment tab as well and shows one value
  both ways. Judging a track means listening to it, and the player is
  there.
- Exactly one video carrying sound and no audio recording beside it: the
  field sets itself, is greyed out, and carries its reason. Adding a
  recording takes it away again.

### Fixed

- Taking the last sound away left "Start" live and the reason line empty.
  The button greys out now, wherever the sound goes, not only in a window
  that opened without any.
- The update box showed the newest release only. Somebody two versions
  behind saw one section and had to guess at the rest; the sections in
  between come down as well now.
- A folder that cannot be read while the program looks for finished tracks
  swallowed the error. It now answers like an empty folder.

### Documentation

- Three chapters of the manual follow the decision to the file sheet, in
  both languages, and name all four cases in which the field settles itself
  instead of asking.
- The channel measurement runs for every multichannel video whatever the
  field says; the field only decides whether the tracks become rows. The
  manual said otherwise.

---

**Deutsch**

### Geändert

- Ob der Ton einer Videodatei verwendet wird, entscheidet sich nun im
  Dateiblatt, bei jedem Video, als Auswahl „Ton nicht verwenden". Bisher
  saß sie im Zuordnungsreiter als Haken.
- Ist der Ton genommen, läuft er durch dieselbe Maschinerie wie eine
  eigens eingelesene Aufnahme: Kanäle gemessen, Stereo-Urteil, stumme
  Kanäle verworfen, in Spuren geschnitten.
- Dasselbe Feld steht auch im Zuordnungsreiter und zeigt an beiden Stellen
  denselben Wert. Eine Spur zu beurteilen heißt, sie zu hören, und der
  Player ist dort.
- Genau ein Video führt Ton, keine Tonaufnahme daneben: Das Feld setzt sich
  selbst, ist ausgegraut und trägt seinen Grund. Kommt eine Aufnahme dazu,
  verschwindet es wieder.

### Behoben

- Nahm man den letzten Ton fort, blieb „Start" aktiv und die
  Begründungszeile leer. Der Knopf graut jetzt aus, wohin der Ton auch
  geht, nicht nur in einem Fenster, das ohne Ton öffnete.
- Der Aktualisierungskasten zeigte nur die neueste Freigabe. Wer zwei
  Versionen zurücklag, sah einen Abschnitt und musste den Rest erraten; die
  Abschnitte dazwischen kommen jetzt mit herunter.
- Ein Ordner, der beim Suchen nach fertigen Spuren nicht lesbar ist,
  verschluckte den Fehler. Er antwortet jetzt wie ein leerer Ordner.

### Dokumentation

- Drei Kapitel des Handbuchs folgen der Entscheidung ins Dateiblatt, in
  beiden Sprachen, und nennen alle vier Fälle, in denen sich das Feld
  selbst setzt, statt zu fragen.
- Die Kanalmessung läuft bei jedem mehrkanaligen Video, gleichgültig, was das
  Feld sagt; das Feld entscheidet allein, ob die Spuren zu Zeilen werden. Das
  Handbuch sagte es anders.

## [2.8.0-beta] - 2026-08-25

**English**

### Added

- Every recording carries its own "Separate speakers" button, in a
  fifth column of the assignment table. One button used to sit in the
  player box, on a file the program picked itself.
- Several recordings no longer block the separation. The line used to
  report several microphones and vanish, so two audio files meant no
  separation at all. The button in the row starts it.
- A camera's sound can be taken as a track where there is only one
  camera. A single video without an audio recording beside it built no
  camera row, so the tick did not exist.
- Exactly one video with sound, no audio recording beside it: the tick
  sits by itself, greyed out, labelled "the only sound there is".
  Adding a recording makes it vanish with nothing left behind.

### Changed

- The state line "Separated: 4 speakers" stands in the row of the file
  it belongs to, in place of the button. It used to stand in the player
  box on the right.
- The button "Not on this machine" stands once, under the tick. It is
  the one question that belongs to the project rather than to a single
  file.
- A click on a voice row plays it. The Listen button is no longer the
  only way.

### Fixed

- Multitrack counted video files where it should have counted tracks.
  A single camera carrying two clip-on microphones was turned away
  before anything was measured. Such a run goes through now.
- One track is a valid result, and two places still turned it away.
  They now say why Multitrack falls away and hand the tracks to the
  ordinary path, which cuts by speaker.
- The channel split never ran for video files, so a camera with two
  microphones stayed a single row for good. It runs on them now.
- No sound left at all used to bring a dialog, or a halt at the end of
  the run. Start is now blocked, with the reason standing under the
  button.

### Documentation

- Four chapters followed the button, in both languages: interface,
  speech, simple path and multitrack.
- Three statements in those chapters were wrong: when the separation
  line appears, when a Mac starts the separation by itself, and what
  the column does where the separation is switched off.

---

**Deutsch**

### Hinzugefügt

- Jede Aufnahme hat in einer fünften Spalte der Zuordnungstabelle einen
  eigenen Knopf „Sprecher trennen". Bisher saß ein Knopf im Kasten des
  Players, auf einer Datei, die das Programm selbst wählte.
- Mehrere Aufnahmen sperren die Trennung nicht mehr. Bisher meldete die
  Zeile mehrere Mikrofone und verschwand; bei zwei Tondateien gab es also
  gar keine Trennung. Der Knopf in der Zeile startet sie.
- Der Ton einer Kamera lässt sich auch bei nur einer Kamera als Spur
  nehmen. Für ein einzelnes Video ohne Tonaufnahme daneben entstand
  keine Kamerazeile; das Häkchen gab es also nicht.
- Genau ein Video mit Ton, keine Tonaufnahme daneben: das Häkchen steht
  allein, grau, beschriftet „der einzige Ton, den es gibt". Kommt eine
  Aufnahme dazu, verschwindet es spurlos.

### Geändert

- Die Zustandszeile „Getrennt: 4 Sprecher" steht in der Zeile der Datei,
  zu der sie gehört, an der Stelle des Knopfes. Bisher stand sie rechts
  im Kasten des Players.
- Der Knopf „Auf diesem Rechner nicht" steht nur einmal, unter dem
  Häkchen. Das ist die eine Frage, die zum Projekt gehört und nicht zu
  einer einzelnen Datei.
- Ein Klick auf eine Stimmzeile spielt sie ab. Der Knopf „Anhören" ist
  nicht mehr der einzige Weg.

### Behoben

- Multitrack zählte Videodateien statt Spuren. Eine einzelne Kamera mit
  zwei Ansteckmikrofonen wurde abgewiesen, bevor überhaupt gemessen
  wurde. Solche Läufe gehen jetzt durch.
- Eine Spur ist ein gültiges Ergebnis; zwei Stellen wiesen sie trotzdem
  ab. Sie sagen jetzt, warum Multitrack wegfällt, und geben die Spuren
  an den gewöhnlichen Weg, der nach Sprechern schneidet.
- Die Kanaltrennung lief bei Videodateien nie; eine Kamera mit zwei
  Mikrofonen blieb deshalb für immer eine einzige Zeile. Jetzt läuft sie
  auch dort.
- War gar kein Ton mehr übrig, kam bisher ein Fenster oder ein Abbruch
  am Ende des Laufs. Jetzt ist der Start gesperrt, und der Grund steht
  unter dem Knopf.

### Dokumentation

- Vier Kapitel sind dem Knopf gefolgt, in beiden Sprachen: Oberfläche,
  Sprache, Einspur-Weg und Multitrack.
- Drei Aussagen in diesen Kapiteln waren falsch: wann die Trennzeile
  erscheint, wann ein Mac die Trennung von selbst startet und was die
  Spalte tut, wo die Trennung abgeschaltet ist.

## [2.7.1-beta] - 2026-08-25

**English**

### Fixed

- Captions were measured on Windows alone. Elsewhere they kept their
  designed width, and on Linux the "+10 s" button fell 9 pixels short
  of its own text. Every system measures now.
- A measured caption now never comes out narrower than the designed
  one, so a layout that already fits does not move.
- One test stood in for a piece of the program too thinly for Windows,
  so opening a project inside that test died there and nowhere else.
  The stand-in is complete now.

### Documentation

- The manual's pictures were taken again, all ten that changed. They
  show the voice row's duration and longest passage, the line at the
  Multitrack tick, and the two new names.

---

**Deutsch**

### Behoben

- Beschriftungen wurden nur unter Windows gemessen. Sonst behielten sie
  ihre entworfene Breite, unter Linux fehlten dem Knopf „+10 s" 9 Pixel
  für den eigenen Text. Jetzt misst jedes System.
- Eine gemessene Beschriftung fällt jetzt nie schmaler aus als die
  entworfene; ein Layout, das ohnehin passt, rückt also nicht.
- Ein Test vertrat ein Stück des Programms zu dünn für Windows; das
  Öffnen eines Projekts starb daher nur innerhalb dieses Tests. Der
  Ersatz ist jetzt vollständig.

### Dokumentation

- Die Bilder des Handbuchs wurden neu aufgenommen, alle zehn geänderten.
  Sie zeigen Dauer und längste Passage der Stimmzeile, die Zeile am
  Multitrack-Häkchen und die zwei neuen Namen.

## [2.7.0-beta] - 2026-08-25

**English**

### Added

- The simple path tells speakers apart and cuts by them. Until now the
  separation ran on the multitrack path alone. One recording, or the
  sound of a single camera, is enough.
- A line beside the Multitrack tick says why it cannot be used yet --
  one track only, or no camera sound left to take. The tick stays
  clickable rather than going grey for no reason.

### Changed

- Multitrack counts input tracks, not recordings. A track is a
  recording of its own, a channel of a multichannel recorder, or a
  camera's sound once "as a track" is ticked for it.
- The voice row showed "0:59:08,376" where a time of day was expected
  and meant that speaker's whole talking time. It gives the length and
  the position of the longest passage.
- Only one voice found is no longer a failure. Nobody hands over, so
  there is no cut; the passages travel as markers and Resolve gets the
  camera in one piece.

### Fixed

- The camera cut hung on the Multitrack tick rather than on the
  question behind it: four speakers told apart in one recording, each
  with a camera, gave an empty Resolve tab. It now cuts.
- The Resolve tab said the camera cut needed the speaker assignment
  from auphonic.com. The separation has run on this machine since
  2.0.0, and the tab no longer sends anybody there.
- A recording of more than two channels went to auphonic.com as mono.
  The count goes as measured now, with a warning that above two
  channels everything travels as one.
- With one camera not a single speaker marker was ever set: they lived
  on the multicam timeline, which one camera never builds. They sit on
  the cut timeline now, a colour per person.
- Fifteen switches carried a "multitrack only" mark in `--help`, and
  `--suffix` a "simple path only" one, although both paths use all of
  them. The marks are gone now.

### Documentation

- Six chapters carried the old restriction that speaker separation and
  the cut need multitrack. Both languages.
- The measurement notes gain "Why one recording does not become four
  tracks": muting the others puts 34.3 % of segment boundaries in a
  real speech pause, against 97 to 99 % for the audio dip.

---

**Deutsch**

### Hinzugefügt

- Der Einspur-Weg trennt Sprecher und schneidet nach ihnen. Bisher lief
  die Trennung allein auf dem Multitrack-Weg. Eine Aufnahme oder der Ton
  einer einzelnen Kamera genügt.
- Eine Zeile neben dem Multitrack-Häkchen sagt, warum es noch nicht geht
  -- nur eine Spur, oder es ist kein Kameraton mehr übrig. Das Häkchen
  bleibt anklickbar, statt grundlos grau zu werden.

### Geändert

- Multitrack zählt Eingangsspuren, keine Aufnahmen. Eine Spur ist eine
  eigene Aufnahme, ein Kanal eines mehrkanaligen Aufnahmegeräts oder der
  Kameraton, sobald „als Spur" dafür angehakt ist.
- Die Stimmzeile zeigte „0:59:08,376", wo eine Uhrzeit zu erwarten war,
  und meinte die gesamte Redezeit. Sie nennt Länge und Lage der
  längsten Passage.
- Nur eine gefundene Stimme gilt nicht mehr als Fehlschlag. Niemand gibt
  das Wort weiter, also gibt es keinen Schnitt; die Passagen reisen als
  Marker mit, und Resolve bekommt die Kamera am Stück.

### Behoben

- Der Kameraschnitt hing am Multitrack-Häkchen statt an der Frage
  dahinter: vier getrennte Sprecher in einer Aufnahme, jeder mit Kamera,
  ergaben einen leeren Resolve-Reiter. Jetzt schneidet er.
- Der Resolve-Reiter sagte, der Kameraschnitt brauche die
  Sprecherzuordnung von auphonic.com. Die Trennung läuft seit 2.0.0 auf
  diesem Rechner, und der Reiter sagt es jetzt nicht mehr.
- Eine Aufnahme mit mehr als zwei Kanälen ging als Mono zu
  auphonic.com. Die Zahl geht jetzt wie gemessen hinaus, mit dem
  Hinweis, dass mehr als zwei Kanäle als einer reisen.
- Bei einer einzigen Kamera wurde nie ein Sprechermarker gesetzt: die
  Marker lagen auf der Multicam-Timeline, die bei einer Kamera nie
  entsteht. Sie sitzen jetzt auf der Schnitt-Timeline, je Person eine
  Farbe.
- Fünfzehn Schalter trugen in `--help` den Zusatz „nur Multitrack",
  `--suffix` den Zusatz „nur Einspur-Weg", obwohl beide Wege sie alle
  nutzen. Die Zusätze sind jetzt weg.

### Dokumentation

- Sechs Kapitel trugen die alte Einschränkung, dass Sprechertrennung und
  Schnitt Multitrack brauchen. In beiden Sprachen.
- Die Messnotizen bekommen „Warum aus einer Aufnahme keine vier Spuren
  werden": Schaltet man die anderen stumm, fallen 34,3 % der Grenzen in
  eine echte Sprechpause, gegen 97 bis 99 % bei der Tonsenke.

## [2.6.1-beta] - 2026-08-24

**English**

### Fixed

- Saving the key in the macOS Keychain hung the window, and it had never
  worked. The helper asked for the word on the terminal behind the
  window. It runs without one now.
- The Keychain asks for the key and then for a repeat. One answer stored
  nothing yet reported success, so every save fell back on putting the
  key in the process list. Both answers go now.
- Connect could sit at "checking ..." for good: no call to auphonic.com
  had a time limit. Short calls now give up after sixty seconds, fifteen
  for the connection.

---

**Deutsch**

### Behoben

- Das Speichern des Schlüssels im Schlüsselbund ließ das Fenster hängen
  und hatte nie funktioniert. Das Hilfsprogramm fragte im Terminal
  hinter dem Fenster nach. Jetzt läuft es ohne Terminal.
- Der Schlüsselbund fragt den Schlüssel ab und lässt ihn wiederholen.
  Eine Antwort speicherte nichts, meldete aber Erfolg; deshalb wich jede
  Sicherung darauf aus, den Schlüssel in die Prozessliste zu stellen.
  Jetzt gehen beide Antworten hinaus.
- „Verbinden" konnte endlos bei „wird geprüft ..." stehen: kein
  Aufruf zu auphonic.com hatte eine Zeitgrenze. Kurze Aufrufe geben
  jetzt nach sechzig Sekunden auf, fünfzehn für die Verbindung.

## [2.6.0-beta] - 2026-08-24

**English**

### Added

- The whole suite runs on Linux, Windows and macOS at every push, on
  Python 3.14.7 and on 3.10. Until now all 98 tests had only ever run on
  one Mac, and the lower bound of 3.10 was a claim.
- Three checks for faults only the eye had caught: a caption wider than
  its field; an English word on the German side; a sentence glued
  together from translated fragments.
- Five checks hold a list in the manual against a table in the source.
  What the manual claims and what the program does have to agree.
- A check runs the speaker separation for real, on speech this machine
  generates itself, so a borrowed interface cannot change under us
  unnoticed again.
- An index of 79 keywords in both READMEs, and a check that keeps every
  entry pointing at a section that exists.
- Every chapter of the manual carries a picture, four of them newly
  taken. One needed an eight-channel recording made for it, one is a
  terminal showing the start of a run.
- A roadmap, in both languages, saying what comes next and what this
  program will not become.

### Changed

- The box that reported "No newer version found" shows what is in the
  version that is running. The release text comes down in the same
  answer that was asked for the version number.

### Fixed

- A coincident pair was not recognised as stereo: the gate that picks
  the loud places hung on the peak of the whole file and dropped 119
  places of 120. It hangs on the ninth decile now.
- Every Windows clone carried a broken speaker model. Git for Windows
  rewrites line endings while checking out, and one changed line made
  the model damaged. It arrives intact now.
- 62 captions did not fit their field on Windows, the worst short by 136
  pixels. At a nominally identical font the text runs 1.89 times wider
  on Windows. The fields compute their own width now.
- The speaker separation stopped on the newest pyannote, which answers
  in a different shape. Both shapes are understood now, and a third one
  is named rather than ending the run without a word.
- The ratchets counted offences instead of holding them. Swap one for
  another, the count stays and the test stays green. They hold the
  findings themselves now.
- A run against a snapshot could pull a ratchet down for good. A
  snapshot run no longer lowers one.
- The player menu killed the window on a Qt built without multimedia.
  It no longer does.

### Documentation

- Thirteen places where the manual said something the program does not
  do are corrected, and the command line table matches the program
  switch for switch, 68 against 68.
- Eleven chapters gained a section on what to do when it goes wrong.

---

**Deutsch**

### Hinzugefügt

- Die ganze Testreihe läuft bei jedem Push unter Linux, Windows und
  macOS, auf Python 3.14.7 sowie auf 3.10. Bisher liefen alle 98 Tests
  nur auf einem Mac, und die Untergrenze 3.10 war eine Behauptung.
- Drei Prüfungen für Fehler, die nur das Auge fand: eine Beschriftung
  breiter als ihr Feld; ein englisches Wort auf der deutschen Seite; ein
  Satz aus übersetzten Bruchstücken.
- Fünf Prüfungen halten eine Liste im Handbuch gegen eine Tabelle im
  Quelltext. Was das Handbuch behauptet und was das Programm tut, müssen
  übereinstimmen.
- Eine Prüfung führt die Sprechertrennung wirklich aus, an Sprache, die
  dieser Rechner selbst erzeugt. So ändert sich eine geliehene
  Schnittstelle nicht mehr unbemerkt unter uns.
- Ein Stichwortverzeichnis mit 79 Einträgen in beiden READMEs, und eine
  Prüfung, die jeden Eintrag an einem Abschnitt festhält, den es
  wirklich gibt.
- Jedes Kapitel des Handbuchs hat ein Bild, vier davon neu aufgenommen.
  Für eines entstand erst eine achtkanalige Aufnahme, eines zeigt ein
  Terminal mit dem Anfang eines Laufs.
- Ein Fahrplan, in beiden Sprachen, sagt, was als Nächstes kommt und was
  dieses Programm nie werden soll.

### Geändert

- Das Feld, das „Keine neuere Version gefunden" meldete, zeigt, was in
  der laufenden Version steckt. Der Text kommt mit der Antwort herunter,
  die auf die Frage nach der Versionsnummer folgt.

### Behoben

- Ein Koinzidenzpaar galt nicht als Stereo: das Tor für die lauten
  Stellen hing an der Spitze der ganzen Datei und verwarf 119 von 120
  Stellen. Es hängt jetzt am neunten Zehntel.
- Jede Windows-Kopie trug ein kaputtes Sprechermodell. Git for Windows
  schreibt beim Auschecken Zeilenenden um, eine geänderte Zeile genügte
  für „beschädigt". Jetzt kommt es heil an.
- 62 Beschriftungen passten unter Windows nicht in ihr Feld, die
  schlimmste um 136 Pixel. Bei nominell gleicher Schrift läuft der Text
  dort 1,89-mal breiter. Die Felder rechnen ihre Breite jetzt selbst aus.
- Die Sprechertrennung brach mit der neuesten pyannote ab, die in
  anderer Form antwortet. Beide Formen werden jetzt verstanden, eine
  dritte wird benannt, statt den Lauf wortlos zu beenden.
- Die Ratschen zählten Verstöße, statt sie festzuhalten. Wurde einer
  gegen einen anderen getauscht, blieb die Zahl stehen und der Test grün.
  Sie halten jetzt die Funde selbst.
- Ein Lauf gegen eine Momentaufnahme konnte eine Ratsche für immer
  herunterziehen. Solche Läufe senken jetzt keine mehr.
- Das Abspielmenü riss das Fenster auf einem Qt ohne Multimedia mit. Das
  geschieht jetzt nicht mehr.

### Dokumentation

- Dreizehn Stellen, an denen das Handbuch etwas behauptete, was das
  Programm gar nicht tut, sind berichtigt. Die Tabelle der Befehlszeile
  deckt sich Schalter für Schalter, 68 gegen 68.
- Elf Kapitel haben einen Abschnitt darüber bekommen, was zu tun ist,
  wenn etwas schiefgeht.

## [2.5.0-beta] - 2026-08-24

**English**

### Added

- The preflight counts samples sitting at full scale, per channel, and
  names the channel with the count. Only integer formats are counted,
  and the count holds nothing up.
- The offset between a recording and a video is also sought over the
  phase. That way is tried where the search over the envelopes comes
  back empty, as on music, which has no speech pauses.
- The log and the command line name the copy of the script that is
  running. Where several copies of one version share a log file, a
  later reader can tell which run was which.

### Changed

- A file recorded past midnight was reported as a recorder with an
  unset clock. Timecodes are now brought onto one axis before they are
  compared, so such a file falls among the others.
- A channel that carries nothing names which of the two rules caught
  it, and by how much. Both used to be reported as "below the noise
  floor", which was wrong for one of them.
- A failed offset measurement says how close it came: how many seconds
  held one voice alone, and how sharp the best find was. It used to say
  only that no pair was measurable.
- `--together` keeps the order it was given in. On one of the two ways
  through the program that row was sorted by name, so the same switch
  gave two different answers.
- The offset line names the residual beside the number of measuring
  points. Three points fit three unknowns exactly, so a residual of
  nothing there says nothing.

### Fixed

- On a Qt without multimedia the window did not come up at all. It now
  comes up, and the player entries in the menu are greyed out: nothing
  stands behind them.

### Documentation

- Thirteen places where the manual described something the program does
  not do are put right: the number of menus, a wrong default, a missing
  switch, what the preflight compares.
- Eleven chapters gained a section "When something goes wrong". It
  names what somebody does where the program jams at that point, not
  the text of the message.
- The command-line chapter was checked switch by switch. Both tables
  name all 68 switches, three that lacked a default have one, and two
  descriptions were incomplete.
- The preflight chapter says what the clipping count is: channel, count
  and peak level, integer formats only, and that it holds nothing up.
- The chapter on channels gave the spacing between the two microphones
  of a pair as 35 cm. It is measured at 30 cm, and the chapter says so
  now.

---

**Deutsch**

### Hinzugefügt

- Der Vorflug zählt die Abtastwerte am Anschlag, je Kanal, und nennt
  den Kanal samt Zahl. Gezählt wird nur in Ganzzahlformaten, und die
  Zählung hält nichts auf.
- Der Versatz zwischen Aufnahme und Video wird auch über die Phase
  gesucht. Diesen Weg geht das Programm, wo die Suche über die
  Hüllkurven leer bleibt, etwa bei Musik ohne Sprechpausen.
- Protokoll und Befehlszeile nennen die laufende Kopie des Skripts. Wo
  mehrere Kopien einer Version dasselbe Protokoll füllen, ist später
  erkennbar, welcher Lauf welcher war.

### Geändert

- Eine nach Mitternacht aufgenommene Datei galt als Rekorder mit
  ungestellter Uhr. Die Timecodes kommen jetzt auf eine Achse, bevor sie
  verglichen werden, und die Datei landet dadurch bei den anderen.
- Ein Kanal ohne Inhalt nennt, welche der beiden Regeln ihn erfasst
  hat, und um wie viel. Bisher hieß es bei beiden „unter dem
  Grundrauschen", was für einen von ihnen falsch war.
- Eine gescheiterte Versatzmessung sagt, wie nah sie kam: wie viele
  Sekunden nur eine Stimme trugen und wie scharf der beste Fund war.
  Bisher hieß es nur, kein Paar sei messbar.
- `--together` behält die angegebene Reihenfolge. Auf einem der beiden
  Wege durch das Programm wurde die Reihe nach Namen sortiert; derselbe
  Schalter gab also zwei verschiedene Antworten.
- Die Versatzzeile nennt den Restfehler neben der Zahl der Messpunkte.
  Drei Punkte passen genau auf drei Unbekannte; ein Restfehler von null
  sagt dort also nichts.

### Behoben

- Auf einem Qt ohne Multimedia kam das Fenster gar nicht hoch. Es kommt
  jetzt hoch, und die Player-Einträge im Menü sind ausgegraut: dahinter
  steht nichts.

### Dokumentation

- Dreizehn Stellen, an denen das Handbuch etwas beschrieb, was das
  Programm nicht tut, sind berichtigt: Zahl der Menüs, falscher
  Vorgabewert, fehlender Schalter, was der Vorflug vergleicht.
- Elf Kapitel haben einen Abschnitt „Wenn etwas klemmt" bekommen. Er
  nennt, was jemand tun kann, wenn es an dieser Stelle hakt -- nicht den
  Wortlaut der Meldung.
- Das Kapitel zur Befehlszeile wurde Schalter für Schalter geprüft.
  Beide Tabellen nennen alle 68 Schalter, drei ohne Vorgabewert haben
  nun einen, zwei Beschreibungen waren unvollständig.
- Das Kapitel Vorflug sagt, was die Zählung am Anschlag ist: Kanal,
  Zahl und Spitzenpegel, nur Ganzzahlformate, und dass sie nichts
  aufhält.
- Das Kapitel Kanäle nannte 35 cm Abstand zwischen den beiden
  Mikrofonen eines Paares. Gemessen sind es 30 cm, und so steht es
  jetzt dort.

## [2.4.0-beta] - 2026-08-23

**English**

### Added

- `--update-check` takes a `--no-update-check` back. A no given once
  could not be undone from the command line, and nothing said why the
  program had stopped looking.
- The update window has a tick, "Do not ask again". The program then
  stops looking by itself; asking from the menu still works, and the
  tooltip says so.
- The tick is remembered whichever button is pressed. Somebody who
  ticks it and then updates all the same still means it for the next
  version.

### Changed

- The update window shows what changed, in the window itself. It used
  to give an address and leave it at that.
- Asking from the menu is answered even where the program was told to
  stop looking by itself. `VPM_NO_UPDATE_CHECK` still holds against
  both.

### Fixed

- The German tooltip on the tick named a menu entry that does not
  exist. It now names the entry as the menu has it, so the way back can
  be found.

### Documentation

- The manual describes how the program keeps itself up to date: what is
  asked of github.com and when, that nothing is sent, what is checked
  before anything is replaced, and how to undo it.
- Both switches were missing from the command-line chapter entirely.
- The manual says how an update is undone: the running version is laid
  down beside the new one, and the way back is to put that file back
  under its own name.

---

**Deutsch**

### Hinzugefügt

- `--update-check` nimmt ein `--no-update-check` zurück. Ein einmal
  gegebenes Nein ließ sich von der Befehlszeile aus nicht mehr
  aufheben, und nirgends stand, warum nicht mehr nachgesehen wurde.
- Das Update-Fenster hat einen Haken, „Nicht mehr nachfragen". Das
  Programm sieht dann nicht mehr von selbst nach; über das Menü lässt
  sich weiter fragen, der Tooltip sagt das.
- Der Haken wird gemerkt, gleich welcher Knopf gedrückt wird. Wer ihn
  setzt und dann doch aktualisiert, meint ihn auch für die nächste
  Version.

### Geändert

- Das Update-Fenster zeigt im Fenster selbst, was sich geändert hat.
  Bisher nannte es eine Adresse und beließ es dabei.
- Die Frage aus dem Menü wird beantwortet, auch wo dem Programm das
  Nachsehen von selbst abgestellt wurde. `VPM_NO_UPDATE_CHECK` gilt
  weiter gegen beides.

### Behoben

- Der deutsche Tooltip am Haken nannte einen Menüpunkt, den es nicht
  gibt. Er nennt ihn jetzt so, wie er im Menü steht, damit der Weg
  zurück auffindbar ist.

### Dokumentation

- Das Handbuch beschreibt, wie das Programm sich aktuell hält: was wann
  von github.com verlangt wird, dass nichts gesendet wird, was vor dem
  Ersetzen geprüft wird und wie es rückgängig geht.
- Beide Schalter fehlten im Kapitel zur Befehlszeile ganz.
- Das Handbuch sagt, wie ein Update rückgängig gemacht wird: Die
  laufende Version wird daneben abgelegt, der Weg zurück ist, diese
  Datei wieder unter ihrem Namen abzulegen.

## [2.3.0-beta] - 2026-08-23

**English**

### Added

- The model for the speaker separation is fetched at the first
  separation, out of the same repository as the program, and held
  against the sums that come with it. It is never fetched twice.
- `L` plays forward and doubles the speed on every press, 1x to 8x; `K`
  stops and goes back to normal. The speed stands on the play button.
  For backwards there is no key.
- The first and the third sheet carry names a reading program can
  announce: the file list, the production fields, the eight cut
  numbers, the four choices and the Resolve button.

### Changed

- Nothing is asked of auphonic.com unless somebody asks for it. A
  remembered key used to be checked at start-up; the presets are
  fetched as the list is opened.
- A key is looked at before it goes out: whether one is set at all, and
  whether it carries a line break, a space in the middle or a character
  nobody can type. Not its length.
- The slider under the player that shows the chosen window takes its
  colours from the colour scheme. Its outline against the handle went
  from 2.94 to 5.17 on light, 6.03 on dark.
- On dark that slider no longer draws a white band across the window.
- Warning text on the light scheme is darker, measured at 5.77 against
  the ground it sits on, where it used to fall under 4.5. The dark
  scheme keeps the colour it had.
- A switch from light to dark arrives while the program runs. The
  scheme was read once at start, and the way back to light was burned
  in.
- The type in the "One more speaker in" row is made smaller only where
  the row would otherwise grow wider than the player leaves it.

### Removed

- `install.py`. The program brings what it needs by itself: numpy and
  PySide6 at the first start, ffmpeg over the package manager, the
  model at the first separation. One file to fetch, one to keep.

### Fixed

- The column "as a track" in the camera table cut its own heading off.
  It is now given the room the heading needs, out of the style rather
  than out of a fixed number.

### Tests

- A new test holds one version number across the program, the changelog
  and both READMEs, the shape of the changelog, every picture in it,
  and the rule that the key never reaches a file.
- A new test covers what is turned away before a key goes out, what
  gets through, that no timer fetches presets at start-up, and that an
  unasked fetch opens no box.
- The picture scripts looked for a tab, found none and returned in
  silence, so the wrong sheet was photographed. They stop and say which
  sheets are on offer.
- The test for a first start does what the manual tells a stranger to
  do: fetch the one file and start it. It used to fetch the installer
  and run that.

### Documentation

- The screenshots showed a window that exists nowhere. They are taken
  in the real style and the real palette now, with the menu bar at the
  top of the screen.
- The requirements chapter says what the program fetches for itself,
  when, and how much, in both languages. It described the installer,
  which is gone.
- The section on ffmpeg named static-ffmpeg as what happens where
  ffmpeg is missing. The package manager comes first and is asked
  about; static-ffmpeg is the way out where there is none.

---

**Deutsch**

### Hinzugefügt

- Das Modell für die Sprechertrennung kommt bei der ersten Trennung,
  aus demselben Repository wie das Programm, und wird gegen die
  mitgelieferten Prüfsummen gehalten. Geholt wird es nur einmal.
- `L` spielt vorwärts, jeder weitere Druck verdoppelt die
  Geschwindigkeit, 1x bis 8x; `K` hält an und stellt sie zurück. Sie
  steht auf dem Abspielknopf, für rückwärts gibt es keine Taste.
- Der erste und der dritte Reiter tragen Namen, die ein
  Vorleseprogramm ansagen kann: Dateiliste, Produktionsfelder, die acht
  Schnittzahlen, die vier Auswahlfelder, der Resolve-Knopf.

### Geändert

- Von auphonic.com wird nichts verlangt, solange niemand danach fragt.
  Ein gemerkter Schlüssel wurde bisher beim Start geprüft; die Presets
  kommen beim Öffnen der Liste.
- Ein Schlüssel wird angesehen, bevor er hinausgeht: ob überhaupt einer
  gesetzt ist, ob er einen Zeilenumbruch, ein Leerzeichen mittendrin
  oder ein untippbares Zeichen trägt. Nicht seine Länge.
- Der Regler unter dem Player, der das gewählte Fenster zeigt, nimmt
  seine Farben aus dem Farbschema. Sein Umriss gegen den Griff ging von
  2,94 auf 5,17 im hellen und auf 6,03 im dunklen Schema.
- Auf dunkel zieht dieser Regler kein weißes Band mehr quer durchs
  Fenster.
- Der Warntext im hellen Schema ist dunkler, gemessen 5,77 gegen den
  Untergrund, wo er bisher unter 4,5 fiel. Das dunkle Schema behält
  seine Farbe.
- Ein Wechsel von hell zu dunkel kommt an, während das Programm läuft.
  Das Schema wurde einmal beim Start gelesen; der Weg zurück zu hell
  lag fest.
- Die Schrift in der Zeile „Ein Sprecher mehr in" wird nur dort
  kleiner, wo die Zeile sonst breiter würde, als der Player ihr Platz
  lässt.

### Entfernt

- `install.py`. Das Programm holt selbst, was es braucht: numpy und
  PySide6 beim ersten Start, ffmpeg über die Paketverwaltung, das
  Modell bei der ersten Trennung. Eine Datei holen, eine behalten.

### Behoben

- Die Spalte „als Spur" in der Kameratabelle schnitt ihre eigene
  Überschrift ab. Sie bekommt jetzt so viel Platz, wie die Überschrift
  braucht, aus dem Stil statt aus einer festen Zahl.

### Tests

- Ein neuer Test hält Programm, Änderungsbericht und beide READMEs auf
  einer Versionsnummer fest, dazu die Form des Berichts, jedes Bild
  darin und die Regel, dass der Schlüssel in keine Datei kommt.
- Ein neuer Test deckt ab, was vor dem Senden eines Schlüssels
  abgewiesen wird, was durchgeht, dass beim Start kein Zeitgeber
  Presets holt, und dass ein ungefragter Abruf kein Fenster öffnet.
- Die Bildskripte suchten einen Reiter, fanden keinen und kehrten stumm
  zurück; so wurde der falsche Reiter fotografiert. Sie halten jetzt an
  und sagen, welche Reiter es gibt.
- Der Test für einen ersten Start tut, was das Handbuch einem Fremden
  sagt: die eine Datei holen und starten. Bisher holte er den Installer
  und führte diesen aus.

### Dokumentation

- Die Bildschirmfotos zeigten ein Fenster, das es nirgends gibt. Sie
  entstehen jetzt im echten Stil und mit der echten Palette, die
  Menüleiste oben am Bildschirm.
- Das Kapitel „Was gebraucht wird" sagt in beiden Sprachen, was sich das
  Programm selbst holt, wann und wie viel. Es beschrieb den Installer,
  den es nicht mehr gibt.
- Der Abschnitt zu ffmpeg nannte static-ffmpeg als das, was bei
  fehlendem ffmpeg geschieht. Zuerst kommt die Paketverwaltung, mit
  Nachfrage; static-ffmpeg hilft, wo es keine Paketverwaltung gibt.

## [2.2.0-beta] - 2026-08-23

**English**

### Added

- A menu bar with seventeen entries. About, Settings and Help stand
  where a Mac expects them, at the top of the screen, rather than
  nowhere at all.
- Space plays and pauses, the arrows step a frame, with Shift a second,
  with Alt ten. I and O set the marks, Shift+I and Shift+O jump to
  them. Only the player takes them, never a name field.
- Ctrl+O adds files, Ctrl+R starts a run, Ctrl+Shift+R the dry run,
  Ctrl+1 to Ctrl+3 pick a sheet, Ctrl+, opens the settings. On a Mac it
  is Command.
- Seventeen controls carry a name a reading program can announce. They
  had none.
- `VPM_CACHE` puts what the program keeps from one run to the next
  somewhere else. A test run leaves no envelopes or measurements in the
  cache of whoever started it.

### Changed

- The reason a run cannot start stands in the window, in full. It used
  to sit in the tooltip of the start button, out of reach of the
  keyboard.
- On the second sheet a file that does not fit is no longer red and
  nothing else. It carries the same sentence the first sheet writes
  beside it.
- The second sheet asks for 743 pixels of width rather than 1800, so it
  fits on a laptop.
- The name of the recording moved out of the "One more speaker in"
  button into a chooser beside it.

### Fixed

- brew asked a second time and waited for an answer nobody was there to
  give. It is now told to ask nothing, so a run with nobody in front of
  it goes through.

### Tests

- The test on the start reason held the old behaviour in place: it
  checked that the footer points at the tooltip. It checks that the
  footer names the reason itself.

### Documentation

- The manual has a section on the menu and the keys, in both languages.
  There was none.
- All five screenshots taken again, English and German. The menu bar
  and the state line at the bottom changed on every one of them.

---

**Deutsch**

### Hinzugefügt

- Eine Menüleiste mit siebzehn Einträgen. Über, Einstellungen und Hilfe
  stehen dort, wo ein Mac sie erwartet, oben am Bildschirm, statt gar
  nicht.
- Leertaste spielt und hält, die Pfeile springen ein Bild, mit Umschalt
  eine Sekunde, mit Alt zehn. Marken setzen I und O, mit Umschalt
  springt man zu ihnen. Alles nur im Player, nie im Namensfeld.
- Strg+O fügt Dateien hinzu, Strg+R startet, Strg+Umschalt+R den
  Probelauf, Strg+1 bis Strg+3 wählen einen Reiter, Strg+, öffnet die
  Einstellungen. Auf dem Mac ist es Befehl.
- Siebzehn Bedienelemente tragen einen Namen, den ein Vorleseprogramm
  ansagen kann. Bisher hatten sie keinen.
- `VPM_CACHE` legt das, was das Programm von Lauf zu Lauf behält, an
  einen anderen Ort. Ein Testlauf lässt keine Hüllkurven und Messungen
  im Zwischenspeicher dessen, der ihn startete.

### Geändert

- Der Grund, warum ein Lauf nicht starten kann, steht im Fenster,
  vollständig. Bisher stand er im Tooltip des Start-Knopfes, für die
  Tastatur unerreichbar.
- Auf dem zweiten Reiter ist eine Datei, die nicht passt, nicht mehr
  nur rot. Sie trägt denselben Satz, den der erste Reiter
  danebenschreibt.
- Der zweite Reiter verlangt 743 Pixel Breite statt 1800 und passt
  damit auf einen Laptop.
- Der Name der Aufnahme ist aus dem Knopf „Ein Sprecher mehr in" in ein
  Auswahlfeld daneben gewandert.

### Behoben

- brew fragte ein zweites Mal und wartete auf eine Antwort, die niemand
  gab. Es wird jetzt angewiesen, nichts zu fragen, so dass ein Lauf ohne
  Aufsicht durchläuft.

### Tests

- Der Test zum Startgrund hielt das alte Verhalten fest: er prüfte, ob
  die Fußzeile auf den Tooltip zeigt. Er prüft jetzt, ob die Fußzeile
  den Grund selbst nennt.

### Dokumentation

- Das Handbuch hat einen Abschnitt zu Menü und Tasten, in beiden
  Sprachen. Bisher gab es keinen.
- Alle fünf Bildschirmfotos wurden neu aufgenommen, englisch und
  deutsch. Menüleiste und Zustandszeile am unteren Rand haben sich auf
  jedem von ihnen geändert.

## [2.1.0-beta] - 2026-08-23

**English**

### Added

- The program looks whether a newer release is out and offers to fetch
  it and start again. It asks at the start of a run, never during one,
  and the file that ran stays beside the new one.
- `--no-update-check` switches that looking off. A no given in the
  window is remembered, so the question does not come back at every
  start.
- `install.py` fetches the newest release by default rather than the
  tip of the main branch. `--ref` takes a tag or a branch, and a
  pre-release never counts as the newest.

### Changed

- ffmpeg is brought in by the system's own package manager, after
  asking: brew on macOS, apt-get, dnf, zypper or pacman on Linux. On
  Windows the program offers to open ffmpeg.org.
- Where no package manager is found, static-ffmpeg is offered, and the
  question says what that brings: sixteen packages and a program
  fetched from a private repository, checked against nothing.
- `VPM_INSTALL_TOOLS=1` answers those questions with yes in advance,
  for a run with nobody sitting in front of it.
- A package removed only in part counted as installed. The program
  skipped it and failed later on. Such remains no longer pass as a
  working package.

### Fixed

- The message that ffmpeg was being installed came at every start, even
  though nothing was being installed. It now appears only where ffmpeg
  is really fetched.

### Tests

- A test file for the update check, 24 checks: which release counts as
  the newer one, and that a no is remembered. Nothing in it touches the
  network.
- `first_run.sh` also removes what a package fetched after its own
  installation, and the entry in the keychain. A machine can be put
  back into the state before the program ever ran.
- The suite stops with a clear word instead of going red where ffmpeg
  is missing.

---

**Deutsch**

### Hinzugefügt

- Das Programm sieht nach, ob es eine neuere Version gibt, holt sie auf
  Wunsch und startet neu. Gefragt wird nur zu Beginn eines Laufs, und
  die Datei, die lief, bleibt neben der neuen liegen.
- `--no-update-check` stellt die Suche nach neuen Versionen ab. Ein
  Nein im Fenster wird gemerkt, die Frage kommt also nicht bei jedem
  Start wieder.
- `install.py` holt standardmäßig die neueste Version statt der Spitze
  des Hauptzweigs. `--ref` nimmt eine Marke oder einen Zweig; eine
  Vorabversion gilt nie als die neueste.

### Geändert

- ffmpeg kommt aus der Paketverwaltung des Systems, nach Rückfrage:
  brew auf macOS, apt-get, dnf, zypper oder pacman auf Linux. Unter
  Windows bietet das Programm an, ffmpeg.org zu öffnen.
- Wo keine Paketverwaltung da ist, wird static-ffmpeg angeboten, und
  die Frage sagt, was das mitbringt: sechzehn Pakete und ein Programm
  aus einer privaten Quelle, gegen nichts geprüft.
- `VPM_INSTALL_TOOLS=1` beantwortet diese Fragen im Voraus mit Ja, für
  einen Lauf, vor dem niemand sitzt.
- Ein nur halb entferntes Paket galt als installiert. Das Programm
  übersprang es und scheiterte später. Solche Reste gehen nicht mehr
  als ein arbeitsfähiges Paket durch.

### Behoben

- Die Meldung, ffmpeg werde installiert, kam bei jedem Start, obwohl
  nichts installiert wurde. Sie erscheint jetzt nur dort, wo ffmpeg
  wirklich geholt wird.

### Tests

- Eine Testdatei für die Update-Prüfung, 24 Prüfungen: welche Version
  die neuere ist, und ob ein Nein gemerkt wird. Nichts darin geht ins
  Netz.
- `first_run.sh` entfernt auch, was ein Paket nach der eigenen
  Installation nachlädt, sowie den Eintrag im Schlüsselbund. So kommt
  ein Rechner in den Zustand vor dem allerersten Lauf zurück.
- Die Testreihe hält mit einem klaren Wort an, statt rot zu werden,
  wenn ffmpeg fehlt.

## [2.0.0-beta] - 2026-08-23

**English**

### Added

- `install.py` brings the program and the voice separation model in one
  command, on macOS, Windows and Linux alike. Every file is held
  against a checksum and dropped where it does not match.
- `--check` holds an installation already there against those sums,
  `--to` puts it somewhere else, `--no-start` stops before the program
  is handed control.
- The voice separation model travels with the program: five files,
  33 MB, with licence and checksums beside them. No account, no token,
  nothing fetched while it runs.
- The program recognises speech itself. On macOS 26 it uses the
  recogniser the system brings, which takes 22 seconds for an hour of
  audio and needs nothing installed.
- Everywhere else speech recognition falls back on Whisper
  (`large-v3-turbo`, 1.5 GB), measured at six times real time on a
  processor. The words carry their punctuation.
- The program tells the voices apart itself, on this machine, uploading
  nothing. Held against the single microphones of two interviews,
  98.7 per cent of 45 473 words land on the right person.
- A voice table under the assignment, one row per voice found. The rows
  are called "Speaker 1, 2 ..." until somebody names them, and each row
  has a button to listen.
- Four answers on tab 3 decide what is shown while nobody is clearly
  speaking: the wide shot, the listener, the two alternating, or no
  change at all.
- The wide shot is placed by the language. It enters at a sentence
  boundary, holds five seconds at least, leaves at a sentence end -- at
  the latest at a clause break by fifteen seconds.
- The exact frame comes from the sound: the quietest stretch near the
  target is taken. It hits a speech pause 97 to 99 times in a hundred,
  where the recogniser's word boundary manages 42 to 46.
- A reaction cut: where somebody asks a question and another answers,
  the picture goes to the answering person while the question is still
  running.

### Changed

- A speaker has to hold the floor for one and a half seconds before the
  picture follows. A short "mhm" used to switch the camera, and the
  picture then stuck for three seconds.
- A short shot is merged into the shot that follows it, no longer into
  the one going before. Over four runs the time the wrong camera is
  shown falls from 326 to 99 seconds.
- Where the voices cannot be told apart cleanly, the program shows the
  wide shot rather than guessing. The longest stretch on the wrong
  person falls from eight seconds to 2.3.
- `--wide-after` is 40 seconds rather than 45. `--wide-length` is the
  shortest time the wide shot is held, no longer its length.
- One "Minimum Edit Duration" for everything. The window offered three
  seconds while a run started without the window cut at 1.2, so the two
  disagreed.
- The opening wide shot survives a recognition that comes in pieces. It
  used to end at the first four-second block of another voice, in one
  measured case 88 seconds early.

### Removed

- auphonic.com no longer supplies speaker data. It counted 0.6 pauses a
  minute where our own measurement finds 16. Levelling, noise removal
  and transcription stay untouched.
- `--wide-min` and `--wide-flow` are gone. With a five-second minimum
  hold they could no longer change anything.

### Fixed

- The preview died on every call with "Preview not possible:
  'min-shot'". It now runs again.
- On macOS the time axis could not find a file whose folder is reached
  through a link: the same file carried two names, one of them unknown
  to the search. It now finds the file.
- Four labels of the preview player stayed English in the German
  window. They now come in German too.
- The button row "One more speaker in ..." grew with every recording
  and pushed the preview player off the edge. The file name sits in a
  chooser now, so the row keeps its width.

### Tests

- Eight new test files, 90 in all. One of them speaks its own audio
  rather than shipping a sound file; another holds the preview's cut
  list against the one the run produces.
- `first_run.sh` puts a machine back into the state before the program
  ever ran: environment, caches, packages, models, keychain. It is not
  part of the suite.

---

**Deutsch**

### Hinzugefügt

- `install.py` bringt Programm und Stimmentrennungsmodell in einem
  Befehl, auf macOS, Windows wie Linux. Jede Datei wird gegen eine
  Prüfsumme gehalten und verworfen, wo sie nicht passt.
- `--check` prüft eine vorhandene Installation gegen diese Summen,
  `--to` legt sie woanders ab, `--no-start` hält vor der Übergabe an
  das Programm an.
- Das Modell zur Stimmentrennung reist mit dem Programm: fünf Dateien,
  33 MB, mit Lizenz und Prüfsummen daneben. Kein Konto, kein Token,
  nichts wird zur Laufzeit geholt.
- Das Programm erkennt Sprache selbst. Auf macOS 26 nimmt es die
  Erkennung des Systems; die braucht 22 Sekunden für eine Stunde Ton,
  und installiert werden muss dafür nichts.
- Sonst greift die Erkennung auf Whisper zurück (`large-v3-turbo`,
  1,5 GB), gemessen bei sechsfacher Echtzeit auf einem Prozessor. Die
  Wörter tragen ihre Satzzeichen.
- Das Programm unterscheidet die Stimmen selbst, auf dem Rechner, ohne
  etwas hochzuladen. Gegen die Einzelmikrofone zweier Interviews
  gehalten, sitzen 98,7 Prozent von 45 473 Wörtern richtig.
- Eine Stimmentabelle unter der Zuordnung, eine Zeile je gefundene
  Stimme. Die Zeilen heißen „Sprecher 1, 2 ...", bis jemand sie
  benennt, und jede Zeile hat einen Knopf zum Anhören.
- Vier Antworten auf dem dritten Reiter entscheiden, was zu sehen ist,
  solange niemand deutlich spricht: der Weitwinkel, der Zuhörer, beide
  im Wechsel oder gar kein Wechsel.
- Der Weitwinkel wird von der Sprache gesetzt. Er kommt an einer
  Satzgrenze, hält mindestens fünf Sekunden und geht an einem Satzende,
  spätestens nach fünfzehn Sekunden an einer Teilsatzgrenze.
- Das genaue Bild kommt aus dem Ton: Die leiseste Stelle nahe am Ziel
  wird genommen. Sie trifft 97- bis 99-mal von hundert eine
  Sprechpause, wo die Wortgrenze der Erkennung auf 42 bis 46 kommt.
- Ein Reaktionsschnitt: Stellt jemand eine Frage und antwortet ein
  anderer, geht das Bild auf den Antwortenden, während die Frage noch
  läuft.

### Geändert

- Ein Sprecher muss anderthalb Sekunden das Wort halten, bevor das Bild
  folgt. Ein kurzes „mhm" schaltete die Kamera um, und das Bild blieb
  dann drei Sekunden stehen.
- Eine kurze Einstellung geht in die folgende auf, nicht mehr in die
  vorangehende. Über vier Läufe fällt die Zeit, in der die falsche
  Kamera zu sehen ist, von 326 auf 99 Sekunden.
- Wo sich die Stimmen nicht sauber trennen lassen, zeigt das Programm
  den Weitwinkel, statt zu raten. Die längste Strecke auf der falschen
  Person fällt von acht auf 2,3 Sekunden.
- `--wide-after` steht auf 40 statt auf 45 Sekunden. `--wide-length`
  ist die kürzeste Haltezeit des Weitwinkels, nicht mehr seine Länge.
- Eine „Mindestschnittdauer" für alles. Das Fenster bot drei Sekunden,
  ein ohne Fenster gestarteter Lauf schnitt auf 1,2; die beiden gingen
  also auseinander.
- Der einleitende Weitwinkel übersteht eine Erkennung, die in Stücken
  kommt. Er endete am ersten Vier-Sekunden-Block einer anderen Stimme,
  in einem gemessenen Fall 88 Sekunden zu früh.

### Entfernt

- auphonic.com liefert keine Sprecherdaten mehr. Der Dienst zählte
  0,6 Pausen je Minute, wo die eigene Messung 16 findet. Pegelung,
  Rauschentfernung und Transkription bleiben unberührt.
- `--wide-min` und `--wide-flow` sind fort. Bei einer Mindesthaltezeit
  von fünf Sekunden konnten sie nichts mehr bewirken.

### Behoben

- Die Vorschau starb bei jedem Aufruf mit „Vorschau nicht möglich:
  'min-shot'". Sie läuft jetzt wieder.
- Auf macOS fand die Zeitachse eine Datei nicht, deren Ordner über eine
  Verknüpfung erreicht wird: Dieselbe Datei trug zwei Namen, einer
  davon war der Suche unbekannt. Sie findet die Datei jetzt.
- Vier Beschriftungen des Vorschau-Players blieben im deutschen
  Fenster englisch. Sie sind jetzt übersetzt.
- Die Knopfreihe „Ein Sprecher mehr in ..." wuchs mit jeder Aufnahme
  und schob den Vorschau-Player über den Rand. Der Dateiname sitzt
  jetzt in einer Auswahlliste, die Reihe bleibt gleich breit.

### Tests

- Acht neue Testdateien, 90 im Ganzen. Eine spricht ihren Ton selbst
  ein, statt eine Tondatei mitzuliefern; eine andere hält die
  Schnittliste der Vorschau gegen die des Laufs.
- `first_run.sh` versetzt einen Rechner in den Zustand vor dem
  allerersten Lauf: Umgebung, Zwischenspeicher, Pakete, Modelle,
  Schlüsselbund. Es gehört nicht zur Testreihe.

## [1.1.0-beta] - 2026-08-22

**English**

### Changed

- "Settings ..." stands in the footer now, with the other buttons at
  the bottom right, flat and set apart. It sat beside the tabs in the
  top right corner.

### Fixed

- "Start" and "Dry run" look switched off in the same way now. "Start"
  used to keep its filled shape and its colour while the other went
  pale, so one of the pair still looked pressable.
- The label on a switched-off button now reaches 4.7 in contrast
  against its own background, where the old grey on grey gave 2.6.
- "No files or project opened yet" now stands in quiet type rather than
  in warning colour. The warning colour is kept for a real lack.
- The quiet grey was darkened a shade so it still reads on the footer:
  now 4.5 in contrast against the footer's own grey, where it was 4.0.

---

**Deutsch**

### Geändert

- „Einstellungen ..." steht nun in der Fußzeile, bei den anderen
  Knöpfen unten rechts, flach und abgesetzt. Bisher saß es neben den
  Reitern oben rechts.

### Behoben

- „Start" und „Probelauf" sehen jetzt gleich abgeschaltet aus. „Start"
  behielt seine gefüllte Form und seine Farbe, während der andere blass
  wurde; einer der beiden sah noch drückbar aus.
- Die Beschriftung eines abgeschalteten Knopfes erreicht jetzt 4,7 im
  Kontrast gegen ihren eigenen Untergrund, wo das alte Grau auf Grau
  2,6 ergab.
- „Noch keine Dateien oder Projekt geöffnet" steht jetzt in ruhiger
  Schrift statt in Warnfarbe. Die Warnfarbe bleibt dem echten Mangel.
- Das ruhige Grau wurde eine Spur dunkler, damit es auf der Fußzeile
  lesbar bleibt: jetzt 4,5 im Kontrast gegen deren eigenes Grau, vorher
  4,0.

## [1.0.0-beta] - 2026-08-22

**English**

### Changed

- The words on screen are DaVinci Resolve's: "In point" and "Out point"
  for the marks, "Mark In" and "Mark Out" for the buttons that set
  them.
- The shortest a shot may be is "Minimum Edit Duration", the wide
  setting "Wide shot". Both come from Resolve's own window.
- The switches are `--in-point`, `--out-point` and
  `--min-edit-duration`; a project file holds `in_point` and
  `out_point`.
- The project file format is at **3** now. An older project file is
  refused with a clear message rather than read by halves.
- A stereo pair has to prove itself three ways. What two channels hear
  together no longer suffices: the spacing has to stay under 0.3 m, and
  the pair has to stand out from its neighbours.
- In a project the program creates, the colour space follows the
  material: HDR material gets an HDR output space, SDR material
  Rec.709. A project somebody else set up is never touched.

### Fixed

- The Resolve part crashed where two cameras carried the same file
  name. It no longer stops there.
- The same collision made the self check report a camera as not
  inserted although its clip was on the timeline. The clip is now
  found.
- The footer bar stood 170 pixels high however wide the window was. It
  follows the window now.
- The run bar of a fresh run could open at full. It now starts empty.

### Tests

- The suite runs in a fifth of the time. Four tests waited on the clock
  rather than on a condition: 112 seconds became 33.
- One test had quietly stopped checking anything. It checks again.

---

**Deutsch**

### Geändert

- Die Wörter auf dem Bildschirm sind die von DaVinci Resolve: „In-Punkt"
  und „Out-Punkt" für die Marken, „In markieren" und „Out markieren"
  für die Knöpfe, die sie setzen.
- Die kürzeste Dauer einer Einstellung heißt „Mindestschnittdauer", die
  weite Einstellung „Weitwinkel". Beide Wörter stehen so im deutschen
  Resolve-Fenster.
- Die Schalter heißen `--in-point`, `--out-point` und
  `--min-edit-duration`; in der Projektdatei stehen `in_point` und
  `out_point`.
- Das Format der Projektdatei steht nun auf **3**. Eine ältere
  Projektdatei wird mit klarer Meldung abgelehnt, statt halb gelesen zu
  werden.
- Ein Stereopaar muss sich auf drei Wegen beweisen. Was zwei Kanäle
  gemeinsam hören, genügt nicht mehr: Der Abstand muss unter 0,3 m
  bleiben, und das Paar muss sich von seinen Nachbarn abheben.
- In einem Projekt, das das Programm selbst anlegt, folgt der Farbraum
  dem Material: HDR bekommt einen HDR-Ausgaberaum, SDR bekommt
  Rec.709. Ein Projekt aus fremder Hand bleibt unangetastet.

### Behoben

- Der Resolve-Teil stürzte ab, wo zwei Kameras denselben Dateinamen
  trugen. Er stürzt dort jetzt nicht mehr ab.
- Dieselbe Kollision ließ die Selbstprüfung eine Kamera als nicht
  eingefügt melden, obwohl ihr Clip auf der Timeline lag. Der Clip wird
  jetzt gefunden.
- Die Fußzeile war 170 Bildpunkte hoch, wie breit das Fenster auch war.
  Sie folgt jetzt dem Fenster.
- Der Laufbalken eines frischen Laufs konnte voll aufgehen. Er beginnt
  jetzt leer.

### Tests

- Die Testreihe läuft in einem Fünftel der Zeit. Vier Tests warteten
  auf die Uhr statt auf eine Bedingung: Aus 112 Sekunden wurden 33.
- Ein Test hatte still aufgehört, überhaupt etwas zu prüfen. Er prüft
  wieder.

## Before 1.0

**English**

What follows is the record from before the first release, counted as
0.x. The versions are the ones that really happened, in the order they
happened, and only their numbers were brought into this scheme. The
program was written for one podcast then and never handed to anybody.

The record starts at 0.1.0. Everything before that was built without a
changelog, and putting it together after the fact would mean guessing
at dates and wording. What the older versions did is in the manual,
which describes the program as it stands rather than how it got there.

**Deutsch**

Was folgt, ist der Stand vor der ersten Freigabe, als 0.x gezählt. Es
sind die Versionen, die es wirklich gab, in der Reihenfolge, in der es
sie gab; nur ihre Nummern sind nachträglich in dieses Schema gebracht.
Das Programm entstand damals für einen einzigen Podcast und
wurde nie aus der Hand gegeben.

Der Bericht beginnt bei 0.1.0. Alles davor entstand ohne Changelog,
und es nachträglich zusammenzusetzen hieße, Datum und Wortlaut zu
raten. Was die älteren Versionen taten, sagt das Handbuch: es
beschreibt das Programm, wie es ist, nicht seinen Weg dorthin.

## 0.11.1

**English**

### Fixed

- The bar in the footer could start a run at nine tenths and then fall
  back: a run begun while the finished bar still stood full took over
  the old plan. Plan and bar are now cleared first.

---

**Deutsch**

### Behoben

- Der Balken in der Fußzeile konnte einen Lauf bei neun Zehnteln
  beginnen und dann zurückfallen: Ein Lauf beim vollen Balken übernahm
  den alten Plan. Plan und Balken werden jetzt zuerst geleert.

## 0.11.0

**English**

Findings from a review of the DaVinci Resolve and render part, read
from the source, none of them confirmed against a running Resolve.

### Changed

- The project is ready for a public repository: a one-off cleanup
  script is gone, no personal name stands in the test material, and
  stray media files stay out.

### Fixed

- A camera with no rendered file lost its measured offset and sat at
  the start of the time axis. The offset is now looked up under the
  source path too; what stays unknown is named in the log.
- Frame width and height were each taken as their own largest value, so
  a landscape and a portrait camera together gave a square frame neither
  had recorded. The largest real frame is now used.
- Where the earliest camera starts before the "In point", the timeline
  start moves back. The report "For checking" measured from the old
  start, so its distances were wrong. It now uses the new one.
- The Full-Mix fallback takes a camera's audio, and that audio begins
  where the camera began, not at the "In point". It ran against the
  picture. The head is now trimmed off.
- A project the program creates itself carried Resolve's factory
  Rec.709, so HDR material would have been delivered as eight bit SDR
  in silence. On its own projects the material now wins.
- The render target was named after the production alone, so a second
  run wrote over the first delivery. The name now counts up, and the
  log says how it reads.
- Clips were found again by file name: two cameras each recording
  C0001.MP4 landed on one clip, and the second showed the first one's
  picture. The real path now decides.

### Tests

- The tests for the timeline can report what landed on a track, which
  is what the timeline report in the program asks of them.

---

**Deutsch**

Befunde aus einer Durchsicht des Resolve- und Ausgabeteils, aus dem
Quelltext gelesen, an einem laufenden Resolve nicht geprüft.

### Geändert

- Das Projekt ist für ein öffentliches Repository bereit: ein
  einmaliges Aufräumskript ist fort, kein persönlicher Name mehr im
  Testmaterial, herumliegende Mediendateien bleiben draußen.

### Behoben

- Eine Kamera ohne ausgegebene Datei verlor ihren gemessenen Versatz
  und saß am Anfang der Zeitachse. Der Versatz wird jetzt auch unter
  dem Quellpfad gesucht; Unbekanntes nennt das Protokoll.
- Bildbreite und Bildhöhe wurden je für sich auf ihr Größtmaß gebracht:
  Quer- und Hochformat zusammen ergaben ein quadratisches Bild, das
  keine Kamera aufnahm. Jetzt gilt das größte echte Bild.
- Beginnt die früheste Kamera vor dem „In-Punkt", rückt der Anfang der
  Timeline zurück. Der Bericht „Zum Nachsehen" maß vom alten Anfang,
  alle Abstände waren falsch. Jetzt misst er vom neuen.
- Der Full-Mix-Ersatz nimmt den Ton einer Kamera, und der beginnt, wo
  die Kamera begann, nicht am „In-Punkt". Der Ton lief gegen das Bild.
  Der Kopf wird jetzt abgeschnitten.
- Ein selbst angelegtes Projekt trug die Werkseinstellung Rec.709 von
  Resolve, HDR-Material wäre wortlos als Acht-Bit-SDR ausgegeben
  worden. Bei eigenen Projekten gewinnt jetzt das Material.
- Das Ausgabeziel hieß nur nach der Produktion, ein zweiter Lauf
  überschrieb also die erste Lieferung. Der Name zählt jetzt hoch, und
  das Protokoll sagt, wie er lautet.
- Clips wurden über den Dateinamen wiedergefunden: Zwei Kameras mit je
  einer C0001.MP4 landeten auf einem Clip, die zweite zeigte das Bild
  der ersten. Jetzt entscheidet der echte Pfad.

### Tests

- Die Tests für die Timeline können melden, was auf einer Spur gelandet
  ist -- genau das, wonach der Timeline-Bericht im Programm sie fragt.

## 0.10.0

**English**

### Tests

- The shared test material no longer lies at a fixed path anybody may
  write to, where two runs on one machine wiped each other's material.
  The path carries the user id, `VPM_FIXTURES` overrides it.
- The suite ends by telling whoever started it not to sit in front of
  it and watch.

### Documentation

- The manual covers the settings window, the preset under the
  assignment table, the plus in a channel pair's name, the tick as an
  offer, and which Python versions this is for.
- A note for whoever works on the program says what a session needs at
  its start: where the state lives, how the tests are run, and the
  rules that do not bend.

---

**Deutsch**

### Tests

- Das Testmaterial liegt nicht mehr an einem festen Pfad, an dem jeder
  schreiben darf und zwei Läufe sich gegenseitig löschten. Der Pfad
  trägt die Benutzerkennung, `VPM_FIXTURES` ändert ihn.
- Am Ende sagt die Testreihe demjenigen, der sie gestartet hat, er
  solle nicht davorsitzen und zusehen.

### Dokumentation

- Das Handbuch beschreibt das Einstellungsfenster, das Preset unter der
  Zuordnungstabelle, das Plus im Namen eines Kanalpaares, den Haken als
  Angebot sowie die passenden Python-Versionen.
- Eine Notiz für alle, die am Programm arbeiten, sagt, was eine Sitzung
  zu Beginn wissen muss: wo der Zustand liegt, wie die Tests laufen,
  welche Regeln unverrückbar sind.

## 0.9.0

**English**

Two reviews went over everything 0.7.0 and 0.8.0 changed. Every fix
below has a test.

### Fixed

- Taking a stereo pair apart freed a channel, the proposal ran again,
  and the freed channel was joined to its other neighbour unasked. The
  measurement now proposes once; a tick corrects it.
- On resume, an output whose channel count came back empty was sent to
  auphonic.com a second time -- a second render on the bill. An output
  set up but not yet written is now found by its suffix.
- An ffmpeg that died half way through reading the channels was taken
  for one that had finished, and the half-read verdict was stored for
  good. A broken read is now seen as broken.
- The channel read held the whole recording twice as the pieces were
  joined -- the very doubling that reading in pieces avoids. Each
  channel is now joined on its own.
- A transfer broken off by an error left the download running in the
  background. It now ends with the transfer.
- Removing the last audio file left the work for that recording
  standing, so it was queued again and again. The work now goes with
  the file.
- The verdict on Resolve stood in a box inside the settings window,
  invisible to anybody who had not opened it. The "Resolve" tab now
  says whether Resolve answers and points to the settings.
- The check on Resolve now runs afresh every time that window is
  opened, rather than once per session.
- "not measured -- nothing is running for it" was shown in the ordinary
  case, as the work registers a moment after the row is drawn. The row
  now says "being looked at ..." again.
- The progress bar did not follow a run that had just been started. It
  now shows how far that run has come.

### Security

- The API key went into curl's configuration unescaped: a key holding a
  quotation mark could have smuggled in directives of its own. It is
  escaped, and the file overwritten where deleting fails.

### Tests

- The arithmetic that combines what was measured per block takes
  made-up numbers. Lists of unequal length no longer stop it, so it is
  tested without gigabytes of material.

---

**Deutsch**

Zwei Durchsichten gingen über alles, was 0.7.0 und 0.8.0 geändert
haben. Jede Behebung unten hat einen Test.

### Behoben

- Ein getrenntes Stereopaar gab einen Kanal frei, der Vorschlag lief
  erneut und legte ihn ungefragt mit dem anderen Nachbarn zusammen.
  Jetzt schlägt die Messung einmal vor, ein Haken berichtigt.
- Beim Fortsetzen ging eine Ausgabe mit leerer Kanalzahl ein zweites
  Mal an auphonic.com -- ein zweiter Durchlauf auf der Rechnung.
  Ungeschriebene Ausgaben erkennt das Programm jetzt an der Endung.
- Ein ffmpeg, das beim Lesen der Kanäle mittendrin starb, galt als
  fertig, und das halbe Urteil wurde für immer gespeichert. Ein
  abgebrochenes Lesen gilt jetzt als abgebrochen.
- Das Kanallesen hielt die ganze Aufnahme beim Zusammenfügen der Stücke
  doppelt -- genau die Verdopplung, die das stückweise Lesen vermeidet.
  Jetzt geht es Kanal für Kanal.
- Ein durch einen Fehler abgebrochener Transfer ließ den Download
  weiterlaufen. Er endet jetzt mit dem Transfer.
- Wurde die letzte Tondatei entfernt, blieb die Arbeit für diese
  Aufnahme stehen und reihte sich immer wieder neu ein. Jetzt geht sie
  mit der Datei.
- Das Urteil über Resolve stand in einem Feld im Einstellungsfenster,
  unsichtbar für jeden, der es nie öffnete. Der Reiter „Resolve" sagt
  jetzt, ob Resolve antwortet, und führt dorthin.
- Die Prüfung auf Resolve läuft jetzt bei jedem Öffnen jenes Fensters
  neu statt nur einmal je Sitzung.
- „nicht gemessen -- es läuft nichts dafür" erschien im Normalfall,
  denn die Arbeit meldet sich erst nach dem Zeichnen der Zeile an. Die
  Zeile sagt jetzt wieder „wird untersucht ...".
- Der Fortschrittsbalken folgte einem gerade gestarteten Lauf nicht.
  Jetzt zeigt er, wie weit dieser Lauf gekommen ist.

### Sicherheit

- Der API-Schlüssel ging unmaskiert in die curl-Konfiguration. Ein
  Schlüssel mit Anführungszeichen hätte eigene Anweisungen einschleusen
  können. Er wird maskiert, die Datei notfalls überschrieben.

### Tests

- Die Rechnung, die das je Block Gemessene zusammenführt, nimmt
  erfundene Zahlen an. Listen ungleicher Länge halten sie nicht mehr
  an, sie lässt sich ohne Gigabytes prüfen.

## 0.8.0

**English**

### Changed

- The lowest Python this runs on is 3.10. Below that the window cannot
  open at all, whatever the command line says.
- `--version`, the log header and every run name the Python that is
  running, and the recommended one where they differ:
  `Python 3.11.15  (recommended version 3.14.7)`.
- How much runs at once follows what this one program may use, not what
  the machine holds. In a container held to two processors of
  thirty-two, thirty threads used to take turns.
- "Settings ...", top right of the tab bar, opens a window holding the
  key for auphonic.com, the tick that stores it, "Connect", and the
  check on Resolve.
- The preset and "Fetch transcript" stand under the assignment table,
  right below the "Multitrack" tick. What a run should do is in one
  place.
- The first tab holds files, production name, spoken language and
  output folder. Nothing else.

### Fixed

- A recording of two blocks said "being looked at ..." for as long as
  the window stayed open, long after the work was done. The row now
  follows the last block to finish.
- A row waiting for a measurement nobody had started said the same as
  one being measured. It now says which of the two it is.
- Where the channel count of a file cannot be made out, the run now
  says so, rather than swallowing it.
- Ticking a channel pair the measurement had found, or unticking one it
  had missed, no longer counts as set by hand. Only a real override is
  remembered.

### Tests

- The suite runs on Python 3.14.7, the version this is used on daily.
  It used to run on 3.11 while the program ran on 3.14.
- The consistency check took two names the 3.14 compiler puts in place
  for names of unknown origin. It no longer reports them.
- A test holds the settings window and the three tabs to their new
  division.

---

**Deutsch**

### Geändert

- Das kleinste Python für dieses Programm ist 3.10. Darunter öffnet
  sich das Fenster überhaupt nicht, was auch immer auf der
  Kommandozeile steht.
- `--version`, der Protokollkopf und jeder Lauf nennen das laufende
  Python sowie die empfohlene Version, wo beide auseinandergehen:
  `Python 3.11.15  (empfohlene Version 3.14.7)`.
- Wie viel gleichzeitig läuft, richtet sich danach, was das Programm
  nutzen darf, nicht nach dem Rechner. In einem Container mit
  zwei von 32 Prozessoren liefen sonst 30 Abläufe abwechselnd.
- „Einstellungen ..." rechts oben in der Reiterleiste öffnet ein
  Fenster mit dem Schlüssel für auphonic.com, dem Haken zum Speichern,
  „Verbinden" und der Resolve-Prüfung.
- Das Preset und „Transkription holen" stehen unter der
  Zuordnungstabelle, gleich unter dem Haken „Multitrack". Was ein Lauf
  tun soll, steht an einer Stelle.
- Der erste Reiter enthält Dateien, Produktionsname, gesprochene
  Sprache und Ausgabeordner. Sonst nichts.

### Behoben

- Eine Aufnahme aus zwei Blöcken sagte „wird untersucht ...", solange
  das Fenster offen blieb, lange nach getaner Arbeit. Die Zeile folgt
  jetzt dem zuletzt fertigen Block.
- Eine Zeile, die auf eine Messung wartet, die niemand gestartet hat,
  sagte dasselbe wie eine laufende. Sie sagt jetzt, welcher der beiden
  Fälle vorliegt.
- Lässt sich die Kanalzahl einer Datei nicht ermitteln, sagt der Lauf
  es jetzt, statt es zu verschlucken.
- Ein Kanalpaar anzuhaken, das die Messung gefunden hat, oder eines
  abzuwählen, das sie übersah, gilt nicht mehr als manuell gesetzt. Nur
  ein echter Eingriff bleibt gemerkt.

### Tests

- Die Testreihe läuft auf Python 3.14.7, der täglich genutzten Version.
  Bisher lief sie auf 3.11, während das Programm auf 3.14 lief.
- Die Konsistenzprüfung hielt zwei Namen, die der Übersetzer von 3.14
  setzt, für Namen unbekannter Herkunft. Sie meldet sie nicht mehr.
- Ein Test hält das Einstellungsfenster und die drei Reiter bei ihrer
  neuen Aufteilung.

## 0.7.0

**English**

### Changed

- The channel measurement is eleven times faster: one pass, in place of
  decoding the whole file once per channel. A 92 MB block of 32
  channels took 22.9 seconds, now 2.0.

### Security

- On a Mac the API key no longer reaches the Keychain as a command line
  argument, which every auditing agent on a managed machine logs. It
  goes over the input instead.

### Tests

- A test reads the same file both ways and compares it sample by
  sample, so the fast reading stays as exact as the slow one.

---

**Deutsch**

### Geändert

- Die Kanalmessung ist elfmal schneller: ein Durchgang statt einer
  Dekodierung der ganzen Datei je Kanal. Ein Block von 92 MB mit 32
  Kanälen brauchte 22,9 Sekunden, nun 2,0.

### Sicherheit

- Auf einem Mac erreicht der API-Schlüssel den Schlüsselbund nicht mehr
  als Kommandozeilenargument, das auf verwalteten Rechnern jeder
  Überwachungsdienst protokolliert. Er geht über die Eingabe.

### Tests

- Ein Test liest dieselbe Datei auf beiden Wegen und vergleicht sie
  Sample für Sample, damit das schnelle Lesen so genau bleibt wie das
  langsame.

## 0.6.0

**English**

### Added

- `requirements.txt` and `requirements-dev.txt` name what the program
  needs and what its tests need. A fresh machine installs all of it in
  one step.

### Changed

- A channel pair used to carry an ampersand, which splits a command in
  two in every shell. It is written with a plus now: "Channel 1+2" on
  screen, `_Channel1+2.wav` on disk.

### Fixed

- A recording made of several blocks took its stereo judgement from the
  last block, so a run-out or a silent block decided whether two
  channels are one track. The loudest block decides now.
- A recording of several blocks never came apart into tracks: two
  32-channel blocks stayed one row with a single voice. It comes apart
  into its tracks now.
- `--together` promised the order it was given and then sorted the files
  by name again. Without a timecode that order is the only one, and it
  is kept now.
- A tick joining two channels to one stereo track outlived the
  measurement it was made under. It is no longer honoured if one of the
  two is an unused input.
- A file named in `--together` and missing from disk went unreported,
  unless one of its partners ended up in a recording of its own. Every
  missing file is named now.
- Two file names spelling the same moment, `260808` and `20260808`, are
  both set aside. That happened silently; it is reported now.
- Intro and outro marks survived the opening of another project, and a
  run could then stop and name a file that was not in the list at all.
  They are cleared now.
- `--help` and `--version` used to fetch twenty megabytes and hunt for
  ffmpeg first, and failed on a machine that had neither. They answer
  without either now.
- Starting the window without Qt printed one line and died silently,
  while a hundred megabytes came down behind a mute terminal. Qt is
  settled first now.
- When installing a missing package failed, the advice underneath was
  the same command that had just failed. The last lines of its own
  output are shown now.
- Below Python 3.7 the program used to run on and fail later on
  something a stranger cannot place. It now says that it will not run
  there, and stops.
- The advice for a missing ffmpeg gave Linux the ways round it for a Mac
  and for Windows. It now names the machine it runs on: brew, the
  package manager, ffmpeg.org.
- Installing past the system package manager happened without a word. It
  is now reported when it happens, with the virtual environment named as
  the way round it.
- A temporary file holding an answer from auphonic.com is removed even
  when the call breaks off, and a failed removal no longer replaces the
  real error.
- On resume, a mixdown of one channel is no longer taken for the
  two-channel one a stereo run needs. An upload sent a second time is
  billed a second time.
- `--lufs` was marked as multitrack only in the help text. The simple
  path reads it too, and the help text says so now.

### Security

- The Auphonic key is no longer handed to the package installer.
  Installing a package runs code out of it, and that code could have
  read the key out of the environment.

### Tests

- A test block for every defect above. The suite holds 78 tests now.
- The test for cutting tracks used the piece names from before 0.4.0,
  which is why it missed the recording that never came apart. It builds
  its names the way the program does.

### Documentation

- The manual claimed the Auphonic key is never in the process list. It
  says now where it can be seen -- `--auphonic-api-key` and the macOS
  Keychain -- and names `AUPHONIC_TOKEN` as the way round.
- The manual names the Python versions that run the program, and what
  Linux costs: no place to store the Auphonic key, so it comes from
  `AUPHONIC_TOKEN` every time.

---

**Deutsch**

### Hinzugefügt

- `requirements.txt` und `requirements-dev.txt` nennen, was das Programm
  braucht und was seine Tests brauchen. Ein frischer Rechner installiert
  alles in einem Schritt.

### Geändert

- Ein Kanalpaar trug bisher ein Kaufmanns-Und, das in jeder Shell den
  Befehl zerteilt. Jetzt steht dort ein Plus: „Channel 1+2" am
  Bildschirm, `_Channel1+2.wav` auf der Platte.

### Behoben

- Eine Aufnahme aus mehreren Blöcken nahm ihr Stereo-Urteil vom letzten
  Block, ein Ausklang oder ein stiller Block entschied also über das
  Kanalpaar. Jetzt entscheidet der lauteste Block.
- Eine Aufnahme aus mehreren Blöcken zerfiel nie in Spuren: Zwei Blöcke
  mit 32 Kanälen blieben eine Zeile mit einer einzigen Stimme. Jetzt
  zerfällt sie in ihre Spuren.
- `--together` versprach die angegebene Reihenfolge und sortierte die
  Dateien dann doch nach Namen. Ohne Timecode ist die angegebene die
  einzige; sie wird jetzt eingehalten.
- Ein Haken, der zwei Kanäle zu einer Stereospur verbindet, überlebte
  die Messung, unter der er gesetzt wurde. Er gilt nicht mehr, wenn
  einer der beiden ein ungenutzter Eingang ist.
- Eine mit `--together` genannte Datei, die auf der Platte fehlt, blieb
  unerwähnt -- es sei denn, einer ihrer Partner bildete eine eigene
  Aufnahme. Jetzt wird jede fehlende Datei genannt.
- Zwei Dateinamen für denselben Zeitpunkt, `260808` und `20260808`,
  werden beide beiseitegelegt. Das geschah stumm; es wird jetzt
  gemeldet.
- Intro- und Outro-Marken überlebten das Öffnen eines anderen Projekts,
  und ein Lauf hielt dann an und nannte eine Datei, die gar nicht in der
  Liste stand. Jetzt werden sie gelöscht.
- `--help` und `--version` holten erst zwanzig Megabyte und suchten
  ffmpeg, und auf einem Rechner ohne beides scheiterten sie. Jetzt
  antworten sie ohne beides.
- Der Start der Oberfläche ohne Qt gab eine Zeile aus und starb still,
  während hundert Megabyte hinter einem stummen Terminal geladen wurden.
  Qt wird jetzt zuerst geklärt.
- Scheiterte die Installation eines fehlenden Pakets, war der Rat
  darunter derselbe Befehl, der eben gescheitert war. Jetzt stehen die
  letzten Zeilen seiner Ausgabe da.
- Unterhalb von Python 3.7 lief das Programm weiter und scheiterte
  später an etwas, das niemand einordnen kann. Jetzt sagt es, dass es
  dort nicht läuft, und hält an.
- Der Rat bei fehlendem ffmpeg nannte auf Linux die Wege für den Mac und
  für Windows. Jetzt nennt er den Rechner, auf dem es läuft: brew, die
  Paketverwaltung, ffmpeg.org.
- Eine Installation am System-Paketverwalter vorbei geschah wortlos.
  Jetzt wird sie gemeldet, und die virtuelle Umgebung wird als Weg darum
  herum genannt.
- Eine temporäre Datei mit einer Antwort von auphonic.com wird auch dann
  entfernt, wenn der Aufruf abbricht, und ein misslungenes Entfernen
  verdeckt nicht mehr den echten Fehler.
- Beim Fortsetzen gilt ein Mixdown mit einem Kanal nicht mehr als der
  zweikanalige, den ein Stereo-Lauf braucht. Ein zweites Mal
  hochgeladen heißt ein zweites Mal bezahlt.
- `--lufs` galt im Hilfetext als reine Multitrack-Sache. Der Einspur-Weg
  liest es ebenso, und der Hilfetext sagt es jetzt.

### Sicherheit

- Der Auphonic-Schlüssel wird der Paketinstallation nicht mehr
  mitgegeben. Eine Installation führt fremden Code aus, der den
  Schlüssel aus der Umgebung hätte lesen können.

### Tests

- Ein Testblock für jeden Fehler oben. Die Testreihe umfasst jetzt 78
  Tests.
- Der Test für das Zerlegen in Spuren nutzte die Stücknamen von vor
  0.4.0; darum entging ihm die Aufnahme, die nie zerfiel. Er bildet die
  Namen jetzt wie das Programm.

### Dokumentation

- Das Handbuch behauptete, der Auphonic-Schlüssel sei nie in der
  Prozessliste. Es sagt jetzt, wo er sichtbar wird -- `--auphonic-api-key`
  und Schlüsselbund -- und nennt `AUPHONIC_TOKEN` als Ausweg.
- Das Handbuch nennt die Python-Versionen, auf denen das Programm läuft,
  und was Linux kostet: kein Platz für den Auphonic-Schlüssel, er kommt
  jedes Mal aus `AUPHONIC_TOKEN`.

## 0.5.0

**English**

### Changed

- Home folders with no bearing on a production -- "Desktop",
  "Downloads" -- were guessed in two languages. macOS and Windows keep
  the English name, and Linux is asked for the names it chose.

### Fixed

- The reason the start button is grey was in the tooltip alone, and a
  disabled button shows no tooltip at all. It now stands in the footer
  beside the button.
- A missing production name left its field unmarked. It now marks the
  field red, the way a duplicate speaker name or a duplicate output name
  marks its row.
- The reason pointed at pages that no longer exist, "2.1 Production" and
  "2.3 Resolve cut". The names are read off the tabs themselves now, so
  they cannot drift apart again.
- The Resolve tab carried a tick though nothing on it can keep a run
  from starting. It no longer carries one.
- Two files set to intro, or two to outro, went into the same switch
  and the last one silently won. A second choice now frees the first,
  and a run that sees two of a kind stops and names them.

### Tests

- New blocks for the folder names, for the reason under the start
  button, and for the doubled intro. The suite holds 77 tests now.

### Documentation

- The metrics table stays comma separated. The manual says what that
  costs on a German system and how to avoid it when opening the table.

---

**Deutsch**

### Geändert

- Heimordner ohne Bezug zu einer Produktion -- „Desktop", „Downloads" --
  wurden in zwei Sprachen geraten. macOS und Windows behalten den
  englischen Namen, Linux wird nach seinen eigenen gefragt.

### Behoben

- Der Grund, warum die Starttaste grau ist, stand allein im Tooltip, und
  eine abgeschaltete Taste zeigt gar keinen Tooltip. Jetzt steht er in
  der Fußzeile daneben.
- Ein fehlender Produktionsname ließ sein Feld unmarkiert. Jetzt wird
  das Feld rot, so wie ein doppelter Sprechername oder ein doppelter
  Ausgabename seine Zeile rot färbt.
- Der Grund nannte Seiten, die es nicht mehr gibt: „2.1 Produktion" und
  „2.3 Resolve-Schnitt". Die Namen werden jetzt von den Reitern selbst
  gelesen, so laufen sie nicht mehr auseinander.
- Der Resolve-Reiter trug einen Haken, obwohl nichts auf ihm einen Lauf
  aufhalten kann. Jetzt trägt er keinen mehr.
- Zwei Dateien als Intro -- oder zwei als Outro -- gingen in denselben
  Schalter, die letzte gewann stumm. Jetzt gibt die zweite Wahl die
  erste frei, und ein Lauf mit zweien hält an und nennt sie.

### Tests

- Neue Blöcke für die Ordnernamen, für den Grund unter der Starttaste
  und für das doppelte Intro. Die Testreihe umfasst jetzt 77 Tests.

### Dokumentation

- Die Kennzahlen-Tabelle bleibt kommagetrennt. Das Handbuch sagt, was
  das auf einem deutschen System kostet und über welchen Weg beim Öffnen
  es sich vermeiden lässt.

## 0.4.0

**English**

### Added

- A stereo track stays stereo the whole way: onto the time axis, through
  the loudness measurement, into its own track on the camera file and
  into the mix. What the source has is kept.
- At auphonic.com the finished mixdown is asked for in two channels as
  soon as one track is stereo. On the simple path the fold to mono is
  switched off for every output the preset asks for.
- Without Multitrack, recordings that ran at the same time go into the
  video as tracks of their own, after the mix. The timecode decides
  that. `--no-single-tracks` leaves them out.
- A camera ticked "as a track" is an audio candidate like any other. Its
  channels are judged and cut by the rule a recorder file gets, so a
  camera with two clip-on microphones gives two speakers.
- The command line does the same. `Osmo.mov Wide.mov --multitrack` reads
  a two-microphone camera as two speakers with no window open, and still
  writes one file per camera.
- Camera tracks get the full camera selector. A microphone plugged into
  one camera may belong to a person another camera is filming.
- A camera counts towards Multitrack as soon as it is ticked as a track,
  on the command line as well as in the window.
- Blocks whose names carry a date and a time instead of a counter are
  joined into one recording, when the next one starts where the previous
  one ends.
- `--together` and the "belongs to" selector put files into one
  recording by hand. They are the counterpart to `--apart`.
- Channel count and sample rate have to match before two blocks are
  joined into one recording.
- The channels of a recording are judged over all its blocks, not the
  first. On a 32-channel mixer the first block was the soundcheck, read
  as one pair; the second was the show, read as ten tracks.
- An absolute floor for a channel that carries anything: under -70 dBFS
  only the converter's noise is left. A pair judged on noise answers
  differently every time it is measured.

### Changed

- Every neighbouring pair of channels is judged, not every second one.
  On a mixer, channels 2 and 3 can be the stereo pair just as well as 1
  and 2.
- One row per channel in the file list, with a tick saying "this one and
  the next are one stereo track". Ticking channel 2 takes the tick from
  channel 3; a channel belongs to one pair only.
- The tick and the reason behind it moved into the wide column. In the
  narrow one the word beside the box was cut off after its first letter.
- Tracks are named after their channels, "Channel 1" and "Channel 2+3".
  So are the files cut from them, with a fingerprint of the source
  folder in the name.
- The hint under a file with more than two channels said they would be
  mixed into one track. That has not happened since 0.1.0, and the hint
  says what does happen.
- `--min-shot` goes from 1.2 seconds to 3. Interview practice asks for
  three to five; a camera that changes faster than the viewer can settle
  on a face reads as nervous.
- The Multitrack tick moved from the settings sheet to under the
  assignment table, where what it needs is decided.
- With cameras only and no audio file, the window offers the Multitrack
  tick instead of stopping the run afterwards.
- Channel conversions are written out rather than left to ffmpeg, both
  ways. On a signal at -24.08 dBFS, ffmpeg gave -27.09 going up to two
  channels and -21.07 coming back to one.

### Fixed

- A production with a transcript did not start when the preset already
  carried the transcript formats; the run waited until the time limit.
  It starts now.
- The check report cleared the channel rows out of the file list when it
  came back, and the stereo tick vanished until a later rebuild. The
  rows stay now.
- A track cut out of a multichannel file lost the recording time, and a
  real pause was then swallowed rather than filled with silence and
  reported. The time is kept now.
- Two files of the same name on two cards wrote over each other's
  tracks, silently. The name of a cut piece now carries a fingerprint of
  where its source lies.
- Above 26 channels the channel letters ran together: channels 1 and 2
  gave the same name as channel 28, and one track held another's audio.
  Every name is distinct now.
- A camera with more than two channels was folded to mono before anybody
  looked at what was on it. Four microphones became one voice. Every
  channel is kept now.
- With a recording made of blocks, the pair judgement took the loudest
  block even where one of the two channels was silent in it. It takes
  the loudest block that measured the pair now.
- Changing the stereo tick dropped the cut tracks of one block only, and
  the rows then mixed block one with block two. Every block is cut again
  now.
- Continuation blocks that were found rather than selected were never
  cut, and a multi-part recording was made from its first block alone.
  All of them are cut now.
- The block-size rule compared a block with itself on the first step and
  always said yes, so a short finished take standing in front of the
  recording was glued on. It is left alone now.
- Two files carrying the same recording time were laid end to end. Two
  recorders started together write exactly that number and run at the
  same time, so the two now lie on top of each other.
- Two groups made by hand could both claim the same block, and it was
  decoded and mixed into two productions. The first to claim it now
  keeps it, and the second is told.
- A file named with `--together` that is not on disk was accepted into
  the recording and then vanished without a word. It is refused now, and
  the refusal is reported.
- Two names spelling one moment, `260808` and `20260808`, put a file
  into two recordings, and the folder listing decided which grouping
  came out. Both are set aside now.
- On a case-sensitive disc, `REC0002.wav` and `rec0002.wav` collapsed
  into one entry, and the folder listing decided which of the two was
  used. Both are kept now.
- A counter like `260808_000001` reads as a time of day. The clock rule
  fired, found nothing and stopped without handing back, and three
  blocks of one recording stayed three. They are joined now.

### Tests

- 75 tests, every one of them checking something. The five that only
  printed their result now measure it, and the three that cannot be
  checked outside Resolve say so.
- New blocks for the stereo mix, the camera as a track, the block
  judgement, the clock rule and the by-hand grouping.
- A test hunts German in seven places where only English belongs, right
  into the output of the running program.

---

**Deutsch**

### Hinzugefügt

- Eine Stereospur bleibt durchgehend stereo: auf der Zeitachse, in der
  Lautheitsmessung, in ihrer eigenen Spur auf der Kameradatei und in der
  Mischung. Was die Quelle hat, bleibt erhalten.
- Bei auphonic.com wird der fertige Mixdown zweikanalig angefordert,
  sobald eine Spur stereo ist. Auf dem Einspur-Weg entfällt die Faltung
  auf Mono für jede Ausgabe des Presets.
- Auch ohne Multitrack kommen gleichzeitig laufende Aufnahmen als eigene
  Spuren ins Video, hinter der Mischung. Der Timecode entscheidet das.
  `--no-single-tracks` lässt sie weg.
- Eine Kamera mit Haken „als Spur" ist ein Tonkandidat wie jeder andere.
  Ihre Kanäle werden wie bei einer Recorder-Datei beurteilt und
  geschnitten; zwei Ansteckmikrofone geben zwei Sprecher.
- Die Befehlszeile kann dasselbe. `Osmo.mov Wide.mov --multitrack` liest
  eine Kamera mit zwei Mikrofonen als zwei Sprecher, ohne Fenster, und
  schreibt weiter eine Datei je Kamera.
- Kameraspuren bekommen die volle Kamera-Auswahl. Ein Mikrofon an der
  einen Kamera kann zu einer Person gehören, die eine andere Kamera
  filmt.
- Eine Kamera zählt für Multitrack, sobald sie als Spur angehakt ist --
  in der Befehlszeile wie im Fenster.
- Blöcke, deren Namen ein Datum und eine Uhrzeit statt eines Zählers
  tragen, werden zu einer Aufnahme verbunden, wenn der nächste dort
  beginnt, wo der vorige endet.
- `--together` und die Auswahl „gehört zu" legen Dateien von Hand in
  eine Aufnahme. Sie sind das Gegenstück zu `--apart`.
- Kanalzahl und Abtastrate müssen übereinstimmen, bevor zwei Blöcke zu
  einer Aufnahme verbunden werden.
- Die Kanäle einer Aufnahme werden über alle Blöcke beurteilt, nicht
  über den ersten. Am 32-Kanal-Pult war der erste Block der Soundcheck
  mit einem Paar, der zweite die Show mit zehn Spuren.
- Eine absolute Schwelle für einen Kanal, der etwas trägt: unter -70
  dBFS liegt nur das Rauschen des Wandlers. Ein am Rauschen beurteiltes
  Paar antwortet bei jeder Messung anders.

### Geändert

- Jedes Nachbarpaar von Kanälen wird beurteilt, nicht jedes zweite. Am
  Pult können Kanal 2 und 3 genauso das Stereopaar sein wie 1 und 2.
- Eine Zeile je Kanal in der Dateiliste, mit einem Haken „dieser und der
  nächste sind eine Stereospur". Ein Haken bei Kanal 2 nimmt ihn Kanal 3
  weg; ein Kanal gehört nur zu einem Paar.
- Der Haken und der Grund dahinter sind in die breite Spalte gewandert.
  In der schmalen war das Wort neben dem Kästchen nach dem ersten
  Buchstaben abgeschnitten.
- Spuren heißen nach ihren Kanälen, „Channel 1" und „Channel 2+3". Die
  daraus geschnittenen Dateien ebenso, mit einem Fingerabdruck des
  Quellordners im Namen.
- Der Hinweis unter einer Datei mit mehr als zwei Kanälen sagte, sie
  würden zu einer Spur gemischt. Das geschieht seit 0.1.0 nicht mehr; er
  sagt jetzt, was wirklich passiert.
- `--min-shot` geht von 1,2 Sekunden auf 3. Die Interviewpraxis will
  drei bis fünf; eine Kamera, die schneller wechselt, als der Zuschauer
  ein Gesicht fassen kann, wirkt nervös.
- Der Multitrack-Haken ist vom Einstellungsblatt unter die
  Zuordnungstabelle gewandert, wo entschieden wird, was er braucht.
- Bei reinen Kameras ohne Tondatei bietet das Fenster den
  Multitrack-Haken an, statt den Lauf hinterher anzuhalten.
- Kanalumrechnungen werden selbst ausgeschrieben statt ffmpeg
  überlassen, in beide Richtungen. Bei -24,08 dBFS gab ffmpeg -27,09 auf
  zwei Kanäle und -21,07 zurück auf einen.

### Behoben

- Eine Produktion mit Transkript startete nicht, wenn das Preset die
  Transkriptformate schon trug; der Lauf wartete bis zur Zeitgrenze.
  Jetzt startet sie.
- Der Prüfbericht räumte bei seiner Rückkehr die Kanalzeilen aus der
  Dateiliste, der Stereo-Haken verschwand bis zum nächsten Neuaufbau.
  Jetzt bleiben die Zeilen stehen.
- Eine aus einer Mehrkanaldatei geschnittene Spur verlor die
  Aufnahmezeit, und eine echte Pause wurde verschluckt, statt mit Stille
  gefüllt und gemeldet zu werden. Jetzt bleibt die Zeit erhalten.
- Zwei gleichnamige Dateien auf zwei Karten überschrieben stumm die
  Spuren der jeweils anderen. Der Name eines geschnittenen Stücks trägt
  jetzt einen Fingerabdruck seiner Herkunft.
- Über 26 Kanäle liefen die Kanalbuchstaben zusammen: Kanal 1 und 2
  ergaben denselben Namen wie Kanal 28, eine Spur trug den Ton einer
  anderen. Jetzt ist jeder Name eindeutig.
- Eine Kamera mit mehr als zwei Kanälen wurde auf Mono gefaltet, bevor
  jemand hinsah. Vier Mikrofone ergaben eine Stimme. Jetzt bleiben alle
  Kanäle erhalten.
- Bei einer Aufnahme aus Blöcken nahm das Paar-Urteil den lautesten
  Block, auch wenn dort einer der beiden Kanäle stumm war. Jetzt zählt
  der lauteste Block, der das Paar wirklich maß.
- Ein geänderter Stereo-Haken verwarf nur die geschnittenen Spuren eines
  Blocks, und die Zeilen mischten dann Block eins und Block zwei. Jetzt
  wird jeder Block neu geschnitten.
- Fortsetzungsblöcke, die gefunden statt ausgewählt wurden, wurden nie
  geschnitten; eine mehrteilige Aufnahme entstand allein aus ihrem
  ersten Block. Jetzt werden alle geschnitten.
- Die Blockgrößenregel verglich im ersten Schritt einen Block mit sich
  selbst und sagte immer ja, so wurde eine kurze fertige Aufnahme davor
  angeklebt. Jetzt bleibt sie für sich.
- Zwei Dateien mit derselben Aufnahmezeit wurden hintereinandergelegt.
  Zwei gemeinsam gestartete Recorder schreiben genau diese Zahl und
  laufen gleichzeitig; jetzt liegen sie übereinander.
- Zwei von Hand gebildete Gruppen konnten denselben Block beanspruchen;
  er wurde in zwei Produktionen dekodiert und gemischt. Jetzt behält ihn
  die erste Gruppe, der zweiten wird es gesagt.
- Eine mit `--together` genannte Datei, die es auf der Platte nicht
  gibt, wurde in die Aufnahme genommen und verschwand wortlos. Jetzt
  wird sie abgelehnt und die Ablehnung gemeldet.
- Zwei Namen für denselben Zeitpunkt, `260808` und `20260808`, legten
  eine Datei in zwei Aufnahmen, und die Ordnerliste entschied über die
  Gruppierung. Jetzt werden beide beiseitegelegt.
- Auf einer Platte, die Groß- und Kleinschreibung unterscheidet, fielen
  `REC0002.wav` und `rec0002.wav` zu einem Eintrag zusammen; die
  Ordnerliste entschied. Jetzt bleiben beide erhalten.
- Ein Zähler wie `260808_000001` sieht aus wie eine Uhrzeit; die
  Uhrzeitregel griff, fand nichts und blieb stehen, ohne an die
  Zählerregel zurückzugeben. Jetzt werden die drei Blöcke verbunden.

### Tests

- 75 Tests, jeder prüft etwas. Die fünf, die ihr Ergebnis nur ausgaben,
  messen es jetzt, und die drei, die außerhalb von Resolve nicht prüfbar
  sind, sagen es.
- Neue Blöcke für die Stereomischung, die Kamera als Spur, das
  Blockurteil, die Uhrzeitregel und die Gruppierung von Hand.
- Ein Test jagt an sieben Stellen Deutsch, wo nur Englisch hingehört,
  bis in die Ausgabe des laufenden Programms.

## 0.3.0

**English**

### Added

- A single continuation file can be taken out of a recording by hand; it
  stays out though the search finds it in the folder again. Added back,
  it becomes a recording of its own.

---

**Deutsch**

### Hinzugefügt

- Eine einzelne Fortsetzungsdatei lässt sich von Hand aus einer Aufnahme
  nehmen; sie bleibt draußen, obwohl die Suche sie im Ordner findet. Neu
  hinzugefügt, wird sie eine eigene Aufnahme.

## 0.2.0

**English**

### Changed

- The camera cut is built even with one camera, so Resolve can group,
  colour and zoom the clips.

---

**Deutsch**

### Geändert

- Der Kameraschnitt entsteht auch bei einer einzigen Kamera, damit
  Resolve die Clips gruppieren, färben und zoomen kann.

## 0.1.0

**English**

### Changed

- The work runs in tracks instead of files. A multichannel recorder file
  is cut into its tracks, each with its own row in the assignment, its
  own name and its own camera.

---

**Deutsch**

### Geändert

- Die Arbeit läuft in Spuren statt in Dateien. Eine
  Mehrkanal-Recorderdatei wird in ihre Spuren geschnitten, jede mit
  eigener Zeile in der Zuordnung, eigenem Namen und eigener Kamera.

[kac]: https://keepachangelog.com/en/1.1.0/
[semver]: https://semver.org/spec/v2.0.0.html
[2.23.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.22.0-beta...v2.23.0-beta
[2.22.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.21.0-beta...v2.22.0-beta
[2.21.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.20.0-beta...v2.21.0-beta
[2.20.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.19.0-beta...v2.20.0-beta
[2.19.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.18.0-beta...v2.19.0-beta
[2.18.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.17.0-beta...v2.18.0-beta
[2.17.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.16.0-beta...v2.17.0-beta
[2.16.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.15.0-beta...v2.16.0-beta
[2.15.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.14.0-beta...v2.15.0-beta
[2.14.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.13.0-beta...v2.14.0-beta
[2.13.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.12.0-beta...v2.13.0-beta
[2.12.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.11.1-beta...v2.12.0-beta
[2.11.1-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.11.0-beta...v2.11.1-beta
[2.11.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.10.1-beta...v2.11.0-beta
[2.10.1-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.10.0-beta...v2.10.1-beta
[2.10.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.9.0-beta...v2.10.0-beta
[2.9.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.8.0-beta...v2.9.0-beta
[2.8.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.7.1-beta...v2.8.0-beta
[2.7.1-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.7.0-beta...v2.7.1-beta
[2.7.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.6.1-beta...v2.7.0-beta
[2.6.1-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.6.0-beta...v2.6.1-beta
[2.6.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.5.0-beta...v2.6.0-beta
[2.5.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.4.0-beta...v2.5.0-beta
[2.4.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.3.0-beta...v2.4.0-beta
[2.3.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.2.0-beta...v2.3.0-beta
[2.2.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.1.0-beta...v2.2.0-beta
[2.1.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.0.0-beta...v2.1.0-beta
[2.0.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v1.1.0-beta...v2.0.0-beta
[1.1.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v1.0.0-beta...v1.1.0-beta
[1.0.0-beta]: https://github.com/Bascht74/videopodcast-magic/releases/tag/v1.0.0-beta

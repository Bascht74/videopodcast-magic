# Roadmap

*In English: [ROADMAP.md](ROADMAP.md)*

Was gebaut ist, was als Nächstes kommt und was dieses Programm nicht
werden soll. Hier steht eine Reihenfolge und kein Datum. Einer
schreibt daran, neben echter Produktionsarbeit, und ein Datum wäre
hier eine Schätzung, die wie eine Zusage aussieht.

Nichts auf dieser Seite ist eine Zusage. Ein Punkt rückt nach vorn,
wenn er sich als wichtiger herausstellt, und er fällt weg, wenn eine
Messung sagt, dass er sich nicht lohnt. Was wirklich fertig ist, steht
in [CHANGELOG.md](CHANGELOG.md), Fassung für Fassung. Diese Seite ist
zuletzt für 2.5.0-beta durchgegangen worden.

## Wo das Programm heute steht

**Fassung 2.5.0-beta.** Es läuft jede Woche, an echtem Material.

Es macht die Arbeit vor dem Schnitt: aufbereiteten Ton als erste Spur
in die Videodateien legen, Rekorder und Kameras auf eine Zeitachse
bringen, die Sprecher allein aus dem Ton trennen, einen ersten Schnitt
nach Sprecher vorschlagen und ein DaVinci-Resolve-Projekt schreiben.

Sprechertrennung und Spracherkennung laufen auf der Maschine, vor der
du sitzt. Das Modell liegt in einem Ordner neben dem Programm: kein
Konto, kein Token, und nach dem einen Download kein Netz. Pegel,
De-Bleed, Rauschunterdrückung und Transkript bei auphonic.com sind
freiwillig, und das Programm lädt erst hoch, wenn es dazu aufgefordert
wird.

Es ist eine Python-Datei mit rund 30000 Zeilen, ohne Paket und ohne
Bauschritt. Python 3.10 oder neuer muss da sein, die zwei Pakete
installiert es selbst. Benutzt wird es unter macOS und Windows, unter
Linux läuft es mit zwei Einschränkungen. Eine Suite aus 98 Tests
braucht rund eine halbe Minute.

**Warum es noch beta heißt.** Das Format der Projektdatei kann sich
noch ändern. Eine ältere Datei wird mit einer klaren Meldung
abgewiesen statt halb gelesen. Wer Projekte über Monate aufhebt, sollte
das wissen. Beta endet, sobald das Format stillhält, und eine Änderung,
die es bricht, hebt die erste Stelle der Fassungsnummer.

## Was als Nächstes kommt

Nach Nutzen gegen Aufwand geordnet. Die ersten drei sind klein und
überfällig, dahinter liegt die Arbeit.

**1. Die Release-Seite bietet die Datei an, die wirklich geholt
wird.** Ein Release bietet heute ein Quellarchiv von rund 60 MB, und
die eine Datei, die der README zum Herunterladen nennt, liegt nicht
dort, wo jemand sie sucht. `videopodcast-magic.py` samt SHA-256-Summe
anzuhängen legt sie dorthin und lässt den Leser prüfen, was angekommen
ist. Jede Modelldatei prüft das Programm längst gegen eine Prüfsumme,
sich selbst noch nicht.

**2. Ein Klon schleppt 32 MB weniger mit.** Der Arbeitsordner eines
Testlaufs ist versehentlich im Repository gelandet und enthält das
Sprechertrennungsmodell ein zweites Mal und eine veraltete Kopie des
Programms. Jeder, der klont, zieht das mit. Herausnehmen kostet einen
Commit, und die Vorgeschichte bleibt, wie sie ist: sie umzuschreiben
würde die Tags verschieben, von denen installierte Programme ihr
Modell holen.

**3. Die Fortschrittsanzeige springt nicht mehr zurück.** Unter Last
kann der Balken zurückfallen, während am Lauf selbst nichts fehlt. In
einem Lauf über viele Minuten ist dieser Balken das Einzige, was sagt,
ob sich noch etwas bewegt. Eine Anzeige, die lügt, ist schlechter als
keine.

**4. Windows und Linux bekommen einen eigenen Lauf.** Das Programm
wird unter Windows benutzt, und die Suite ist dort noch nie gelaufen.
Ein Ablauf, der sie auf einem fremden Läufer startet, wird gerade
erprobt, und die offene Frage ist, ob sie unter Windows oder unter
Linux überhaupt grün wird. Eine Lücke bleibt, wie der Lauf auch
ausgeht: den Auphonic-Schlüssel legt das Programm unter Windows in die
Registry, und diesen Weg rührt kein einziger Test an.

**5. Das Handbuch entfernt sich nicht mehr stillschweigend vom
Programm.** Fünf Listen im Handbuch schreiben eine Liste aus dem
Quelltext ab: die Schaltertabelle, die Menüleiste, die Schnittregeln,
die Zahlvorgaben und die Verweise zwischen den Kapiteln. Rund 140
Zeilen Test halten Menge gegen Menge und werden rot, sobald eine Seite
sich bewegt. Verglichen werden Mengen, nie Sätze. Ein Test, der bei
jeder Umformulierung rot wird, ist nach einer Woche abgeschaltet und
bewacht danach nichts mehr.

**6. Multitrack benennt seine Stimmen selbst.** Bei einem Mikrofon je
Person weiß das Programm, wer wann spricht, und es weiß, welches
Mikrofon welches ist. Beides gegeneinander zu halten müsste von selbst
ergeben, dass „Stimme 2“ das Mikrofon dessen ist, der die Fragen
stellt. Dann fällt das Benennen von Hand weg. Derselbe Vergleich ist
eine Absicherung: wo Trennung und Mikrofon sich widersprechen, ist
etwas faul. Die Daten liegen vor, gemessen ist es nicht.

**7. Die Totale bekommt einen ruhigeren Takt.** Der Abstand, nach dem
die Totale wiederkommt, entscheidet als einziger Wert darüber, wie
unruhig der Schnitt wirkt, und an der Erkennung ändert er nichts. Ein
größerer Abstand bringt weniger und längere Totalen bei gleicher
Trefferquote. Wie lange eine Folge ohne eine Totale auskommt, ist
Geschmackssache, deshalb bleibt die Zahl ein Schalter.

**8. Die zwei Wege zu auphonic.com laufen einmal gegen den echten
Dienst.** Das Transkript einer einzelnen Spur und eine
Multitrack-Produktion mit einer Stereospur sind beide gebaut, und
keiner der beiden ist je wirklich hochgeladen worden. Ob der Dienst
eine Stereospur zweikanalig zurückgibt, ist offen. Bis dahin
beschreibt das Handbuch diese zwei Wege aus dem Quelltext statt aus
einem Lauf.

## Was später kommt

Gröber, und in keiner festen Reihenfolge.

* **Genau zwischen zwei Wörtern schneiden.** Der Reaktionsschnitt
  landet dort, wo der Ton am leisesten ist, und das ist fast immer
  eine echte Sprechpause. Ihn zwischen zwei Wörter zu setzen braucht
  die Wortzeiten von Whisper. Die Erkennung, die macOS mitbringt, ist
  weit schneller, liefert aber ein Raster von 60 ms und lässt zwischen
  zwei Wörtern gar keine Lücke. Auf ihren Zahlen ist „zwischen zwei
  Wörtern“ von „mitten im Wort“ nicht zu unterscheiden. Tempo gegen
  Genauigkeit, und es wird ein Schalter statt einer Entscheidung.

* **Ein „mhm“ zählt nicht mehr als Stille.** Lautblöcke unter vier
  Zehntelsekunden fliegen weg, bevor die Pausensuche läuft. Eine kurze
  Reaktion sieht danach aus wie eine Pause, und eine Totale kann
  jemandem über die Antwort fallen. Die Grenze zu berichtigen ändert,
  an wie viele Pausen das Programm glaubt, deshalb ist es eine Messung
  und keine Zeile.

* **Vorgaben, die einen Beleg tragen.** Ein paar Zahlen stammen aus
  einem einzelnen Referenzschnitt statt aus einer Messung.
  `--wide-latest` ist der deutlichste Fall. Jede von ihnen wird
  gemessen oder kleiner.

* **Der Reaktionsschnitt wird gesichtet, bevor er scharf bleibt.** Er
  greift ein paar Dutzend Mal in einer Folge und ist voreingestellt
  an, und niemand hat bisher jede Stelle angesehen. Zwei Fälle, in
  denen er falsch liegt, sind bekannt: die rhetorische Frage und das
  technische Vorgeplänkel, wo Blicke zu Geräten fliegen statt zu
  Gesichtern.

* **Der Vorspann wird in einem echten Resolve-Projekt geprüft.** Das
  Programm legt ihn auf die zweite Videospur und liest nach, wie viele
  Clips dort liegen. In den Tests steht eine Attrappe für Resolve,
  bestätigen kann es also nur ein echtes Projekt.

* **Die Ränder des Programms bekommen Tests.** Gemessen sind rund zwei
  Drittel abgedeckt. Was die Suite nicht anrührt, ist der ganze Lauf
  als Lauf, der Einzeldateiweg, der Weg zu auphonic.com, die Trennung
  und das Selbst-Aktualisieren. Die Abdeckung wird gelegentlich
  gemessen und nie zum Ziel.

* **Das Handbuch bekommt, was ihm fehlt.** Jede Zahl mit Spanne,
  Vorgabe und Richtung. Ein Bildschirmfoto, das den falschen Reiter
  zeigt. Ein Bild für das Kanalkapitel. Ein Stichwortverzeichnis neben
  der Kapitelliste. Eine veröffentlichte Adresse, sobald jemand eine
  zum Weitergeben braucht.

* **Kleinere Commits.** Ein Commit, dessen Betreff ein „und“ braucht,
  sind zwei Commits. Das kostet nichts, und `git bisect` und
  `git blame` beantworten danach eine Frage, statt auf einen Haufen zu
  zeigen.

## Was wir nicht vorhaben

Der nützlichste Abschnitt dieser Seite, weil er dir das Fragen spart.
Ein Wunsch, der auf dieser Seite fehlt, ist etwas anderes: er ist
nicht abgelehnt, er ist nur noch nicht aufgekommen.

* **Die Folge schneiden.** Der Kameraschnitt ist ein Vorschlag, der
  Schnitt bleibt deiner. Das Programm misst und übergibt; Entscheiden
  ist keine spätere Stufe davon.

* **Pull Requests als Prüfstelle, Pflichtdurchsichten, CODEOWNERS.**
  Alle drei setzen einen zweiten Menschen voraus. Wer sich selbst
  freigibt, hat nur den Weg verlängert. Pull Requests können trotzdem
  kommen, sobald es einen Ablauf gibt, dessen Ergebnis daran hängt.

* **Discussions.** Ein leerer Raum wirkt schlechter als kein Raum.
  Issues sind an, und dorthin gehört eine Frage.

* **Ein Wiki.** Das Handbuch steht in `docs/`, in zwei Sprachen, und
  ein Test hält die beiden Seiten gegeneinander. Ein Wiki wäre eine
  zweite Fassung, die nichts prüft.

* **Verhaltensregeln, Beitragsanleitung, Vorlagen für Issues und Pull
  Requests.** Sie heben eine Prozentzahl auf einer GitHub-Seite,
  solange niemand schreibt. Die Vorlagen kommen an dem Tag, an dem
  wirklich jemand etwas meldet.

* **Conventional Commits.** Ihr Zweck ist ein erzeugter Changelog und
  eine erzeugte Fassungsnummer. Dieser Changelog ist von Hand
  geschrieben und trägt in fast jedem Punkt einen Messwert; ein
  Generator machte daraus eine Liste von Betreffzeilen.

* **Ein Umbau auf pytest, ruff, mypy und pre-commit.** Alle vier
  wollen ein Paket mit `pyproject.toml`. Hier wären es vier neue
  Abhängigkeiten für eine Datei, deren 98 Tests als schlichte Scripts
  in einer halben Minute durchlaufen. Eine dünne pytest-Schicht, die
  genau diese Scripts unverändert startet, ist etwas anderes und kann
  kommen.

* **Bildvergleich der Handbuchbilder in der Suite.** Die Bilder
  entstehen im echten Fensterstil, dafür braucht es einen Bildschirm
  mit angemeldetem Benutzer, und ein Test darf sich den Vordergrund
  nicht nehmen. Ein solcher Test wäre überall sonst rot oder blind.
  Ein niedergeschriebener Sollstand des Fensterbaums leistet dasselbe
  billiger und ist im Vergleich zweier Stände lesbar.

* **Doku-Tests, die Sätze vergleichen.** Am heutigen Handbuch
  gemessen: jede fette Beschriftung oder jede genannte Vorgabe zu
  prüfen bringt am ersten Tag ein Fünftel bis ein Drittel Fehlalarm,
  und der erste Tag ist der beste, den so ein Test hat. Einen Test, der
  über fünf Prozent Fehlalarm anfängt, bauen wir nicht.

* **Eine Abdeckungsschwelle als Tor.** Wer eine Zahl zum Ziel macht,
  bekommt die Zahl. Die Liste der Funktionen, die kein Test je aufruft,
  ist etwas wert; der Prozentsatz nicht.

* **Den Testlauf auf mehrere Rechner verteilen, flatterhafte Tests
  wiederholen, Bots für die Triage.** Die Suite braucht eine halbe
  Minute, bisher hat kein Test geflattert, und es gibt keine Schlange
  von Meldungen. All das beantwortet eine Menge, die es hier nicht
  gibt.

* **Installationsprogramme, signierte Pakete, Notarisierung, PyPI.**
  Es ist mit Absicht eine Datei: holen und starten.

* **Sponsors, Projects.** Papierkram ohne Gegenwert.

## Wie du einen Fehler meldest oder mitmachst

**Issues sind an**, unter
[Issues](https://github.com/Bascht74/videopodcast-magic/issues).
Discussions sind mit Absicht aus. Eine Frage, ein Fehler und ein Wunsch
gehen an dieselbe Stelle, und keines davon braucht eine Vorlage.

**Kein Punkt oben trägt eine Issue-Nummer.** Die Liste ist bisher
leer, und ein Punkt bekommt sein Issue an dem Tag, an dem jemand außer
dem Autor ihn verfolgen will. Danach zu fragen ist ein guter Anlass.

**Was eine Meldung brauchbar macht:** was du gestartet hast, was
herauskam und was du stattdessen erwartet hast. Das Log nennt die
Fassung und welche Kopie des Scripts gelaufen ist. Diese Zeile lohnt
sich mitzuschicken: mehrere lauffähige Kopien einer Fassung sind hier
normal, und ohne diese Zeile ist später nicht zu sagen, warum zwei
Läufe verschieden ausgingen.

**Der Auphonic-Schlüssel gehört nie in eine Meldung.** Das Programm
hält ihn im Schlüsselbund oder in der Registry, nie in einer Datei,
und aus der Projektdatei nimmt es ihn heraus. Keine Meldung braucht
ihn.

**Patches sind willkommen, und einen zweiten Leser gibt es nicht.**
Eine kleine Änderung, die eine Sache tut, wird gelesen und übernommen;
eine große wartet. MIT, und nichts zu unterschreiben.

**Vor einem Patch:** `cd tests && bash run.sh` laufen lassen und grün
lassen. Das Handbuch ist zweisprachig, und ein Test achtet darauf: ein
englisches Kapitel zu ändern heißt, das deutsche im selben Commit mit
zu ändern.

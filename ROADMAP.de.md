# Roadmap

*In English: [ROADMAP.md](ROADMAP.md)*

Was gebaut ist, was als Nächstes kommt und was dieses Programm nicht
werden soll. Hier steht eine Reihenfolge und kein Datum. Einer
schreibt daran, neben echter Produktionsarbeit, und ein Datum wäre
hier eine Schätzung, die wie eine Zusage aussieht.

Nichts auf dieser Seite ist eine Zusage. Ein Punkt rückt nach vorn,
wenn er sich als wichtiger herausstellt, und er fällt weg, wenn eine
Messung sagt, dass er sich nicht lohnt. Was wirklich fertig ist, steht
in [CHANGELOG.md](CHANGELOG.md), Version für Version. Diese Seite ist
zuletzt für 2.14.0-beta durchgegangen worden.

## Wo das Programm heute steht

**Version 2.22.0-beta.** Es läuft jede Woche, an echtem Material.

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

Es ist eine Python-Datei mit rund 36000 Zeilen, ohne Paket und ohne
Bauschritt. Python 3.10 oder neuer muss da sein, die zwei Pakete
installiert es selbst. Benutzt wird es unter macOS und Windows, unter
Linux läuft es mit zwei Einschränkungen. Eine Suite aus 119 Tests
braucht rund eine halbe Minute und läuft bei jedem Push auf allen drei
Systemen.

**Warum es noch beta heißt.** Das Format der Projektdatei kann sich
noch ändern. Eine ältere Datei wird mit einer klaren Meldung
abgewiesen statt halb gelesen. Wer Projekte über Monate aufhebt, sollte
das wissen. Beta endet, sobald das Format stillhält, und eine Änderung,
die es bricht, hebt die erste Stelle der Versionsnummer.

## Was als Nächstes kommt

Nach Nutzen gegen Aufwand geordnet. Der erste wartet auf einen Lauf, im
zweiten liegt die Arbeit, der dritte folgt darauf.

**1. Die zwei Wege zu auphonic.com werden einmal gegen den Dienst
gelaufen.** Das Transkript einer einzelnen Spur und eine
Multitrack-Produktion mit einer Stereospur sind beide gebaut, und
keiner ist je wirklich hinausgegangen. Ob der Dienst eine Stereospur
mit beiden Kanälen zurückgibt, ist offen. Bis das gelaufen ist,
beschreibt das Handbuch diese zwei Wege aus dem Quelltext statt aus
einem Lauf.

**2. Eine Zeitachse statt zwei.** Jeder Lauf muss Bilder und Ton auf
eine gemeinsame Zeitlinie legen. Dafür gibt es heute zwei getrennte
Stücke Code — eins für Multitrack, eins für den gewöhnlichen Lauf —,
und sie sind sich nicht einig. Auf dem gewöhnlichen Weg wurden zwei
Kameras übereinander an Resolve übergeben, und ein Zeitfenster meint
dort für jede Kamera einen anderen Moment, während Multitrack einen
Moment für alle meint.

Der gewöhnliche Lauf soll ein Sonderfall des Multitrack-Laufs werden.
Gemessen: an der Rechnung hindert nichts. Fünf geänderte Zeilen
genügen, um einen gewöhnlichen Lauf durch die gemeinsame Maschine zu
schicken, und an echtem Material legt sie drei Kameras auf das
Einzelbild genau an ihre eigenen Uhren. Es fehlen eine Weiche und eine
Entscheidung: wo der Nullpunkt der Achse liegt, wenn mehrere Kameras zu
verschiedenen Zeiten anfangen.

Alles bisherige war Vorarbeit, fertig und veröffentlicht: beide Wege
benennen ihre Dateien und Spuren jetzt gleich, beide prüfen die Farbe
und übernehmen die Schlüssel der Kamera, beide messen die Lautheit, und
beide sagen, in welcher Stufe ein Lauf gerade ist.

**3. Multitrack ohne Kamera.** Mehrere Aufnahmen und kein Bild wird
heute abgelehnt, und der Grund ist richtig: die Spuren werden an die
Kameras gelegt. Man könnte sie aber gegeneinander legen — gleich lang,
ein Startpunkt, fertig für auphonic. Das wartet, bis es eine Achse
gibt, damit es nicht zweimal gebaut wird.

## Was später kommt

Gröber, und in keiner festen Reihenfolge.

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

* **Die Ränder des Programms bekommen Tests.** Gemessen sind 71
  Prozent der Anweisungen abgedeckt. Die Trennung, das
  Selbst-Aktualisieren und ein Lauf ohne auphonic.com werden inzwischen
  durchgefahren; was kein Test betritt, sind die zwei Funktionen, die
  eine ganze Produktion mit auphonic.com darin zusammensetzen, das
  erste Hochladen einer neuen Produktion, die Hälfte des
  Einzeldateiwegs und der Rückweg nach einer misslungenen
  Selbst-Aktualisierung. Die
  Abdeckung wird gelegentlich gemessen und nie zum Ziel.

* **Das Handbuch bekommt, was ihm fehlt.** Rund ein Dutzend Zahlen
  stehen noch ohne ihre Vorgabe und ohne die Richtung, in die sie
  ziehen. Und eine veröffentlichte Adresse, sobald jemand eine zum
  Weitergeben braucht.

* **Kleinere Commits.** Ein Commit, dessen Betreff ein „und“ braucht,
  sind zwei Commits. Das kostet nichts, und `git bisect` und
  `git blame` beantworten danach eine Frage, statt auf einen Haufen zu
  zeigen.

## Was wir nicht vorhaben

Der nützlichste Abschnitt dieser Seite, weil er dir das Fragen spart.
Ein Wunsch, der auf dieser Seite fehlt, ist etwas anderes: er ist
nicht abgelehnt, er ist nur noch nicht aufgekommen.

* **Eine Produktion bei auphonic.com ohne Preset.** Deren eigene
  Seite lässt das zu, und bei uns wäre es der dritte Eintrag in der
  Liste. Er kommt nicht: eine Produktion ohne Preset trägt keine
  Einstellungen, und die hier anzubieten hieße, deren Oberfläche ein
  zweites Mal zu bauen. Das Preset wird dort gewählt und hier
  ausgesucht.

* **Die Folge schneiden.** Der Kameraschnitt ist ein Vorschlag, der
  Schnitt bleibt deiner. Das Programm misst und übergibt; Entscheiden
  ist keine spätere Stufe davon.

* **Einen Schnitt auf eine Wortgrenze legen statt auf den Ton.** Das
  stand unter „Was später kommt“, und die Messung hat es andersherum
  beantwortet: die leiseste Stelle landet 97 bis 99 mal
  von hundert in einer echten Sprechpause, die Wortgrenze der
  Erkennung 42 bis 46 mal. Der Text sagt weiterhin ungefähr wo --
  Satz- und Teilsatzenden kommen aus den Wortzeiten --, und der Ton
  sagt genau wo. Das zu tauschen machte den Schnitt schlechter.

* **Pull Requests als Prüfstelle, Pflichtdurchsichten, CODEOWNERS.**
  Alle drei setzen einen zweiten Menschen voraus. Wer sich selbst
  freigibt, hat nur den Weg verlängert. Pull Requests können trotzdem
  kommen, sobald es einen Ablauf gibt, dessen Ergebnis daran hängt.

* **Discussions.** Ein leerer Raum wirkt schlechter als kein Raum.
  Issues sind an, und dorthin gehört eine Frage.

* **Ein Wiki.** Das Handbuch steht in `docs/`, in zwei Sprachen, und
  ein Test hält die beiden Seiten gegeneinander. Ein Wiki wäre eine
  zweite Version, die nichts prüft.

* **Verhaltensregeln, Beitragsanleitung, Vorlagen für Issues und Pull
  Requests.** Sie heben eine Prozentzahl auf einer GitHub-Seite,
  solange niemand schreibt. Die Vorlagen kommen an dem Tag, an dem
  wirklich jemand etwas meldet.

* **Conventional Commits.** Ihr Zweck ist ein erzeugter Changelog und
  eine erzeugte Versionsnummer. Dieser Changelog ist von Hand
  geschrieben und trägt in fast jedem Punkt einen Messwert; ein
  Generator machte daraus eine Liste von Betreffzeilen.

* **Ein Umbau auf pytest, ruff, mypy und pre-commit.** Alle vier
  wollen ein Paket mit `pyproject.toml`. Hier wären es vier neue
  Abhängigkeiten für eine Datei, deren 103 Tests als schlichte Scripts
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

**Kein Punkt oben trägt eine Issue-Nummer.** Die Liste hält ein
einziges Issue, und das zeigt auf diese Seite. Ein Punkt bekommt sein
eigenes Issue an dem Tag, an dem jemand außer dem Autor ihn verfolgen
will. Danach zu fragen ist ein guter Anlass.

**Was eine Meldung brauchbar macht:** was du gestartet hast, was
herauskam und was du stattdessen erwartet hast. Das Log nennt die
Version und welche Kopie des Scripts gelaufen ist. Diese Zeile lohnt
sich mitzuschicken: mehrere lauffähige Kopien einer Version sind hier
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

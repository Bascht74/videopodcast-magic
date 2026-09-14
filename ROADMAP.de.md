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
zuletzt für 3.0.0b13 durchgegangen worden.

## Wo das Programm heute steht

**Version 3.0.0b13.** Es läuft jede Woche, an echtem Material.

Es macht die Arbeit vor dem Schnitt: aufbereiteten Ton als erste Spur
in die Videodateien legen, Rekorder und Kameras auf eine Zeitachse
bringen, die Sprecher allein aus dem Ton trennen, aufschreiben, was
gesagt wurde, einen ersten Schnitt nach Sprecher vorschlagen und ein
DaVinci-Resolve-Projekt schreiben.

Jeder Lauf geht denselben Weg. `--multitrack` sagt nur noch, wie die
Aufnahmen zu Produktionen zusammengefasst werden: Die Zeitachse, die
Lage jeder Kamera und die Dateien am Ende sind mit dem Schalter
dieselben wie ohne ihn. Mehrere Aufnahmen, unter denen keine Kamera
ist, werden stattdessen gegeneinander gelegt — gleich lang, ein Anfang
für alle — statt abgewiesen.

Wo eine Datei auf der gemeinsamen Zeitachse liegt, kommt aus ihrem Ton.
Die eigene Uhr einer Kamera zählt nur dort, wo der Ton nichts hergab,
und der Lauf nennt jede Datei, die er allein nach der Uhr setzen musste
— denn zwei Kameras gehen nur gleich, wenn jemand sie darauf gestellt
hat, und dann noch um ein, zwei Bilder daneben. Fenster, Vorschau und
fertiges Projekt stehen alle auf dieser einen Rechnung.

Sprechertrennung, Spracherkennung und Niederschrift laufen auf der
Maschine, vor der du sitzt. Trennung und Erkennung
brauchen je ein Modell, das beim ersten Gebrauch einmal geholt wird: das
der Trennung liegt in einem Ordner neben dem Programm, das der Erkennung
in einem eigenen Zwischenspeicher. Kein Konto, kein Token, und nach dem
einen Download kein Netz. Die Niederschrift bei auphonic.com zu bestellen ist weggefallen,
mit ihr der Haken und der Schalter dafür; die Worte hängen also weder
daran, dass der Dienst erreichbar ist, noch daran, dass eine
Voreinstellung gewählt wurde. Pegel, De-Bleed und Rauschunterdrückung
dort sind weiterhin freiwillig, und das Programm lädt erst hoch, wenn es
dazu aufgefordert wird.

Wo eine Tatsache fehlt, sagt das Fenster es, statt eine Antwort
entgegenzunehmen, die nichts bewirkt. Die Einstellungen, die die Worte
brauchen, und die, die einen Weitwinkel brauchen, stehen gesperrt, mit
dem Grund darunter, und sie öffnen sich wieder, sobald die Tatsache da
ist.

Das Protokoll neben dem Programm sagt, was ein Lauf außerhalb von sich
getan hat: jeden Aufruf von ffmpeg und ffprobe mit der Datei, um die es
ging, und mit seiner Dauer, Spracherkennung und Sprechertrennung ebenso,
was die beiden Abspieler geladen und gespielt haben, und auf welchem der
drei Wege jede Aufnahme gesetzt wurde. Was das Fenster rot gezeigt hat,
steht dort ebenfalls, mit der Uhrzeit — eine rote Marke ist weg, sobald
ihre Zeile neu gezeichnet wird, und die Beschwerde darüber kommt Stunden
später.

Das Fenster spricht dreizehn Sprachen, und jede sagt alles: jeder der
zwölf Kataloge hat für jeden der rund 1400 Texte des Programms eine
Antwort, die Zeilen eines Laufs und den Schritt nach Resolve
eingeschlossen. Was jede Sprache beantwortet, wird bei jedem Push
gezählt und darf nur wachsen, und jede wird an allem gemessen.

Es ist ein Python-Programm: ein Ordner, `videopodcast_magic/`, in dem
eine kleine Datei liegt, mit der das Programm startet, daneben
fünfunddreißig Stücke in je einem eigenen Ordner und das Sprechermodell.
Installiert wird es mit `pip3 install git+...`, zu bauen ist daran
nichts. Eine einzelne Datei zu holen und zu starten war bis zum 4.9.2026
der zweite Weg hinein und ist keiner mehr -- eine Kopie ohne den übrigen
Ordner bleibt schon beim Import stehen. Python 3.10 oder neuer muss da
sein und `ffmpeg`, das kein Python ist und das Einzige, was pip nicht
mitbringen kann; jedes Python-Paket, das es braucht, steht auf der
Liste, die pip liest, und kommt mit der Installation. Benutzt wird es
unter macOS und Windows, unter Linux läuft es mit zwei Einschränkungen.

**Bis zum 4.9.2026 war es eine Datei, und jetzt ist es ein Ordner.**
Zuerst gingen die Texte heraus, je Sprache eine Datei, und in den drei
Tagen danach folgte der Rest: die Datei, mit der das Programm startet,
hatte an jenem Tag 37 535 Zeilen und hat jetzt 717, und das größte
Stück, das Fenster, hat 3867. Für jeden, der daran arbeitet, folgt
daraus nur eines -- das Programm wird als Ordner kopiert, nie als die
Datei darin. Eine Suite aus 263 Tests läuft bei jedem Push: sechs Läufe
nebeneinander, drei Systeme und zwei Python-Versionen. Daneben liegen
vier weitere, die ein echtes Resolve brauchen und nirgends sonst laufen
können. Die sechs sind nicht gleich schnell, und der langsame ist
Windows: über die letzten sieben grünen Läufe, gemessen am 3.9.2026,
brauchte der langsamste der sechs zwischen 404 und 835 Sekunden, und es
war jedes Mal ein Windows-Lauf. Gewartet wird auf diesen einen, nicht
auf die Summe der sechs.

**Warum es noch beta heißt.** Das Format der Projektdatei kann sich
noch ändern. Eine ältere Datei wird mit einer klaren Meldung
abgewiesen statt halb gelesen. Wer Projekte über Monate aufhebt, sollte
das wissen. Beta endet, sobald das Format stillhält, und eine Änderung,
die es bricht, hebt die erste Stelle der Versionsnummer.

## Was als Nächstes kommt

Sechs Punkte. Die ersten vier sind Arbeit. Die letzten zwei sind gebaut,
und was ihnen fehlt, ist jemand, der sich mit echtem Material hinsetzt,
nicht weiteres Bauen.

**Sechzehn Sprachen kommen dazu.** Bengalisch, Vietnamesisch und
Koreanisch, dazu dreizehn europäische — Polnisch, Rumänisch,
Niederländisch, Griechisch, Schwedisch, Ungarisch, Serbisch,
Tschechisch, Kroatisch, Dänisch, Finnisch, Slowakisch und Norwegisch,
das Norwegische als Bokmål und das Serbische kyrillisch. Das sind dann
neunundzwanzig Sprachen, jede mit einer Antwort auf jeden Text des
Programms, so wie die dreizehn von heute; die Prüfung der Feldbreiten
sieht schon jede Sprache an, die das Fenster anbietet.

**Der ganze Weg bekommt Tests, nicht die einzelnen Funktionen an ihm.**
Sieben Schritte, und jeder davon auf beiden Wegen: Das Programm öffnet
sich, Dateien kommen herein, In und Out werden markiert, der Wechsel auf
Reiter 3, der richtige Schnitt mitsamt einer schon vorhandenen
Sprechererkennung, der Lauf selbst, der Import nach Resolve. Das ist ein
Punkt und keine Liste von fünfzig: Wer ihn anfasst, deckt einen der
sieben Schritte ganz, denn nach Nummer abgearbeitete Lücken geben je
einen Test und zusammen keinen Weg. Die Erhebung, die diese Lücken
gezählt hat, ist mehrere Fassungen alt, und das meiste, was sie nannte,
ist seither gedeckt — sie lohnt sich noch einmal, bevor darauf gebaut
wird.

**Tests gegen ein echtes DaVinci Resolve.** In der Suite können sie
nicht stehen: Auf einer Maschine ohne Resolve wäre jeder von ihnen rot
aus einem Grund, der kein Fehler ist. Sie liegen daneben, in einem
eigenen Ordner mit einem eigenen Starter, den die Suite nicht kennt, und
sie laufen einer nach dem anderen auf der einen Maschine, auf der
Resolve steht. Vier sind gebaut, und drei davon laufen jetzt auch gegen
das unbenannte Projekt, mit dem Resolve aufmacht — also nach jedem
Start. Der Vorspann gehört hierher: das Programm legt ihn auf die zweite
Videospur und liest nach, wie viele Clips dort liegen, und eine Attrappe
kann das nicht bestätigen. Und der Fall, den keine Attrappe je gezeigt
hat: ein Resolve, das nein sagt.

**Die Tests ziehen in Ordner wie die Stücke, die sie prüfen.** Das
Programm ist in Stücke geteilt, jedes in einem eigenen Ordner. Bis auf vier
stehen die Tests noch nebeneinander in einem, weit über zweihundert. Wenn sie
folgen, stehen ein Stück und seine Prüfungen an einer Stelle, und wer
ein Stück ändert, findet seine Tests daneben.

**Die zwei Wege zu auphonic.com werden einmal gegen den Dienst
gelaufen.** Beide stellen dieselbe Frage — kommt eine Stereo-Aufnahme
zweikanalig zurück — und sie stellen sie auf zwei ganz verschiedene
Arten. Eine einzelne Aufnahme geht über die einfache Schnittstelle: Die
Produktion wird angelegt, ohne sie zu starten, die Ausgabedateien werden
zurückgelesen, auf jeder wird die Faltung auf Mono gestrichen, und das
Ganze geht noch einmal hin — also zwei Aufrufe. Mehrere Aufnahmen gehen
über die volle Schnittstelle, die denselben Wunsch gleich in die eine
Anfrage setzt. Keiner der beiden ist je wirklich hinausgegangen, und
einer vertritt den anderen nicht. Bis das gelaufen ist, beschreibt das
Handbuch diese zwei Wege aus dem Quelltext statt aus einem Lauf.

**Der Reaktionsschnitt wird gesichtet, bevor er scharf bleibt.** Er
greift ein paar Dutzend Mal in einer Folge und ist voreingestellt an,
und niemand hat bisher jede Stelle angesehen. Zwei Fälle, in denen er
falsch liegt, sind bekannt: die rhetorische Frage und das technische
Vorgeplänkel, wo Blicke zu Geräten fliegen statt zu Gesichtern.

## Was später kommt

Gröber, und in keiner festen Reihenfolge.

* **Vorgaben, die einen Beleg tragen.** Ein paar Zahlen stammen aus
  einem einzelnen Referenzschnitt statt aus einer Messung.
  `--wide-latest` ist der deutlichste Fall: 120 Sekunden, und dahinter
  ein einziger Schnitt. Jede von ihnen wird gemessen oder kleiner.

* **Die Ränder des Programms bekommen Tests.** Wie weit die Tests
  reichen, sagt ein Lauf: coverage.py über `bash run.sh`, mit gesetztem
  `COVERAGE_PROCESS_START`, damit die Läufe mitzählen, die die Tests
  selbst starten. Beim letzten solchen Lauf betrat die
  Suite rund sieben von zehn Anweisungen. Die Zahl wird als Spanne gelesen und nie als
  Ziel, und sie stammt aus der Zeit, als das Programm noch eine einzige
  Datei war — sie will neu erhoben werden. Was so ein Lauf wirklich wert
  ist, ist die Liste der Stellen, die kein Test betritt. Zwei sind auch
  ohne ihn bekannt: die Meldungen, mit denen das Programm abbricht, wenn
  unterwegs etwas Unerwartetes schiefgeht, und der Weg, der den Ton
  allein aus den Kameras nimmt, wenn es keine eigenen Aufnahmen gibt.
  Ein dritter, ein Resolve, das sich weigert, gehört zu den Tests gegen
  ein echtes Resolve weiter oben.

* **Acht lange Definitionen bekommen ihre Beschreibung.** Die Kommentare
  im Programm haben bekommen, was die Tests schon hinter sich hatten:
  Kommentar und Docstring sind von knapp einem Drittel der Zeilen auf
  ein Viertel gefallen, und die Stellen, an denen ein Kommentar länger
  läuft, als die Regeln wollen, von 104 und 141 auf je sieben. Übrig
  ist die umgekehrte Lücke. Acht Definitionen von hundert Zeilen und
  mehr, der Schnittplayer darunter, tragen noch gar keine Beschreibung,
  und eine Prüfung hält diese Zahl fest, sodass sie nur noch fallen
  kann.

* **Das Handbuch bekommt, was ihm fehlt.** Rund ein Dutzend Zahlen
  stehen noch ohne ihre Vorgabe und ohne die Richtung, in die sie
  ziehen. Und eine veröffentlichte Adresse, sobald jemand eine zum
  Weitergeben braucht.

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
  Erkennung 42 bis 46 mal. Der Text sagt weiterhin ungefähr wo —
  Satz- und Teilsatzenden kommen aus den Wortzeiten —, und der Ton
  sagt genau wo. Das zu tauschen machte den Schnitt schlechter.

* **Pflichtdurchsichten und CODEOWNERS.** Beide setzen einen zweiten
  Menschen voraus, und wer sich selbst freigibt, hat nur den Weg
  verlängert. Was vor `main` steht, ist der Baurechner: Eine Änderung
  kommt als Pull Request, und hinein kommt sie erst, wenn alle sechs
  Läufe grün zurück sind.

* **Discussions.** Ein leerer Raum wirkt schlechter als kein Raum.
  Issues sind an, und dorthin gehört eine Frage.

* **Ein Wiki.** Das Handbuch steht in `docs/`, in zwei Sprachen, und
  ein Test hält die beiden Seiten gegeneinander. Ein Wiki wäre eine
  zweite Version, die nichts prüft.

* **Verhaltensregeln und Vorlagen für Issues.** Sie heben eine
  Prozentzahl auf einer GitHub-Seite, solange niemand schreibt. Die
  Vorlage für Issues kommt an dem Tag, an dem wirklich jemand etwas
  meldet. Was ein Patch mitbringen muss, steht aus dem umgekehrten
  Grund niedergeschrieben: Fünf Regeln weisen hier eine Änderung
  zurück, so gut der Gedanke auch ist, und wer nicht nachfragen kann,
  muss sie in zehn Minuten lesen können. Das ist
  [CONTRIBUTING.md](CONTRIBUTING.md), und das Formular, mit dem ein Pull
  Request aufgeht, fragt sie bereits ab.

* **Conventional Commits.** Ihr Zweck ist ein erzeugter Changelog und
  eine erzeugte Versionsnummer. Dieser Changelog ist von Hand
  geschrieben und trägt in fast jedem Punkt einen Messwert; ein
  Generator machte daraus eine Liste von Betreffzeilen.

* **Ein Umbau auf pytest, ruff, mypy und pre-commit.** Das wären vier
  neue Abhängigkeiten für ein Programm, dessen 263 Tests als schlichte
  Scripts durchlaufen. Eine dünne pytest-Schicht, die genau diese
  Scripts unverändert startet, ist etwas anderes und kann kommen.

* **Bildvergleich der Handbuchbilder in der Suite.** Die Bilder
  entstehen im echten Fensterstil, dafür braucht es einen Bildschirm
  mit angemeldetem Benutzer, und ein Test darf sich den Vordergrund
  nicht nehmen. Ein solcher Test wäre überall sonst rot oder blind.
  Stattdessen werden die Bilder einer Version, die das Fenster ändert,
  vor ihrer Freigabe neu aufgenommen, damit das Handbuch das Fenster
  zeigt, mit dem sie hinausgeht.

* **Doku-Tests, die Sätze vergleichen.** Am heutigen Handbuch
  gemessen: jede fette Beschriftung oder jede genannte Vorgabe zu
  prüfen bringt am ersten Tag ein Fünftel bis ein Drittel Fehlalarm,
  und der erste Tag ist der beste, den so ein Test hat. Einen Test, der
  über fünf Prozent Fehlalarm anfängt, bauen wir nicht.

* **Eine Abdeckungsschwelle als Tor.** Wer eine Zahl zum Ziel macht,
  bekommt die Zahl. Die Liste der Funktionen, die kein Test je aufruft,
  ist etwas wert; der Prozentsatz nicht.

* **Den Testlauf auf mehrere Rechner verteilen, Bots für die Triage.**
  Die sechs Läufe antworten in Minuten, und es gibt keine Schlange von
  Meldungen. Beides beantwortet eine Menge, die es hier nicht gibt.
  Einen Test ein zweites Mal laufen zu lassen ist etwas anderes, und
  das ist gebaut: Ein abgestürzter Test bekommt einen weiteren Anlauf,
  ein neben den anderen roter läuft noch einmal allein, und in beiden
  Fällen heißt er danach unstet, statt grün gezählt zu werden. Ein
  flatternder Test ist ein Fehler, den man sucht, kein Rauschen, das
  man durch Wiederholen loswird.

* **Installationsprogramme, signierte Pakete, Notarisierung, ein Eintrag
  bei PyPI.** Ein Weg hinein reicht: aus dem Repository, mit
  `pip3 install`, oder mit `pipx install` und derselben Adresse, wo das
  Python des Systems pip nicht hineinlässt. Die erste Installation dauert
  Minuten, weil das Fenster, die Spracherkennung und die
  Sprechertrennung mitkommen. Das Programm kommt aus dem Repository, was
  es von anderen braucht, von PyPI; drei Dinge kommen an pip vorbei —
  ffmpeg, wo es fehlt, denn es ist kein Python, und beim ersten Gebrauch
  zwei Modelle: das der Sprechertrennung aus dem eigenen Repository des
  Programms, das der Spracherkennung, das die Erkennung selbst holt.
  Aktualisiert wird auf demselben Weg, aus dem Fenster wie von der
  Kommandozeile: Es ruft pip auf.

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
Läufe verschieden ausgingen. Bei einer Beschwerde über die Vorschau
oder darüber, wo eine Kamera gelandet ist, gehört das Protokoll selbst
dazu: darin steht, was die Abspieler geladen und gespielt haben, welche
Aufnahme unter welches Bild gelegt wurde, und wie jede Datei zu ihrem
Platz auf der Zeitachse kam.

**Der Auphonic-Schlüssel gehört nie in eine Meldung.** Auf dem Mac hält
das Programm ihn im Schlüsselbund, unter Windows in der Registry; unter
Linux speichert es ihn gar nicht. Die Projektdatei enthält keine
Befehlszeile, also steht er auch dort nicht drin. Keine Meldung braucht
ihn.

**Patches sind willkommen, und einen zweiten Leser gibt es nicht.**
Eine kleine Änderung, die eine Sache tut, wird gelesen und übernommen;
eine große wartet. MIT, und nichts zu unterschreiben.

**Vor einem Patch: [CONTRIBUTING.md](CONTRIBUTING.md) lesen.** Zehn
Minuten, und darin stehen die Regeln, die eine Änderung zurückweisen, so
gut der Gedanke auch ist: `cd tests && bash run.sh` laufen lassen und
grün lassen, zu jeder Prüfung gehört ein Beleg, dass sie auch rot werden
kann, und das Handbuch ist zweisprachig, worauf ein Test achtet — ein
englisches Kapitel zu ändern heißt, das deutsche im selben Commit mit zu
ändern.

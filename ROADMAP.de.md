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
zuletzt für 3.0.0b0 durchgegangen worden.

## Wo das Programm heute steht

**Version 3.0.0b1.** Es läuft jede Woche, an echtem Material.

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
Maschine, vor der du sitzt. Das Modell liegt in einem Ordner neben dem
Programm: kein Konto, kein Token, und nach dem einen Download kein
Netz. Die Niederschrift bei auphonic.com zu bestellen ist weggefallen,
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

Es ist eine Python-Datei mit rund 40 000 Zeilen, die man holen und
starten oder mit pip installieren kann; zu bauen ist daran nichts.
Python 3.10 oder neuer muss da sein, und nach den zwei Paketen, die es
braucht, fragt es, bevor es sie installiert. Benutzt wird es unter
macOS und Windows, unter Linux läuft es mit zwei Einschränkungen. Eine
Suite aus 220 Tests läuft bei jedem Push: sechs Läufe nebeneinander,
drei Systeme und zwei Python-Versionen. Daneben liegen vier weitere,
die ein echtes Resolve brauchen und nirgends sonst laufen können. Die sechs sind nicht gleich
schnell, und der langsame ist Windows: über die letzten sieben grünen
Läufe, gemessen am 3.9.2026, brauchte der langsamste der sechs zwischen
404 und 835 Sekunden, und es war jedes Mal ein Windows-Lauf. Gewartet
wird auf diesen einen, nicht auf die Summe der sechs.

**Warum es noch beta heißt.** Das Format der Projektdatei kann sich
noch ändern. Eine ältere Datei wird mit einer klaren Meldung
abgewiesen statt halb gelesen. Wer Projekte über Monate aufhebt, sollte
das wissen. Beta endet, sobald das Format stillhält, und eine Änderung,
die es bricht, hebt die erste Stelle der Versionsnummer.

## Was als Nächstes kommt

Vier Punkte. Die ersten zwei sind Arbeit. Die letzten zwei sind gebaut,
und was ihnen fehlt, ist jemand, der sich mit echtem Material hinsetzt,
nicht weiteres Bauen.

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
  reichen, sagt ein Lauf: coverage.py über `bash run.sh`, mit
  gesetztem `COVERAGE_PROCESS_START`, damit die Läufe mitzählen, die
  die Tests selbst starten. Grün sind es rund drei Viertel der
  Anweisungen — gelesen als Spanne und nie als Ziel. Was so ein Lauf
  wirklich wert ist, ist die Liste der Stellen, die kein Test betritt,
  und die will neu erhoben werden: Die letzte ist mehrere Fassungen alt,
  und das meiste, was sie nannte — die Schalter, die genommen wurden,
  ohne dass jemand prüfte, was sie tun, eingeschlossen —, ist seither
  gedeckt.

* **Die Kommentare im Programm bekommen, was die Tests schon hinter
  sich haben.** 27 % der Datei sind Kommentar, und das meiste davon ist
  vor den Regeln geschrieben worden, nach denen einer geschrieben wird.
  In den Tests ist es getan, und sie sind dabei um ein Drittel kürzer
  geworden.

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
  Erkennung 42 bis 46 mal. Der Text sagt weiterhin ungefähr wo —
  Satz- und Teilsatzenden kommen aus den Wortzeiten —, und der Ton
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

* **Verhaltensregeln und Vorlagen für Issues.** Sie heben eine
  Prozentzahl auf einer GitHub-Seite, solange niemand schreibt. Die
  Vorlage für Issues kommt an dem Tag, an dem wirklich jemand etwas
  meldet. Was ein Patch mitbringen muss, steht aus dem umgekehrten
  Grund niedergeschrieben: Vier Regeln weisen hier eine Änderung
  zurück, so gut der Gedanke auch ist, und wer nicht nachfragen kann,
  muss sie in zehn Minuten lesen können. Das ist
  [CONTRIBUTING.md](CONTRIBUTING.md), und das Formular, mit dem ein Pull
  Request aufgeht, fragt sie bereits ab.

* **Conventional Commits.** Ihr Zweck ist ein erzeugter Changelog und
  eine erzeugte Versionsnummer. Dieser Changelog ist von Hand
  geschrieben und trägt in fast jedem Punkt einen Messwert; ein
  Generator machte daraus eine Liste von Betreffzeilen.

* **Ein Umbau auf pytest, ruff, mypy und pre-commit.** Das wären vier
  neue Abhängigkeiten für eine Datei, deren 220 Tests als schlichte
  Scripts durchlaufen. Eine dünne pytest-Schicht, die genau diese
  Scripts unverändert startet, ist etwas anderes und kann kommen.

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

* **Den Testlauf auf mehrere Rechner verteilen, Bots für die Triage.**
  Die sechs Läufe antworten in Minuten, und es gibt keine Schlange von
  Meldungen. Beides beantwortet eine Menge, die es hier nicht gibt.
  Einen Test ein zweites Mal laufen zu lassen ist etwas anderes, und
  das ist gebaut: Ein abgestürzter Test bekommt einen weiteren Anlauf,
  ein neben den anderen roter läuft noch einmal allein, und in beiden
  Fällen heißt er danach unstet, statt grün gezählt zu werden. Ein
  flatternder Test ist ein Fehler, den man sucht, kein Rauschen, das
  man durch Wiederholen loswird.

* **Installationsprogramme, signierte Pakete, Notarisierung, PyPI.**
  Zwei Wege hinein reichen: die eine Datei holen und starten, oder sie
  mit pip aus dem Repository installieren.

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

**Der Auphonic-Schlüssel gehört nie in eine Meldung.** Das Programm
hält ihn im Schlüsselbund oder in der Registry, und aus der Projektdatei
nimmt es ihn heraus. Keine Meldung braucht ihn.

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

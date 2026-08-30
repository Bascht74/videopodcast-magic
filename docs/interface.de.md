# Die Oberfläche

*In English: [interface.md](interface.md). Zurück zum
[Inhalt](README.de.md).*

## Die vier Reiter

Vier Reiter, in der Reihenfolge, in der man sie braucht.

- **Dateien & Produktion**: oben die Dateiliste, darunter ein schmaler
  Streifen mit Produktionsname, gesprochener Sprache und Ausgabeordner.
  Dateien oder ganze Ordner hineinziehen, hinzufügen oder ein früheres
  Projekt öffnen. Solange die Liste leer ist, steht dort eine
  Ablegefläche, die den Ablauf erklärt.

  Das Programm nennt den Blick auf das Material vor einem Lauf den
  Vorflug. Jede Datei bekommt daraus schon beim Hinzufügen ein
  Prüfzeichen: ✓ nichts zu bemängeln, ! ein Hinweis, ✕ so geht es nicht.
  Unter der Liste steht das Ergebnis in einem Satz;
  [Vorflug](preflight.de.md) sagt, was jedes Prüfzeichen bedeutet.

  **Projekt öffnen ...** steht auf der Ablegefläche und unter **Datei**.
  Ein geöffnetes Projekt nimmt jederzeit neue Dateien auf, und sein Name
  steht in der Titelzeile — ein Fenster mit geöffnetem Projekt und eines
  ohne sind so nicht dasselbe Bild.

  Liegt beim Material eine Projektdatei, bietet das Programm sie an,
  während die Dateien hereinkommen, und bevor eine davon vermessen wird:
  findet es eine, fragt es einmal und nennt sie mit dem Tag, an dem sie
  geschrieben wurde; findet es mehrere, zeigt es sie zur Auswahl; findet
  es keine, geschieht nichts. Teilweise wird nie geladen — das Projekt
  kommt ganz zurück, mit den Namen, der Trennung, wer vor welcher Kamera
  sitzt, den Typen und dem Zeitfenster, oder es wird gar nicht geöffnet.

  Ein **Nein** lässt die hereingekommenen Dateien genau dort, wo sie
  sind. Die Liste entsteht aus ihnen und wird vermessen wie sonst auch,
  einmal, und dieselbe Projektdatei wird kein zweites Mal angeboten. Ein
  **Ja** setzt die Dateien des Projekts an ihre Stelle, und weil die
  Frage zuerst kam, wurde nichts vermessen, was die Antwort gleich
  darauf wegwirft. Material aus einem anderen Ordner bietet das Projekt
  dieses Ordners an; weiteres Material aus einem Ordner, nach dem schon
  gefragt wurde, fragt nicht noch einmal. Ist ein Projekt offen, wird
  nichts mehr angeboten.

  Der Ausgabeordner wird nicht geraten. Er bleibt leer, bis er gewählt
  wird oder bis ein Projekt sagt, wohin es geht. Der Produktionsname
  wird aus dem Ordner vorgeschlagen, in dem das Material liegt, und
  lässt sich überschreiben.

  Jede Videodatei trägt in der Liste das Feld **Kameraton**. Es steht
  auf **Ton nicht verwenden**, bis jemand es auf **Ton verwenden**
  stellt. Dann geht dieser Ton denselben Weg wie eine eingelesene
  Aufnahme: Kanäle gemessen, eine Spur oder zwei entschieden, leere
  Kanäle bleiben draußen, in Spuren zerlegt. Zum Synchronisieren wird
  dieser Ton ohnehin genommen; darüber entscheidet das Feld nicht.

  Wo nichts zu entscheiden ist, setzt sich das Feld selbst, ist
  ausgegraut und trägt den Grund daneben:

  - die Datei hat keine Tonspur,
  - die Datei bleibt ganz draußen,
  - die Datei ist ein Intro oder ein Outro,
  - eine einzige Videodatei trägt Ton, und keine Tonaufnahme steht
    daneben. Dieser Ton ist dann der einzige, den es gibt, und das Feld
    steht auf **Ton verwenden**. Kommt eine Tonaufnahme dazu, ist die
    Wahl wieder frei.

  Dasselbe Feld steht auf **Zuordnung & Zeitfenster** bei der Kamera,
  auf demselben Wert: ändert man eines, folgt das andere sofort.

  Jede Videodatei trägt in der Liste außerdem das Feld **Typ**:
  **Inhalt**, **Weitwinkel**, **Vorspann**, **Abspann** oder
  **Video ignorieren**. Wer auf dem Feld stehen bleibt, erfährt, was die
  fünf bedeuten. Das Feld selbst wird nie im Ganzen ausgegraut — Grau
  über dem ganzen Kasten hieße „hier ist nichts zu machen“, und zu
  machen ist immer etwas.

  Gesperrt wird höchstens ein Eintrag der Liste: er steht grau da und
  lässt sich nicht wählen, und der Grund steht an ihm — wer darauf
  stehen bleibt, liest ihn. Zwei Einträge können so gesperrt sein, jeder
  mit seinem eigenen Satz.

  - Eine Kamera, der niemand zugeordnet ist, zeigt **Weitwinkel**,
    obwohl niemand sie so gekennzeichnet hat. Gesperrt ist dann
    **Inhalt**, weil ihr kein Sprecher zugeordnet ist. Gibt man dieser
    Kamera einen Sprecher oder setzt den **Typ** selbst, ist der Eintrag
    wieder frei.
  - Eine Datei, für die die Messung keinen Platz gefunden hat, kann
    nicht der Weitwinkel sein: auf den Weitwinkel fällt der Schnitt
    zurück, also muss er auf der Zeitachse liegen. Gesperrt ist dann
    **Weitwinkel**, mit eben diesem Grund.

  Vorspann, Abspann und die Datei ganz herauszulassen werden nie
  gesperrt. Das sind Antworten über die Datei selbst und haben nichts
  damit zu tun, wer vor welcher Kamera sitzt.

  Eine Datei mit mehr als einem Kanal sagt darunter, was aus ihr wird: je
  Kanal eine Zeile, mit einem Häkchen, das in der ersten Zeile
  **mit Channel 2 zusammenlegen** anbietet, und daneben, was gemessen
  wurde. Das Programm benennt Kanäle, in denen nichts steht, und lässt
  sie aus allem Weiteren heraus.
  [Kanäle: eine Spur oder zwei?](channels.de.md) sagt, wie das Programm
  die beiden unterscheidet.

  Eine einzelne Fortsetzungsdatei lässt sich für sich entfernen. Sie
  bleibt dann draußen, obwohl sie im Ordner liegt, und später wieder
  hinzugefügt ist sie eine eigene Aufnahme. Erst wenn die ganze Aufnahme
  entfernt und wieder hinzugefügt wird, gehören die Blöcke wieder
  zusammen.

  ![Die Dateiliste](images/files.de.png)

  *Die Liste nach dem Öffnen eines Projekts, mit den Prüfzeichen aus
  dem Vorflug und dem Streifen darunter.*
- **Zuordnung & Zeitfenster**: links die Tabellen, rechts der Player.
  Erscheint mit den Dateien.

  Die Aufnahmen sind ein Baum. Seine zweite Spalte ist der
  **Sprechername**. Sie startet leer, mit dem Namen, den der Dateiname
  nahelegt, grau darin: ein eingetippter Name sagt, dass die Aufnahme
  diese eine Person ist, und der Eintrag **mehrere Sprecher**, den man
  stattdessen wählen kann, setzt das Programm daran, auf diesem Rechner
  zu ermitteln, wer wann in genau dieser Aufnahme spricht. Erst diese
  Antwort zeigt die Stimmen. Eine Trennung, die niemand beantwortet
  hat, lässt das Feld leer und die Zeilen verborgen, und eine spätere
  Antwort holt sie sofort hoch, mit den Namen und Kameras, die sie
  schon hatten. Die fünfte Spalte, **Sprecher**, sagt, wie es darum
  steht -- **Abbrechen**, solange es läuft, in dieser Zeile und in
  keiner anderen, danach **Getrennt: 4 Sprecher**, und daneben das
  Angebot **Nur ein Sprecher -- Spur auftrennen?**, wo immer ein Name
  im Feld steht.

  Bei mehr als einer Tonaufnahme läuft nichts von selbst; die Antwort in
  der Zeile startet es. Unter den Aufnahmen steht **Auf diesem Rechner
  nicht**: das schaltet die Trennung für das ganze Projekt ab.

  Die Stimmen sind die Zeilen unter der Aufnahme, in der sie gehört
  wurden ([Spracherkennung und Sprechertrennung](speech.de.md)),
  eingerückt und zunächst aufgeklappt. Jede sagt in der ersten Spalte
  **Stimme**, damit die Stufe zu sehen ist, und trägt den Namen und die
  zugehörige Kamera. Zugeklappt sagt die Aufnahme unter **gehört zu**,
  was das Zuklappen vom Schirm nimmt -- die Kameras: **auf 2 Kameras**,
  oder **auf 1 Kamera, 1 ohne**, wenn eine Stimme noch keine hat;
  aufgeklappt bleibt diese eigene Zelle leer, damit die Zuordnung nie
  auf zwei Ebenen zugleich steht. Ein Klick auf eine Stimme holt den
  Player an die Stelle, wo diese Stimme am längsten redet, und spielt
  sie ab. Aufnahmen, die keine Stimmen zeigen, sind eine flache Liste,
  ohne Dreiecke.

  Die Kameratabelle darunter trägt noch einmal **Kameraton**, bei jeder
  Kamera, auf dem Wert aus der Dateiliste. Eine Kamera auf
  **Ton verwenden** bekommt eine Zeile in der Zuordnungstabelle
  darüber, wie eine eigene Aufnahme.

  ![Zuordnungstabelle und Player](images/assignment.de.png)

  *Oben, welche Aufnahme zu welcher Kamera gehört, unten, was aus
  jeder Kamera wird.*
- **Resolve-Schnitt**: eine Zeile, die sagt, ob Resolve antwortet, mit
  dem Weg zu den Einstellungen daneben. Dann das Zeitfenster, der Kasten
  mit den Werten für den Schnitt und der Kasten **Sprecher**, dessen
  Überschrift die Quelle der Sprecher nennt. Zuletzt der Kasten
  **Kameraschnitt -- Vorschau** mit Schnittband und abspielbarer
  Vorschau.

  Der Kasten mit den Werten heißt **Kameraschnitt**, wenn die Sprecher
  auf zwei oder mehr Kameras sitzen. Bei einer Kamera für alle heißt er
  **Erster Schnitt nach Sprechern**. Dort wird nichts gewechselt: der
  Schnitt fällt bei jedem Sprecherwechsel, und Resolve bekommt je Person
  einen Clip. Bei einer Person und einer zweiten Kamera, auf der niemand
  ist, heißt er **Schnitt mit dem Weitwinkel**: die Kamera dieser Person
  steht, und der Weitwinkel bricht sie auf. Mit gesetztem **Multitrack**
  bleibt der Name **Kameraschnitt**.

  Der Kasten erscheint, sobald **Multitrack** gesetzt ist oder zwei
  Personen einen Namen und eine Kamera tragen -- die Stimmen unter einer
  getrennten Aufnahme oder die Zeilen der Zuordnungstabelle. Eine Person
  genügt, wo es zwei oder mehr Kameras gibt. Eine Person auf einer
  einzigen Kamera bekommt keinen Kasten, und das ist richtig: es gibt
  nichts, wohin geschnitten werden könnte. Bis dahin steht an der
  Stelle von Kasten und Vorschau eine Zeile, die sagt, was fehlt. Ein
  Resolve-Projekt entsteht trotzdem, mit jeder Kamera am gemessenen
  Platz.

  Beide hinteren Reiter stehen mit und ohne getrennte Spuren da. Ohne sie
  zeigt die Zuordnungsspalte grau „in alle Kameras“.
- **Ausgabe**: erscheint, sobald etwas läuft, in denselben Farben wie
  das Terminal, mit den Knöpfen **Ergebnis-Ordner öffnen** und
  **Resolve-Projekt anlegen**.

**Multitrack (je Sprecher eine Spur)** hat eine eigene Zeile unter der
Zuordnungstabelle, über dem Auphonic-Kasten. Es geht mit auphonic.com
und ohne; nach dem API Key fragt das Programm erst auf dem Weg über
auphonic.com. Der Kameraschnitt braucht das Häkchen nicht.

Multitrack braucht zwei Eingangsspuren. Eine Eingangsspur ist eine
eigene Aufnahme, ein Kanal eines mehrkanaligen Aufnahmegeräts oder der
Ton einer Videodatei, die auf **Ton verwenden** steht. Mehrere Blöcke
derselben Aufnahme zählen als eine Spur, eine beiseitegelegte Spur gar
nicht.

Das Häkchen bleibt anklickbar, was auch immer im Projekt liegt. Bei nur
einer Spur sagt das eine graue Zeile daneben, und sie nennt den Weg zur
zweiten: **Kameraton** bei einer Kamera, gestellt auf
**Ton verwenden**. Wenn jede Kamera ihren Ton schon hergibt, sagt diese
Zeile, dass keiner mehr übrig ist.

**Sprache** neben dem Produktionsnamen ist die in der Aufnahme gesprochene
Sprache, vorbelegt aus der Systemsprache. Sie wird zur Kennzeichnung der
geschriebenen Tonspur und sagt auphonic.com, was es beim Transkribieren
erwarten soll. „nicht gesetzt“ lässt die Spur ungekennzeichnet und
überlässt der Erkennung die Sprache.

**Lautheit** in der Gruppe **Produktion** auf der ersten Seite legt fest,
wie laut die fertige Folge gemacht wird; derselbe Gewinn geht auf jede
Spur, so bleibt das Verhältnis der Sprecher erhalten. Fünf Einträge:

- **-16 LUFS (Podcast-Verzeichnisse, stereo)**
- **-19 LUFS (Podcast-Verzeichnisse, mono)**
- **-14 LUFS (YouTube -- regelt nur herunter, nie herauf)**
- **-23 LUFS (EBU R128, Rundfunk)**
- **Aus Quelldateien übernehmen**

Ein neues Projekt beginnt bei −16 LUFS. Das Fenster merkt sich den zuletzt
gewählten Eintrag, und eine geladene Projektdatei sticht diese Erinnerung.
**Aus Quelldateien übernehmen** passt gar nichts an: auphonic.com macht
weiter, was in seinem Preset steht, und ohne auphonic.com bleibt der Ton
wie in den Quelldateien -- die Datei kommt Byte für Byte gleich heraus.

[Welches Lautheitsziel gilt](preflight.de.md#welches-lautheitsziel-gilt)
sagt, was sonst noch am Ziel hängt: die Normalisierung der Spuren, die
Anzeige im Resolve-Projekt und was im Protokoll steht.

**Probelauf** ist der Lauf, der misst und berichtet, aber nichts schreibt.
Er und **Start** bleiben gesperrt, solange etwas offen ist, und
**unter den Knöpfen steht, was**, mitsamt dem Reiter, auf dem es steht:

- keine Dateien,
- kein Ton in Verwendung: keine Tonaufnahme, und keine Videodatei auf
  **Ton verwenden**,
- kein Produktionsname,
- weniger als zwei Spuren in der Zuordnungstabelle für Multitrack,
- bei Multitrack eine Aufnahme ganz ohne Namen: keiner getippt, und
  keiner, den der Dateiname nahelegt -- der graue Vorschlag gilt als
  Name, wo nichts darüber getippt wird,
- bei Multitrack alle Aufnahmen unter demselben Namen,
- zwei Kameras mit derselben Ausgabedatei.

Das Feld oder die Zeile, die gemeint ist, wird rot. Ein Häkchen hinter
einem Reiter heißt: dort ist nichts mehr offen. Kein Fenster geht dafür
auf.

Dann eine Zusammenfassung: wie viele Kameras und Tonspuren, wie
lang, welches Preset, wie viele Dateien entstehen, wieviel Platz sie
brauchen und wieviel frei ist. Wenn der Lauf bestehende Dateien
überschreiben würde, zeigt ein Fenster erst, welche.

Der Player hat Abspielen und Pause, sekunden- und frameweise vor und
zurück, Lautstärke und Tempo; links der Timecode, rechts die Position, ab
dem In-Punkt gezählt.

- Ein Klick auf eine Zeile der Zuordnungs- oder der Kameratabelle holt
  die Datei an dieselbe Stelle im Geschehen, so lassen sich zwei Kameras
  vergleichen. Ein Klick auf eine Stimme unter einer Aufnahme öffnet
  diese Aufnahme dort, wo die Stimme am längsten redet, und spielt
  sofort. Das Häkchen **zugeordneten Ton hören** spielt die dieser
  Kamera zugeordnete Aufnahme; ohne das Häkchen ist der Kameraton zu
  hören.
- In-Punkt und Out-Punkt nehmen die Stelle aus dem Bild, ein blauer
  Streifen zeigt das Fenster, und beim Ziehen laufen nur die Zahlen mit.
  Solange die Zeitachse fehlt, sind sie gesperrt.
- Formate, die der Rechner nicht abspielen kann (MXF, R3D, manche
  ProRes-Spielarten), bekommen einen Knopf für `ffplay`.

Die Ausgabe landet zusätzlich in `videopodcast-magic.log` neben dem
Script, mit Version, Zeit und Rechner in der Kopfzeile und einer
Trennlinie je Lauf; vom vorletzten Lauf bleibt
`videopodcast-magic_1.log`. Auch was Qt und ffmpeg an Python vorbei
ausgeben, steht darin.

Neben **Start** läuft **ein Balken für alles Ausstehende**, mit einer
Zeile daneben, woran gerade gearbeitet wird; er läuft immer nur vorwärts.
Er deckt beide Hälften ab: das Messen nach jeder Änderung an der
Dateiliste und den Lauf selbst. Zu diesem Messen gehören Hüllkurven,
Kameraton, Kanäle und die Prüfung, und eine Hüllkurve ist die Lautheit
über die Länge einer Spur.

Ein Abschnitt, der echte Prozente meldet, nimmt den Balken mit. Bei einem
Abschnitt, der nichts meldet, kriecht er langsam weiter und bleibt vor
dem Ende stehen.

Für den Lauf selbst nennt die Zeile den Abschnitt, auf beiden Wegen mit
denselben Namen, mit Multitrack und ohne:

- **Plan wird gelesen**
- **Ton aus den Kameras**: nur mit Multitrack. Ohne richtet der Lauf sich
  an den Kameras aus und lässt sie in Ruhe.
- **Gemeinsame Zeitachse**
- **Aufbereitung bei auphonic.com**, ohne Schlüssel **Lautheit und Pegel**
- **Wer wann spricht**
- **Kameradateien werden geschrieben**
- **Übergabe und Ergebnis**

Ein Abschnitt, der gar nicht vorkommt, steht auch nicht in der Liste; der
Balken hält also keinen Anteil für ihn zurück. Bleibt ein Lauf stehen,
sagt die Zeile, in welchem Abschnitt.

### Was hinter Einstellungen ... steht

Der Knopf **Einstellungen ...** sitzt im Fußbereich, neben **Start**.
Dahinter steht, was man einmal einrichtet und dann nicht mehr anfasst:
der Schlüssel für auphonic.com samt Häkchen, das ihn ablegt, und ob
Resolve antwortet. Das Preset und die Transkription gehören zur
Produktion und stehen dort, wo über die Spuren entschieden wird: unter
der Zuordnungstabelle.

Das Fenster hinter dem Knopf hat zwei Kästen.

- **Zugang zu auphonic.com**: das Feld für den API Key und das Häkchen,
  das ihn behält (**Im Schlüsselbund speichern** auf dem Mac, **In der
  Registry speichern** unter Windows). **Verbinden** prüft den Schlüssel
  und holt die Presets.
- **Verbindung zu Resolve**: ob Resolve antwortet, mit Version, wenn ja,
  und den Gründen, wenn nein. **Erneut prüfen** fragt noch einmal, das
  Öffnen des Fensters ebenso.
  [DaVinci Resolve](resolve.de.md) sagt, was ein Nein bedeutet.

![Das Einstellungsfenster](images/settings.de.png)

*Hinter Einstellungen ...: der Schlüssel für auphonic.com, und ob
Resolve antwortet.*

## Alles über Menü oder Taste erreichen

Die Menüleiste trägt vier Menüs: **Datei**, **Ansicht**, **Wiedergabe**
und **Hilfe**.

**Datei** steht in der Reihenfolge, in der die Arbeit geht. Zuerst das
Projekt — **Projekt öffnen ...**, **Projekt speichern**, **Projekt
schließen** —, dann das Material, dann der Lauf. **Projekt schließen**
räumt das Fenster leer, bis es aussieht wie nach dem Start, und lässt
die Datei unberührt, aus der es kam; das ist der Weg zu einer zweiten
Produktion, ohne das Programm zu beenden. **Projekt speichern**
schreibt die Projektdatei dorthin, wohin der Ausgabeordner zeigt, ohne
etwas laufen zu lassen.

**Ansicht** nennt die Reiter beim Namen, statt sie zu nummerieren.
**Hilfe** enthält den Weg in dieses Handbuch, **Was sich in dieser
Version geändert hat**, **Nach Update suchen ...** und **Über Video
Podcast Magic**.

Auf dem Mac sitzt die Menüleiste oben am Bildschirmrand, sonst oben im
Fenster. **Einstellungen ...** wandert dort ins Programmmenü und steht
sonst überall unter **Datei**.

Alles, was über einen Knopf geht, geht auch über eine Taste. Die Tasten
ohne Zusatztaste gehören dem Player und wirken nur, solange er den
Fokus hat.

| Taste | Was sie tut |
|---|---|
| `Cmd+P` | Projekt öffnen |
| `Cmd+S` | Projekt speichern |
| `Cmd+W` | Projekt schließen |
| `Cmd+O` | Dateien hinzufügen |
| `Cmd+Rückschritt` | Das Ausgewählte entfernen |
| `Cmd+Umschalt+O` | Ausgabeordner wählen |
| `Cmd+R` | Start |
| `Cmd+Umschalt+R` | Probelauf |
| `Cmd+1` `Cmd+2` `Cmd+3` | Auf diesen Reiter |
| `Cmd+,` | Einstellungen |

Im Player:

| Taste | Was sie tut |
|---|---|
| `Leertaste` | Abspielen und anhalten |
| `L` | Vorwärts abspielen, mit jedem Druck doppelt so schnell |
| `K` | Anhalten, zurück auf 1× |
| `Links` `Rechts` | Ein Frame |
| `Umschalt+Links` `Umschalt+Rechts` | Eine Sekunde |
| `Alt+Links` `Alt+Rechts` | Zehn Sekunden |
| `I` `O` | In-Punkt setzen, Out-Punkt setzen |
| `Umschalt+I` `Umschalt+O` | Zum In-Punkt, zum Out-Punkt springen |

`L` verdoppelt bis 8×, und das Tempo steht am Vorlauf-Knopf. Der Player
hat kein `J`: Qt spielt hier nichts rückwärts, gemessen.

Unter Windows und Linux steht `Strg` statt `Cmd`. Es ist die Belegung,
die die Schnittprogramme gemeinsam haben.

## Sich selbst aktuell halten

Kurz nachdem das Fenster steht, fragt das Programm github.com, ob es eine
neuere Version gibt. Es sieht nur dann nach, nicht während eines Laufs.
Das ist eine Frage nach einer Nummer.

Wenn es eine gibt, nennt ein Fenster sie und die Version, die hier läuft.
Es zeigt, was sich in der neuen Version geändert hat, in ihren eigenen
Worten, und darunter die Adresse. Zwei Knöpfe:

- **Später** lässt die laufende Version an ihrem Platz.
- **Aktualisieren** holt die neue Version, setzt sie an die Stelle der
  Datei und startet das Programm neu.

Das Programm liest, was herunterkommt, bevor es das benutzt: es muss
lesbarer Text sein, es muss wie dieses Programm aussehen, und es muss
sich übersetzen lassen. Wenn eine der drei Prüfungen fehlschlägt, bleibt
die Datei liegen, die funktioniert, und das Fenster sagt, was nicht
stimmte.

Die Version, die lief, bleibt als `videopodcast-magic.py.old` neben der
neuen liegen. **Hilfe > Zurück auf 2.3.0-beta** setzt sie wieder ein;
der Eintrag nennt die Nummer aus dieser Datei und steht nur im Menü,
solange die Datei da ist.

Es wird vorher gefragt, und die aufbewahrte Datei muss dieselben drei
Prüfungen bestehen wie das, was herunterkommt. Danach startet das
Programm neu. Die Datei ist damit aufgebraucht, und vorwärts geht es
wieder über das Update aus dem Netz.

Das Häkchen **Nicht mehr nachfragen** hält das Programm davon ab, von
selbst nachzusehen. Über **Hilfe > Nach Update suchen ...** geht es
weiterhin.

## Wie die Zeitachse ohne Timecode entsteht

Wenn eine Datei keinen Timecode trägt, misst die Oberfläche im
Hintergrund, wo sie liegt, mit dem Verfahren des Laufs selbst. Danach
springt der Player zwischen den Dateien auf dieselbe Stelle im Geschehen,
und In-Punkt und Out-Punkt gelten für alle gleich.

Ein einziger Timecode genügt, um die Achse daran zu hängen; ohne jeden zählt
sie ab dem Anfang des Materials und wird als virtueller Timecode angezeigt.

Die Achse steht in der Projektdatei, mit Größe und Änderungszeit jeder
Datei, und der nächste Start übernimmt sie. Dateien, die nicht dazu
passen, erscheinen rot. Mehr über die Projektdatei steht in
[camera-cut.de.md](camera-cut.de.md).

Die Messung unterscheidet zwei Urteile. Eine Datei, deren Ton schlecht zu
den anderen passt, steht in Rot. Eine Datei, die überhaupt keinen Platz
hat -- ihr Ton hat mit dem übrigen Material nichts gemeinsam, und kein
Timecode ordnet sie zwischen die anderen ein --, wird in der Spalte
**Typ** auf **Video ignorieren** gesetzt, und das Protokoll sagt, warum.
Das ist ein Vorschlag wie die für die Stimmen: Er füllt nur einen **Typ**,
in dem noch die eigene Antwort des Programms steht, nie einen, den jemand
gewählt hat, und eine Datei, die eine spätere Messung wieder einordnen
kann, bekommt ihren alten Eintrag zurück.

## Wenn etwas klemmt

- **Start** bleibt gesperrt: die Zeile unter den Knöpfen nennt, was
  fehlt, und das gemeinte Feld oder die gemeinte Zeile wird rot. Ist
  das nachgetragen, gibt der Knopf sich frei.
- **Der Player zeigt kein Bild**: an seine Stelle tritt ein Knopf, der
  die Datei an `ffplay` übergibt; das öffnet ein eigenes Fenster.
- **In-Punkt und Out-Punkt sind gesperrt**: das Programm misst die
  Zeitachse noch. Der Balken neben **Start** sagt, was gerade läuft.
- **Eine Datei steht plötzlich auf „Video ignorieren“**: die Messung hat
  keinen Platz für sie gefunden. Ihr einen Timecode geben, der zum
  übrigen Material passt -- der muss mit einem anderen Programm gesetzt
  werden --, oder von Hand einen **Typ** wählen, was die Sache endgültig
  entscheidet.
- **Das Update ging nicht durch**: die Datei, die funktioniert, bleibt
  liegen, und das Fenster sagt, was nicht stimmte. **Hilfe > Nach Update
  suchen ...** versucht es noch einmal.
- **Beim Nachfragen mitschicken**: die Version aus `--version`, das
  Betriebssystem, `videopodcast-magic.log` und was man vorhatte, vor
  den Einzelheiten des Fehlers.

Das ist das ganze Fenster. Im nächsten Kapitel, [Vorflug](preflight.de.md),
geht es um die Prüfungen vor einem Lauf und um die Bedeutung jedes
Prüfzeichens in der Dateiliste.

### Weitere Optionen über die Kommandozeile

Im Fenster gibt es diese Optionen nicht.

`--update-check` holt das ungefragte Nachsehen zurück, nachdem das
Häkchen **Nicht mehr nachfragen** gesetzt wurde.

`--no-update-check` setzt dasselbe Nein wie dieses Häkchen. Ein Lauf von
der Kommandozeile sieht ohnehin nicht nach: aus einem Script gestartet,
darf er an keiner Frage stehen bleiben.

`VPM_NO_UPDATE_CHECK` in der Umgebung schaltet das Ganze ab, den
Menüeintrag mit. Der Eintrag sagt das dann, statt nachzusehen. Diese
Variable setzt, wer die Maschine betreibt.

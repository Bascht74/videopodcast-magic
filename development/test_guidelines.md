# Testrichtlinien

Für `tests/`. Sie sind an dieser Suite entstanden: was hier steht, hat
sich beim Bauen bewährt oder ist durch einen Fehler gelernt worden.

Der Anlaß in einem Satz. Beim Lesen aller Testköpfe fielen an einem Tag
siebzehn Tests auf, die weniger prüfen als ihr Kopf verspricht. Keiner
war rot. Gefunden hat sie das Lesen, nicht die Suite — **und darum muß
alles, was hier steht, beim Schreiben auffallen und nicht erst beim
Lesen.** Die Liste am Ende ist der eigentliche Ertrag; die Abschnitte
davor sagen, warum ihre Punkte draufstehen.

Diese Suite hat kein Rahmenwerk, keine Klassen, keine Testbibliothek.
Ein Test ist ein Skript, das ein Urteil je Zeile druckt und einen
Rückgabewert setzt. Was aus der Literatur übernommen ist, steht mit dem
Grund dabei, warum es auf diese Form paßt; was nicht paßt, steht in
Abschnitt 9.

---

## 1. Wie ein Test gebaut wird

**Ein Test, der nichts zusichert, ist kein Test.** Ruft er eine
Funktion, druckt das Ergebnis und endet, dann heißt grün dort
ausschließlich „ist nicht abgestürzt" — und von außen sieht das genau
aus wie ein Test, der besteht. Das ist der Fehler, aus dem alle
anderen dieser Liste folgen.

Die Literatur führt das unter der selbstprüfenden Eigenschaft, dem S
der FIRST-Merksätze: *„Tests are pass-fail. No agency must examine the
results to determine if they are valid and reasonable."* Ein Test ohne
Zusicherung entzieht sich dieser Unterscheidung; der Katalog der
Testgerüche nennt ihn den Test, der nie fällt — *„If a test won't fail
even when the code to implement the functionality doesn't exist, how
useful is it?"*

Und er ist nicht selten. In einer Erhebung über 656 quelloffene
Programme trug fast die Hälfte mindestens einen Test ohne jede
Zusicherung, und jede dritte Testdatei. Befragt, nannten die Autoren
solcher Tests es durchweg ein Versehen. Es ist die häufigste Art, wie
eine Suite größer wird, ohne mehr zu prüfen.

**Das Urteil fällt `check`, nie ein nacktes `assert`.** Vier Gründe,
und jeder einzelne reicht:

* `assert` wirft eine Rückverfolgung statt einer lesbaren Zeile.
* Der erste Fehlschlag bricht ab; alles dahinter läuft nicht mehr und
  wird auch nicht als ungeprüft gemeldet. Ein Test mit vier Blöcken
  meldet dann einen Fehler und verschweigt drei.
* Eine Zusicherung trägt keine Zahlen. Was erwartet war und was da
  war, steht nirgends.
* Es wird nichts gezählt, und ohne Zählung fällt niemandem auf, daß
  ein Test null Urteile fällt.

Die Form, in der es hier steht:

```python
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))
```

**Der Rückgabewert kommt aus der Zahl der Fehlschläge, nicht aus dem
Ende des Programms.** Die Schlußzeilen sind immer dieselben:

```python
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
```

**Jeder Weg durch den Test führt an dieser Stelle vorbei.** Ein Test,
dessen Zusicherungen in einem Zweig einer Zeitgeberkette stehen,
während ein zweiter Zeitgeber das Programm nach einer Frist unabhängig
davon beendet, geht mit 0 hinaus, obwohl er beim ersten Schritt
abgestürzt ist. Er gilt monatelang als bestanden. Wo nebenläufig
gearbeitet wird, endet der Test an einer Stelle, und diese Stelle
fragt die Zählung.

**Die gedruckte Zahl der Urteile ist die zweite Sicherung.** Sie steht
in jedem Lauf da. Wer sie liest, sieht eine Null, und er sieht drei,
wo der Kopf zwölf verspricht. Keine Zusicherung findet das; eine Zahl
neben der Erwartung findet es beim Hinsehen.

**Eine Lage herstellen, viele Dinge daran prüfen.** Arrange-Act-Assert
verlangt eine Handlung je Test, und die schärfste Lesart eine
Zusicherung je Test. Das ist für Tests geschrieben, die Millisekunden
kosten; hier kostet die Lage einen ffmpeg-Vorlauf. Also wird sie einmal
hergestellt und dann zwanzigmal befragt — aber jede Frage mit eigenem
Namen auf eigener Zeile, damit die Trennung erhalten bleibt, die AAA
meint.

Das ist kein Sonderweg: schon wer das Muster benannt hat, hält sich
nicht an die eine Zusicherung, und die verbreitete Abschwächung lautet
nicht eine Zusicherung je Test, sondern **ein Begriff je Test.** Die
Grenze verläuft also nicht bei der Zahl der Prüfungen, sondern dort, wo
ein Test zwei verschiedene Dinge behauptet. Dann sind es zwei Tests.

**Keine Logik im Test.** Eine Schleife, die die Erwartung ausrechnet,
rechnet meist genauso falsch wie das Programm. Was der Test erwartet,
steht als Wert da, und wo es berechnet werden muß, dann auf einem
anderen Weg als im Programm.

**Wo ein Test wirklich nur einen Absturz fangen kann**, sagt er das im
Kopf **und** in seiner Schlußzeile, und er behauptet keine Zählung, die
er nicht hat. Diese Suite hat drei solche Fälle, und sie bleiben es:
was sie bauen, kann nur ein fremdes Programm beurteilen. Das ist eine
Ausnahme mit Grund, kein Muster.

## 2. Wie er dokumentiert wird

**Die erste Zeile sagt, was gilt, wenn der Test grün ist.** Nicht, was
er tut. Eine Aussage über das Programm, in einem Satz, so daß man aus
ihr allein entscheiden könnte, ob einen der rote Lauf angeht.

**Was im Kopf steht, hat ein `check`. Was ein `check` prüft, steht im
Kopf.** Beide Richtungen. Der Kopf ist der Vertrag, und ein Kopf, der
mehr verspricht als der Test hält, hat in der Literatur einen Namen:
der Lügner — *„a test that runs, but does not test what it claims to
test … Liars give a false sense of security."* Beide Seiten werden
gebrochen: ein Test endet mit „Farbmarken und Kameraton kamen
mit", geprüft wird genau eine Farbmarke — und ein anderer prüft in
allen zwölf Abschnitten auch die Zurückweisungen, obwohl sein Kopf nur
nach dem gebauten Ergebnis fragt. Der zweite Fall ist der harmlosere
und trotzdem ein Fehler: was im Kopf nicht steht, wird beim nächsten
Umbau weggeräumt.

**Der Kopf wird bei jeder Änderung mitgelesen.** Ein Kopf, der von
einem Aufbau redet, den der Test seit einem Umbau nicht mehr baut,
schickt jeden Leser in die falsche Richtung — und er ist die
wahrscheinlichste Ursache dafür, daß ein Loch jahrelang niemandem
auffällt.

**Keine Zahl im Kopf, die mitwandern müßte.** „Sechs Dinge" über sieben
Blöcken, ein Block „8" zweimal und keiner 9, eine Stufennummer aus
einem Plan von vorgestern. Eine Zahl im Kopf ist eine zweite Stelle,
die gepflegt werden will, und sie verliert immer. Die Blöcke tragen
Namen, nicht Nummern; wo doch numeriert wird, ist die Numerierung das,
was der Test druckt, und wird von dort abgeschrieben.

**Ein Vermerk „dieser Schritt ist rot" geht mit der Reparatur hinaus,
nicht im nächsten Aufräumen.** Sonst ist der Satz in dem Moment
unwahr, in dem er geschrieben wird, und bleibt es. Wer danach kommt,
glaubt ihm und läßt eine arbeitende Prüfung in Ruhe.

**Länge: acht Zeilen**, wie für jeden Docstring. Was hineingehört:
die Aussage, danach die Abschnitte in der Reihenfolge, in der sie
kommen, und ein Satz über die Grenze der Methode, wenn es eine gibt.
Was nicht hineingehört: ein Datum, ein Name, ein Pfad, der Weg, der
dorthin geführt hat, und eine Zahl aus einem einzelnen Lauf. Das alles
altert, und keiner Zeile hilft es.

## 3. Wie er heißt

**`<gegenstand>_check_<behauptung>_test.py`**, höchstens dreißig
Zeichen vor `_test.py`, Kleinbuchstaben, Englisch.

**Zwölf feste Präfixe für den Gegenstand:** `files_`, `sound_`,
`time_`, `voice_`, `cut_`, `project_`, `auphonic_`, `window_`,
`table_`, `run_`, `text_`, `source_`.

**Das Präfix sagt, wo der Fehler säße, nicht wovon die Daten
handeln.** Das ist die Regel, die alle Grenzfälle entscheidet. Ein Test
über Kanäle, dessen Fehler in der Tabelle sichtbar würde, heißt
`table_check_channel_rows`. Ein Name nach dem Material — nach der
Aufnahme, nach dem Weg, nach dem Ordner — zwingt jeden, der die rote
Zeile sieht, die Datei zu öffnen, um zu wissen, welcher Teil des
Programms kaputt ist.

**Die zweite Hälfte ist eine Behauptung, kein Ding**: `atom_travels`,
nicht `log_atom`. Ein Ding im Namen läßt offen, was gelten soll, und
deckt darum jede Prüfung, die irgendwie mit dem Ding zu tun hat — auch
eine, die etwas ganz anderes mißt. Genau so kommt ein Kopf zustande,
der „zeigt den Schnitt richtig" verspricht, während überwiegend
Bildpunktfarben gezählt werden.

**Die erste Docstring-Zeile ist die Langform derselben Behauptung**,
höchstens 79 Zeichen: was gilt, wenn der Test grün ist.

**Dasselbe gilt für jedes einzelne `check`.** Sein Name ist der Satz,
der im Bericht steht, und er wird gelesen, wenn nichts anderes mehr da
ist:

```python
# richtig
check("a marked camera is the wide shot even with a speaker on it", ...)

# falsch
check("wide shot", ...)
```

**Paßt die Behauptung nicht in den Namen, hält der Test zwei.** Nach
dem Präfix und `check_` bleiben fünfzehn bis zwanzig Zeichen, also zwei
oder drei Wörter. Das ist knapp, und die Enge ist nützlich: wer die
Behauptung nicht in drei Wörter bekommt, behauptet meistens zwei
Dinge. Dann wird geteilt — und nicht der Name zu einem Ding
zurückgekürzt.

### Die bekannten Einwände

Eine Regel, deren Einwände danebenstehen, hält länger als eine, die
so tut, als gäbe es keine. Von den vier Teilen des Schemas ist einer
schwach belegt, zwei sind offen, einer ist geteilt.

**Das Wort `check` unterscheidet nichts, und die Literatur ist
dagegen.** Sie warnt vor Füllwörtern und vor einem Vorsatz, den alle
Namen tragen, weil er dann nichts trennt. Ein Stilhandbuch, das genau
diesen Fall regelt — Testdateien statt Testmethoden —, sagt es
ausdrücklich: die Testmarkierung gehört an das Suffix und in den
Ordner, nicht ein zweites Mal in den Namen. Und `_check_` kostet sechs
der dreißig Zeichen, ein Fünftel des Budgets. Ein Beleg dafür, ein
bedeutungsloses, überall gleich lautendes Wort zu führen, ist nicht zu
finden.

**Es steht trotzdem da**, aus einem Grund, den die Literatur nicht
kennt: ohne Verb liest sich der Name als Ding, und ein Ding zu lesen,
wo eine Behauptung stehen soll, ist genau der Fehler, den das Schema
verhindern will. `files_log_atom` wurde prompt als Ding verstanden.
Das Wort ist die Fuge, die den Leser zwingt, den Rest als Aussage zu
lesen. **Das ist der schwächste Punkt des Schemas**, und wenn sich
zeigt, daß die Behauptungen auch ohne die Fuge als Behauptungen gelesen
werden, kann das Wort gehen und sechs Zeichen mitnehmen.

**Die Datei trägt zwanzig Behauptungen und heißt nach einer.** Dazu
gibt es keine Literatur: alles Geschriebene setzt voraus, daß die Datei
nach dem Gegenstand heißt und die Behauptungen in den Namen der
einzelnen Prüfungen stehen. Die eine Quelle, die Dateinamen überhaupt
regelt, benennt sie nach Bereich und Teilbereich — nach einem Ding.
Unser Schema hebt die Behauptung eine Ebene höher; das ist unbelegt,
aber auch unwidersprochen.

**Das Risiko ist benannt:** neunzehn Behauptungen sind im Namen
unsichtbar. Die Gegenmaßnahme ist Abschnitt 2 und Punkt 2 der
Checkliste — der Kopf führt sie alle, in beide Richtungen geprüft.
Ohne diesen Punkt wäre das Schema gefährlich, denn es macht den Namen
zu einem Versprechen über die Datei, von dem sie ein Zwanzigstel
einlöst.

**Die Lage fehlt im Namen.** Die verbreiteten Schemata haben drei
Teile — Gegenstand, Lage, Erwartung —, unseres hat zwei; die Lage
steht im Kopf darunter. Der Verlust ist in der Literatur ausdrücklich
benannt: der Name sei oft das einzige, was in einem Fehlerbericht
sichtbar ist, und man müsse verstehen können, was kaputt ist, **ohne
den Testquelltext zu lesen.**

**Die Antwort darauf ist, wo bei uns der Fehlerbericht anfängt.**
Sichtbar wird dort nicht der Dateiname, sondern die gefallene
`check`-Zeile — und die trägt Lage und Erwartung, weil Abschnitt 4 es
verlangt. Die Forderung der Literatur ist also erfüllt, nur eine Ebene
tiefer, als sie es meint. Dazu kommt: eine Datei mit zwanzig Lagen
kann keine davon im Namen nennen, ohne die anderen neunzehn zu
verschweigen. Wofür die Literatur uneingeschränkt einsteht, ist die
Kürze — und der Dreißig-Zeichen-Deckel ist die Regel des Schemas, die
am besten belegt ist.

**Zwölf Präfixe nach Programmteil: die Quellen sind geteilt.** Die eine
Seite warnt davor, Tests nach der Programmstruktur zu ordnen — man
prüfe Verhalten, nicht Quelltext, und eine Spiegelung Eins-zu-Eins
bindet die Tests an die Bauweise. Die andere Seite ordnet ausdrücklich
nach dem Bereich des Programms, mit derselben Absicht wie wir: einen
Test schnell finden und einen Fehlschlag schnell einordnen. Der
Unterschied, der beides verträglich macht: **ein grobes Gebiet ist
keine Spiegelung.** Zwölf Präfixe auf 141 Tests bilden
keinen Programmteil ab, sie machen ein Register.

**Ein Zahlenmaß für zu grob oder zu fein gibt die Literatur nicht
her.** Der brauchbare Prüfstein ist ein anderer: **trennt jedes Präfix
wirklich?** Ein Präfix mit einem einzigen Mitglied ist keine Kategorie,
eines mit sechzig ist keine Auskunft. Daran gemessen ist zwölf gut
gewählt: heute tragen die 141 Tests zweiundneunzig verschiedene
erste Wörter, also praktisch keine Einteilung; zwölf ergeben im Schnitt
ein Dutzend je Präfix. Wächst eines über ein Viertel des Bestands oder
schrumpft eines auf einen Test, ist die Einteilung nachzuziehen — nicht
der Test umzubiegen.

## 4. Wie die Fehlerzeile aussehen muß

**Auf fremden Rechnern existiert nur, was in der Zeile selbst steht.**
Sechs Baurechner-Jobs, und aus der ganzen Ausgabe eines Tests sucht
der Bericht die Zeilen heraus, die nach einem Fehler aussehen. Alles,
was vorher gedruckt wurde, ist dann weg. Wer die Zahl daneben braucht,
muß den Lauf wiederholen — auf einer Maschine, die er nicht hat.

Das ist die eine Eigenschaft, unter der alle anderen dieses Abschnitts
stehen: **ein Fehlschlag muß handlungsfähig machen.** *„When a test
fails, you should be able to begin investigation with nothing more than
the test's name and its failure messages — no need to add more
information and rerun the test."* Name und Zeile, sonst nichts.

**Jede Fehlerzeile trägt, was erwartet war und was da war.** Dafür ist
das dritte Argument da, und es ist nicht wahlfrei:

```python
# richtig
check("the shot does not fall below the minimum",
      shortest >= limit,
      "shortest %.2f s against a minimum of %.2f s" % (shortest, limit))

# falsch
check("the shot does not fall below the minimum", shortest >= limit)
```

**Zahlen, keine Eigenschaftswörter.** „zu kurz" sagt nichts, was man
nachrechnen könnte. „0,31 s gegen 0,80 s" sagt alles.

Das ist die Antwort auf einen Geruch mit eigenem Namen, das
Zusicherungs-Roulette: mehrere gleichartige Zusicherungen in einem
Test, und die rote Meldung sagt nicht, welche gefallen ist. Die
Faustregel dagegen — jeder Zusicherung eine eigene Meldung, sobald es
mehr als eine gleicher Art gibt — nennt ausdrücklich den Fall, in dem
sie am meisten zählt: einen Testlauf auf der Befehlszeile, wo keine
Entwicklungsumgebung die gefallene Zeile hervorhebt. Das ist unsere
Lage, in jedem Lauf.

Und es wird selten befolgt. In zwanzig quelloffenen Vorhaben trugen
etwa fünf Prozent der Zusicherungen überhaupt eine Meldung, während in
einer Befragung sechs von zehn Entwicklern angaben, immer oder sehr oft
eine mitzugeben. Es ist nichts, was man von selbst tut, sondern etwas,
das auf einer Liste stehen muß.

**Und sie muß den richtigen Fehler nennen.** Eine Zeile behauptete,
die Kamera habe nicht gewechselt, während in Wahrheit der Abspieler
nie gelaufen war. Wo eine Behauptung auf einer Voraussetzung ruht,
wird die Voraussetzung eine eigene Prüfung und steht davor. Dann nennt
die rote Zeile das erste, was nicht stimmte, statt das letzte.

**Eine Zeile je Urteil, und die Schlußzeile faßt zusammen.** Der
Bericht zeigt die Zusammenfassung zuerst; sie muß darum alle
gefallenen Prüfungen nennen, nicht nur die Zahl.

## 5. Wie gegengeprüft wird

**Das ist der wichtigste Abschnitt dieser Datei.**

**Eine Prüfung, die niemand rot bekommt, ist nichts wert.** Grün sagt
über das Programm nichts, solange nicht gezeigt ist, daß dieselbe
Prüfung rot wird, wenn die geprüfte Sache falsch ist. In dieser Suite
standen zwölf Prüfungen, die überhaupt nicht fallen konnten: eine
verglich einen Aufruf mit sich selbst, eine war zufrieden, sobald ein
Wort irgendwo im Quelltext stand, eine lief über eine Liste, die sich
nie füllen konnte, eine sicherte zweimal dasselbe zu, eine fragte, ob
ein Schlüssel mit einem Vorsatz beginnt, statt mit welchem, eine ging
bei null durch. Alle zwölf waren grün, jahrelang, und keine Suite der
Welt hätte das gemeldet.

**Wie er geht.** Eine Kopie des Programms, in der genau die geprüfte
Sache wirklich falsch ist, und der Test dagegen:

```bash
cp videopodcast-magic.py /tmp/broken.py
# genau die eine Sache kaputtmachen, die die Prüfung behauptet
VPM_SCRIPT=/tmp/broken.py python3 tests/<name>_test.py
```

Prüft der Test nicht das Programm, sondern eine Rechnung über Daten,
dann liegt die verfälschte Fassung im Test selbst, neben der Prüfung:
dieselbe Ablesung über eine gefälschte Liste, mit abgeschaltetem
Schalter, mit einem umgedrehten Versatz. Ein Test dieser Suite macht
das durchgehend und sagt es in seinem Kopf: *„a check nobody can make
fail proves nothing."*

**Kaputt heißt: genau die eine Sache, und klein.** Wer das Programm
insgesamt zerlegt, bekommt alles rot und hat über diese Prüfung nichts
gelernt. Ein umgedrehtes Vorzeichen, eine Grenze um eins verschoben,
ein weggelassener Aufruf reichen: die Untersuchungen zum
Mutationstesten haben gemessen, daß Testdaten, die die kleinen
Abweichungen fangen, über 99 Prozent der zusammengesetzten mitfangen.
Ein aufwendig nachgebauter, lebensechter Fehler bringt also nichts,
was das umgedrehte Vorzeichen nicht auch bringt.

Umgekehrt gilt: bleiben beim Gegenbeweis andere Prüfungen grün, die
denselben Fehler hätten fangen müssen, ist das ein zweiter Fund.

**Was nur der Gegenbeweis fängt.** Eine Prüfung suchte das Wort
*offset* in allem Gedruckten. Sie war immer grün, weil das Programm
seinen eigenen absoluten Pfad druckt und der Arbeitsordner so heißt.
Kein Lesen findet das, keine Ratsche, keine Abdeckungszahl: die Zeile
wird ausgeführt, die Bedingung ist wahr, alles sieht richtig aus. Eine
kaputte Fassung, in der das Wort nie gedruckt wird, findet es beim
ersten Versuch.

### Die Attrappe

**Wird der Gegenbeweis nicht rot, ist die erste Frage: liegt es an der
Prüfung oder an der Attrappe?** Wer diese Frage nicht stellt, hält eine
großzügige Attrappe für eine bestandene Prüfung.

**Eine Attrappe, die mehr erlaubt als das Echte, macht jede Prüfung
darüber wertlos — und zwar unsichtbar, weil alles grün bleibt.** Sie
muß in jedem Punkt, den die Prüfung berührt, **mindestens so streng
sein wie das Nachgebildete**: verweigern, was jenes verweigert, und die
Verfahren haben, deren Fehlen jenes bemerkbar machen würde.

Beide Hälften sind einzeln aufgetreten. Eine nachgebaute Medienablage
erfand jede Spur, nach der gefragt wurde; die Prüfung „nur eine
Videospur angelegt" war deshalb grün, während Dinge auf Spuren lagen,
die es nicht gab — das Echte verweigert das stillschweigend, und genau
deswegen schafft das Programm vorher Platz. Und einer nachgebauten
Zeitachse fehlte das Verfahren zum Löschen einer Spur. Die Funktion,
die leere Spuren entfernt, lief also in eine verschluckte Ausnahme,
und zehn leere Spuren überlebten jeden Lauf.

**Ein verschlucktes `except` in der Attrappe ist der gefährlichste
Fall**, weil dann nicht einmal eine Rückverfolgung erscheint: das
Programm fragt nach etwas, das die Attrappe nicht hat, und der Test
sieht davon nichts.

**Damit prüft der Gegenbeweis nicht nur die Prüfung, sondern auch das
Gerüst darunter.** Das ist sein zweiter Ertrag, und ohne ihn wäre
keiner der beiden Fälle je aufgefallen.

### Wieviel genügt

**Je Prüfung, nicht je Datei.** Eine Datei mit fünfundsechzig
Prüfungen braucht fünfundsechzig Gegenbeweise, nicht einen. Das ist
nicht Buchstabentreue, sondern folgt aus dem, was ein Gegenbeweis
zeigt: er zeigt, daß **diese eine** Prüfung fällt, wenn **diese eine**
Sache falsch ist. Über die vierundsechzig daneben sagt er nichts. Die
zwölf Prüfungen, die überhaupt nicht fallen konnten, standen genau
dort: in Dateien voller Prüfungen, die taten, was sie sollten.

Und es ist billiger, als es aussieht. Die Kopie wird einmal angelegt,
die kaputte Stelle wandert von Prüfung zu Prüfung, und der Lauf ist
derselbe. Was Zeit kostet, ist das Nachdenken darüber, was genau
kaputtzumachen wäre — und dieses Nachdenken ist der Ertrag: es zwingt
dazu, die Prüfung als Behauptung über das Programm zu lesen statt als
Zeile Quelltext.

**Wo es unverhältnismäßig wird**, und dann steht der Grund im Eintrag:
wenn die geprüfte Sache nur außerhalb dieses Programms falsch sein
kann — bei einem fremden Werkzeug, das man nicht kaputtmachen kann,
ohne es zu ersetzen. Dann ist eine strengere Attrappe der Gegenbeweis,
oder es ist ein Rauchtest, und der sagt es im Kopf (Abschnitt 1). Was
nicht als Grund zählt: es sind viele.

**Für jede geänderte Prüfung, nicht nur für neue.** Eine Umbenennung
ist eine Änderung. Wer zehn Prüfungen anfaßt, führt zehn Gegenbeweise.

### Der Nachweis

**Ein Gegenbeweis, den niemand nachlesen kann, ist keiner.** Er wird
darum aufgeschrieben, in `tests/state/counterproof`, ein Eintrag je
Test. `counterproof_test.py` ist die Ratsche über die Tests ohne
Eintrag: die Zahl darf fallen, nie steigen. Ein neuer Test ohne
Gegenbeweis macht sie sofort rot; der Bestand wird nach und nach
abgearbeitet, ohne daß die Suite stehenbleibt.

**Keine Änderung an einem Test und kein neuer Test ist fertig, bevor
sein Eintrag darin steht.**

Was der Eintrag trägt, damit er in einem halben Jahr noch etwas wert
ist:

* **Welche Prüfung**, beim Namen, mit dem sie sich druckt.
* **Wie kaputtgemacht wurde** — die eine Stelle und die eine Änderung,
  so genau, daß jemand sie ohne Nachdenken wiederholen kann.
* **Die rote Zeile im Wortlaut.** Sie ist der Beleg. Ohne sie ist der
  Eintrag eine Behauptung, und Behauptungen sind genau das, wogegen
  dieser Abschnitt geschrieben ist.
* **Wogegen**, wenn es nicht das Programm war: die verfälschten Daten,
  die strengere Attrappe.

Die rote Zeile ist auch das, was den Eintrag prüfbar macht: nennt sie
etwas anderes als die kaputtgemachte Sache, dann hat die Prüfung nicht
das gefangen, was sie fangen sollte, und der Eintrag verrät es beim
Lesen.

**Ein Gegenbeweis von gestern sagt nichts über eine Prüfung, die heute
umgeschrieben wurde.** Das ist die unangenehme Frage, und sie läßt
sich nicht sauber lösen: eine Maschine kann nicht entscheiden, ob eine
geänderte Zeile dieselbe Behauptung noch aufstellt. Die Faustregel:

> Ändert sich, **was** die Prüfung behauptet, ist der Eintrag
> ungültig und wird neu erbracht. Ändert sich nur, **wie** sie es
> nachsieht, bleibt er gültig — und das Wie zu ändern, ohne das Was zu
> ändern, ist selten, also im Zweifel neu erbringen.

Umbenennen, umstellen, aufteilen: das Was bleibt. Eine Grenze
verschieben, einen Vergleich umdrehen, ein Feld gegen ein anderes
tauschen: das Was ändert sich. Der Eintrag trägt die Prüfung beim
Namen, damit man die Frage überhaupt stellen kann.

Die Herkunft: Mutationstesten. Man ändert das Programm an einer Stelle
und sieht nach, ob ein Test rot wird; wird er es nicht, prüft er dort
nichts. Das Werkzeug dieser Schule sagt selbst, wogegen es antritt:
*„Traditional test coverage measures only which code is executed by
your tests. It does not check that your tests are actually able to
detect faults in the executed code."* Genau das ist der Unterschied
zwischen einer Zeile, die gelaufen ist, und einer Zeile, über die
etwas behauptet wurde.

Im Großen ist das zu teuer — ein Mutant kostet einen Suitenlauf, und
für alle Stellen dieses Programms wären es Tage. Auf die geänderten
Zeilen beschränkt ist es bezahlbar, und genau so wird es hier von Hand
gemacht: eine kaputte Fassung je geänderter Prüfung. Ein Werkzeug dafür
braucht es nicht.

## 6. Wie mit Warten umgegangen wird

**Auf eine Bedingung warten, nie auf die Uhr.** Eine feste Pause
kostet Zeit in jedem Lauf für immer, und sie läßt den Test in beide
Richtungen lügen: zu kurz, und er fällt auf einer belasteten Maschine;
zu lang, und niemand merkt, daß er auf etwas wartet, das nie eintritt.
Ein Test dieser Suite verbrachte 121 von 123 Sekunden mit dem Warten
auf ein Ereignis, das an dieser Stelle nie kommt, und meldete danach
grün. Nach der richtigen Bedingung gefragt, brauchte er drei Sekunden.

Die Form ist immer dieselbe: ein kurzer Abstand, die Bedingung, und
eine obere Schranke, damit eine langsame Maschine nicht rot wird.

**Der Abstand ist kurz, die Schranke darf großzügig sein.** Die beiden
Zahlen kosten Verschiedenes: der Abstand ist die Zeit, die im Normalfall
verlorengeht, die Schranke wird im Normalfall nie erreicht. Eine hohe
Schranke ist deshalb umsonst zu haben, solange kurz nachgefragt wird —
und sie ist es, die den Baurechner grün hält. Wer statt dessen an der
festen Pause dreht, macht jeden Lauf teurer und schiebt den Fehler nur
bis zur nächsten, langsameren Maschine.

**Aufgeben, wenn nichts mehr vorangeht — nicht, wenn eine Frist
abläuft.** Der Baurechner ist bis zu dreimal langsamer als der
Arbeitsplatz. Eine Frist, die hier großzügig ist, ist dort zu knapp,
und der Test wird rot, während das Fenster die ganze Zeit gearbeitet
hat. Gemessen wird deshalb der Stillstand: seit wann hat sich nichts
mehr geändert. Das trifft die Maschine nicht mit, und es fängt den
Fall, den eine Frist gar nicht sieht — daß etwas hängt, obwohl noch
Zeit übrig wäre.

Die Fließbandwerkzeuge kennen das als Abbruch nach Ausgabestille, mit
einer eigenen Einstellung neben der Wanduhr-Frist. **Unser Baurechner
hat sie nicht** — er kennt nur eine Frist auf die Wanduhr. Der
Stillstandszähler muß deshalb im Test selbst stehen; niemand nimmt ihn
uns ab. Und das ist auch der Grund, warum er sich lohnt: eine
Wanduhr-Frist über sechs verschieden schnelle Jobs kann nur falsch
eingestellt sein, ein Stillstandszähler nicht.

**Und grün auf dieser Maschine beweist nichts über den Baurechner.**
In einer Untersuchung an fünf großen Vorhaben ließen sich 86 Prozent
der Tests, die auf dem Fließband flatterten, auf einem gewöhnlichen
Arbeitsplatz nicht zum Flattern bringen — auch nicht in hundert
Läufen. Wer eine Wartestelle anfaßt, prüft sie auf dem Baurechner nach
und nicht hier.

**Ein taugliches Lebenszeichen ändert sich, weil das Programm
arbeitet.** Ein Fortschrittsbalken, der von allein weiterkriecht, ist
keines: er bewegt sich, ob etwas geschieht oder nicht. „Das Fenster
steht noch" ist keines. Tauglich sind ein Wert, den der Schritt selbst
schreibt, eine Datei, die entsteht, eine Zahl, die steigt, ein
Zustand, den das Programm ausdrücklich meldet.

**Erschöpfte Geduld ist rot, nicht grün.** Daß die Frist abgelaufen
ist und daß die Bedingung eingetreten ist, dürfen von außen nicht
gleich aussehen. Wo beides denselben Wert zurückgibt, läuft der Test
weiter und mißt etwas Halbfertiges. Die Zeile sagt, wie lange gewartet
wurde und was nie kam.

**Die Fristen der Schritte bleiben unter der des Ganzen.** Addieren
sich die Wartezeiten der einzelnen Schritte über die Frist des ganzen
Laufs, dann erfährt eine langsame Maschine, die Gesamtzeit sei um —
und nicht, welcher Schritt nie kam.

**Eine feste Pause ist erlaubt, während ein Test geschrieben wird, und
sonst nirgends.** Was die Bedingung sein muß, ist es wert, gemessen zu
werden: eine Sonde auf eine Kopie und nachsehen, wann die Sache
wirklich geschieht, statt eine Zahl zu raten, die sicher aussieht.

Die Herkunft: in der größten Aufstellung über flatterhafte Tests — 201
Reparaturen aus 51 Vorhaben — ist das Warten auf eine feste Zeit mit
Abstand die größte Ursachengruppe, 45 Prozent, vor der Nebenläufigkeit.
Der Rat ist dort als Verbot formuliert: *„Never use bare sleeps to wait
for asynchronous responses: use a callback or polling."* Und Flattern
ist kein Verschleiß: 78 Prozent der flatterhaften Tests flatterten
schon, als sie geschrieben wurden. Es wird eingebaut — darum steht
diese Regel hier und nicht in einem Aufräumplan.

## 7. Wie Überspringen aussehen darf

**Ein übersprungener Test ist nicht grün.** Er druckt `SKIPPED:` auf
einer eigenen Zeile, der Lauf zählt ihn getrennt, und die
Zusammenfassung nennt ihn — `green: 50 skipped: 1`, nie grün für einen
Test, der nichts geprüft hat.

**Kein `sys.exit(0)` im Vorbeigehen.** Wer aussteigt, weil sein
Material fehlt, und dabei 0 zurückgibt, ist von einem Test, der alles
geprüft hat, nicht zu unterscheiden.

**Der Grund steht in der Zeile:** was fehlt, und was es zurückbrächte.
„kein Testprojekt" ist kein Grund; „kein Testprojekt — `VPM_MEDIA` auf
einen Ordner mit … zeigen lassen" ist einer.

**Auch ein teilweise übersprungener Test sagt es.** Ein Schritt, der
stillschweigend ausgelassen wird, weil ein Ordner fehlt, fehlt auf dem
Baurechner vermutlich immer. Die Schlußzeile darf dann nicht behaupten,
alles sei geprüft worden: sie sagt, wie viele von wie vielen
Abschnitten in voller Länge liefen.

**Rot schlägt übersprungen.** Beides kann in einem Lauf zutreffen — ein
Test läßt aus, was diese Maschine nicht kann, und fällt über den Rest.
Wird zuerst nach dem Überspringen gefragt, liest sich das als
„übersprungen", der Fehlschlag wird nicht gezeigt und nicht gezählt,
und das ist dieselbe Lüge wie grün.

**Wieviel übersprungen werden darf, ist eine Ratsche.** Sie darf
fallen, nicht steigen.

**Und was auf keiner Maschine läuft, wird nicht übersprungen, sondern
entfernt.** Ein Test, der Dateien sucht, die es nicht gibt, und
zufrieden hinausgeht, steht als vollwertiger in der Liste und ist
schlechter als gar keiner: er belegt den Platz, an dem jemand einen
richtigen vermuten würde.

## 8. Wie ein Test aufräumt

**Ein temporärer Ordner, kein fester Pfad.** `tempfile.mkdtemp()`
legt unter `TMPDIR` an, und der Lauf zeigt `TMPDIR` auf einen Ordner
je Lauf und wirft ihn am Ende weg. Ein fester Pfad kollidiert, sobald
zwei Tests nebeneinander laufen, er überlebt den Lauf, und er läßt das
Ergebnis eines Laufs vom vorigen abhängen.

Die geteilten Vorlagenordner sind die Ausnahme: sie werden einmal vor
dem Auffächern gebaut und danach nur gelesen. Wer dort hineinschreibt,
macht sie zur gemeinsamen veränderlichen Sache und damit zur Ursache
des nächsten Flatterns.

**Nichts stehenlassen, was ein zweiter Lauf findet.** Auch nicht im
Zwischenspeicher, auch nicht in der Voreinstellungsablage, auch nicht
im Schlüsselbund. Was der Test setzt, setzt er zurück.

**Nie eine Datei löschen, die er nicht selbst angelegt hat.** Nicht
`tests/state/`, nicht den Zwischenspeicher dessen, der ihn gestartet
hat, nicht das Material im Projektordner. Was vorher da war, gehört
dem, der es hingelegt hat.

**Und nichts nach draußen.** Kein Netz, kein Hochladen, keine
Prüfung, ob es eine neuere Fassung gibt. Wo eine Verbindung geprüft
werden muß, wird die Stelle ausgetauscht, die sie öffnet.

## 9. Was hier nicht übernommen wird

Der Vollständigkeit halber, damit es nicht dreimal neu erwogen wird.

**Ein Rahmenwerk.** Was es gibt — Auffinden, Nebenläufigkeit,
Trennung, Überspringen, Zeitgrenze — hat der Lauf schon. Der Preis
wäre das Umschreiben der ganzen Mappe, und aus jeder gedruckten Zeile
mit ihrem Meßwert daneben würde ein `assert`. Genau diese Zeile ist
das, woran man den Fall wiedererkennt.

**Ein Abdeckungsziel.** Wird eine Abdeckung zum Ziel gemacht, wird sie
erreicht, und die Suite wird davon nicht besser. Die Zahl taugt als
Suchhilfe für ungeprüfte Wege und für nichts sonst.

**Die Testpyramide.** Sie verlangt viele kleine Tests. Klein ist dabei
nicht über den Umfang des Geprüften bestimmt, sondern über die
erlaubten Betriebsmittel: ein Prozeß, ein Faden, kein Netz, keine
Platte, **kein Schlafen**. Nach diesem Maß ist hier kein einziger Test
klein, weil das Programm aus Dateien, ffmpeg und einem Fenster besteht.
Klein bekäme man sie nur mit einem ffmpeg-Ersatz, und dann prüft der
Test den Ersatz — eine Attrappe dieser Größe wäre nach Abschnitt 5
ohnehin nicht zu verantworten. Dafür gehen unsere Tests den Weg, den
ein Benutzer geht, und je ähnlicher ein Test der wirklichen Benutzung
ist, desto mehr Vertrauen trägt er.

**Der Preis wird aber bezahlt und nicht weggeredet.** Große Tests
flattern mehr, fast linear mit ihrer Größe; das ist gemessen. Genau
das, was kleinen Tests verboten ist — schlafen, blockieren, warten —,
tun unsere unvermeidlich. Deshalb ist Abschnitt 6 keine Feinheit,
sondern das, was die Bauform tragbar macht. Und deshalb ist die
Flatterquote eine Zahl, die man kennt: sie verliert ihren Wert, wenn
sie sich einem Prozent nähert.

**Eine Handlung je Test.** Siehe Abschnitt 1: dafür ist die Lage hier
zu teuer.

---

## Die Checkliste

Für jeden neuen Test und für jede geänderte Prüfung. Zwölf Punkte, und
sie werden einzeln beantwortet, nicht überflogen.

**1. Zusichern.** Fällt der Test überhaupt ein Urteil — mit `check`,
nicht mit einem nackten `assert`? Wie viele? Und wenn keins: steht das
im Kopf **und** in der Schlußzeile?

**2. Kopf und Prüfungen decken sich.** Hat jede Behauptung der ersten
Zeile ein `check`? Und steht jedes `check` im Kopf? Beide Richtungen.

**3. Der Schluß wird immer erreicht.** Führt jeder Weg durch den Test
— auch der abgestürzte, auch der nebenläufige — an der Zeile vorbei,
die zählt und den Rückgabewert setzt? Wird die Zahl der Urteile
gedruckt, und stimmt sie mit dem überein, was der Kopf verspricht?

**4. Der Name ist eine Behauptung.** Sagt das Präfix, welcher Teil des
Programms kaputt wäre — und nicht, wovon das Material handelt? Ist die
zweite Hälfte eine Behauptung und kein Ding? Gilt das auch für jedes
einzelne `check`?

**5. Die Fehlerzeile trägt ihre Belege.** Steht in jeder — erwartet und
tatsächlich, als Zahl? Und nennt sie den ersten Umstand, der nicht
stimmte, statt eines Folgefehlers: ist jede Voraussetzung eine eigene
Prüfung davor?

**6. Der Gegenbeweis ist geführt — für jede Prüfung einzeln.** Eine
Fassung, in der genau diese eine Sache falsch ist, der Test dagegen
gelaufen, die rote Zeile gelesen. Nicht eine je Datei, sondern eine je
Prüfung. Ohne das zählt die Prüfung nicht.

**7. Und er steht in `tests/state/counterproof`.** Prüfung beim Namen,
wie kaputtgemacht wurde, die rote Zeile im Wortlaut. Dieser Punkt ist
nicht abzuhaken, ohne daß der Eintrag geschrieben ist — und wo eine
Prüfung umgeschrieben wurde, ist der alte Eintrag zu ersetzen, sobald
sich geändert hat, *was* sie behauptet.

**8. Und wenn er nicht rot wurde: Prüfung oder Attrappe?** Erlaubt die
Attrappe irgendwo mehr als das Echte — erfindet sie, was jenes
verweigert; fehlt ihr ein Verfahren, dessen Fehlen jenes bemerkbar
machen würde? Verschluckt irgendwo ein `except` die Antwort darauf?

**9. Gewartet wird auf eine Bedingung.** Keine feste Pause. Bricht der
Test bei Stillstand ab und nicht beim Ablauf einer Frist? Ist das
Lebenszeichen etwas, das sich nur bewegt, weil das Programm arbeitet?
Bleiben die Fristen der Schritte unter der des Ganzen? Ist erschöpfte
Geduld rot?

**10. Übersprungen wird sichtbar.** `SKIPPED:` mit Grund und mit dem
Weg zurück, kein stiller `sys.exit(0)`, kein stillschweigend
ausgelassener Schritt — und die Schlußzeile behauptet nichts, was
nicht geprüft wurde. Was auf keiner Maschine laufen kann, wird
entfernt statt übersprungen.

**11. Aufgeräumt wird.** Temporärer Ordner statt festem Pfad, nichts
steht hinterher noch da, und nichts wurde gelöscht oder verändert, was
der Test nicht selbst angelegt hat.

**12. Der Kopf ist nachgelesen.** Beschreibt er noch, was der Test
heute baut? Steht keine Zahl darin, die mitwandern müßte? Ist ein
Vermerk „dieser Schritt ist rot" mit der Reparatur hinausgegangen?

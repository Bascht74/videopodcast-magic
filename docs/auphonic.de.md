# Aufbereitung über auphonic.com

*In English: [Processing at auphonic.com](auphonic.md). Zurück zum [Inhalt](README.de.md).*

## Aufbereitung über auphonic.com

Der zusammengesetzte Ton wird bei auphonic.com mit einem gespeicherten
Preset verarbeitet und kommt als gewöhnliche Tondatei zurück. Der Zugang
wird einmal hinterlegt, das Preset gehört zur einzelnen Produktion.

Den Schlüssel gibt es in den Auphonic-Kontoeinstellungen, alternativ in
`AUPHONIC_TOKEN`. In der Oberfläche steht er hinter **Einstellungen ...**
im Fußbereich, mit dem Häkchen **Im Schlüsselbund speichern**,
das ihn im Schlüsselbund (macOS) oder in der Registry (Windows) behält; das
Fenster selbst ist in [Die Oberfläche](interface.de.md) beschrieben. Nie in
einer Datei, nie in der Projektdatei.

Im Kasten **Zugang zu auphonic.com** kommt der Schlüssel in das Feld
**API Key:**; **Verbinden** prüft ihn und holt die Presets (auf der
Kommandozeile `--auphonic-api-key`).

Ein Schlüssel, der nicht angenommen wird, öffnet kein Fenster.
**Verbinden** wird nicht grün, und unter dem Feld sagt eine Zeile, was
auphonic.com geantwortet hat; daneben steht ein Knopf, der die
Einstellungen öffnet. Dieselbe Zeile steht im Einstellungsfenster und
im Kasten auf dem Reiter **Zuordnung & Zeitfenster**, und sie nennt
auch einen fehlenden Schlüssel.

Zwei Dinge zum Schlüssel sollte man wissen statt sie anzunehmen:

* Auf dem Weg zu auphonic.com steht er nie in der Prozessliste: curl liest ihn
  aus einer Konfigurationsdatei, die nur ihrem Eigentümer lesbar ist und
  danach gelöscht wird — vorher überschrieben, wo sie sich nicht löschen
  lässt, und der Schlüssel geht maskiert hinein, damit ein Anführungszeichen
  oder ein Zeilenumbruch darin keine eigenen Direktiven anfügen kann.
* Aber `--auphonic-api-key SCHLUESSEL` schreibt ihn in die Kommandozeile
  dieses Programms, wo `ps` und die Shell-Historie ihn sehen — auf der
  Kommandozeile also lieber `AUPHONIC_TOKEN`.

Das Ablegen im macOS-Schlüsselbund übergibt ihn dem Programm `security` über
dessen Eingabe, nicht als Argument, und liest ihn zurück, um zu sehen, dass er
angekommen ist; nur wenn der falsche Schlüssel zurückkommt, folgt die Form mit
dem Argument, die die Schwäche der Kommandozeile hat. Der Weg über die
Windows-Registry hat sie nicht.

Auf dem Reiter **Zuordnung & Zeitfenster** steht im Kasten
**Aufbereitung bei auphonic.com (optional)**, was dieser Lauf tut. Der
Kasten steht unter der Zuordnungstabelle, gleich unter dem Häkchen
**Multitrack (je Sprecher eine Spur)**.

* das Preset unter **Preset:** (auf der Kommandozeile
  `--auphonic-preset`)
* das Häkchen **Transkription holen** daneben

Die Produktion wird aus dem Preset neu gebaut.

### Transkription holen

Mit **Transkription holen** schreibt auphonic.com mit, was gesprochen
wird (auf der Kommandozeile `--transcript`). Neben dem Ton kommen drei
Dateien zurück:

* ein json mit Zeiten
* ein srt für Untertitel
* ein txt zum Lesen

Die Arbeit macht Auphonics eigenes Whisper: kein Konto anderswo, keine
Zusatzkosten, eine längere Produktion. Bei Multitrack trägt die
Transkription die Sprechernamen.

### Ohne Auphonic arbeiten

Multitrack braucht den Dienst nicht mehr. Der erste Eintrag der
Presetliste, **ohne Auphonic arbeiten**, hält diesen Lauf hier (auf der
Kommandozeile `--without-auphonic`). Er ist kein Preset, sondern die
Ansage, diesen Lauf nicht dorthin zu schicken; der Schlüssel bleibt im
Feld, gemerkt und geprüft, nur nicht weitergereicht. Das
Multitrack-Häkchen steht über dem Auphonic-Kasten und braucht keinen
Schlüssel.

Alles läuft dann hier: die Spuren werden auf die gemeinsame Achse
ausgerichtet, gemischt, auf die Ziellautheit gebracht (`--lufs`,
voreingestellt -16) und auf die Kameras verteilt. Kameraschnitt und
Resolve-Projekt entstehen wie sonst. Es fehlt nur, was der Dienst tut:
De-Bleed, Leveler, Rauschentfernung. Das Übersprechen bleibt im Ton.

Wer wann spricht, kommt aus der örtlichen Sprechertrennung
([Spracherkennung und Sprechertrennung](speech.de.md)); ohne sie wird es aus
den Spuren gemessen, und das Übersprechen wird aus dieser Messung
herausgerechnet, nicht aus dem Ton. Wie gemessen wird, und wie weit hinunter
das trägt, steht in [Sprecherstatistik, Kameraschnitt, EDL](camera-cut.de.md).

Ohne Multitrack gibt es keine getrennten Spuren und damit keinen
Kameraschnitt, mit Dienst wie ohne. Der Ton wird zusammengelegt und so ins
Video gelegt, wie er aufgenommen wurde; die Lautheit setzt nur Auphonic.

Solange kein Schlüssel geprüft ist, steht nur dieser Eintrag in der
Liste. Sobald die Presets eintreffen, springt die Auswahl auf das erste
davon. Eine bewusste Wahl übersteht den Neuaufbau der Liste und steht in
der Projektdatei.

### Eine Produktion, die es schon gibt

Gibt es dort schon eine Produktion dieses Namens, wird gefragt:

1. vorhandenes Ergebnis übernehmen — nichts rechnen, nichts bezahlen
2. mit dem gewählten Preset neu rechnen, Dateien bleiben stehen — kostet
   nichts
3. alles neu hochladen und neu rechnen — kostet Guthaben
4. abbrechen

Nur das Hochladen kostet Guthaben — Presets lassen sich durchprobieren, ohne
zu zahlen; von allein lädt das Script nie hoch. Punkt 1 erscheint nur, wenn
alles Nötige da ist. Heißen die Spuren dort anders, wird gefragt, ob deren
Namen übernommen werden — auch das kostet nichts.

Beim Neurechnen kommen auch die Spureinstellungen auf das Preset. Weitere
Spuren dort gehen in den Mix, eine Warnung nennt sie.

Heruntergeladen wird alles: Einzelspuren und jede weitere Ausgabe des
Presets — Kapitelmarken, Transkript, Auswertungen. Alles landet in
`auphonic-tracks/` neben den fertigen Videos, später auch die `final_*.wav`.

In-Punkt und Out-Punkt nachträglich zu setzen kostet keinen zweiten Lauf
bei Auphonic. Die Spuren werden auf das neue Fenster beschnitten. Passt
die Länge weder zum Fenster noch zum ganzen gemessenen Bereich, gehören
die Dateien zu einem anderen Lauf, und das sagt die Meldung.

### Weitere Optionen über die Kommandozeile

Im Fenster gibt es diese Optionen nicht.

* `--auphonic-preset` ohne Namen: die vorhandenen Presets werden nummeriert
  abgefragt, der Schlüssel ohne Dateien listet sie auf.
* `--auphonic-resume result|rerun|adopt|upload|abort` beantwortet die Frage
  nach einer schon vorhandenen Produktion im Voraus.
* `--auphonic-done ORDNER` holt nichts, sondern nimmt die dort liegenden
  Spuren, benannt nach den Sprechern.

# Aufbereitung über auphonic.com

*In English: [auphonic.md](auphonic.md). Zurück zum
[Inhalt](README.de.md).*

## Der Schlüssel und das Preset

Der Dienst auphonic.com verarbeitet den zusammengesetzten Ton mit einem
gespeicherten Preset und schickt ihn als gewöhnliche Tondatei zurück.
Der Zugang wird einmal hinterlegt, das Preset gehört zur einzelnen
Produktion.

Den Schlüssel gibt es in den Auphonic-Kontoeinstellungen, alternativ in
`AUPHONIC_TOKEN`. Nie in einer Datei, nie in der Projektdatei.

1. Im Fußbereich **Einstellungen ...** öffnen; das Fenster selbst ist in
   [Die Oberfläche](interface.de.md) beschrieben.
2. Im Kasten **Zugang zu auphonic.com** das Feld **API Key:** füllen
   (auf der Kommandozeile `--auphonic-api-key`).
3. Optional: das Häkchen **Im Schlüsselbund speichern** setzen, das den
   Schlüssel im Schlüsselbund (macOS) oder in der Registry (Windows)
   behält.
4. **Verbinden** drücken. Der Knopf prüft den Schlüssel und holt die
   Presets.

![Der Kasten für den Schlüssel](images/settings.de.png)

*Das Fenster, das Einstellungen ... öffnet: oben der Kasten für den
Schlüssel, unten der für Resolve. Das Feld ist noch leer.*

Ein Schlüssel, den auphonic.com nicht annimmt, öffnet kein Fenster.
**Verbinden** wird nicht grün, und unter dem Feld sagt eine Zeile, was
auphonic.com geantwortet hat; daneben steht ein Knopf, der die
Einstellungen öffnet. Dieselbe Zeile steht im Einstellungsfenster und
im Kasten auf dem Reiter **Zuordnung & Zeitfenster**. Sie nennt auch
einen fehlenden Schlüssel.

* Auf dem Weg zu auphonic.com steht der Schlüssel nie in der
  Prozessliste: curl liest ihn aus einer Konfigurationsdatei, die nur
  ihrem Eigentümer lesbar ist. Das Programm löscht die Datei danach und
  überschreibt sie vorher, wenn sie sich nicht löschen lässt. Der
  Schlüssel geht maskiert hinein, damit ein Anführungszeichen oder ein
  Zeilenumbruch darin keine eigenen Direktiven anfügen kann.
* Aber `--auphonic-api-key SCHLUESSEL` schreibt ihn in die Kommandozeile
  dieses Programms, wo `ps` und die Shell-Historie ihn sehen. Auf der
  Kommandozeile also lieber `AUPHONIC_TOKEN`.

Das Ablegen im macOS-Schlüsselbund übergibt ihn dem Programm `security`
über dessen Eingabe, nicht als Argument. Das Programm liest ihn zurück,
um zu sehen, dass er angekommen ist. Nur wenn der falsche Schlüssel
zurückkommt, greift es zur Form mit dem Argument, die die Schwäche der
Kommandozeile hat. Der Weg über die Windows-Registry hat sie nicht.

Auf dem Reiter **Zuordnung & Zeitfenster** steht im Kasten
**Aufbereitung bei auphonic.com (optional)**, was dieser Lauf tut.

* das Preset unter **Preset:** (auf der Kommandozeile
  `--auphonic-preset`)
* das Häkchen **Transkription holen** daneben

Das Programm baut die Produktion aus dem Preset neu.

Das Häkchen **Multitrack (je Sprecher eine Spur)** steht nicht im
Auphonic-Kasten und braucht keinen Schlüssel. Es entscheidet hier, ob
jede Person eine eigene Spur behält: nur getrennte Spuren kann
auphonic.com einzeln aufbereiten und vom Übersprechen der anderen
befreien. Wo alle in einer Spur stehen, gibt es nichts, was der De-Bleed
auseinandernehmen könnte.

Über die Art der Produktion entscheidet die Zahl der Spuren. Eine
einzelne Spur geht als gewöhnliche Produktion hoch, zwei oder mehr als
Multitrack-Produktion, und das Preset muss dazu passen: ein gewöhnliches
für die eine, ein Multitrack-Preset für die anderen.

### Transkription holen

Mit **Transkription holen** schreibt auphonic.com mit, was gesprochen
wird (auf der Kommandozeile `--transcript`). Neben dem Ton kommen drei
Dateien zurück:

* ein json mit Zeiten
* ein srt für Untertitel
* ein txt zum Lesen

Die Arbeit macht Auphonics eigenes Whisper: kein Konto anderswo, keine
Zusatzkosten, eine längere Produktion. Gehen mehrere Spuren hoch, trägt
die Transkription die Sprechernamen: jede Spur ist eine Person, und
auphonic.com weiß, welche welche ist.

### Ohne Auphonic arbeiten

Jeder Lauf kommt ohne den Dienst aus. Der erste Eintrag der Presetliste,
**ohne Auphonic arbeiten**, hält diesen Lauf hier (auf der
Kommandozeile `--without-auphonic`). Er ist kein Preset. Der Schlüssel
bleibt im Feld, gemerkt und geprüft, nur nicht weitergereicht.

Alles läuft dann hier: das Programm richtet die Spuren auf der
gemeinsamen Achse aus, mischt sie und verteilt sie auf die Kameras.
Kameraschnitt und Resolve-Projekt entstehen wie sonst. Es fehlt nur,
was der Dienst tut: De-Bleed, Leveler, Rauschentfernung. Das
Übersprechen bleibt im Ton.

Die Ziellautheit setzt `--lufs`; eine kleinere Zahl ist leiser. Auf jede
Spur kommt dieselbe Anhebung, so bleibt das Verhältnis der Sprecher
erhalten. Ohne ihn, und mit **Aus Quelldateien übernehmen** im Fenster,
wird gar nichts angepasst: der Ton bleibt, wie er in den Quelldateien ist.

Die örtliche Sprechertrennung sagt, wer wann spricht ([Spracherkennung
und Sprechertrennung](speech.de.md)). Ohne sie misst das Programm es aus
den Spuren und rechnet das Übersprechen aus dieser Messung heraus, nicht
aus dem Ton. Die Messung und ihre untere Grenze stehen in
[Sprecherstatistik, Kameraschnitt, EDL](camera-cut.de.md).

Solange das Programm keinen Schlüssel geprüft hat, steht nur dieser
Eintrag in der Liste. Sobald die Presets eintreffen, springt die Auswahl
auf das erste davon. Eine bewusste Wahl übersteht den Neuaufbau der
Liste und steht in der Projektdatei.

### Wenn es die Produktion schon gibt

Das Programm erkennt die Produktion am Namen und fragt, was mit ihr
geschehen soll:

1. vorhandenes Ergebnis übernehmen: nichts rechnen, nichts hochladen
2. mit dem gewählten Preset neu rechnen, Dateien bleiben stehen: kostet
   kein Guthaben
3. alles neu hochladen und neu rechnen: kostet Guthaben
4. abbrechen

Guthaben verbraucht allein das Hochladen. Punkt 2 rechnet mit dem neuen
Preset und lädt nichts hoch, also lässt sich ein Preset nach dem anderen
durchgehen. Das Programm lädt erst hoch, wenn es dazu aufgefordert wird.
Punkt 1 erscheint nur, wenn alles Nötige da ist. Bei anderen Spurnamen
dort fragt das Programm, ob es sie übernimmt.

Beim Neurechnen bringt das Programm auch die Spureinstellungen auf das
Preset. Weitere Spuren dort gehen in den Mix, eine Warnung nennt sie.

Das Programm lädt alles herunter, die Einzelspuren und jede weitere
Ausgabe des Presets: Kapitelmarken, Transkript, Auswertungen. Alles
landet in `auphonic-tracks/` neben den fertigen Videos, später auch die
`final_*.wav`.

Einen nachträglich gesetzten In- oder Out-Punkt verrechnet das Programm
hier, nicht bei Auphonic. Es beschneidet die zurückgekommenen Spuren auf
das neue Fenster. Wenn die Länge weder zum Fenster noch zum ganzen
gemessenen Bereich passt, gehören die Dateien zu einem anderen Lauf, und
die Meldung sagt das.

### Wenn etwas klemmt

* **Verbinden wird nicht grün.** Die Zeile unter dem Feld sagt, was
  auphonic.com geantwortet hat. Der Knopf daneben öffnet die
  Einstellungen; dort den Schlüssel berichtigen.
* **In der Presetliste steht nur ihr erster Eintrag.** Es ist noch kein
  Schlüssel geprüft: **Verbinden** drücken.
* **Die zurückgekommenen Spuren passen weder zum Zeitfenster noch zum
  ganzen gemessenen Bereich.** Sie gehören zu einem anderen Lauf. Den
  Ordner dieses Laufs nehmen, oder den Ton noch einmal über
  auphonic.com schicken.
* **Der Lauf soll Guthaben kosten, das nicht gemeint war.** Nur Punkt 3
  lädt hoch, und nur das Hochladen kostet. Punkt 1 und Punkt 2 lassen
  die Dateien stehen, wo sie sind.

Der Ton ist jetzt aufbereitet und liegt in `auphonic-tracks/`. Wie die
Spuren über mehrere Sprecher und mehrere Kameras verteilt werden, steht
in [Multitrack: mehrere Sprecher, mehrere Kameras](multitrack.de.md).

### Weitere Optionen über die Kommandozeile

Im Fenster gibt es diese Optionen nicht.

* `--auphonic-preset` ohne Namen: das Programm fragt die vorhandenen
  Presets nummeriert ab, der Schlüssel ohne Dateien listet sie auf.
* `--auphonic-resume result|rerun|adopt|upload|abort` beantwortet die
  Frage nach einer schon vorhandenen Produktion im Voraus. Er erreicht
  nur einen Lauf, der mehrere Spuren hochlädt; bei einer einzelnen Spur
  gibt es keinen Upload je Spur, den man wieder aufnehmen könnte.
* `--auphonic-done ORDNER` holt nichts, sondern nimmt die dort
  liegenden Spuren, benannt nach den Sprechern.

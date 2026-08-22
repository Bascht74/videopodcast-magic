# Alle Schalter

*In English: [All switches](command-line.md). Zurück zum [Inhalt](README.de.md).*

## Alle Schalter

`--help` gibt diese Liste auch aus, immer auf Englisch. Vorgaben in Klammern.

**Grundlagen**

| Schalter | Wirkung |
|---|---|
| `--lang {de,en}` | Sprache der Meldungen (Systemsprache) |
| `--out ORDNER` | wohin die Ergebnisse kommen (neben jedes Video) |
| `--suffix TEXT` | wird an den Dateinamen gehängt (`_audio`) |
| `--name TEXT` | Name der neuen Tonspur (`Processed audio`) |
| `--name-camera TEXT` | Name der Kameraspur (`Camera Original`) |
| `--parallel ANZAHL` | so viele Videodateien gleichzeitig; 0 entscheidet selbst, 1 nacheinander |
| `--dry-run` | nur messen und berichten, nichts schreiben |
| `--version` | Versionsnummer, und auf welchem Python das läuft |

**Ton und Bild**

| Schalter | Wirkung |
|---|---|
| `--no-camera-audio` | den Kameraton wegwerfen statt behalten |
| `--no-follow-ups` | nicht nach nummerierten Fortsetzungsdateien suchen |
| `--together DATEI ...` | diese Dateien sind eine Aufnahme, in dieser Reihenfolge; wiederholbar |
| `--apart DATEI` | dieser Block steht für sich, was immer sein Name sagt; wiederholbar |
| `--transcript` | auphonic.com schreibt mit, was gesagt wird: json, srt und txt |
| `--no-trim` | Ton in voller Länge statt auf das Bild beschnitten |
| `--no-single-tracks` | nur den Mix ins Video, nicht die Aufnahmen daneben |
| `--head ZEIT` | so viel vorne abschneiden: Sekunden, MM:SS, HH:MM:SS |
| `--tail ZEIT` | dasselbe für das Ende |
| `--no-drift` | Uhrendrift messen und melden, aber nicht herausrechnen |
| `--tc HH:MM:SS:FF` | Starttimecode des Bildes, wenn die Kamera keinen oder einen falschen geschrieben hat |
| `--fps ZAHL` | anzunehmende Bildrate, wenn ffprobe eine falsche meldet |
| `--lufs ZAHL` | Lautheitsziel der Summe aller Spuren (-16) |
| `--platform NAME` | dieses Ziel nach Plattform: `broadcast` -23, `podcast` -16, `podcast-mono` -19, `youtube` -14 |
| `--speech-language CODE` | Sprachkennung der Tonspuren, ISO 639-2/B: `ger`, `eng`. Vorsicht, `deu` wirft ffmpeg stillschweigend weg (keine) |
| `--speech-language-camera CODE` | dasselbe für die Kameraspur (keine — nur so unterscheidet der QuickTime-Player die beiden Einträge im Tonmenü) |

**Auphonic**

| Schalter | Wirkung |
|---|---|
| `--auphonic-api-key SCHLÜSSEL` | Schlüssel aus den Kontoeinstellungen, schaltet die Aufbereitung ein. Ohne Dateien listet er nur die Vorlagen |
| `--auphonic-preset NAME` | Name oder Kennung der Vorlage (wird gefragt) |
| `--auphonic-wait SEKUNDEN` | wie lange gewartet wird (7200) |
| `--auphonic-resume WAS` | Produktion ist schon da: `result`, `rerun`, `adopt`, `upload`, `abort` (wird gefragt) |
| `--auphonic-done ORDNER` | schon aufbereitete Spuren, nach den Sprechern benannt — es wird nichts hochgeladen und kein Guthaben verbraucht |
| `--multitrack` | jede Tondatei als eigene Spur, damit das Übersprechen heraus kann. Braucht eine Multitrack-Vorlage |
| `--assign DATEI` | JSON, welcher Ton zu welcher Kamera gehört; die Oberfläche schreibt es |
| `--without-auphonic` | örtlich ausrichten, mischen und schreiben, Kameraschnitt aus eigener Spracherkennung |

**Zeitfenster**

| Schalter | Wirkung |
|---|---|
| `--in-point ZEIT` | Anfang: `17:20:14` absolut, `+12:30` oder `90` ab Fensterbeginn |
| `--out-point ZEIT` | Ende, gleiche Schreibweise; `-30` zählt vom Ende zurück |

**Kameraschnitt**

| Schalter | Wirkung |
|---|---|
| `--min-edit-duration SEKUNDEN` | wie kurz eine Einstellung stehen darf; kürzere gehen in die vorige auf, 0 aus (3) |
| `--edit-change-delay SEKUNDEN` | wie viel später als der Ton das Bild schneidet; negativ lässt es vorlaufen (0,3) |
| `--wide-after SEKUNDEN` | ab dieser Standzeit wird die Einstellung mit einem Blick in den Weitwinkel aufgebrochen, 0 aus (45) |
| `--wide-length SEKUNDEN` | längster so eingeschobener Weitwinkel (2,5) |
| `--wide-min SEKUNDEN` | kürzester, auf den er schrumpft (1,5) |
| `--wide-flow SEKUNDEN` | wie lange er steht, wenn mitten im Satz geschnitten werden muss (6) |
| `--wide-latest SEKUNDEN` | wie lange eine Kamera höchstens ohne Schnitt stehen darf (120) |
| `--no-wide-edges` | den Weitwinkel nicht über Begrüßung und Verabschiedung halten |

**Vorflug und Kennzahlen**

| Schalter | Wirkung |
|---|---|
| `--no-preflight` | die Prüfung vor dem ersten langen Schritt überspringen |
| `--preflight-again` | neu messen statt die gespeicherte Messung zu nehmen |
| `--anyway` | auch laufen, wenn der Vorflug einen Grund zum Anhalten gefunden hat |
| `--no-metrics` | am Ende keine Kennzahlen und keinen Farbvergleich |

**Vorspann und Abspann**

| Schalter | Wirkung |
|---|---|
| `--intro DATEI` | über den Anfang gelegt, auf der zweiten Bild- und Tonspur. Wird weder ausgerichtet noch aufbereitet |
| `--outro DATEI` | dasselbe für das Ende; beginnt, wo das letzte Wort endet |

**DaVinci Resolve**

| Schalter | Wirkung |
|---|---|
| `--resolve` | danach Projekt und Timelines bauen. Resolve muss laufen |
| `--resolve-json DATEI` | nur den Resolve-Teil, aus einer schon vorhandenen `..._resolve.json` |
| `--resolve-project WAS` | Projekt ist schon da: `update`, `keep`, `new`, `abort` (wird gefragt) |
| `--resolve-audio-tracks` | nur die Tonzuordnung des offenen Projekts ausgeben. Ändert nichts |
| `--hdr-check DATEI` | nur nachsehen, ob eine fertige Datei alles trägt, was sie als HDR ausweist |

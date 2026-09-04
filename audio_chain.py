#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Der lokale Weg einer Aufnahme -- die Schritte, bei denen klar ist, wie.

    python3 audio_chain.py --in EINGABE.wav --out AUSGABE.wav

Diese Datei steht **neben** videopodcast-magic.py und importiert daraus
nichts. Sie soll unabhaengig weiterentwickelt und gegen das grosse
Programm gemessen werden koennen; ein Import haette beide aneinander
gebunden und jede Messung waere dann eine Messung des Programms gegen
sich selbst. Wo sie dasselbe tut, steht es hier noch einmal, und an der
Stelle steht ein Satz, warum.

**Sie rechnet ausschliesslich hier.** Kein Netz, kein Hochladen, kein
Schluessel -- weder gelesen noch gebraucht.

Was sie tut, und nur das:

  1. einlesen und die Lautheit des Rohmaterials messen
  2. Hochpass gegen Trittschall und Rumpeln
  3. entbrummen -- aber nur, wo der Brumm **eindeutig** da und laut
     genug ist, um zu stoeren; je Oberwelle einzeln entschieden. Ein
     knapper Fund wird gemeldet und liegengelassen, nicht abgewogen.
     Ab Werk aus (--dehum 0)
  4. die Pegelfuehrung: den langsamen Gang einer Stimme geradeziehen,
     ohne die Pausen anzufassen und ohne der Sprache ihre Betonung zu
     nehmen. Gemessen wird immer, gefuehrt nur, wenn es genug zu tun
     gibt -- sonst wird gemeldet und liegengelassen. Ab Werk aus
     (--leveler 0)
  5. auf die Ziellautheit verstaerken (EBU R 128 / ITU-R BS.1770-5)
  6. die wahren Spitzen begrenzen, 4-fach uebertastet gemessen
  7. nachmessen und schreiben

Was sie **bewusst nicht** tut, obwohl auphonic.com es tut: entrauschen,
Uebersprechen wegnehmen, Sprach-EQ, schneiden. Bei keinem dieser
Schritte ist klar, *wieviel* davon richtig ist -- das Urteil haengt am
Material, und ein fest verdrahteter Wert waere geraten. Die Begruendung
je Schritt steht in docs/notes/audio_chain.html. Ein Schritt, der
stimmt, ist mehr wert als vier, die ungefaehr stimmen.

Die Pegelfuehrung stand bis zum 4.9.2026 in derselben Liste, aus
demselben Grund. Sie steht heute oben, weil ihre Zahlen gemessen sind
und weil sie sagen darf, dass sie nichts zu tun hat -- aber sie bleibt
ab Werk aus, und warum, steht bei LEVELER_LOHNT_DB.

**Die Schalter tragen die Namen eines auphonic-Presets.** Ein Preset
dort hat 37 Felder in neun Wurzeln; sie stehen unten alle in
PRESET_SCHALTER, jedes mit auphonics eigener Vorgabe. Die wenigen, zu
denen es hier einen gebauten Schritt gibt, wirken. Die anderen werden
angenommen und tun nichts -- der Lauf sagt dann, welche das waren und
warum. So laesst sich ein Preset hier abbilden, ohne zu behaupten, es
werde befolgt. `--preset-tafel` druckt die ganze Tafel und hoert auf.

Gebraucht werden: ffmpeg und ffprobe im Pfad, numpy, scipy.
"""

import argparse
import math
import os
import re
import subprocess
import sys
import time

import numpy as np
from scipy.signal import resample_poly


# --------------------------------------------------------------------
# Zahlen, und woher sie kommen
# --------------------------------------------------------------------

# EBU R 128 v5 nennt -23,0 LUFS. Die im Podcast ueblichen -16,0 sind ein
# ausdruecklicher Uebergangswert (R 128 s2). videopodcast-magic.py haelt
# in PLATFORMS dieselben vier Werte bereit; -16,0 ist dort "podcast".
ZIEL_LUFS = -16.0

# -1,0 dBTP ist der Wert, den auch das grosse Programm nimmt
# (CEILING_DBTP). Er steht hier noch einmal, damit diese Datei ohne das
# grosse Programm lauffaehig ist. BS.1770-5 beziffert den eigenen
# systematischen Fehler der 4-fachen Uebertastung mit bis zu 0,688 dB;
# wer ganz sicher gehen will, legt das Ziel auf -1,5 oder -2 dBTP.
ZIEL_DBTP = -1.0

# 80 Hz, zwei Pole. Gemessen am 3.9.2026 (siehe HTML): nimmt 22,4 dB
# unter 45 Hz weg und kostet 0,01 dB im Band 300-3400 Hz, an einer
# tiefen Stimme 0,08 dB ueber alles.
HOCHPASS_HZ = 80.0

# Soviel darf der Begrenzer hoechstens wegnehmen. Daselbe Dach wie
# LIMIT_MAX_DB im grossen Programm; hier wiederholt, damit diese Datei
# fuer sich steht. Wird es erreicht, wird die Verstaerkung zurueck-
# genommen und die Ziellautheit ausdruecklich als verfehlt gemeldet --
# lieber leiser als plattgedrueckt.
BEGRENZER_MAX_DB = 6.0

# Der Begrenzer rechnet blockweise. 256 Proben sind bei 48 kHz 5,3 ms.
BLOCK = 256
VORLAUF_BLOECKE = 1          # ein Block Vorausschau
RUECKKEHR_S = 0.050          # 50 ms zurueck auf volle Verstaerkung
UEBERTASTUNG = 4             # 4-fach, wie in BS.1770-5 beschrieben

# Unter dieser Lautheit wird nicht mehr verstaerkt. BS.1770-5 tort
# absolut bei -70 LKFS, und was passiert, wenn *kein* Block darueber
# liegt, ist weder dort noch in EBU Tech 3341 festgelegt. Also wird es
# hier festgelegt und gesagt, statt still etwas zu tun.
ZU_LEISE_LUFS = -70.0

# --------------------------------------------------------------------
# Entbrummen: die Zahlen und woher sie kommen
# --------------------------------------------------------------------

# Die Kerbe ist 2 Hz breit, nicht "Guete 30". Guete 30 heisst feste
# *relative* Breite: 1,7 Hz bei 50 Hz, aber 13,3 Hz bei 400 Hz -- oben
# also zehnmal mehr Stimme weg als noetig. Eine Netzlinie ist dagegen
# ueberall gleich schmal.
#
# Gemessen am 3.9.2026 an vier gebauten Stimmen (Aufbau siehe HTML):
# in einem Band von 5 Hz um die Kerbe nimmt Guete 30 bei 50 Hz 0,9 bis
# 1,2 dB weg und bei 400 Hz 8,4 bis 9,1 dB -- die feste Breite von 2 Hz
# nimmt ueberall 1,0 bis 1,7 dB. Darum lohnt die feste Breite bei 400 Hz
# rund elf dB frueher: der Kipppunkt liegt bei 12,5 bis 14,2 dB
# Abstand, mit Guete 30 bei 23,0 bis 27,6 dB.
#
# 1 Hz waere noch schmaler, ist aber gegen eine wandernde Netzfrequenz
# schwaecher. Gemessen an einem reinen Ton bei 400 Hz: liegt er 0,2 Hz
# neben der Kerbe, nimmt eine 1-Hz-Kerbe 9,2 dB weg, eine 2-Hz-Kerbe
# 14,0 dB, Guete 30 aber 30,6 dB. Wer breiter kerbt, trifft die
# wandernde Linie besser und die Stimme haerter; 2 Hz ist der Punkt,
# an dem beides noch vertretbar ist.
KERBE_BREITE_HZ = 2.0

# --- Die erste Schwelle: steht da ueberhaupt eine Linie? -------------
# Sie erkennt nur, sie erlaubt nichts. Gemessen am 3.9.2026 an Material
# *ohne* Brumm -- vier gebaute Stimmen, zwei Rauschboeden, acht Linien,
# 64 Messungen: der Abstand blieb meist unter 5 dB, erreichte aber
# **14,1 dB** an einer Stimme, deren Grundton bei 102 Hz liegt und deren
# zweite Oberwelle damit auf der 100-Hz-Linie sitzt. Eine zweite Stimme
# kam bei 350 Hz auf 8,3 dB. Dazu 24 Linien in echtem Material (die
# 100-Hz-Linie ausgenommen): bis 12,6 dB.
# 15 dB liegt ueber jedem gemessenen falschen Alarm. Darunter wird
# nichts gemeldet und nichts getan.
BRUMM_SICHTBAR_DB = 15.0

# --- Die zweite Schwelle: ist der Brumm eindeutig? -------------------
# Nur diese darf kerben. Sie ist nicht die Stelle, an der eine Kerbe
# rechnerisch beginnt sich zu lohnen -- die liegt tiefer und wurde
# gemessen: an 352 Faellen (vier Stimmen, zwei Rauschboeden, vier
# Linien, elf Stufen) kippte die Kerbe vom Schaden zum Nutzen zwischen
# **10,0 und 23,1 dB** Abstand, Mittel 16,4.
# 25 dB liegt ueber dem hoechsten dieser Kipppunkte. Wer hier kerbt,
# gewinnt also in jedem gemessenen Fall -- und ein knapper Fall wird
# nicht abgewogen, sondern gemeldet und liegengelassen.
BRUMM_STOEREND_DB = 25.0

# --- Und die dritte: ist er laut genug, um zu stoeren? --------------
# **Diese eine Zahl ist gesetzt, nicht gemessen**, und das ist keine
# Nachlaessigkeit: ab wann ein stehender Ton einen Menschen stoert,
# entscheidet ein Hoerversuch (ITU-T P.835, ITU-R BS.1116), kein
# Messgeraet. Aus demselben Grund hat diese Datei keinen Entrauscher.
# Gesetzt sind 30 LU: liegt der Brumm mehr als 30 LU unter dem
# Programm, wird er gemeldet und nicht angetastet.
# Was daran gemessen ist, ist die Wirkung. Am 3.9.2026 an drei Spuren
# echten Materials: der Brumm lag 21,7 / 25,2 / 36,2 LU unter dem
# Programm -- die Regel kerbt also zwei der drei Spuren und meldet die
# dritte. Wer die Zahl aendert, aendert genau diese Aufteilung.
BRUMM_HOERBAR_LU = 30.0

# --- Das Netz darunter: nimmt die Kerbe mehr Brumm als Stimme? ------
# Kein Erfahrungswert, sondern eine Bilanz: die Kerbe nimmt Brumm *und*
# Stimme weg, und sie lohnt genau dann, wenn die Linie mehr als die
# Haelfte dessen ist, was die Kerbe herausnimmt. 0 dB ist dieser Punkt.
# Gemessen am 3.9.2026 an denselben 352 Faellen: mit dieser Bedingung
# wurden 176 Kerben gesetzt und **keine einzige** war schaedlich (der
# Gewinn lag zwischen 5,2 und 25,0 dB, Median 18,9). Ohne sie waren von
# 259 Kerben **43 schaedlich**, die schlimmste um 40,1 dB. Sie ist also
# nicht die Feinheit, sondern der Grund, warum hier kein fester Kamm
# steht.
BRUMM_LOHNT_DB = 0.0

# So hoch wird die Bilanz ueberhaupt beziffert. Darueber sagt sie nur
# noch, dass die Kerbe fast nichts ausser der Linie getroffen hat -- wie
# viel genau, kann die Schaetzung des Rauschbodens nicht mehr auflösen.
# Eine gedeckelte Zahl ist ehrlicher als eine erfundene.
BILANZ_MAX_DB = 40.0

BRUMM_LINIEN = 8             # so weit hinauf wird gesucht (50..400 Hz)
BRUMM_FFT = 65536            # 1,37 s bei 48 kHz, 0,73 Hz je Linie
BRUMM_PERZENTIL = 10.0       # der Rauschboden: die leisesten Rahmen

# Vor der Lautheitsmessung des Brumms allein wird um soviel angehoben.
# Grund: BS.1770-5 tort absolut bei -70 LKFS, und ein Brumm *allein*
# liegt darunter -- gemessen am 3.9.2026 gab ebur128 fuer zwei von drei
# echten Spuren glatt -70,00 LUFS zurueck, was keine Messung ist,
# sondern das Tor. Mit 40 dB Vorlauf kamen -81,3 und -70,6 heraus. Die
# Lautheit ist im Pegel geradlinig, der Vorlauf wird darum einfach
# wieder abgezogen und die *Differenz* bleibt unberuehrt.
BRUMM_VORLAUF_DB = 40.0

# --------------------------------------------------------------------
# Pegelfuehrung: die Zahlen und woher sie kommen
# --------------------------------------------------------------------
#
# Alles hier ist am 4.9.2026 an gebautem Material gemessen: drei
# Rollenspuren (Guest, Presenter, CoPresenter) zu je 240 s, aus einzeln
# gesprochenen Saetzen auf eine gemeinsame Zeitachse gelegt, mit festem
# Keim und unter /tmp. Zwei Spuren tragen eine **aufgepraegte**
# Haltungsaenderung von 10,0 und 7,0 dB, die dritte ist die Kontrolle
# und bewegt sich nicht. Von jeder Spur gibt es dieselbe Fassung ohne
# Haltungsaenderung -- daran wird gemessen, was die Fuehrung der Sprache
# wegnimmt, wenn es gar nichts zu tun gibt. Redeanteil 31 / 29 / 11 %,
# laengste Sprechpause 25 / 24 / 48 s.

# --- Das Fenster: in Sekunden REDE, nicht in Sekunden Wanduhr --------
# Das ist der Unterschied, an dem der ganze Schritt haengt, und er kam
# aus einer gescheiterten Messung. Ein Fenster in Wanduhrzeit haengt am
# Redeanteil: in 30 s Wand liegen bei 31 % Rede rund 9 s Sprache, bei
# 11 % aber nur 3 s -- und ein Mittel aus 3 s Rede wackelt um 0,47 bis
# 0,63 dB (gemessen, 400 Ziehungen je Spur), also um mehr, als die
# Fuehrung nachher ausrichten soll. Auf der Redeachse hat eine Pause
# dagegen **gar keine Laenge**. Sie wird uebersprungen statt gemessen,
# und damit ist die uebliche Frage "wie lang muss das Fenster sein,
# damit es Pausen nicht fuer leise haelt" gegenstandslos.
#
# Wie breit: gemessen wurde beides gegeneinander -- was von der
# aufgepraegten Haltungsaenderung stehenbleibt (der Rest), und was die
# Fuehrung auf der Spur *ohne* Haltungsaenderung noch bewegt (das Leck,
# und das ist gestohlene Sprachdynamik). Der Rest hat ein Minimum:
#   Fenster    1 s    3 s    5 s    8 s   12 s   20 s   30 s   45 s
#   Rest    3,1/2,5 1,9/1,4 1,9/1,1 1,7/1,2 1,9/1,6 2,6/2,8 3,6/4,0 5,7/5,7
#   Leck    3,1/2,5 1,7/1,2 1,3/0,9 1,0/0,6 0,7/0,4 0,6/0,3 0,5/0,2 0,3/0,1
# (Guest/Presenter, in dB). Kurz laeuft die Fuehrung der Sprache
# hinterher, lang verschmiert sie die Haltungsaenderung selbst; 8 s Rede
# ist der gemessene Tiefpunkt der Summe ueber alle drei Spuren.
LEVELER_FENSTER_S = 8.0

# --- Mittig, nicht nachlaufend ---------------------------------------
# Ein nachlaufendes Fenster kennt nur die Vergangenheit und kommt darum
# zu spaet. Gemessen, Rest der aufgepraegten Haltungsaenderung bei 8 s:
# mittig 1,7 / 1,2 dB, nachlaufend 3,5 / 2,9 dB -- und mit laengerem
# Fenster wird nachlaufend *schlechter*, bei 30 s 9,2 / 8,5 dB gegen
# 3,6 / 4,0 dB mittig. Diese Datei liest die Aufnahme ohnehin ganz in
# ein Feld; die Zukunft zu kennen kostet sie also nichts, und darum
# gibt es hier keinen Schalter dafuer.

# --- Das Tor: die Frage, ob in der Pause aufgedreht wird -------------
# Ohne Tor hebt die Fuehrung den Raumton in den Sprechpausen um
# **35,6 / 32,3 dB** an (gemessen). Das ist der Fehler, der einen
# Regler unbrauchbar macht, und er ist kein Feinheitsproblem: das
# Steuersignal faellt in der Pause auf den Raumton, die Fuehrung haelt
# das fuer eine leise Stelle und dreht auf.
#
# Das Tor nimmt nur Rahmen, die nicht mehr als so viele LU unter der
# Programmlautheit liegen. Gegen die gebaute Wahrheit gemessen, bei
# -12 LU: es nimmt 93,6 / 99,2 / 98,8 % der wahren Rederahmen, und
# 6,2 / 6,8 / 7,6 % des Genommenen ist keine Rede -- letzteres ist der
# Wortrand, an dem das 400-ms-Fenster halb auf Sprache liegt, und es
# aendert sich mit der Schwelle kaum.
#
# Warum nicht tiefer: bei einem Raumton nur 25 dB unter der Rede liegt
# der Raum selbst 23,5 bis 26,6 LU unter dem Programm. Ein Tor bei
# -30 LU nimmt ihn dann mit, und die Anhebung springt zurueck auf
# 12,6 bis 15,9 dB. -12 LU laesst dafuer 11,5 dB Luft.
# Warum nicht hoeher: bei -6 LU faellt der Anteil erkannter Rede auf
# 80,1 %, bei -4 LU auf 64,3 %, und der Rest steigt auf 2,4 dB.
# Zwischen -15 und -10 LU liegen alle Zahlen innerhalb von 0,1 dB
# beieinander -- die Wahl ist an dieser Stelle nicht scharf, und das
# hier zu sagen ist ehrlicher, als eine Schaerfe zu behaupten.
LEVELER_TOR_LU = -12.0

# --- Wie schnell die Kurve sich bewegen darf -------------------------
# Zwei Zahlen, gemessen, und sie liegen weit auseinander. Was die
# Fuehrung selbst braucht: P99 0,94 / 0,96 / 0,46 dB/s. Was die Sprache
# von allein tut (M ueber 1 s, in der Rede, P90): 7,01 / 5,89 / 5,37
# dB/s. Dazwischen ist Platz, und dort steht die Schranke: sie liegt
# ueber allem, was die Fuehrung zu tun hat, und 5,4- bis 7,0-mal unter
# dem, was Sprache ohnehin tut. Gekostet hat sie 0,00 bis 0,01 dB am
# Rest. Enger wird es teuer: bei 0,3 dB/s kostet sie 1,5 dB, bei
# 0,05 dB/s 4,9 dB.
LEVELER_STEIGUNG_DB_S = 1.0

# --- Und wieviel sie hoechstens darf ---------------------------------
# Ein Netz, kein Arbeitswert. Gemessen brauchte die Fuehrung auf diesem
# Material hoechstens 4,95 / 5,88 / 0,90 dB in eine Richtung; bei 12, 9
# und 6 dB Schranke ist der Rest unveraendert, bei 4 dB kostet sie
# schon 0,6 bis 1,6 dB. 9 dB laesst den ganzen gemessenen Bedarf frei
# und faengt trotzdem eine Fuehrung ab, die davonlaeuft -- und wenn sie
# greift, sagt der Lauf es, statt es zu verschweigen. Wer mehr als das
# braucht, hat kein Fuehrungsproblem, sondern eine Spur, die falsch
# ausgesteuert aufgenommen wurde.
LEVELER_HOECHSTENS_DB = 9.0

# --- Erst melden, dann tun -------------------------------------------
# Dieselbe Regel wie beim Entbrummen: ein knapper Fall wird gemeldet
# und liegengelassen. Entschieden wird an der Streuung des getorten
# Steuersignals (P90-P10 ueber die Rederahmen) -- das ist genau der
# Weg, den die Fuehrung zuruecklegen wuerde.
# Gemessen: auf einer Spur, die sich nicht bewegt, betraegt sie
# 1,05 / 0,59 / 0,91 dB und ist damit reines Leck. Auf einer Spur mit
# 7,0 dB aufgepraegter Haltungsaenderung betraegt sie 6,81 dB, bei
# 10,0 dB Aufpraegung 8,82 dB. Zwischen dem hoechsten gemessenen Leck
# und der kleinsten gemessenen echten Aufgabe liegt also der Faktor
# 6,5. 2,0 dB liegt doppelt ueber dem Leck und 3,4-fach unter der
# Aufgabe. Darunter wird gemeldet und nichts getan -- denn was die
# Fuehrung dort bewegte, waere die Sprache und nicht die Haltung.
LEVELER_LOHNT_DB = 2.0

# --- Ab Werk aus, und warum -----------------------------------------
# Nicht, weil die Zahlen wackeln -- sie sind gemessen. Sondern weil
# zwei Faelle, die diesen Schritt schaden lassen koennen, in dem
# Material, an dem er gemessen wurde, **nicht vorkommen**:
#   * Uebersprechen. Auf einem echten Set traegt das leise Mikrofon den
#     lauten Sprecher mit. Wer diese Spur um 6 dB anhebt, hebt ihn mit
#     an -- und diese Datei sieht immer nur eine Spur und kann es nicht
#     bemerken.
#   * Ein Lacher, ein Husten, ein Stoss ans Mikrofon. Alles davon ist
#     lauter als Rede, kommt durch das Tor und zieht die Fuehrung nach
#     unten. Im gebauten Material steht keines davon.
# Darum dasselbe wie beim Entbrummen: gemessen wird immer, getan wird
# nur auf Verlangen. Der Lauf sagt bei jeder Spur, wieviel es zu tun
# gaebe -- auch und gerade, wenn er nichts tut.
LEVELER_AB_WERK = "0"

TREFFER_LU = 0.05            # naeher als das muss die Lautheit nicht.
                             # EBU R 128 nennt fuer die Qualitaetskontrolle
                             # an Dateien +-0,2 LU; das hier ist strenger.
MAX_RUNDEN = 5


# --------------------------------------------------------------------
# Die Felder eines auphonic-Presets -- und was hier davon wirkt
# --------------------------------------------------------------------
#
# Gelesen am 3.9.2026 aus https://auphonic.com/api/info/algorithms.json.
# Die Karte ist ohne Schluessel abrufbar; **diese Datei ruft nichts ab**,
# die Werte stehen hier abgeschrieben. 37 Felder in neun Wurzeln:
# filtering, denoise, gate, crossgate, leveler, backforeground, cutter,
# normloudness, segments.
#
# Je Zeile:
#   Name       wie das Feld im Preset heisst
#   Wurzel     wessen Kind es dort ist ("" = selbst eine der neun Wurzeln)
#   Typ        "ja/nein", "zahl" oder "wahl:a,b,c"
#   auphonic   **ihre** Vorgabe, woertlich aus der Karte
#   hier       unsere Vorgabe. Wo sie abweicht, sagt der Satz warum.
#   wirkt      True: es gibt hier einen gebauten Schritt dafuer
#   Satz       was es tut -- oder warum es nichts tut
#
# Ein Feld ohne Wirkung wird trotzdem angenommen. Ein Schalter, den es
# nicht gibt, sieht aus wie ein vergessener; einer, der da ist und
# ausdruecklich nichts tut, ist eine Auskunft.

PRESET_SCHALTER = [
 # --- filtering ----------------------------------------------------
 ("filtering", "", "ja/nein", "ja", "ja", True,
  "Hochpass an oder aus. Bei auphonic wandert seine Grenze mit dem "
  "Material, hier steht sie fest; --hochpass sagt wo."),
 ("filtermethod", "filtering", "wahl:hipfilter,autoeq,bwe,studiovoice",
  "hipfilter", "hipfilter", True,
  "Nur hipfilter ist gebaut. autoeq, bwe und studiovoice sind ihre "
  "eigenen Modelle -- wer sie waehlt, bekommt eine Absage statt einer "
  "stillen Umdeutung."),
 # --- denoise ------------------------------------------------------
 ("denoise", "", "ja/nein", "nein", "nein", False,
  "Es gibt hier keinen Entrauscher. Wieviel Entrauschen richtig ist, "
  "entscheidet nach ITU-T P.835 ein Hoerversuch, kein Messwert."),
 ("denoisemethod", "denoise",
  "wahl:classic,dynamic,speech_isolation,static", "classic", "classic",
  False, "Kein Entrauscher, also keine Wahl zwischen vier Verfahren."),
 ("denoiseamount", "denoise", "zahl", "0 (= voll, 100 dB)", "0", False,
  "Dasselbe: ohne Entrauscher hat die Menge nichts, worauf sie wirkt."),
 ("debreathamount", "denoise", "zahl", "-1 (= aus)", "-1", False,
  "Atemzuege zu finden ist eine eigene Erkennung, und frei gibt es "
  "dafuer nichts."),
 ("dehum", "denoise", "wahl:0,50,60,auto", "0 (= aus)", "0", True,
  "Entbrummen. 50 oder 60 setzt die Netzfrequenz fest, auto laesst sie "
  "messen. Bei auphonic ist dehum ein Kind von denoise; hier nicht, "
  "weil es hier keinen Entrauscher gibt, dessen Kind es sein koennte."),
 ("dehumamount", "denoise", "zahl", "0 (= voll, 100 dB)", "0", True,
  "Wie tief die Kerbe wird, in dB. 0 heisst voll. Eine flache Kerbe "
  "kostet weniger Stimme, und genau darum ist sie der Hebel im Bereich "
  "des Stimmgrundtons: gemessen lohnt eine 3-dB-Kerbe bei 100 Hz 4,9 "
  "bis 7,6 dB frueher als eine volle, bei 150 Hz 7,4 bis 7,7 dB."),
 # --- gate ---------------------------------------------------------
 ("gate", "", "ja/nein", "ja", "nein", False,
  "Ihr Rauschtor hat keinen einzigen einstellbaren Wert, und was es "
  "tut, war nur von aussen zu messen. Hier ist keines gebaut."),
 # --- crossgate ----------------------------------------------------
 ("crossgate", "", "ja/nein", "ja", "nein", False,
  "Uebersprechen wegzunehmen braucht alle Spuren auf einmal. Diese "
  "Datei sieht immer nur eine."),
 # --- leveler ------------------------------------------------------
 ("leveler", "", "ja/nein", "ja", "nein", True,
  "Pegelfuehrung ueber die Zeit. Gebaut, aber ab Werk aus: gemessen "
  "wird immer, gefuehrt nur auf Verlangen. Uebersprechen und Lacher "
  "kamen im Messmaterial nicht vor, und beide koennen ihr schaden."),
 ("levelerstrength", "leveler", "zahl", "100", "100", True,
  "Wieviel von der gemessenen Abweichung wirklich ausgeglichen wird, "
  "in Prozent. 100 zieht ganz gerade, 50 halb, 0 ist wie aus. Bei "
  "auphonic steuert dieselbe Zahl ein anderes Verfahren -- gleich "
  "heisst hier nur der Name und die Richtung, nicht das Ergebnis."),
 ("levelerstrength_m", "leveler", "zahl", "-1 (= wie oben)", "-1", False,
  "Dasselbe, fuer Musik."),
 ("compressor", "leveler", "wahl:auto,off,soft,medium,hard", "auto",
  "auto", False, "Ohne Leveler ohne Wirkung."),
 ("compressor_m", "leveler", "wahl:Same,auto,off,soft,medium,hard",
  "Same", "Same", False, "Dasselbe, fuer Musik."),
 ("maxlra", "leveler", "zahl", "0 (= aus)", "0", False,
  "Eine Schranke fuer den Lautheitsumfang. Hier wird der Umfang "
  "gemessen und berichtet, aber nicht beschnitten."),
 ("maxs", "leveler", "zahl", "0 (= aus)", "0", False,
  "Schranke fuer die kurzzeitige Lautheit. Ohne Leveler nichts, "
  "womit sie einzuhalten waere."),
 ("maxm", "leveler", "zahl", "0 (= aus)", "0", False,
  "Dasselbe fuer die momentane Lautheit."),
 ("musicgain", "leveler", "zahl", "0", "0", False,
  "Braucht die Unterscheidung Musik gegen Sprache; die gibt es hier "
  "nicht."),
 ("msclassifier", "leveler", "wahl:on,speech,music", "on", "on", False,
  "Genau dieser Klassierer fehlt hier."),
 ("pan", "leveler", "zahl", "0.0 (= Mitte)", "0.0", False,
  "Diese Datei mischt nicht und stellt darum nichts im Bild auf."),
 # --- backforeground -----------------------------------------------
 ("backforeground", "",
  "wahl:auto,foreground,background,ducking,unchanged", "auto", "auto",
  False, "Vorder- gegen Hintergrund und Ducking brauchen mehr als eine "
  "Spur."),
 ("gain", "backforeground", "zahl", "0", "0", False,
  "Eine feste Verstaerkung je Spur. Hier bestimmt die Ziellautheit die "
  "Verstaerkung; beides zugleich waere ein Widerspruch."),
 ("backgroundgain", "backforeground", "zahl", "-18", "-18", False,
  "Ohne Ducking ohne Wirkung."),
 ("ducking_fadetime", "backforeground", "zahl", "500", "500", False,
  "Dasselbe."),
 # --- cutter -------------------------------------------------------
 ("cutter", "", "ja/nein", "nein", "nein", False,
  "Automatisch schneiden. Diese Datei schneidet nichts -- sie gibt "
  "genauso viele Proben zurueck, wie sie bekommen hat."),
 ("silence_cutter", "cutter", "ja/nein", "ja", "nein", False,
  "Ohne Schneider ohne Wirkung."),
 ("filler_cutter", "cutter", "ja/nein", "nein", "nein", False,
  "Fuellwoerter zu finden braucht eine Worterkennung."),
 ("cough_cutter", "cutter", "ja/nein", "nein", "nein", False,
  "Husten zu finden -- kein freies Werkzeug bekannt."),
 ("music_cutter", "cutter", "ja/nein", "nein", "nein", False,
  "Braucht wieder die Unterscheidung Musik gegen Sprache."),
 ("cut_mode", "cutter",
  "wahl:apply_cuts,export_uncut_audio,set_cuts_to_silence", "apply_cuts",
  "apply_cuts", False, "Ohne Schnitte gibt es nichts anzuwenden."),
 # --- normloudness -------------------------------------------------
 ("normloudness", "", "ja/nein", "ja", "ja", True,
  "Lautheit und Spitzenbegrenzung an oder aus. Aus heisst: nur der "
  "Hochpass und, wenn bestellt, das Entbrummen; der Pegel bleibt."),
 ("loudnesstarget", "normloudness", "zahl", "-16", "-16", True,
  "Die Ziellautheit in LUFS. Auch als --lufs. Achtung: -16 ist ein "
  "Wert fuer die *Mischung*. Je Spur ist er an echtem Material nicht "
  "zu halten -- siehe den Hinweis, den der Lauf dann druckt."),
 ("maxpeak", "normloudness", "zahl", "99.0 (= automatisch)", "99.0",
  True, "Die Decke fuer die wahre Spitze in dBTP. Auch als --dbtp. "
  "99.0 heisst automatisch, und automatisch ist bei ihnen nicht "
  "geraten, sondern genannt: -1 dBTP, und -2 dBTP ab -24 LUFS "
  "abwaerts."),
 ("dualmono", "normloudness", "ja/nein", "nein", "nein", True,
  "Fuer eine Monospur, die spaeter auf zwei Kanaele verdoppelt wird. "
  "Dann wird sie 3,01 LU zu laut (BS.1770-5), also wird das Ziel hier "
  "um 3,01 LU abgesenkt."),
 ("loudnessmethod", "normloudness", "wahl:program,dialog,rms", "program",
  "program", True,
  "Nur program ist gebaut, und program ist die Messung nach BS.1770. "
  "dialog braucht eine Sprecherkennung, rms ist eine andere Messung."),
 # --- segments -----------------------------------------------------
 ("segments", "", "kein Schalter", "[] (= keine)", "[]", False,
  "Eigene Einstellungen je Abschnitt. Ohne die Segmentierung, auf der "
  "bei ihnen alles aufsitzt, gibt es hier keine Abschnitte."),
]


def preset_tafel():
    """Die ganze Tafel drucken -- was ein Preset kann und was hier wirkt.

    Der Kopf dieser Datei verspricht diesen Ausdruck seit dem 3.9.2026;
    gebaut war er nicht. Aufgefallen ist es, als `leveler` von "wirkt
    nicht" auf "wirkt" wechselte und es keinen Weg gab, das nachzusehen.
    """
    wurzeln = []
    for name, wurzel, typ, ihre, unsere, wirkt, satz in PRESET_SCHALTER:
        if wurzel and wurzel not in wurzeln:
            wurzeln.append(wurzel)
        elif not wurzel:
            wurzeln.append(name)
    sys.stdout.write("\nDie Felder eines auphonic-Presets, und was hier "
                     "davon wirkt\n")
    sys.stdout.write("  %d Felder in %d Wurzeln. * heisst: dafuer gibt es "
                     "hier einen gebauten Schritt.\n\n"
                     % (len(PRESET_SCHALTER), len(set(wurzeln))))
    sys.stdout.write("    %-18s %-34s %-22s %-22s\n"
                     % ("Feld", "Typ", "auphonic", "hier"))
    for name, wurzel, typ, ihre, unsere, wirkt, satz in PRESET_SCHALTER:
        sys.stdout.write("  %s %-18s %-34s %-22s %-22s\n"
                         % ("*" if wirkt else " ",
                            ("  " if wurzel else "") + name, typ, ihre,
                            unsere))
    sys.stdout.write("\n  Ein Feld ohne Stern wird angenommen und tut "
                     "nichts. Warum, sagt die\n  Tafel im Quelltext bei "
                     "jedem Feld in einem Satz.\n\n")
    wirken = sum(1 for z in PRESET_SCHALTER if z[5])
    sys.stdout.write("  %d von %d Feldern wirken.\n\n"
                     % (wirken, len(PRESET_SCHALTER)))


# --------------------------------------------------------------------
# Protokoll: jeder Schritt eine Zeile, mit seiner Dauer
# --------------------------------------------------------------------

class Protokoll(object):
    """Schreibt je Schritt eine Zeile: was getan wurde, und wie lange."""

    def __init__(self):
        self.nummer = 0
        self.beginn = time.time()

    def start(self, name):
        self.nummer += 1
        self._name = name
        self._t = time.time()
        return self

    def fertig(self, was):
        d = time.time() - self._t
        sys.stdout.write("  %d  %-22s %-58s %6.2f s\n"
                         % (self.nummer, self._name, was, d))
        sys.stdout.flush()

    def hinweis(self, text):
        sys.stdout.write("     %s\n" % text)
        sys.stdout.flush()

    def summe(self):
        return time.time() - self.beginn


# --------------------------------------------------------------------
# ffmpeg
# --------------------------------------------------------------------

def _lauf(cmd, eingabe=None, roh=False):
    p = subprocess.run(cmd, input=eingabe,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        text = p.stderr.decode("utf-8", "replace").strip().splitlines()
        raise RuntimeError("%s scheiterte: %s"
                           % (cmd[0], text[-1] if text else "ohne Meldung"))
    return p.stdout if roh else p


def form(pfad):
    """Abtastrate, Kanalzahl und Laenge der ersten Tonspur."""
    aus = _lauf(["ffprobe", "-v", "error", "-select_streams", "a:0",
                 "-show_entries", "stream=sample_rate,channels",
                 "-show_entries", "format=duration",
                 "-of", "default=nw=1:nk=1", pfad]).stdout
    zeilen = aus.decode().split()
    if len(zeilen) < 3:
        raise RuntimeError("in %s ist keine Tonspur zu finden" % pfad)
    return int(zeilen[0]), int(zeilen[1]), float(zeilen[2])


def einlesen(pfad, kanaele):
    """Die Datei als float32-Feld, Form (Proben, Kanaele)."""
    roh = _lauf(["ffmpeg", "-v", "error", "-i", pfad,
                 "-map", "a:0", "-f", "f32le", "-acodec", "pcm_f32le", "-"],
                roh=True)
    return np.frombuffer(roh, dtype="<f4").reshape(-1, kanaele)


def durch_ffmpeg(x, sr, filterkette):
    """Ein Feld durch eine ffmpeg-Filterkette schicken, ohne Zwischendatei."""
    kanaele = x.shape[1]
    roh = _lauf(["ffmpeg", "-v", "error",
                 "-f", "f32le", "-ar", str(sr), "-ac", str(kanaele), "-i", "-",
                 "-af", filterkette,
                 "-f", "f32le", "-acodec", "pcm_f32le", "-"],
                eingabe=np.ascontiguousarray(x, dtype="<f4").tobytes(),
                roh=True)
    return np.frombuffer(roh, dtype="<f4").reshape(-1, kanaele)


_ZAHL = r"(-?(?:\d+\.?\d*(?:[eE][-+]?\d+)?|inf|nan))"


def lautheitsverlauf(x, sr):
    """Wie `lautheit`, aber sie gibt auch die ganze M-Reihe zurueck.

    Der Metadatenstrom von ebur128 traegt alle 100 ms einen Rahmen mit
    der momentanen Lautheit M (400-ms-Fenster). `lautheit` hat davon
    immer nur den letzten gelesen und den Rest weggeworfen -- bei 240 s
    Material sind das 2399 von 2400 Rahmen. Genau diese Reihe ist das
    Steuersignal der Pegelfuehrung. Sie kostet also keinen zweiten
    Durchgang, sondern nur, sie nicht mehr wegzuwerfen.

    Zurueck kommt (I, LRA, wahre Spitze in dBTP, Zeiten, M-Reihe). Die
    Zeit eines Rahmens ist das **Ende** seines Fensters; die Mitte
    liegt 0,2 s frueher, und dorthin gehoert sein Wert. Gemessen am
    4.9.2026, wie stark das ueberhaupt zaehlt: eine Verschiebung um
    0,0 bis 0,4 s aendert das Ergebnis der Fuehrung um 0,02 dB. Es ist
    also richtig gerechnet, aber es ist nicht die Stelle, an der etwas
    haengt.
    """
    kanaele = x.shape[1]
    aus = _lauf(["ffmpeg", "-hide_banner", "-nostats", "-v", "error",
                 "-f", "f32le", "-ar", str(sr), "-ac", str(kanaele), "-i", "-",
                 "-af", "ebur128=peak=true:metadata=1,"
                        "ametadata=mode=print:file=-",
                 "-f", "null", os.devnull],
                eingabe=np.ascontiguousarray(x, dtype="<f4").tobytes(),
                roh=True).decode("utf-8", "replace")
    if "lavfi.r128.I" not in aus:
        raise RuntimeError("ebur128 hat nichts berichtet")
    zeit, mreihe = [], []
    for t in re.finditer(r"pts_time:([\d.]+)\n(?:lavfi\.[^\n]*\n)*?"
                         r"lavfi\.r128\.M=" + _ZAHL, aus):
        w = t.group(2)
        # -inf ist keine Zahl, mit der sich rechnen laesst. Ein Rahmen
        # ohne jede Energie liegt weit unter jedem Tor; -200 sagt das,
        # ohne die Vergleiche zu vergiften.
        zeit.append(float(t.group(1)))
        mreihe.append(-200.0 if w in ("-inf", "nan") else float(w))
    # Der letzte Rahmen traegt die endgueltigen Werte.
    schwanz = aus[aus.rindex("lavfi.r128.M="):]

    def hol(schluessel):
        t = re.search(r"lavfi\.r128\." + schluessel + r"=" + _ZAHL, schwanz)
        if not t:
            return float("nan")
        w = t.group(1)
        return float("-inf") if w == "-inf" else float(w)

    spitze = hol("true_peak")
    spitze_db = (20.0 * math.log10(spitze)
                 if spitze == spitze and spitze > 0 else float("-inf"))
    return (hol("I"), hol("LRA"), spitze_db,
            np.array(zeit), np.array(mreihe))


def lautheit(x, sr):
    """I, LRA und wahre Spitze nach EBU R 128, gemessen von ffmpeg.

    Derselbe Messer, den auch videopodcast-magic.py benutzt
    (`ebur128=peak=true`). Er steht hier noch einmal, weil diese Datei
    ohne das grosse Programm laufen koennen soll -- und weil noch offen
    ist, ob ffmpeg, libebur128 oder pyloudnorm die Messung machen soll.
    Diese Datei entscheidet das nicht. Sie nimmt, was das Programm heute
    schon nimmt, damit die Zahlen vergleichbar bleiben.

    Gelesen wird aber nicht die Schlusstafel, sondern der Metadatenstrom:
    die Tafel druckt eine Nachkommastelle, der Strom drei. Bei einer
    Toleranz von 0,1 LU waere die Tafel selbst schon das Hindernis.
    """
    return lautheitsverlauf(x, sr)[:3]


def schreiben(x, sr, pfad):
    """Als 24-Bit-PCM schreiben -- die Bittiefe, die auch das grosse
    Programm fuer Zwischenstaende nimmt."""
    kanaele = x.shape[1]
    _lauf(["ffmpeg", "-y", "-v", "error",
           "-f", "f32le", "-ar", str(sr), "-ac", str(kanaele), "-i", "-",
           "-c:a", "pcm_s24le", pfad],
          eingabe=np.ascontiguousarray(x, dtype="<f4").tobytes())


# --------------------------------------------------------------------
# Die wahre Spitze
# --------------------------------------------------------------------

def _bloecke(n, block):
    return (n + block - 1) // block


def blockspitzen(x, block, up=UEBERTASTUNG):
    """Die wahre Spitze je Block, 4-fach uebertastet.

    Warum uebertastet: die Probenspitze ist nicht die wahre Spitze. Fuer
    einen unguenstig liegenden Ton bei einem Viertel der Abtastrate
    lassen sich 3 dB Unterschaetzung zeigen (BS.1770-5), und Konsonanten
    sind genau solche Transienten. Ein Begrenzer auf die Probenspitze
    laesst darum Spitzen durch, die ein Wandler danach wieder herstellt.

    Stueckweise gerechnet, damit eine Stunde Material nicht als
    vierfache Kopie im Speicher liegt.
    """
    n = x.shape[0]
    nb = _bloecke(n, block)
    spitze = np.zeros(nb, dtype=np.float64)
    # Der Polyphasenfilter von resample_poly ist rund 20*up+1 Proben
    # lang; 4 Bloecke Ueberlappung sind reichlich.
    rand = 4 * block
    schritt = max(block, (1 << 20) // block * block)
    for a in range(0, n, schritt):
        b = min(n, a + schritt)
        a2, b2 = max(0, a - rand), min(n, b + rand)
        o = resample_poly(x[a2:b2].astype(np.float64), up, 1, axis=0)
        o = np.abs(o).max(axis=1)
        # zurueck auf das Blockraster des Ausschnitts
        for k in range(a // block, _bloecke(b, block)):
            va = max(k * block, a) - a2
            ve = min((k + 1) * block, n) - a2
            if ve > va:
                spitze[k] = max(spitze[k], float(o[va * up:ve * up].max()))
    return spitze


def wahre_spitze_db(x):
    if x.size == 0:
        return float("-inf")
    s = float(blockspitzen(x, 1 << 16).max())
    return 20.0 * math.log10(s) if s > 0 else float("-inf")


# --------------------------------------------------------------------
# Entbrummen -- erst nachsehen, dann kerben
# --------------------------------------------------------------------

def rauschboden(x, sr, nfft=BRUMM_FFT, perzentil=BRUMM_PERZENTIL):
    """Das Spektrum der *stehenden* Anteile.

    Je Frequenzlinie ein niedriges Perzentil ueber die Zeit. In den
    Sprechpausen ist die Stimme weg, eine Netzlinie nicht -- der Boden
    zeigt darum, was ununterbrochen da ist, und nur das. Das ist der
    ganze Trick an dieser Erkennung: sie sucht nicht nach 50 Hz, sie
    sucht nach etwas, das nicht aufhoert.
    """
    m = x.mean(axis=1) if x.ndim > 1 else x
    fenster = np.hanning(nfft)
    schritt = nfft // 4
    anzahl = 1 + max(0, (m.shape[0] - nfft) // schritt)
    if anzahl < 4:
        return None, None, 0
    P = np.empty((anzahl, nfft // 2 + 1))
    for i in range(anzahl):
        P[i] = np.abs(np.fft.rfft(m[i * schritt:i * schritt + nfft]
                                  * fenster)) ** 2
    return (np.fft.rfftfreq(nfft, 1.0 / sr),
            np.percentile(P, perzentil, axis=0), anzahl)


def linie_lesen(f, boden, fk, nfft=BRUMM_FFT):
    """Was bei fk steht: der Abstand zum Untergrund und die Leistung.

    Der Untergrund ist der Median eines Rings daneben (6 bis 30 Hz),
    nicht der Wert unmittelbar neben der Linie -- eine Linie leckt in
    ihre Nachbarschaft, und wer dort misst, misst sie noch einmal.
    """
    nah = np.abs(f - fk) <= 2.5
    ring = (np.abs(f - fk) >= 6.0) & (np.abs(f - fk) <= 30.0)
    if not nah.any() or not ring.any():
        return 0.0, 0.0
    unten = float(np.median(boden[ring]))
    spitze = float(boden[nah].max())
    if unten <= 0 or spitze <= 0:
        return 0.0, 0.0
    fenster = np.hanning(nfft)
    ueber = max(float(np.sum(boden[nah])) - unten * int(nah.sum()), 0.0)
    # Auf die Leistung im Zeitbereich zurueckgerechnet (Parseval, ein-
    # seitiges Spektrum). Am 3.9.2026 an drei bekannten Sinuslinien
    # geprueft: -20, -40 und -60 dB, Fehler 0,00 / 0,03 / 0,31 dB.
    leistung = ueber * 2.0 / (nfft * float(np.sum(fenster * fenster)))
    return 10.0 * math.log10(spitze / unten), leistung


def kerbe(x, sr, fk, tiefe_db, breite_hz=KERBE_BREITE_HZ):
    """Eine Kerbe bei fk, feste Breite in Hz, wahlweise endlich tief."""
    if tiefe_db is None:
        f = "bandreject=f=%g:width_type=h:w=%g" % (fk, breite_hz)
    else:
        f = "equalizer=f=%g:width_type=h:w=%g:g=%g" % (fk, breite_hz,
                                                       -abs(tiefe_db))
    return durch_ffmpeg(x, sr, f)


def brumm_suchen(x, sr, netz=None, tiefe_db=None,
                 sichtbar_db=BRUMM_SICHTBAR_DB,
                 stoerend_db=BRUMM_STOEREND_DB,
                 hoerbar_lu=BRUMM_HOERBAR_LU,
                 lohnt_db=BRUMM_LOHNT_DB):
    """Welche Linien gekerbt gehoeren -- und welche nur gemeldet.

    Je Oberwelle einzeln. Es gibt keine feste Zahl von Kerben: steht bei
    150 Hz eine Linie und bei 200 Hz keine, wird nur bei 150 gekerbt.

    Vier Fragen nacheinander, und keine zwei sind dieselbe:

    1. *Steht da eine Linie?* -- der Abstand zum Untergrund im
       Rauschboden. Darunter passiert nichts, und es wird nichts
       gemeldet. Das ist **Erkennung**, keine Erlaubnis.

    2. *Ist sie eindeutig?* -- eine zweite, viel hoehere Schwelle auf
       derselben Zahl. Nur sie darf kerben. Alles zwischen der ersten
       und der zweiten wird **gemeldet und liegengelassen**: eine Zeile
       im Protokoll, die sagt, was da ist und dass nichts getan wurde.
       Dann entscheidet ein Mensch und setzt den Schalter von Hand.

    3. *Ist sie laut genug, um zu stoeren?* -- der Brumm allein, gegen
       das Programm gemessen, K-bewertet nach BS.1770. Ein eindeutig
       stehender, aber sehr leiser Brumm wird gemeldet, nicht gekerbt.

    4. *Nimmt die Kerbe mehr Brumm als Stimme?* -- eine Bilanz, kein
       Erfahrungswert: die Linie aus dem Rauschboden gegen das, was die
       Kerbe insgesamt herausnimmt. Was nicht Linie ist, ist Stimme.

    Im Zweifel wird nichts getan. Das ist der ganze Unterschied zu
    einem festen Kamm, und er ist gemessen: ohne die vierte Frage waren
    von 259 gesetzten Kerben 43 schaedlich, die schlimmste um 40,1 dB.
    Mit ihr war von 176 keine einzige schaedlich.

    Zurueck kommt (Netzfrequenz, zu kerbende Linien, Urteil je Linie,
    Fehler). Das Urteil je Linie ist
    (Frequenz, Abstand in dB, Bilanz in dB oder None, Brummpegel gegen
    das Programm in LU oder None, Satz).
    """
    f, boden, rahmen = rauschboden(x, sr)
    if f is None:
        return None, [], [], "zu kurz, um einen Rauschboden zu messen"
    familien = {}
    for f0 in (50.0, 60.0):
        familien[f0] = [linie_lesen(f, boden, f0 * k)[0]
                        for k in range(1, BRUMM_LINIEN + 1)]
    if netz:
        f0 = float(netz)
    else:
        # Nach der ganzen Familie waehlen, nicht nach dem Grundton. An
        # echtem Material stand ein Brumm bei 100 Hz, dessen 50-Hz-
        # Grundton **gar nicht da war** (so sieht der Restwelligkeit
        # eines Gleichrichters aus). Wer nach dem Grundton auswaehlt,
        # greift dort daneben und findet 60 Hz, wo 50 richtig waere.
        punkte = dict((g, sum(max(0.0, v - sichtbar_db) for v in familien[g]))
                      for g in familien)
        f0 = max((50.0, 60.0),
                 key=lambda g: (punkte[g], familien[g][0]))
    urteil = []
    setzen = []
    vorlauf = 10.0 ** (BRUMM_VORLAUF_DB / 20.0)
    i_programm = None
    for k in range(1, BRUMM_LINIEN + 1):
        fk = f0 * k
        abstand = familien[f0][k - 1]
        if abstand < sichtbar_db:
            urteil.append((fk, abstand, None, None, "keine Linie"))
            continue
        _, leistung = linie_lesen(f, boden, fk)
        # Gemessen wird **immer mit der vollen Kerbe**, auch wenn spaeter
        # eine flache gesetzt wird. Sonst haengt die Messung an der
        # Behandlung: eine 3-dB-Kerbe nimmt nur einen Teil der Linie weg,
        # und dann sieht der Brumm leiser aus als er ist. Am 3.9.2026
        # gemessen, bevor es getrennt war: dieselbe Spur meldete mit
        # --dehumamount 3 einen Brumm 35,8 LU unter dem Programm statt
        # 25,2, und die Bilanz lief auf +230 dB davon. Die volle Kerbe
        # ist zudem das strengere Urteil -- eine flache lohnt gemessen
        # 4,9 bis 7,7 dB frueher, wer also mit der vollen bestehen kann,
        # besteht mit jeder.
        y = kerbe(x, sr, fk, None)
        n = min(x.shape[0], y.shape[0])
        weg = float(np.mean((x[:n] - y[:n]) ** 2))
        rest = weg - leistung
        if rest <= 0.0:
            # Die Kerbe hat nicht mehr herausgenommen, als die Linie
            # ohnehin ist. Besser wird eine Bilanz nicht; wie viel
            # besser, kann die Schaetzung des Rauschbodens nicht mehr
            # auflösen, also wird hier gedeckelt statt eine Zahl
            # erfunden.
            bilanz = BILANZ_MAX_DB
        else:
            bilanz = min(BILANZ_MAX_DB,
                         10.0 * math.log10(max(leistung, 1e-30) / rest))
        # Wie laut der Brumm gegen das Programm steht. Gemessen wird der
        # Teil, den die Kerbe herausnimmt -- das ist die Linie selbst,
        # und sie mit demselben Messer zu wiegen wie das Programm ist
        # der einzige Weg, beide Zahlen vergleichbar zu halten.
        if i_programm is None:
            i_programm = lautheit(x * vorlauf, sr)[0]
        i_brumm = lautheit((x[:n] - y[:n]) * vorlauf, sr)[0]
        pegel_lu = i_brumm - i_programm
        if abstand < stoerend_db:
            urteil.append((fk, abstand, bilanz, pegel_lu,
                           "steht da, aber nicht eindeutig (unter %.0f dB) "
                           "-- gemeldet, nichts getan" % stoerend_db))
        elif pegel_lu < -hoerbar_lu:
            urteil.append((fk, abstand, bilanz, pegel_lu,
                           "eindeutig, aber %.1f LU unter dem Programm und "
                           "damit zu leise -- gemeldet, nichts getan"
                           % -pegel_lu))
        elif bilanz < lohnt_db:
            urteil.append((fk, abstand, bilanz, pegel_lu,
                           "die Kerbe nimmt mehr Stimme als Brumm "
                           "-- gemeldet, nichts getan"))
        else:
            setzen.append(fk)
            urteil.append((fk, abstand, bilanz, pegel_lu, "kerben"))
    return f0, setzen, urteil, None


def kerben_setzen(x, sr, linien, tiefe_db, breite_hz=KERBE_BREITE_HZ):
    """Alle beschlossenen Kerben in *einem* Durchgang.

    Nicht eine ffmpeg-Fahrt je Kerbe: jede Fahrt schiebt das ganze
    Material durch die Rohre, und mehrere Fahrten kosten ein Mehrfaches
    einer Kette mit mehreren Gliedern. Gemessen am 3.9.2026 an 180 s,
    drei Kerben, je drei Laeufe: einzeln 0,49 s, als Kette 0,17 s.
    """
    if not linien:
        return x
    if tiefe_db is None:
        glieder = ["bandreject=f=%g:width_type=h:w=%g" % (fk, breite_hz)
                   for fk in linien]
    else:
        glieder = ["equalizer=f=%g:width_type=h:w=%g:g=%g"
                   % (fk, breite_hz, -abs(tiefe_db)) for fk in linien]
    return durch_ffmpeg(x, sr, ",".join(glieder))


# --------------------------------------------------------------------
# Pegelfuehrung -- erst nachsehen, dann fuehren
# --------------------------------------------------------------------

def fuehrung_messen(zeit, mreihe, i_programm, tor_lu=LEVELER_TOR_LU,
                    fenster_s=LEVELER_FENSTER_S):
    """Wo eine Stimme im Lauf der Zeit steht -- gemessen, noch nichts getan.

    Drei Schritte, und der mittlere ist der, an dem sich alles
    entscheidet:

    1. *Welche Rahmen sind Rede?* -- die, die nicht mehr als `tor_lu`
       unter der Programmlautheit liegen. Alles andere ist Pause,
       Raumton, Atem. Diese Rahmen werden nicht leiser gewichtet,
       sondern **gar nicht angesehen**.

    2. *Mitteln, aber auf der Redeachse.* Das Fenster ist in Sekunden
       Rede breit, nicht in Sekunden Wanduhrzeit. Eine Sprechpause hat
       auf dieser Achse keine Laenge -- sie wird uebersprungen. Damit
       ist die Frage, wie lang ein Fenster sein muss, damit es Pausen
       nicht fuer leise haelt, gar nicht mehr zu stellen: es haelt sie
       nie fuer leise, weil es sie nie misst. Gemittelt wird ueber die
       Leistung, nicht ueber die Dezibel, denn Lautheit ist eine
       Energiegroesse.

    3. *Zwischen den Rederahmen geradlinig verbinden.* Das ist das
       Halten ueber die Pause, und es ist kein eigener Mechanismus,
       sondern dasselbe Mittel von zwei Seiten. Ueber die laengste
       Pause im Messmaterial -- 47,8 s -- bekommt der Raumton dadurch
       hoechstens 0,05 dB mehr als die Rede unmittelbar davor und
       danach (gemessen). Ohne Tor waren es 35,6 dB.

    Zurueck kommt ein Wortbuch mit dem Steuersignal, der Redemaske, der
    Streuung des Steuersignals und dem Redeanteil -- oder None, wenn zu
    wenig Rede da ist, um ueberhaupt etwas zu sagen.
    """
    dt = float(np.median(np.diff(zeit))) if zeit.size > 1 else 0.1
    rede = mreihe >= (i_programm + tor_lu)
    idx = np.where(rede)[0]
    if idx.size < 3:
        return None
    breite = max(1, int(round(fenster_s / dt)))
    # Deckt das Fenster die ganze Spur, gibt es nur einen einzigen Wert
    # und damit nichts zu fuehren. Das ist kein Fehler, sondern die
    # richtige Antwort auf eine Spur, in der kaum geredet wird.
    ganze_spur = breite >= idx.size
    breite = min(breite, idx.size)
    leistung = 10.0 ** (mreihe[idx] / 10.0)
    summe = np.convolve(leistung, np.ones(breite), mode="same")
    anzahl = np.convolve(np.ones(idx.size), np.ones(breite), mode="same")
    mittel = 10.0 * np.log10(np.maximum(summe / np.maximum(anzahl, 1e-30),
                                        1e-30))
    steuer = np.interp(np.arange(mreihe.size), idx, mittel)
    spanne = float(np.percentile(steuer[rede], 90)
                   - np.percentile(steuer[rede], 10))
    return {"steuer": steuer, "rede": rede, "spanne": spanne, "dt": dt,
            "anteil": float(rede.mean()), "ganze_spur": ganze_spur,
            "tor_lufs": i_programm + tor_lu,
            "rede_s": float(idx.size) * dt}


def _steigung_begrenzen(g, dt, max_db_s):
    """Die Kurve darf sich nur so schnell bewegen -- und zwar symmetrisch.

    Zweimal gerechnet, einmal vorwaerts und einmal rueckwaerts, dann
    gemittelt. Ein einziger Durchgang vorwaerts haelt die Schranke zwar
    auch ein, verzoegert aber jede Bewegung und verschiebt die Kurve
    damit in der Zeit -- was das mittige Fenster gerade vermeiden soll.
    Das Mittel zweier Kurven, die beide hoechstens `max_db_s` steigen,
    steigt selbst hoechstens `max_db_s`; die Schranke bleibt also
    eingehalten.
    """
    if max_db_s is None or max_db_s <= 0 or g.size < 2:
        return g
    d = max_db_s * dt
    vor = g.copy()
    for i in range(1, vor.size):
        vor[i] = min(max(vor[i], vor[i - 1] - d), vor[i - 1] + d)
    zurueck = g.copy()
    for i in range(zurueck.size - 2, -1, -1):
        zurueck[i] = min(max(zurueck[i], zurueck[i + 1] - d), zurueck[i + 1] + d)
    return 0.5 * (vor + zurueck)


def fuehrung_kurve(mess, staerke=100.0, hoechstens_db=LEVELER_HOECHSTENS_DB,
                   steigung_db_s=LEVELER_STEIGUNG_DB_S):
    """Aus dem Steuersignal die Verstaerkungskurve, mit beiden Schranken.

    Bezugspunkt ist der **Median des Steuersignals ueber die Rede**,
    nicht die Ziellautheit. Die Fuehrung zieht eine Stimme also auf
    ihren eigenen mittleren Sprechpegel gerade und sagt nichts darueber,
    wie laut sie insgesamt sein soll -- das tut der Schritt
    "verstaerken, begrenzen", und das Angleichen zwischen mehreren
    Spuren gehoert ebenfalls dorthin. Beides in einem Schritt zu tun
    waere bequem und hiesse, zwei Fragen mit einer Zahl zu beantworten.
    Gemessen am 4.9.2026, warum das die billigere Haelfte ist: drei
    Spuren, die 6,46 dB auseinanderliegen, stehen nach dem blossen
    Angleichen je Spur noch 0,05 dB auseinander -- dafuer braucht es
    diese Fuehrung ueberhaupt nicht. Was sie beitraegt, ist das andere:
    innerhalb einer Spur blieben 8,82 und 6,81 dB Wanderung stehen, und
    danach 0,65 und 0,64 dB.

    Ganz lautheitsneutral ist sie trotzdem nicht: gemessen verschob sie
    die integrierte Lautheit um -1,31 bis +0,08 LU, weil sich mit der
    Huellkurve auch verschiebt, welche Rahmen das Tor von BS.1770
    nimmt. Genau darum steht sie **vor** der Lautheitsmessung und nicht
    dahinter.

    Zurueck kommen die Kurve, ihr Bezugspunkt und wie oft die beiden
    Schranken gegriffen haben.
    """
    steuer, rede = mess["steuer"], mess["rede"]
    mitte = float(np.median(steuer[rede]))
    roh = (mitte - steuer) * (max(0.0, min(100.0, staerke)) / 100.0)
    g = np.clip(roh, -hoechstens_db, hoechstens_db)
    gedeckelt = float(np.mean(np.abs(roh) > hoechstens_db + 1e-9))
    vorher = g
    g = _steigung_begrenzen(g, mess["dt"], steigung_db_s)
    gebremst = float(np.mean(np.abs(g - vorher) > 1e-6))
    return g, mitte, gedeckelt, gebremst


def fuehrung_anlegen(x, sr, zeit, g):
    """Die Kurve an die Proben legen, stueckweise.

    Zwischen den Rahmen wird geradlinig verbunden: bei 100 ms Abstand
    und hoechstens 1 dB/s liegen zwischen zwei Stuetzen 0,1 dB, da ist
    nichts zu hoeren. Stueckweise, damit eine Stunde Material nicht als
    zweites Feld in doppelter Genauigkeit im Speicher liegt.
    """
    n = x.shape[0]
    y = np.empty((n, x.shape[1]), dtype=np.float32)
    stuetzen = zeit - 0.2          # die Mitte des 400-ms-Fensters
    schritt = 1 << 21
    for a in range(0, n, schritt):
        b = min(n, a + schritt)
        t = np.arange(a, b, dtype=np.float64) / float(sr)
        f = 10.0 ** (np.interp(t, stuetzen, g) / 20.0)
        y[a:b] = x[a:b] * f[:, None].astype(np.float32)
    return y


# --------------------------------------------------------------------
# Verstaerken und begrenzen
# --------------------------------------------------------------------

def begrenzerkurve(spitze_je_block, verstaerkung_db, decke_dbtp, sr, block):
    """Eine Verstaerkungskurve, die die wahre Spitze unter die Decke holt.

    Blockweise, ein Block Vorausschau, 50 ms zurueck -- dieselbe Form,
    die videopodcast-magic.py in `limiter_curve` benutzt. Sie steht hier
    noch einmal, weil diese Datei ohne das grosse Programm laufen soll,
    und sie rechnet auf der *uebertasteten* Spitze, wo jenes auf der
    Probenspitze rechnet: das ist der Unterschied, den zu messen diese
    Datei da ist.

    Zurueck kommen die Kurve je Block und wieviel dB sie hoechstens
    weggenommen hat.
    """
    decke = 10.0 ** (decke_dbtp / 20.0)
    s = spitze_je_block * (10.0 ** (verstaerkung_db / 20.0))
    noetig = np.where(s > decke, decke / np.maximum(s, 1e-30), 1.0)
    for _ in range(VORLAUF_BLOECKE):
        noetig = np.minimum(noetig, np.roll(noetig, -1))
    zurueck = math.exp(-block / (sr * RUECKKEHR_S))
    kurve = np.empty_like(noetig)
    stand = 1.0
    for k in range(noetig.shape[0]):
        stand = min(noetig[k], stand * zurueck + (1.0 - zurueck))
        kurve[k] = stand
    kleinste = float(kurve.min())
    weg_db = -20.0 * math.log10(kleinste) if kleinste > 0 else 999.0
    return kurve, max(0.0, weg_db)


def kurve_anwenden(x, kurve, verstaerkung_db, block):
    """Die Kurve blockweise anlegen, innerhalb des Blocks als Rampe."""
    n = x.shape[0]
    g = np.empty(n, dtype=np.float32)
    vorher = 1.0
    for k in range(kurve.shape[0]):
        a, b = k * block, min(n, (k + 1) * block)
        if b <= a:
            break
        g[a:b] = np.linspace(vorher, kurve[k], b - a,
                             endpoint=False, dtype=np.float32)
        vorher = kurve[k]
    g *= np.float32(10.0 ** (verstaerkung_db / 20.0))
    return x * g[:, None]


# --------------------------------------------------------------------
# Der Weg
# --------------------------------------------------------------------

def gehen(quelle, ziel, ziel_lufs, ziel_dbtp, hochpass_hz, begrenzer_max_db,
          dehum="0", dehumamount=0.0, leveler=LEVELER_AB_WERK,
          levelerstrength=100.0, leveler_fenster=LEVELER_FENSTER_S,
          leveler_tor=LEVELER_TOR_LU, leveler_steigung=LEVELER_STEIGUNG_DB_S,
          leveler_hoechstens=LEVELER_HOECHSTENS_DB,
          leveler_lohnt=LEVELER_LOHNT_DB):
    p = Protokoll()
    sys.stdout.write("\nDer Weg einer Aufnahme -- lokal, ohne Netz\n")
    sys.stdout.write("  von  %s\n  nach %s\n\n" % (quelle, ziel))

    # --- 1 -----------------------------------------------------------
    p.start("einlesen")
    sr, kanaele, dauer = form(quelle)
    x = einlesen(quelle, kanaele)
    p.fertig("%d Hz, %d Kanal/Kanaele, %.1f s"
             % (sr, kanaele, x.shape[0] / float(sr)))

    p.start("Rohmaterial messen")
    i_roh, lra_roh, tp_roh = lautheit(x, sr)
    p.fertig("I %.2f LUFS, LRA %.2f LU, Spitze %.2f dBTP"
             % (i_roh, lra_roh, tp_roh))

    if not (i_roh > ZU_LEISE_LUFS):
        p.hinweis("Diese Aufnahme liegt unter %.0f LUFS. BS.1770-5 tort "
                  "absolut bei" % ZU_LEISE_LUFS)
        p.hinweis("-70 LKFS, und was gilt, wenn kein Block darueber liegt, "
                  "ist nirgends")
        p.hinweis("festgelegt. Hier wird darum nicht verstaerkt: eine "
                  "Verstaerkung auf")
        p.hinweis("ein Ziel, das aus nichts gemessen wurde, waere geraten. "
                  "Nichts geschrieben.")
        return 2

    # --- 2 -----------------------------------------------------------
    if hochpass_hz > 0:
        p.start("Hochpass")
        x = durch_ffmpeg(x, sr, "highpass=f=%g:p=2" % hochpass_hz)
        p.fertig("%g Hz, zwei Pole -- Trittschall und Rumpeln heraus"
                 % hochpass_hz)
    else:
        p.start("Hochpass")
        p.fertig("uebergangen (--hochpass 0)")

    # --- 3 -----------------------------------------------------------
    # Vor der Lautheit, nicht danach: eine Kerbe aendert die Lautheit,
    # und wer erst normalisiert und dann kerbt, verfehlt das Ziel um
    # genau diesen Betrag. Gemessen am 3.9.2026 an drei Spuren echten
    # Materials: die Kerbe bei 100 Hz verschob die Lautheit um +0,001
    # bis +0,162 LU. Klein, aber nicht null -- und die Richtung ist
    # ueberraschend (nach oben), was am relativen Tor von BS.1770 liegen
    # duerfte. Das ist erschlossen, nicht belegt.
    p.start("entbrummen")
    if str(dehum) == "0":
        p.fertig("uebergangen (--dehum 0)")
    else:
        netz = None if str(dehum) == "auto" else float(dehum)
        tiefe = None if dehumamount <= 0 else float(dehumamount)
        f0, setzen, urteil, fehler = brumm_suchen(x, sr, netz, tiefe)
        gemeldet = [z for z in (urteil or []) if "gemeldet" in z[4]]
        if fehler:
            p.fertig("nicht entschieden: %s" % fehler)
        elif not setzen:
            p.fertig("keine Kerbe -- kein eindeutiger Brumm (%g Hz geprueft, "
                     "%d Fund(e) gemeldet)" % (f0, len(gemeldet)))
        else:
            x = kerben_setzen(x, sr, setzen, tiefe)
            p.fertig("%d Kerbe(n) bei %s Hz, je %g Hz breit%s"
                     % (len(setzen),
                        "/".join("%g" % v for v in setzen),
                        KERBE_BREITE_HZ,
                        ", voll" if tiefe is None else ", %g dB tief" % tiefe))
        # Jede Linie, die ueberhaupt zu sehen war, einzeln -- auch und
        # gerade die liegengelassenen. Eine Erkennung, die nur ihre
        # Treffer nennt, ist nicht nachzupruefen, und ein knapper Fund
        # soll gesehen werden, damit ein Mensch entscheiden kann.
        for fk, abstand, bilanz, pegel, was in (urteil or []):
            if bilanz is None:
                continue          # unter der Erkennung; nicht erwaehnenswert
            p.hinweis("%7.1f Hz  %+5.1f dB ueber dem Untergrund, "
                      "%.1f LU unter dem Programm, Bilanz %+5.1f dB"
                      % (fk, abstand, -pegel, bilanz))
            p.hinweis("           %s" % was)
        if urteil and not fehler:
            still = [z for z in urteil if z[2] is None]
            p.hinweis("Netzfrequenz %g Hz (%s), %d Linien geprueft, %d davon "
                      "unter %.0f dB und" % (f0, "gesetzt" if netz else
                                             "gemessen", len(urteil),
                                             len(still), BRUMM_SICHTBAR_DB))
            p.hinweis("damit nicht zu sehen. Gekerbt wird nur, was "
                      "**eindeutig** ist: %.0f dB ueber dem" % BRUMM_STOEREND_DB)
            p.hinweis("Untergrund, hoechstens %.0f LU unter dem Programm, und "
                      "die Kerbe muss mehr" % BRUMM_HOERBAR_LU)
            p.hinweis("Brumm nehmen als Stimme. Ein knapper Fall wird "
                      "gemeldet und liegengelassen.")

    # --- 4 -----------------------------------------------------------
    # Vor dem Verstaerken und vor dem Begrenzer, und beides mit Grund:
    # die Fuehrung verschiebt die integrierte Lautheit (gemessen -1,31
    # bis +0,08 LU), also muss danach neu gemessen werden; und sie hebt
    # leise Stellen an, also muss der Begrenzer das Ergebnis sehen und
    # nicht den Zustand davor.
    p.start("Pegelfuehrung")
    i_vor, lra_vor, _, zeit, mreihe = lautheitsverlauf(x, sr)
    mess = fuehrung_messen(zeit, mreihe, i_vor, leveler_tor, leveler_fenster)
    gefuehrt = False
    if mess is None:
        p.fertig("nicht entschieden: unter drei Rederahmen ueber dem Tor")
    elif mess["ganze_spur"]:
        p.fertig("nichts zu tun -- nur %.1f s Rede, das Fenster deckt "
                 "die ganze Spur" % mess["rede_s"])
    elif mess["spanne"] < leveler_lohnt:
        # Bewusst ohne "getan" oder "uebergangen": ob der Schalter an
        # war, spielt hier keine Rolle mehr, und die Zeile soll nicht
        # eine Entscheidung behaupten, die die Messung schon getroffen
        # hat.
        p.fertig("nichts zu tun -- %.2f dB Spanne, gefuehrt wird ab %.1f dB"
                 % (mess["spanne"], leveler_lohnt))
    elif str(leveler) == "0":
        p.fertig("uebergangen (--leveler 0) -- es waeren %.2f dB Spanne "
                 "zu tun" % mess["spanne"])
    else:
        g, mitte, gedeckelt, gebremst = fuehrung_kurve(
            mess, levelerstrength, leveler_hoechstens, leveler_steigung)
        x = fuehrung_anlegen(x, sr, zeit, g)
        gefuehrt = True
        p.fertig("%.2f dB Spanne geglaettet, angelegt %+.2f bis %+.2f dB"
                 % (mess["spanne"], g.min(), g.max()))
    if mess is not None:
        p.hinweis("Programm %.2f LUFS, Tor bei %.2f LUFS (%.0f LU darunter); "
                  "%.0f %% der Rahmen" % (i_vor, mess["tor_lufs"], -leveler_tor,
                                          100.0 * mess["anteil"]))
        p.hinweis("sind danach Rede, zusammen %.1f s. Das Steuersignal "
                  "streut %.2f dB" % (mess["rede_s"], mess["spanne"]))
        p.hinweis("(P90-P10 ueber die Rederahmen); gefuehrt wird ab %.1f dB. "
                  "Das Fenster ist" % leveler_lohnt)
        p.hinweis("%.0f s **Rede** breit und liegt mittig -- eine Sprechpause "
                  "hat auf dieser" % leveler_fenster)
        p.hinweis("Achse keine Laenge und wird darum nie fuer eine leise "
                  "Stelle gehalten.")
    if gefuehrt:
        p.hinweis("Gezogen wird auf den eigenen mittleren Sprechpegel dieser "
                  "Spur, %.2f LUFS --" % mitte)
        p.hinweis("nicht auf die Ziellautheit. Wie laut sie am Ende ist, "
                  "entscheidet der Schritt")
        p.hinweis("\"verstaerken, begrenzen\" -- und das Angleichen "
                  "zwischen mehreren Spuren auch.")
        p.hinweis("Hoechstens %.1f dB/s und hoechstens %.1f dB; die "
                  "Steigungsschranke griff bei" % (leveler_steigung,
                                                   leveler_hoechstens))
        p.hinweis("%.1f %% der Rahmen, die Betragsschranke bei %.1f %%. "
                  "Staerke %.0f %%." % (100.0 * gebremst, 100.0 * gedeckelt,
                                        levelerstrength))
        if gedeckelt > 0.0:
            p.hinweis("Die Betragsschranke hat gegriffen. Eine Fuehrung, die "
                      "mehr als %.1f dB" % leveler_hoechstens)
            p.hinweis("braucht, gleicht nicht mehr eine Haltung aus, sondern "
                      "eine Aufnahme, die")
            p.hinweis("falsch ausgesteuert wurde -- und das ist ein anderer "
                      "Schritt.")
        if mess["anteil"] > 0.6:
            p.hinweis("Ueber 60 %% der Rahmen gelten als Rede. Entweder hoert "
                      "diese Stimme nicht")
            p.hinweis("auf, oder das Tor nimmt den Raum mit. Im zweiten Fall "
                      "fuehrt sie nach")
            p.hinweis("dem Raumton -- dann gehoert --leveler-tor hoeher.")
        # Was hier nicht gemessen werden konnte, und darum an dieser
        # Stelle steht und nicht in einer Notiz: es entscheidet, ob man
        # dem Ergebnis trauen darf.
        p.hinweis("Unsicher bleibt zweierlei, und beides kam im Material "
                  "nicht vor, an dem")
        p.hinweis("diese Zahlen gemessen wurden: Uebersprechen -- wer diese "
                  "Spur anhebt,")
        p.hinweis("hebt den Nachbarn mit an, und diese Datei sieht immer nur "
                  "eine Spur --")
        p.hinweis("und ein Lacher, ein Husten, ein Stoss ans Mikrofon: alles "
                  "lauter als Rede,")
        p.hinweis("alles durch das Tor, und alles zieht die Fuehrung nach "
                  "unten.")

    # --- 5 und 6 ------------------------------------------------------
    p.start("Spitzen vermessen")
    spitzen = blockspitzen(x, BLOCK)
    p.fertig("%d Bloecke zu %d Proben, %d-fach uebertastet"
             % (spitzen.shape[0], BLOCK, UEBERTASTUNG))

    p.start("Lautheit messen")
    if gefuehrt:
        i_alt, lra_alt = i_vor, lra_vor
        i_vor, lra_vor, _ = lautheit(x, sr)
        p.fertig("I %.2f LUFS, LRA %.2f LU (vor der Fuehrung %.2f / %.2f)"
                 % (i_vor, lra_vor, i_alt, lra_alt))
    else:
        # Die Pegelfuehrung hat schon gemessen und nichts veraendert.
        # Ein zweiter Durchgang wuerde dieselbe Zahl noch einmal holen.
        p.fertig("I %.2f LUFS, LRA %.2f LU (aus Schritt 4, unveraendert)"
                 % (i_vor, lra_vor))

    p.start("verstaerken, begrenzen")
    # Erst geradeaus: die Verstaerkung, die das Ziel ohne Begrenzer
    # traefe. Danach nachfuehren, denn der Begrenzer nimmt selbst
    # Lautheit weg, und wieviel, haengt am Material.
    g = ziel_lufs - i_vor
    versuche = []          # (Verstaerkung, erreichte Lautheit)
    y = None
    gedeckelt = False
    for runde in range(MAX_RUNDEN):
        kurve, weg = begrenzerkurve(spitzen, g, ziel_dbtp, sr, BLOCK)
        if weg > begrenzer_max_db:
            # Nicht weiter druecken. Die Verstaerkung wird um den
            # Ueberschuss zurueckgenommen und die Kurve neu gerechnet.
            g -= (weg - begrenzer_max_db)
            kurve, weg = begrenzerkurve(spitzen, g, ziel_dbtp, sr, BLOCK)
            gedeckelt = True
        y = kurve_anwenden(x, kurve, g, BLOCK)
        i_ist, _, _ = lautheit(y, sr)
        versuche.append((g, i_ist))
        if abs(i_ist - ziel_lufs) <= TREFFER_LU or gedeckelt:
            break
        if len(versuche) >= 2 and versuche[-1][0] != versuche[-2][0]:
            # Sekantenschritt: der Begrenzer frisst einen Teil jeder
            # zusaetzlichen Verstaerkung wieder auf, also ist die
            # Steigung kleiner als eins und ein voller Schritt zu klein.
            steigung = ((versuche[-1][1] - versuche[-2][1])
                        / (versuche[-1][0] - versuche[-2][0]))
            steigung = min(1.0, max(0.2, steigung))
            g += (ziel_lufs - i_ist) / steigung
        else:
            g += (ziel_lufs - i_ist)
    p.fertig("%+.2f dB Verstaerkung, Begrenzer nimmt %.2f dB, %d Runde(n)"
             % (g, weg, len(versuche)))
    if gedeckelt:
        p.hinweis("Der Begrenzer haette mehr als %.1f dB nehmen muessen. "
                  "Die Verstaerkung" % begrenzer_max_db)
        p.hinweis("wurde zurueckgenommen: lieber leiser als "
                  "plattgedrueckt. Das kommt meist")
        p.hinweis("von einzelnen lauten Stellen -- einem Stoss ans "
                  "Mikrofon, einer Uebersteuerung.")
        p.hinweis("Die wegzunehmen ist ein eigener Schritt, und den tut "
                  "diese Datei nicht.")

    # --- 7 -----------------------------------------------------------
    p.start("nachmessen")
    i_ist, lra_ist, tp_ffmpeg = lautheit(y, sr)
    tp_selbst = wahre_spitze_db(y)
    p.fertig("I %.2f LUFS, LRA %.2f LU, Spitze %.2f dBTP"
             % (i_ist, lra_ist, tp_ffmpeg))
    if abs(tp_selbst - tp_ffmpeg) > 0.05:
        p.hinweis("Eigene Messung der wahren Spitze: %.2f dBTP "
                  "(ffmpeg: %.2f)." % (tp_selbst, tp_ffmpeg))
    if abs(i_ist - ziel_lufs) > TREFFER_LU:
        p.hinweis("Ziel %.1f LUFS um %.2f LU verfehlt."
                  % (ziel_lufs, i_ist - ziel_lufs))
    if kanaele == 1:
        p.hinweis("Achtung: das ist eine Monospur. Wer sie spaeter auf "
                  "zwei Kanaele")
        p.hinweis("verdoppelt, liegt 3,01 LU zu laut (BS.1770-5). Hier "
                  "gemessen: eine")
        p.hinweis("Mischung auf einem Kanal -29,4 LUFS, dieselbe auf "
                  "beiden -26,3 LUFS.")

    p.start("schreiben")
    schreiben(y, sr, ziel)
    p.fertig("24 Bit PCM, %d Hz, %d Kanal/Kanaele" % (sr, kanaele))

    sys.stdout.write("\n  %.1f s Material, %.2f s gerechnet "
                     "(%.0f s je Stunde Material)\n\n"
                     % (x.shape[0] / float(sr), p.summe(),
                        p.summe() / (x.shape[0] / float(sr)) * 3600.0))
    return 0


def main(argv=None):
    a = argparse.ArgumentParser(
        description="Der lokale Weg einer Aufnahme: Hochpass, entbrummen "
                    "(auf Verlangen), Lautheit, wahre Spitzen. Nichts wird "
                    "hochgeladen.")
    # Nicht `required`, weil --preset-tafel ohne Datei auskommt; dass
    # beide da sein muessen, wird unten geprueft und gesagt.
    a.add_argument("--in", dest="quelle", metavar="DATEI",
                   help="die Aufnahme")
    a.add_argument("--out", dest="ziel", metavar="DATEI",
                   help="wohin das Ergebnis geht")
    a.add_argument("--lufs", type=float, default=ZIEL_LUFS,
                   help="Ziellautheit (Vorgabe %(default)s; EBU R 128 "
                        "waere -23)")
    a.add_argument("--dbtp", type=float, default=ZIEL_DBTP,
                   help="Decke fuer die wahre Spitze (Vorgabe %(default)s)")
    a.add_argument("--hochpass", type=float, default=HOCHPASS_HZ,
                   metavar="HZ",
                   help="Hochpass in Hz, 0 schaltet ihn ab "
                        "(Vorgabe %(default)s)")
    a.add_argument("--grenze", type=float, default=BEGRENZER_MAX_DB,
                   metavar="DB",
                   help="soviel darf der Begrenzer hoechstens nehmen "
                        "(Vorgabe %(default)s)")
    # Name und Werte wie im auphonic-Preset, damit ein Preset hier
    # abbildbar bleibt (siehe PRESET_SCHALTER).
    a.add_argument("--dehum", choices=("0", "50", "60", "auto"), default="0",
                   help="entbrummen: 0 aus, 50 oder 60 setzt die "
                        "Netzfrequenz, auto laesst sie messen "
                        "(Vorgabe %(default)s). Ob und wo gekerbt wird, "
                        "entscheidet die Messung je Oberwelle -- nicht "
                        "dieser Schalter. Gekerbt wird nur, was eindeutig "
                        "ist; ein knapper Fund wird gemeldet und "
                        "liegengelassen")
    a.add_argument("--dehumamount", type=float, default=0.0, metavar="DB",
                   help="wie tief die Kerbe wird, in dB; 0 heisst voll "
                        "(Vorgabe %(default)s)")
    # Auch hier der Name aus dem Preset. Die vier Zahlen darunter haben
    # dort kein Feld -- auphonic stellt sie nicht ein, sondern hat sie
    # entschieden --, darum tragen sie deutsche Namen.
    a.add_argument("--leveler", choices=("0", "1"), default=LEVELER_AB_WERK,
                   help="Pegelfuehrung ueber die Zeit: 0 aus, 1 an "
                        "(Vorgabe %(default)s). Gemessen wird sie immer, "
                        "auch bei 0 -- der Lauf sagt dann, wieviel es zu "
                        "tun gaebe. Ob wirklich gefuehrt wird, entscheidet "
                        "die Messung und nicht dieser Schalter: liegt die "
                        "Spanne unter --leveler-lohnt, wird gemeldet und "
                        "liegengelassen")
    a.add_argument("--levelerstrength", type=float, default=100.0,
                   metavar="PROZENT",
                   help="wieviel von der gemessenen Abweichung ausgeglichen "
                        "wird (Vorgabe %(default)s)")
    a.add_argument("--leveler-fenster", type=float,
                   default=LEVELER_FENSTER_S, metavar="S",
                   help="Breite des Fensters in Sekunden **Rede**, nicht in "
                        "Sekunden Wanduhrzeit (Vorgabe %(default)s)")
    a.add_argument("--leveler-tor", type=float, default=LEVELER_TOR_LU,
                   metavar="LU",
                   help="soweit unter dem Programm gilt ein Rahmen noch als "
                        "Rede (Vorgabe %(default)s). Hoeher heisst weniger "
                        "Raum im Steuersignal und weniger erkannte Rede")
    a.add_argument("--leveler-steigung", type=float,
                   default=LEVELER_STEIGUNG_DB_S, metavar="DB_S",
                   help="so schnell darf die Fuehrung hoechstens laufen "
                        "(Vorgabe %(default)s)")
    a.add_argument("--leveler-hoechstens", type=float,
                   default=LEVELER_HOECHSTENS_DB, metavar="DB",
                   help="soviel darf sie hoechstens anheben oder absenken "
                        "(Vorgabe %(default)s)")
    a.add_argument("--leveler-lohnt", type=float, default=LEVELER_LOHNT_DB,
                   metavar="DB",
                   help="darunter gibt es nichts zu fuehren, und es wird "
                        "gemeldet statt getan (Vorgabe %(default)s)")
    a.add_argument("--preset-tafel", action="store_true",
                   help="die 37 Felder eines auphonic-Presets mit ihrer "
                        "Vorgabe drucken und aufhoeren")
    n = a.parse_args(argv)
    if n.preset_tafel:
        preset_tafel()
        return 0
    if not n.quelle or not n.ziel:
        a.error("--in und --out werden gebraucht")

    if not os.path.exists(n.quelle):
        sys.stderr.write("Die Datei %s gibt es nicht.\n" % n.quelle)
        return 2
    try:
        return gehen(n.quelle, n.ziel, n.lufs, n.dbtp,
                     n.hochpass, n.grenze, n.dehum, n.dehumamount,
                     n.leveler, n.levelerstrength, n.leveler_fenster,
                     n.leveler_tor, n.leveler_steigung,
                     n.leveler_hoechstens, n.leveler_lohnt)
    except RuntimeError as e:
        sys.stderr.write("Abgebrochen: %s\n" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main())

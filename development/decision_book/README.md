# The decision book

`index.html` is the board this project is run from: one page where the
owner of the repository decides and an AI agent (Claude) reports. Every
open question is a **card** with a description, options and a
recommendation; the owner answers on the card, the agent builds, and the
card moves across the board until it is done. Beside the cards the page
carries **orders** (free text to the agent), **live talks**, a
**release bar** with ten steps, and a **statistics** tab per release.

This copy is the bare template: no cards, no history, no links of its
own. **The interface is German** -- "Du" is the owner, "ich" the agent --
and stays so; this file is in English like the rest of the repository.

## Running it

It runs only as a claude.ai artifact. Opened as a plain file it shows
"nicht verbunden – nur Ansicht" and stores nothing: all state lives in the
artifact's shared database, reached through `window.claude.use(...)`.

Publish it with Claude Code's Artifact tool, with these capabilities:

```
{"db": {}, "user": {}, "assets": {}, "comments": {}}
```

* `db` -- every collection below; without it the page is read-only.
* `user` -- `can("data.write")` decides whether fields are editable, and
  `isOwner()` whether this viewer is the owner (only the owner's view
  applies the two automatic rules below).
* `assets` -- pasted images are uploaded; without it they are stored as
  shrunk JPEG data URLs.
* `comments` -- the live channel; without it everything still lands in
  the database and waits for the agent's next look.

The agent reads and writes the same database with the `ArtifactData`
tool. Republishing keeps the data. Bump `PAGE_VERSION` on every publish
and add an entry to `BUCH_LOG` (the change log behind the version label).

## The working rhythm the page assumes

* **The agent reads orders every few minutes** -- the page promises an
  answer "spätestens nach drei Minuten": new `auftraege` with status
  `neu`, open `gespraech` documents with `wartet: "Claude"`.
* **A slower pass collects answers**: cards the owner has answered carry
  `wartet: "Claude"`; the agent takes them up, writes `verlauf` entries
  and `abweichung`, and moves them on.
* **A card moves `offen` → `entschieden` → `arbeit` → `pruefen` →
  `erledigt`** (field `blatt`). `vorrat` holds what the agent has not
  shown yet. `pruefen` is only for what was not built exactly as decided,
  or what the agent decided alone; "Gesichtet" files it, "Zurückgeben"
  sends it back to `entschieden`. Before a release, `pruefen` is empty.
* **A card with `art: "hinweis"` is an answer**, to be read ("Gelesen");
  `art: "aufgabe"` is something the owner has to do ("Erledigt"). Both
  stand at the top of "Für Dich". An answer to an order is never filed
  straight into `erledigt`: the owner's view turns such a card back into
  a Hinweis.
* **A card goes to `pruefen` or `erledigt` only with both token numbers**
  (`tokens_prognose`, `tokens_ist`); the owner's view pulls one without
  them back to `arbeit`. `TOKEN_RULE_AB` and `ANSWER_RULE_AB` in the page
  say from which moment the two rules apply (0: always).

## The live channel

"Senden" in the orders tab and "Antworten" on a card also post a comment
sent to Claude, which wakes the agent's session at once. The comment text
starts with a prefix saying where the answer belongs:

* `[G:<id>]` -- a live talk, the document `gespraech/<id>`;
* `[K:E-nnn]` -- a card, the document `entscheidungen/E-nnn`.

The agent answers into that document, not in the comment. Each message
is capped at 3800 bytes.

## The data model

Everything the page reads and writes. Times are ISO strings; the page
writes UTC.

**`entscheidungen/<nr>`** -- one card; the document id is the card
number (`E-nnn`), which is also what the search finds.
`ueberschrift`, `beschreibung`, `option1`, `option2`, `weitere`,
`empfehlung` (the agent's text); `entscheidung` (the owner's answer);
`blatt` (column: `vorrat`, `offen`, `entschieden`, `arbeit`, `pruefen`,
`erledigt`); `status` (`offen`, `entschieden`, `rückfrage`,
`beantwortet`, `umgesetzt`, `zurückgestellt`, `verworfen`, `abgelöst`);
`ziel` (target release, `Buch`, `später` or empty); `wartet` (`Dich`,
`Claude` or empty); `von` (`Claude`, anything else is the owner);
`typ` (`Aufgabe`, `Auftrag`, `Thema`, `Roadmap`); `art` (`hinweis`,
`aufgabe` or empty); `quelle`; `rang` (order within `entschieden`, set by
dragging); `tokens_prognose`, `tokens_ist`, `token_fehlt`; `verlauf`
(`[{zeit, text}]`, the agent's steps); `kommentare` (`[{von, text, zeit,
live, bilder}]`); `abweichung` (the agent's answer, or what to check);
`bilder` (ids in `auftragsbilder`); `thread` (the comment thread);
`geaendert`; and the stamps only the owner's hand writes: `eigner_am`,
`gesichtet`, `zurueck`, `gelesen`, `erledigt_am`. `release` is an old
field, read only by the statistics.

**`auftraege/<id>`** -- an order. `text`, `zeit`, `bilder`, `status`
(`neu` -- the agent reads only these; `in_bearbeitung` while the owner
edits it; `übernommen`), `bearbeitet_seit`, and from the agent `karte`,
`karte_am` or `antwort`.

**`gespraech/<id>`** -- a live talk. `start`, `status` (`offen`,
`gelesen`), `wartet`, `thread`, `karte`, `gelesen_am`, and `nachrichten`
(`[{von, text, zeit, bilder, live}]`).

**`auftragsbilder/<id>`** -- one pasted image: `{asset_id, url, type,
zeit}`, or `{data, zeit}` without the assets capability.

**`statistik/<id>`** -- one release, written by the agent, only shown:
`version`, `ordnung`, `veroeffentlicht`, `zyklus_std`, `commits`,
`geaenderte_zeilen`, `codezeilen`, `tokens_neu`, `tokens_ausgabe`,
`ci_pr_s`, `ci_langsamster`, `ci_langsamster_s`, `release_lauf_s`,
`release_versuche`, `release_weg` (`short`, `long`), `suite_lokal_s`,
`nicht_gelaufen`, `changelog` (`{Added: n, ...}`), `changelog_summe`,
`testdateien`, `pruefungen`, `test_summe_s`, `test_gemessen`. A missing
value shows as "–".

**`meta/stand`** -- `aktuell` (the release being worked on),
`wartet_auf_start` (shows the "Release … starten" button), `gestartet`.

**`meta/schritte`** -- the release bar: `release`, and `schritte` as
`{"2": {zustand, text, teile: [{name, zustand, text}]}, ...}`. `zustand`
is `erledigt`, `läuft`, `wartet …` or anything else for "noch nicht
dran". Steps 1 and 8 are counted from the cards, not stored.

**`meta/claude`** -- the agent's live line: `auftraege_gelesen`,
`karten_bearbeitet`, `zuletzt`; and `sitzung_url`, the link to the
agent's session, if one should be shown.

**`meta/laeufe`** -- test runs the agent started: `laeufe` (`[{name,
url, status, gestartet}]`, shown while `status` is not `fertig`) and
`alle_url`, a link to all runs. The page carries no link of its own:
every link out comes from these two documents.

Unsent text and pasted images stay in the viewer's `localStorage`
(`eb-draft:*`) until they are sent, so a republish loses nothing.

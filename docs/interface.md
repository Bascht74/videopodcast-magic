# The interface

*Auf Deutsch: [interface.de.md](interface.de.md). Back to the [contents](README.md).*

## The interface

Four tabs, in the order they are needed. The button **Settings ...** sits in
the footer, next to **Start**. Behind it stands what is set up once and then
left alone: the key for auphonic.com with the tick that stores it, and whether
Resolve answers. What belongs to the production being made -- the preset, the
transcript -- stands where the tracks are decided, under the assignment table.

The window behind the button holds two boxes.

- **Access to auphonic.com** -- the field for the API key, the tick that
  keeps it (**Save in Keychain** on a Mac, **Save in Registry** on
  Windows) and **Connect**, which checks the key and fetches the presets.
- **Connection to Resolve** -- whether Resolve answers, with its version
  where it does and the reasons where it does not. **Check again** asks
  once more, and so does opening the window.

![The settings window](images/settings.png)

*Behind Settings ...: the key for auphonic.com, and whether Resolve
answers.*

1. **Files & production** -- the file list on top, below it a narrow strip
   with production name, spoken language and output folder. Drag files or
   whole folders in, add them, or open an earlier project; while the list is
   empty a drop area stands in its place and explains the workflow.

   Every file gets a mark from the preflight, which runs as files are added:
   ✓ nothing to fault, ! a note, ✕ this will not work. Below the list the
   result stands in one sentence.

   **Open project ...** sits on the drop area only. Files can be added to an
   open project at any time.

   A file with more than one channel says underneath what will become of
   it: one row per channel, with a tick offering **join with Channel 2**
   and, beside it, what was measured. Channels that hold nothing are
   named and stay out of everything after.

   A single block of a multi-part recording can be removed on its own. It
   then stays out although it lies in the folder, and putting it back
   later makes it a recording of its own. Only removing the whole
   recording and adding it again joins the blocks up as before.

   ![The file list](images/files.png)

   *The list after a project was opened, with the marks from the
   preflight and the strip underneath.*
2. **Assignment & time window** -- tables on the left, player on the right.
   Appears with the files.

   Beside the player the button **Separate speakers** works out who
   speaks when, on this machine and without uploading; the voices then
   stand in a table of their own under the assignment table
   ([Speech recognition and speaker separation](speech.md)).

   ![Assignment table and player](images/assignment.png)

   *Above which recording belongs to which camera, below what becomes
   of each camera.*
3. **Resolve cut** -- one line saying whether Resolve answers, with the way
   to the settings beside it, the time window, the values for the camera
   cut, the box **Speaker**, whose heading names where the speakers came
   from, and the box **Camera cut -- preview** with the cut band and a
   picture that plays.

   Both rear tabs are there with or without separate tracks. Without them the
   assignment column reads "into every camera" in grey, and sliders and
   preview for the camera cut give way to a line saying why.
4. **Output** -- appears as soon as something runs, in the same colours as
   the terminal, with the buttons **Open result folder** and
   **Create Resolve project**.

**Multitrack (one track per speaker)** has a line of its own above the
Auphonic box and needs no API key: one track per speaker is the basis for the
camera cut, with auphonic.com or without.

**Language** beside the production name is the language spoken in the
recording, preset from the system language. It becomes the tag of the written
audio track and tells auphonic.com what to expect when transcribing. "not
set" leaves the track untagged and lets the recognition work the language out
for itself.

**Start** and **Dry run (writes nothing)** stay locked while something is
outstanding, and **they say what**:

- no files,
- no production name,
- fewer than two recordings for multitrack,
- a recording without a speaker name,
- all recordings under the same name,
- two cameras with the same output file.

The field or the row it means turns red. A tick behind a tab means nothing
on it is outstanding.

Then a summary: how many cameras and audio tracks, how long, which preset,
how many files this makes, how much room they need and how much is free.
Where existing files would be overwritten, a window first shows which.

The player has play and pause, seconds and frames forward and back,
volume and speed; timecode on the left, position on the right, counted
from the In point.

- A click on a table row brings that file in at the same point in what is
  happening, so two cameras can be compared. It plays the assigned
  recording, not the camera sound.
- In point and Out point take the spot from the picture, a blue stripe
  shows the window, and dragging the rail moves only the numbers.
- Formats the machine cannot play (MXF, R3D, some ProRes variants) get a
  button for `ffplay`.

The output also goes to `videopodcast-magic.log` next to the script, with
version, time and machine in the header and a dividing line per run; the
previous run stays as `videopodcast-magic_1.log`. What Qt and ffmpeg write
past Python is in there too.

Beside **Start** runs **one bar for everything outstanding**, with a line
saying what is being worked on. It covers both halves: the measuring that
follows every change to the file list -- envelopes, camera audio,
channels, the check -- and the run itself. Where a step reports a real
percentage the bar follows it; where a step reports nothing it creeps on
slowly and stops short of the end. Backwards it never goes.

## Menu and keys

The menu bar carries what the window has no room for and what the
system expects to find there: **About**, **Settings**, and **Help**
with the way into this manual. On a Mac it sits in the system menu bar
at the top of the screen, everywhere else at the top of the window.

Everything reachable from a button is reachable from a key. The keys
that need no modifier belong to the player and only work while the
player has the focus -- otherwise a bare `I` would set the In point
while somebody is typing a name into a field.

| Key | What it does |
|---|---|
| `Ctrl+O` | Add files |
| `Ctrl+Backspace` | Remove what is selected |
| `Ctrl+Shift+O` | Choose the output folder |
| `Ctrl+R` | Start |
| `Ctrl+Shift+R` | Dry run |
| `Ctrl+1` `Ctrl+2` `Ctrl+3` | To that sheet |
| `Ctrl+,` | Settings |

In the player:

| Key | What it does |
|---|---|
| `Space` | Play and pause |
| `Left` `Right` | One frame |
| `Shift+Left` `Shift+Right` | One second |
| `Alt+Left` `Alt+Right` | Ten seconds |
| `I` `O` | Set In point, set Out point |
| `Shift+I` `Shift+O` | Jump to In point, to Out point |

This is the layout the editing programs share, so nobody who edits has
to learn it twice.

## Time axis without timecode

Where a file carries no timecode, the interface measures in the background
where it sits, with the method of the run itself. The player then jumps
between files to the same point in what is happening, and In point and
Out point hold for all alike.

One timecode anywhere is enough to hang the axis on; without any it counts
from the start of the material and shows as a virtual timecode. Until the
axis stands, In point and Out point are locked.

The axis goes into the project file, with size and modification time of every
file, and is reused at the next start; what else stands in that file is in
[camera-cut.md](camera-cut.md). Files that no longer fit it show red.

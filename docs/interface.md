# The interface

*Auf Deutsch: [interface.de.md](interface.de.md). Back to the
[contents](README.md).*

## The four tabs

Four tabs, in the order they are needed.

- **Files & production**: the file list on top, below it a narrow strip
  with production name, spoken language and output folder. Drag files or
  whole folders in, add them, or open an earlier project. While the list
  is empty a drop area stands in its place and explains the workflow.

  The program calls the look at the material before a run the preflight.
  Every file gets a mark from it as it joins the list: ✓ nothing to
  fault, ! a note, ✕ this will not work. Below the list the result stands
  in one sentence; [Preflight](preflight.md) says what each mark means.

  **Open project ...** sits on the drop area only. An open project takes
  new files at any time.

  Every video file carries **Camera audio** in the list. It reads
  **do not use the audio** until somebody sets it to **use the audio**.
  Set, that sound goes the same way as a recording that was read in:
  channels measured, one track or two decided, empty channels left out,
  cut into tracks. Synchronising takes that sound either way; the field
  does not decide it.

  Where there is nothing to decide the field sets itself, greys out and
  carries the reason beside it:

  - the file has no audio track,
  - the file stays out entirely,
  - the file is an intro or an outro,
  - one video file carries sound and no audio recording stands beside
    it. That sound is the only one there is, and the field stands on
    **use the audio**. Adding a recording gives the choice back.

  The same field stands at the camera on **Assignment & time window**,
  on the same value: change one and the other follows at once.

  A file with more than one channel says underneath what will become of
  it: one row per channel, with a tick offering **join with Channel 2**
  on the first row and, beside it, what was measured. The program names
  channels that hold nothing and leaves them out of everything after.
  [Channels: one track or two?](channels.md) says how the program tells
  the two apart.

  A single block of a multi-part recording can be removed on its own. It
  then stays out although it lies in the folder, and putting it back
  later makes it a recording of its own. Only removing the whole
  recording and adding it again joins the blocks up as before.

  ![The file list](images/files.png)

  *The list after a project was opened, with the marks from the
  preflight and the strip underneath.*
- **Assignment & time window**: tables on the left, player on the right.
  Appears with the files.

  The recordings are a tree. Its second column is the **Speaker
  name**. It starts empty, with the name the file name suggests
  standing in it in grey: a name typed in says the recording is that
  one person, and the entry **several speakers**, which can be picked
  instead, sets the program to work out who speaks when in that one
  recording, on this machine. Only that answer shows the voices. A
  separation nobody has answered for leaves the field empty and the
  rows hidden, and answering later brings them up at once, with the
  names and cameras they already had. The fifth column, **Speakers**,
  says how that stands -- **Break off** while it runs, in that row and
  no other, then **Separated: 4 speakers**, and beside it the offer
  **Only one speaker -- separate the track?** wherever a name stands in
  the field.

  With more than one audio recording nothing starts by itself; the
  answer in the row starts it. Under the recordings stands **Not on
  this machine**: it switches the separation off for the whole project.

  The voices are the rows under the recording they were heard in
  ([Speech recognition and speaker separation](speech.md)), indented
  and open to begin with. Each says **Voice** in the first column, so
  that the step down can be seen, and carries the name and the camera
  it belongs to. Folded away, the recording says under **belongs to**
  what folding takes off the screen -- the cameras: **on 2 cameras**,
  or **on 1 camera, 1 without** where a voice has none yet; open, that
  cell of its own stays empty, so the assignment is never on two levels
  at once. A click on a voice takes the player to where that voice
  speaks longest and plays it. Recordings that show no voices are a
  flat list, without triangles.

  The camera table under it carries **Camera audio** again, at every
  camera, on the value from the file list. A camera set to
  **use the audio** gets a row in the assignment table above, like a
  recording of its own.

  ![Assignment table and player](images/assignment.png)

  *Above which recording belongs to which camera, below what becomes
  of each camera.*
- **Resolve cut**: one line saying whether Resolve answers, with the way
  to the settings beside it. Then the time window, the box with the cut
  values and the box **Speaker**, whose heading names where the speakers
  came from. Last the box **Camera cut -- preview**, with the cut band
  and a picture that plays.

  The box with the cut values is called **Camera cut** when the speakers
  sit on two cameras or more. On one camera for everybody it is called
  **First cut by speaker**. Nothing is switched there: the cut falls at
  every change of speaker, and Resolve gets one clip per person. With
  one person and a second camera nobody is on it is called **Cut with
  the wide shot**: that person's camera stands, and the wide shot breaks
  it up. With **Multitrack** ticked the name stays **Camera cut**.

  The box appears as soon as **Multitrack** is ticked, or as soon as two
  people carry a name and a camera -- the voices under a separated
  recording, or the rows of the assignment table. One person is enough
  where there are two cameras or more. One person on a single camera
  gets no box, and rightly: there is nowhere to cut to. Until then a
  line stands in place of box and preview and says what is missing. A
  Resolve project is written anyway, with every camera at its measured
  place.

  Both rear tabs are there with or without separate tracks. Without them
  the assignment column reads "into every camera" in grey.
- **Output**: appears as soon as something runs, in the same colours as
  the terminal, with the buttons **Open result folder** and
  **Create Resolve project**.

**Multitrack (one track per speaker)** has a line of its own under the
assignment table, above the Auphonic box. It works with auphonic.com and
without; the program asks for the API key only on the way over
auphonic.com. The camera cut does not need the tick.

Multitrack needs two input tracks. An input track is a recording of its
own, a channel of a multichannel recorder, or the audio of a video file
set to **use the audio**. Several blocks of one recording count as one
track, and a track set aside counts as none.

The tick stays clickable whatever the material. With one track only a
grey line beside it says so, and it names the way to a second:
**Camera audio** at a camera, set to **use the audio**. If every camera
already gives its audio away, that line says there is none left to
take.

**Language** beside the production name is the language spoken in the
recording, preset from the system language. It becomes the tag of the
written audio track and tells auphonic.com what to expect when
transcribing. "not set" leaves the track untagged and lets the
recognition work the language out for itself.

**Loudness** in the **Production** box on the first page sets how loud
the finished episode is made; the same gain goes on every track, so the
balance between the speakers is kept. Five entries:

- **-16 LUFS (Podcast directories, stereo)**
- **-19 LUFS (Podcast directories, mono)**
- **-14 LUFS (YouTube -- turns down only, never up)**
- **-23 LUFS (EBU R128, broadcast)**
- **Take from source files**

A new project starts on -16 LUFS. The window remembers the entry last
chosen, and a loaded project file beats that memory.
**Take from source files** adjusts nothing at all: auphonic.com goes on
doing what its preset says, and without auphonic.com the sound stays as
it is in the source files -- the file comes out byte for byte the same.

[Which loudness target holds](preflight.md#which-loudness-target-holds)
says what else hangs on the target: normalising the tracks, the meter in
the Resolve project, and what the log records.

**Dry run** is the run that measures and reports but writes nothing. It
and **Start** stay locked while something is outstanding, and **what it
is stands under the buttons**, with the tab it is on:

- no files,
- no sound in use: no audio recording, and no video file set to
  **use the audio**,
- no production name,
- fewer than two tracks in the assignment table for multitrack,
- with multitrack, a recording with no name at all: none typed, and
  none the file name suggests -- the grey suggestion counts as the name
  wherever nothing is typed over it,
- with multitrack, all recordings under the same name,
- two cameras with the same output file.

The field or the row it means turns red. A tick behind a tab means
nothing on it is outstanding. No window opens for any of this.

Then a summary: how many cameras and audio tracks, how long, which
preset, how many files this makes, how much room they need and how much
is free. If the run would overwrite files that are already there, a
window first shows which.

The player has play and pause, seconds and frames forward and back,
volume and speed; timecode on the left, position on the right, counted
from the In point.

- A click on a row of the assignment or camera table brings that file in
  at the same point in what is happening, so two cameras can be
  compared. A click on a voice under a recording opens that recording
  where the voice speaks longest and plays at once. The tick **hear
  assigned audio** plays the recording assigned to that camera; without
  it the camera's own sound is heard.
- In point and Out point take the spot from the picture, a blue stripe
  shows the window, and dragging the rail moves only the numbers. Until
  the time axis stands they are locked.
- Formats the machine cannot play (MXF, R3D, some ProRes variants) get a
  button for `ffplay`.

The output also goes to `videopodcast-magic.log` next to the script, with
version, time and machine in the header and a dividing line per run; the
previous run stays as `videopodcast-magic_1.log`. What Qt and ffmpeg write
past Python is in there too.

Beside **Start** runs **one bar for everything outstanding**, with a line
saying what is being worked on; it only ever moves forward. It covers
both halves: the measuring that follows every change to the file list,
and the run itself. That measuring takes in envelopes, camera audio,
channels and the check, and an envelope is the loudness over the length
of a track.

A step that reports a real percentage takes the bar with it. A step that
reports nothing lets the bar creep on slowly and stop short of the end.

### What Settings ... holds

The button **Settings ...** sits in the footer, next to **Start**. Behind
it stands what is set up once and then left alone: the key for
auphonic.com with the tick that stores it, and whether Resolve answers.
The preset and the transcript belong to the production being made and
stand where the tracks are decided, under the assignment table.

The window behind the button holds two boxes.

- **Access to auphonic.com**: the field for the API key and the tick that
  keeps it (**Save in Keychain** on a Mac, **Save in Registry** on
  Windows). **Connect** checks the key and fetches the presets.
- **Connection to Resolve**: whether Resolve answers, with its version if
  it does and the reasons if it does not. **Check again** asks once more,
  and so does opening the window.
  [DaVinci Resolve](resolve.md) says what a no means.

![The settings window](images/settings.png)

*Behind Settings ...: the key for auphonic.com, and whether Resolve
answers.*

## Reaching everything by menu or key

The menu bar carries four menus: **File**, **View**, **Player** and
**Help**. **Help** holds the way into this manual, **What changed in this
version**, **Look for a newer version now** and **About Video Podcast
Magic**.

On a Mac the menu bar sits at the top of the screen, everywhere else at
the top of the window. **Settings ...** moves into the application menu
there and stands under **File** everywhere else.

Everything reachable from a button is reachable from a key. The keys that
need no modifier belong to the player and only work while the player has
the focus.

| Key | What it does |
|---|---|
| `Ctrl+O` | Add files |
| `Ctrl+Backspace` | Remove what is selected |
| `Ctrl+Shift+O` | Choose the output folder |
| `Ctrl+R` | Start |
| `Ctrl+Shift+R` | Dry run |
| `Ctrl+1` `Ctrl+2` `Ctrl+3` | To that tab |
| `Ctrl+,` | Settings |

In the player:

| Key | What it does |
|---|---|
| `Space` | Play and pause |
| `L` | Play forward, twice as fast on every press |
| `K` | Pause, back to 1× |
| `Left` `Right` | One frame |
| `Shift+Left` `Shift+Right` | One second |
| `Alt+Left` `Alt+Right` | Ten seconds |
| `I` `O` | Set In point, set Out point |
| `Shift+I` `Shift+O` | Jump to In point, to Out point |

`L` doubles up to 8×, and the speed stands on the fast forward button.
The player has no `J`: Qt plays nothing backwards here, measured.

On a Mac, `Cmd` stands in place of `Ctrl`. This is the layout the editing
programs share.

## Keeping itself up to date

A moment after the window is up, the program asks github.com whether a
newer version is out. It looks only then, not while a run is going on.
That is one question for a version number.

If one is out, a window names it and the version running here. It shows
what changed in the new version, in its own words, and the address
underneath. Two buttons:

- **Later** leaves the version that is running in place.
- **Update** fetches the new version, puts it in place of the file and
  starts the program again.

The program reads what comes down before it uses it: it has to be
readable text, it has to look like this program, and it has to compile.
If one of the three fails, the file that works stays where it is and the
window says what was wrong.

The version that was running stays beside the new one as
`videopodcast-magic.py.old`. **Help > Back to 2.3.0-beta** puts it
back; the entry names the version out of that file and stands in the
menu only while the file is there.

It asks first, and the kept file has to pass the same three checks as
what comes down. Then the program starts again. That uses the file up,
and the way forward is the update over the network again.

The tick **Do not ask again** stops the program from looking by itself.
**Help > Look for a newer version now** still asks whenever it is
chosen.

## How the time axis is built without timecode

If a file carries no timecode, the interface measures in the background
where it sits, with the method of the run itself. The player then jumps
between files to the same point in what is happening, and In point and
Out point hold for all alike.

One timecode anywhere is enough to hang the axis on; without any it counts
from the start of the material and shows as a virtual timecode.

The axis goes into the project file, with size and modification time of
every file, and the next start takes it up again. Files that no longer
fit it show red. More about the project file stands in
[camera-cut.md](camera-cut.md).

## When something goes wrong

- **Start** stays locked: the line under the buttons names what is
  missing, and the field or the row it means turns red. Fill that in
  and the button frees itself.
- **The player shows no picture**: a button takes its place and hands the
  file to `ffplay`, which opens a window of its own.
- **In point and Out point are locked**: the program is still measuring
  the time axis. The bar beside **Start** says what is running.
- **The update did not go through**: the file that works stays where it
  is, and the window says what was wrong. **Help > Look for a newer
  version now** tries again.
- **Asking for help**: send the version from `--version`, the operating
  system, `videopodcast-magic.log` and what you were trying to do, before
  the details of the fault.

That is the whole window. The next chapter, [Preflight](preflight.md),
covers the checks before a run and the meaning of each mark in the file
list.

### Further options on the command line

The window does not offer these.

`--update-check` brings the unasked look back after the tick **Do not ask
again** was set.

`--no-update-check` sets the same no as that tick. A run from the command
line leaves the looking out anyway: started from a script, it must not
stop at a question.

`VPM_NO_UPDATE_CHECK` in the environment switches the whole thing off,
the menu entry with it. The entry then says so instead of looking. That
one is for whoever runs the machine.

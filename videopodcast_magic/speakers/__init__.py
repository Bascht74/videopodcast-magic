# -*- coding: utf-8 -*-
"""Who speaks, and when: separated, heard off the tracks, or read back.

Everything about a voice is here -- the separation, the microphones,
the names, a stored separation back on the axis, and what the window
shows of it. Which camera that puts on screen is the cut's.

A piece of the program, read by beside(). It cannot import the file it
was cut out of, so the program is handed in and bound below by name.
"""

# beside() puts the program here before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program, bound once. Missing: np
# below, and apply_time_window, choose_zero_point and cells_laid_out,
# whose files are read after this one.

# Ten more are read as PROGRAM.<name> at the place they are used: their
# files are read after this one. Out of cut/: as_minutes,
# camera_after_a_mark, wide_bar_of. Out of fittings/, which the window
# reads: mark_red, voice_row_cells.

# The last five are the window's own and can never be head lines here,
# because ui/ is the last piece read: SpeakerName, camera_tracks_of,
# camera_tracks_clashing, choices_shut, queue_once.

ByFile = PROGRAM.ByFile
CATALOGUE = PROGRAM.CATALOGUE
CLOSING_MARKS = PROGRAM.CLOSING_MARKS
COLOURS = PROGRAM.COLOURS
IGNORE_AUDIO = PROGRAM.IGNORE_AUDIO
MIX_ONLY = PROGRAM.MIX_ONLY
PIP_SOURCE = PROGRAM.PIP_SOURCE
SPEAKER_ROWS_SHOWN = PROGRAM.SPEAKER_ROWS_SHOWN
SR = PROGRAM.SR
T = PROGRAM.T
TN = PROGRAM.TN
TYPE_IGNORED = PROGRAM.TYPE_IGNORED
TYPE_INTRO = PROGRAM.TYPE_INTRO
TYPE_OUTRO = PROGRAM.TYPE_OUTRO
VERSION = PROGRAM.VERSION
Value = PROGRAM.Value
as_head = PROGRAM.as_head
as_hms = PROGRAM.as_hms
as_warn = PROGRAM.as_warn
assignment_pairs = PROGRAM.assignment_pairs
cache_folder = PROGRAM.cache_folder
camera_row_cameras = PROGRAM.camera_row_cameras
camera_to_remember = PROGRAM.camera_to_remember
clocks_apart = PROGRAM.clocks_apart
cut_box_title = PROGRAM.cut_box_title
cut_has_people = PROGRAM.cut_has_people
decode_audio = PROGRAM.decode_audio
ffprobe_json = PROGRAM.ffprobe_json
file_fingerprint = PROGRAM.file_fingerprint
file_timecode = PROGRAM.file_timecode
fix_table_width = PROGRAM.fix_table_width
folded_summary = PROGRAM.folded_summary
hashlib = PROGRAM.hashlib
how_many_processors = PROGRAM.how_many_processors
https_context = PROGRAM.https_context
json = PROGRAM.json
label_of = PROGRAM.label_of
math = PROGRAM.math
microphones_apart_db = PROGRAM.microphones_apart_db
multitrack_state_note = PROGRAM.multitrack_state_note
number_text = PROGRAM.number_text
os = PROGRAM.os
parallel_map = PROGRAM.parallel_map
path_key = PROGRAM.path_key
pip_repair = PROGRAM.pip_repair
re = PROGRAM.re
remove_quietly = PROGRAM.remove_quietly
row_picker_watch = PROGRAM.row_picker_watch
run_ffmpeg_with_progress = PROGRAM.run_ffmpeg_with_progress
running_from = PROGRAM.running_from
sample_count = PROGRAM.sample_count
sentences_of = PROGRAM.sentences_of
show_progress = PROGRAM.show_progress
speech_word = PROGRAM.speech_word
speech_words_done = PROGRAM.speech_words_done
speech_words_kick_off = PROGRAM.speech_words_kick_off
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
time = PROGRAM.time
timecode_seconds = PROGRAM.timecode_seconds
timecode_string = PROGRAM.timecode_string
tree_cell = PROGRAM.tree_cell
tree_field = PROGRAM.tree_field
tree_row = PROGRAM.tree_row
tree_row_of = PROGRAM.tree_row_of
tree_rows_fit = PROGRAM.tree_rows_fit
trouble_log = PROGRAM.trouble_log
video_facts = PROGRAM.video_facts
words_of_recording = PROGRAM.words_of_recording


# The program holds a stand-in for numpy until the first sum asks and
# binds the real module then -- which a copy taken up here would never
# see. So this asks the program instead, the same way.
class LateNumpy:
    """Stands in for the program's numpy until a sum wants it."""

    def __getattr__(self, name):
        global np
        got = getattr(PROGRAM.np, name)
        np = PROGRAM.np
        return got


np = LateNumpy()


#---------------------------------------------- Local speaker separation

# Who speaks when out of one recording everybody is audible on, not out
# of separate microphones -- that is speakers_from_tracks. Measured,
# 98.7 % of 45473 words land on the right person, raw file or mix.

# A process of its own, for two reasons: the packages pin versions this
# program should not have to follow, and a process can be broken off
# where a thread with a model inside it cannot.

SPEAKER_MODEL_NAME = "speaker-diarization-community-1"

# What the model was trained on; anything else is resampled inside it.
SPEAKER_SPLIT_RATE = 16000

# Widening by 0.2 s buys 4.2 points. 0.5 s is the F1 optimum for the
# boundaries but doubles the words falling to two speakers at once.
# Applied where the segments are used, never where they are stored.
SPEAKER_MARGIN_S = 0.2

# How wide a hole inside one speaker is still that speaker breathing.
# 0.75 s shows whoever really talks 83.6 % of the time against 73.0 %
# at 0.25 s, for six words of 10 158 wrong; from 1.0 s both get worse.
SPEAKER_GAP_S = 0.75

# On Apple Silicon with the graphics unit: an hour of audio in a little
# over two minutes. Gives the step its share of the bar.
SPEAKER_SPLIT_SPEED = 28.0

# From four processors upwards everything starts at once: the kinds of
# work do not slow each other down. Below that the prework is narrowed
# while the separation runs -- a full processor costs +10 to +34 %.
SPEAKER_SPLIT_TOGETHER_CORES = 4

# One at a time. Two raise throughput by 12 % and charge 1.75 times the
# wait for the first answer plus 4.5 GB for the second process, where a
# smaller machine starts swapping.
SPEAKER_SPLIT_TURN = threading.Semaphore(1)

# Where nothing may be fetched and nothing may compute for minutes
# unasked -- a test suite, a metered line -- this switches the
# separation off. It never starts by itself then; the button still does.
SPEAKER_SPLIT_OFF = bool(os.environ.get("VPM_NO_SPEAKER_SPLIT"))

# The mix auphonic.com writes is not offered as a source: it separates
# no better than the raw recording and exists only after an upload.
SPEAKER_SOURCE_MIX_ALLOWED = False


def media_seconds(file_path):
    """How long a file is. 0 where it cannot be asked."""
    try:
        return float(ffprobe_json(file_path).get("format", {})
                     .get("duration") or 0.0)
    except Exception:
        return 0.0

def clocks_not_set(paths):
    """Which of these files carry a timecode from a clock never set.

    The file whose timecode window overlaps none of the others; one
    without a timecode is not in the result. Returns path_key names.
    """
    spans = []
    for p in paths:
        try:
            t = file_timecode(p)
        except (OSError, ValueError, RuntimeError):
            t = None
        if t is not None:
            spans.append((float(t), media_seconds(p), path_key(p)))
    return clocks_apart(spans)[0]


def speaker_model_folder():
    """Return the folder holding the separation model, or "".

    It travels with the program: a folder is all the pipeline needs,
    with an empty HOME, no Hugging Face cache and no network.
    """
    # The program's own folder, one above this piece.
    here = os.path.dirname(running_from())
    folder = os.path.join(here, "models", SPEAKER_MODEL_NAME)
    return folder if os.path.isfile(
        os.path.join(folder, "config.yaml")) else ""


# The same repository the program comes from, so the two always match.
MODEL_BASE = ("https://raw.githubusercontent.com/Bascht74"
              "/videopodcast-magic/%s/videopodcast_magic/models/"
              + SPEAKER_MODEL_NAME + "/")
MODEL_MB = 33


def model_reference():
    """Which state of the repository the model is fetched from.

    The tag of this version, so program and model are never a version
    apart; off the main branch there is no such tag and the branch does.
    """
    return "v" + VERSION


def fetch_model(report=None, ref=""):
    """Fetch the separation model beside the program. "" when it worked.

    The SHA-256 sums are fetched first and every file held against them:
    one that does not match is not written, and no second list of files
    can drift from what the model is.
    """
    # The program's own folder, one above this piece.
    here = os.path.dirname(running_from())
    if not os.access(here, os.W_OK):
        return T('The folder of the program cannot be written to: %s') \
            % here
    import urllib.request
    base = MODEL_BASE % (ref or model_reference())

    def take(name):
        with urllib.request.urlopen(base + name,
                                    context=https_context(),
                                    timeout=120) as answer:
            return answer.read()

    try:
        raw = take("SHA256SUMS.txt")
    except Exception as e:
        if not ref:
            # No tag of that name: a run off the branch, not a release.
            return fetch_model(report, "main")
        return T('The model could not be fetched: %s') % e
    sums = {}
    for line in raw.decode("utf-8", "replace").splitlines():
        line = line.strip()
        parts = line.split()
        if line and not line.startswith("#") and len(parts) >= 2 \
                and len(parts[0]) == 64:
            sums[parts[-1]] = parts[0].lower()
    if not sums:
        return T('The list of model files came back empty.')
    folder = os.path.join(here, "models", SPEAKER_MODEL_NAME)
    done = 0
    for name in sorted(sums):
        if report:
            report(T('Fetching the model (about %s MB): %s')
                   % (number_text(MODEL_MB, 0), name),
                   0.05 + 0.9 * done / len(sums))
        try:
            data = take(name)
        except Exception as e:
            return T('The model could not be fetched: %s') % e
        if hashlib.sha256(data).hexdigest() != sums[name]:
            return T('%s does not match its checksum and was not '
                     'written.') % name
        where = os.path.join(folder, name.replace("/", os.sep))
        try:
            os.makedirs(os.path.dirname(where), exist_ok=True)
            beside = where + ".part"
            with open(beside, "wb") as f:
                f.write(data)
            os.replace(beside, where)
        except OSError as e:
            return T('The model could not be written: %s') % e
        done += 1
    # The licence and what it says about the model travel with it.
    for name in ("SHA256SUMS.txt", "LICENSE-CC-BY-4.0.txt",
                 "MODEL_CARD.md", "NOTICE.md"):
        try:
            data = raw if name == "SHA256SUMS.txt" else take(name)
            with open(os.path.join(folder, name), "wb") as f:
                f.write(data)
        except Exception:
            pass          # nice to have, not worth failing over
    return ""


def read_checksums(file_path):
    """Read a SHA256SUMS file: {file name: digest}.

    The plain format, digest and name separated by spaces: that is what
    shasum -c reads back.
    """
    out = {}
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(None, 1)
                if len(parts) == 2:
                    out[parts[1].strip().lstrip("*")] = parts[0].lower()
    except OSError:
        return {}
    return out


def file_digest(file_path):
    """The SHA-256 of a file, read in pieces."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            piece = f.read(1 << 20)
            if not piece:
                break
            h.update(piece)
    return h.hexdigest()


def speaker_model_checked(folder=""):
    """Hold every model file against its checksum before it is loaded.

    "" when all of them match, else the name of the first that does not:
    changed weights are not put into a process that decides who speaks.
    """
    folder = folder or speaker_model_folder()
    if not folder:
        return SPEAKER_MODEL_NAME
    sums = read_checksums(os.path.join(folder, "SHA256SUMS.txt"))
    if not sums:
        return "SHA256SUMS.txt"
    for name in sorted(sums):
        here = os.path.join(folder, name)
        try:
            if file_digest(here) != sums[name]:
                return name
        except OSError:
            return name
    return ""


def speaker_model_mark(folder=""):
    """A short mark for the model, so a changed one is measured again.

    Out of the checksum file, which names every weight and its digest:
    a different model marks differently without reading a gigabyte.
    """
    folder = folder or speaker_model_folder()
    if not folder:
        return ""
    try:
        with open(os.path.join(folder, "SHA256SUMS.txt"), "rb") as f:
            raw = f.read()
    except OSError:
        return ""
    return hashlib.sha1(raw).hexdigest()[:12]


#------------------------------------------------------ The environment

# What the separation stands on, named because a repair has to name
# it. torchvision is pulled in anyway; without it torchmetrics dies at
# a name it never uses, so a repair that leaves it out repairs nothing.
SPEAKER_PACKAGES = ("pyannote.audio", "torchvision")

# One attempt in a run, and this list is what holds it: a second
# recording must not start the same install over again.
_SPEAKER_MENDED = []


def speaker_split_missing():
    """The one sentence for "it cannot run here", with the way back.

    One place, so the console, the window and the dry run cannot say
    three different things about the same fault.
    """
    return T('The speaker separation is not installed here. This puts '
             'it back: %s') % ("pip3 install -U " + PIP_SOURCE)


def speaker_python():
    """The interpreter the separation runs in: this one.

    pyannote stands on the list pip reads, so it is here already. The
    separate *process* stays: the telemetry switch has to be thrown
    before anything else, and a crash inside torch must not take the
    window with it.
    """
    return sys.executable
def forget_speaker_split():
    """Ask again whether the separation can run, and mend it again too.

    Everything this run knew about the separation is void, the one
    attempt at a repair with it: whoever throws the answer away is
    saying the ground under it has moved.
    """
    PROGRAM._SPEAKER_READY, PROGRAM._SPEAKER_WHY = None, ""
    del _SPEAKER_MENDED[:]


def speaker_split_why():
    """What the import really said when it failed, or "".

    The one line naming the fault, out of whatever the other process
    wrote: without it the window can only guess, and "not installed" is
    the wrong guess for an import that fell over a library beside it.
    """
    speaker_split_available()
    return PROGRAM._SPEAKER_WHY


def speaker_split_available(deep=False):
    """Say whether the separation can run. Measured, not assumed.

    The import is really done, in a process of its own: nothing else
    answers the question. *deep* asks again from scratch rather than
    reading the answer kept in this run.
    """
    if deep:
        PROGRAM._SPEAKER_READY = None
    if PROGRAM._SPEAKER_READY is None:
        try:
            p = subprocess.run([speaker_python(), "-c",
                                "import pyannote.audio"],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.PIPE)
            PROGRAM._SPEAKER_READY = p.returncode == 0
            # The last line of a traceback is the exception itself;
            # the frames above it are pyannote's own imports.
            said = (p.stderr or b"").decode("utf-8", "replace").strip()
            PROGRAM._SPEAKER_WHY = "" \
                if PROGRAM._SPEAKER_READY or not said \
                else said.splitlines()[-1].strip()
        except OSError as e:
            PROGRAM._SPEAKER_READY, PROGRAM._SPEAKER_WHY = \
                False, str(e)
    return PROGRAM._SPEAKER_READY


def speaker_split_mend(say=None):
    """One attempt in this run to put the separation back. True where it runs.

    pip is given the packages the separation stands on, and then the
    question is put again from scratch: an install that reported
    success proves nothing until the import really goes through. The
    list above holds it to one attempt, so a machine with no way in
    does not spend the same minutes on every recording.
    """
    if _SPEAKER_MENDED:
        return speaker_split_available()
    _SPEAKER_MENDED.append(True)
    if say:
        say(T('Putting the speaker separation back ...'), 0.02)
    if not pip_repair(SPEAKER_PACKAGES):
        return speaker_split_available()
    return speaker_split_available(deep=True)


def speaker_split_trouble():
    """What a separation that cannot run says: a short line, then the whole.

    Two texts in one, parted at the line break. The first is what fits
    in the cell of a row, which is one line wide; under it goes the
    sentence with the command that puts it back, for the line under
    the table where there is room. The reason itself, uncut, is in the
    log.
    """
    why = speaker_split_why()
    return ((T('The speaker separation reports: %s') % why[:80]) if why
            else T('The speaker separation is not set up.')) \
        + "\n" + speaker_split_missing()


#------------------------------------------------------- The worker

# What runs in the other process, in a file so that a failure has a
# line number. Its first act, before any pipeline exists, is to switch
# pyannote's telemetry off; without that switch it refuses to run.
SPEAKER_SPLIT_WORKER = r'''"""Run one speaker separation and report it.

Reads a header line and then the raw waveform from standard input,
writes progress to standard error and the segments to standard output.
"""
import json
import os
import sys


def hush():
    """Switch off what pyannote would send home. "" when it is off.

    Two different things can go wrong here and they used to come back
    as one word. The package may not load at all -- a dependency of a
    dependency taken out by hand, say -- and then what comes back is
    that error, so the sentence names it. Or it loads and has no such
    switch, and then the refusal stands and "telemetry" is the truth.
    """
    loaded, first = False, ""
    for where in ("pyannote.audio.telemetry", "pyannote.audio"):
        try:
            mod = __import__(where, fromlist=["set_telemetry_metrics"])
        except Exception as e:
            first = first or "%s: %s" % (e.__class__.__name__, e)
            continue
        loaded = True
        switch = getattr(mod, "set_telemetry_metrics", None)
        if switch is not None:
            switch(False)
            return ""
    return "telemetry" if loaded else (first or "telemetry")


def read_header():
    """Read one line off the raw stream, before any waveform."""
    line = b""
    while not line.endswith(b"\n"):
        piece = sys.stdin.buffer.read(1)
        if not piece:
            return None
        line += piece
    return json.loads(line.decode("utf-8"))


def say(text):
    sys.stderr.write(text + "\n")
    sys.stderr.flush()


def main():
    trouble = hush()
    if trouble:
        print(json.dumps({"error": trouble}))
        return 3
    head = read_header()
    if not head:
        return 2
    raw = sys.stdin.buffer.read(int(head["samples"]) * 4)
    import numpy
    import torch
    from pyannote.audio import Pipeline
    wave = numpy.frombuffer(raw, dtype="<f4").copy()
    piece = torch.from_numpy(wave).reshape(1, -1)
    pipeline = Pipeline.from_pretrained(head["model"])
    # The graphics unit is what makes this 28 times real time. Where
    # there is none the processor does it, slower and not wrongly.
    for name, there in (("mps", lambda: torch.backends.mps.is_available()),
                        ("cuda", lambda: torch.cuda.is_available())):
        try:
            if there():
                pipeline.to(torch.device(name))
                say("D\t%s" % name)
                break
        except Exception:
            continue

    def hook(step, artifact=None, file=None, total=None, completed=None):
        say("P\t%s\t%s\t%s" % (step, completed or 0, total or 0))

    asked = {}
    if int(head.get("speakers") or 0) > 0:
        asked["num_speakers"] = int(head["speakers"])
    # The waveform, not the path: torchcodec cannot load the ffmpeg
    # libraries on every machine, and the audio is already decoded
    # here.
    out = pipeline({"waveform": piece,
                    "sample_rate": int(head["sample_rate"])},
                   hook=hook, **asked)
    # pyannote 4 hands back a DiarizeOutput and keeps the annotation in
    # its speaker_diarization field; up to 3 the pipeline returned the
    # annotation itself. Measured on 4.0.7, where the object carries
    # speaker_diarization, exclusive_speaker_diarization and
    # speaker_embeddings. Asking beats pinning a version: the worker
    # installs whatever pip offers that day, and a program that dies on
    # the newest release of its own dependency is a program that dies
    # in a year.
    turns = out if hasattr(out, "itertracks") else getattr(
        out, "speaker_diarization", None)
    if turns is None or not hasattr(turns, "itertracks"):
        raise RuntimeError(
            "pyannote returned %s, and nothing in it answers to "
            "itertracks" % type(out).__name__)
    segments = []
    for turn, _track, label in turns.itertracks(yield_label=True):
        segments.append([str(label), round(float(turn.start), 3),
                         round(float(turn.end), 3)])
    print(json.dumps({"segments": segments}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def speaker_worker_file():
    """Write the worker out once and return where it is.

    Its name marks its source: a changed program never runs the old one.
    """
    folder = cache_folder("pyannote")
    if not folder:
        return ""
    mark = hashlib.sha1(
        SPEAKER_SPLIT_WORKER.encode("utf-8")).hexdigest()[:12]
    here = os.path.join(folder, "worker_%s.py" % mark)
    if not os.path.exists(here):
        fd, beside = tempfile.mkstemp(dir=folder, prefix=".vpm_",
                                      suffix=".py")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(SPEAKER_SPLIT_WORKER)
        os.replace(beside, here)
    return here


def speaker_split_run(path, num_speakers=0, report=None,
                      stopping=None):
    """Work out who speaks when in one file, on this machine.

    Returns (segments, "") raw and in the file's own time -- [(label,
    [(from, to), ...])], no widened edges, no closed gaps -- so a later
    change of offset, window or edge costs nothing. ([], sentence)
    where it could not run; *stopping* ends the run when it answers
    true.
    """
    folder = speaker_model_folder()
    if not folder:
        # Fetched once, beside the program, where it stays: whoever
        # installed pyannote and torch has the far larger part already,
        # so the 33 MB of the model need no second question.
        if report:
            report(T('Fetching the model (about %s MB) ...')
                   % number_text(MODEL_MB, 0), 0.02)
        trouble = fetch_model(report)
        if trouble:
            return [], trouble
        folder = speaker_model_folder()
    if not folder:
        return [], T('The speaker separation model is not beside the '
                     'program.')
    wrong = speaker_model_checked(folder)
    if wrong:
        return [], T('The model file %s does not match its checksum.') \
            % wrong
    python = speaker_python()
    worker = speaker_worker_file()
    if not python or not worker:
        return [], T('The speaker separation is not set up.')
    if report:
        report(T('Reading the audio ...'), 0.02)
    try:
        wave = decode_audio(path, SPEAKER_SPLIT_RATE, dtype=np.float32)
    except Exception as e:
        return [], T('The speaker separation reports: %s') % str(e)[:140]
    if not len(wave):
        return [], T('Nothing was audible in the recording.')
    head = json.dumps({"model": folder,
                       "sample_rate": SPEAKER_SPLIT_RATE,
                       "samples": int(len(wave)),
                       "speakers": int(num_speakers or 0)})
    clean = dict(os.environ)
    clean.pop("AUPHONIC_TOKEN", None)
    # Belt and braces: the folder branch never asks a server anyway.
    clean["HF_HUB_OFFLINE"] = "1"
    # One at a time: a second costs 4.5 GB for 12 % more throughput.
    with SPEAKER_SPLIT_TURN:
        if stopping and stopping():
            return [], ""
        return _speaker_split_talk(python, worker, head, wave, clean,
                                   report, stopping)


def _speaker_split_talk(python, worker, head, wave, environment,
                        report, stopping):
    """Start the worker, feed it the waveform and read it out."""
    seconds = len(wave) / float(SPEAKER_SPLIT_RATE)
    try:
        proc = subprocess.Popen([python, worker], stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=environment)
    except OSError as e:
        return [], T('The speaker separation reports: %s') % e
    trouble, device = [], []

    def listen():
        """Read what the worker says about how far it is."""
        for line in proc.stderr:
            text = line.decode("utf-8", "replace").rstrip()
            parts = text.split("\t")
            if parts[0] == "D":
                device.append(parts[-1])
            elif parts[0] == "P":
                share = 0.0
                try:
                    if float(parts[3]) > 0:
                        share = float(parts[2]) / float(parts[3])
                except (ValueError, IndexError):
                    share = 0.0
                if report:
                    report(T('Separating ...'),
                           0.05 + 0.9 * max(0.0, min(1.0, share)))
            elif text:
                trouble.append(text)

    watcher = threading.Thread(target=listen, daemon=True)
    watcher.start()
    try:
        proc.stdin.write(head.encode("utf-8") + b"\n")
        proc.stdin.write(wave.tobytes())
        proc.stdin.close()
    except (OSError, ValueError):
        pass
    answer = []

    def collect():
        answer.append(proc.stdout.read())

    reader = threading.Thread(target=collect, daemon=True)
    reader.start()
    # Asked rather than waited on, so a cancel takes effect within a
    # fraction of a second instead of at the end of three minutes.
    while proc.poll() is None:
        if stopping and stopping():
            proc.terminate()
            return [], ""
        time.sleep(0.2)
    reader.join(5.0)
    watcher.join(5.0)
    raw = (answer[0] if answer else b"").decode("utf-8", "replace")
    line = (raw.strip().splitlines() or [""])[-1]
    try:
        d = json.loads(line)
    except ValueError:
        d = {}
    if d.get("error") == "telemetry":
        return [], T('pyannote sends a trace home on every run and this '
                     'version offers no way to switch it off, so the '
                     'separation was not started.')
    if d.get("error"):
        # Anything else the worker refused on is its own error, and it
        # is handed on as it stands: a package that will not load says
        # which name it died at, and that is what a repair needs.
        return [], T('The speaker separation reports: %s') \
            % str(d["error"])[:160]
    if proc.returncode != 0 or "segments" not in d:
        note = (trouble or [""])[-1]
        return [], T('The speaker separation reports: %s') % note[:160]
    # What it ran on, not what it should have run on: on the processor
    # the same file takes many times as long, and that belongs in the
    # log beside the time it took.
    found = len(set(x[0] for x in d["segments"]))
    print(TN(found,
             '  Speaker separation (%s): %s speaker out of %s of audio',
             '  Speaker separation (%s): %s speakers out of %s of audio')
          % (device[-1] if device else "cpu", number_text(found, 0),
             as_hms(seconds)))
    return speaker_segments_group(d["segments"]), ""


def speaker_segments_group(rows):
    """Turn [label, from, to] rows into [(label, [(from, to), ...])].

    In order of speaking time, longest first: that is the order the
    voices are numbered in.
    """
    per = {}
    for row in rows or ():
        # Read first, then filed, or an entry made before the numbers
        # are known leaves behind a speaker who never spoke.
        try:
            stretch = (round(float(row[1]), 3), round(float(row[2]), 3))
        except (TypeError, ValueError, IndexError):
            continue
        per.setdefault(str(row[0]), []).append(stretch)
    for label in per:
        per[label].sort()
    return sorted(per.items(),
                  key=lambda x: -sum(b - a for a, b in x[1]))


#--------------------------------------------------------- Arithmetic

def speaker_segments_polish(segments, margin=SPEAKER_MARGIN_S,
                            gap=SPEAKER_GAP_S):
    """Widen the edges and close the small gaps inside one speaker.

    Worth 4.2 points on the assignment of words to people: a recogniser
    reports a word a tenth of a second late and the separation stops
    before the sound dies away. Nothing moves before zero. Arithmetic
    on the stored measurement, so it happens where the segments are
    used.
    """
    out = []
    for label, parts in segments or ():
        wide = sorted((max(0.0, a - margin), b + margin)
                      for a, b in parts)
        joined = []
        for a, b in wide:
            if joined and a - joined[-1][1] <= gap:
                joined[-1] = (joined[-1][0], max(joined[-1][1], b))
            else:
                joined.append((a, b))
        out.append((label, [(round(a, 3), round(b, 3))
                            for a, b in joined]))
    return out


def voices_in_use(segments, ignored=()):
    """The voices minus the ones somebody set to "do not use".

    "Do not use" makes a voice as good as not there: it goes out of the
    passages and not only of the names, so the picture holds whoever it
    was on until the next voice that counts. The separation itself
    stays whole in the project file -- switching the voice back on must
    not cost the three minutes of computing again.
    """
    ignored = set(ignored or ())
    if not ignored:
        return list(segments)
    return [(label, parts) for label, parts in segments
            if label not in ignored]


def voice_key(source, label):
    """The name one voice is remembered under: recording and label.

    The model calls the first voice of every recording SPEAKER_00, so
    the label alone is not a name and two recordings would read each
    other's names and cameras back. A newline stands in no path and in
    no label, so the two parts always come apart again.
    """
    return "%s\n%s" % (os.path.abspath(source), label) if source else label


def voice_key_parts(key):
    """(recording, label) out of such a name; a bare label has none."""
    source, _sep, label = str(key or "").rpartition("\n")
    return source, label


# What the table remembers about one file, by the head of the key. A
# recording's voices are remembered under it, and struck with it.
REMEMBERED_PER_FILE = ("audio", "kind", "own", "ownname", "several", "video")
REMEMBERED_PER_VOICE = ("voice", "voicename")


def remembered_forget(remembered, gone):
    """Strike what the table remembers about files that have left.

    The table is redrawn out of this store and the project written out
    of it, so whatever stays here comes back with the file. *gone* are
    the paths that left.
    """
    gone = set(path_key(p) for p in (gone or ()) if p)
    struck = []
    if not gone:
        return struck
    for api_key in list(remembered or {}):
        head, _sep, rest = str(api_key).partition(":")
        if not rest:
            continue
        if head in REMEMBERED_PER_FILE:
            path = rest
        elif head in REMEMBERED_PER_VOICE:
            path = voice_key_parts(rest)[0]
        else:
            continue
        if path and path_key(path) in gone:
            remembered.pop(api_key, None)
            struck.append(api_key)
    return struck


def voice_lines_here(voice_lines, source=""):
    """The rows of *voice_lines* that belong to one recording.

    Without a recording named, all of them.
    """
    if not source:
        return list(voice_lines or ())
    want = os.path.abspath(source)
    out = []
    for row in voice_lines or ():
        mine, _label = voice_key_parts(row[0])
        here = os.path.abspath(mine) if mine else ""
        if not here or here == want:
            out.append(row)
    return out


def voice_lines_here_not(voice_lines, source):
    """The rows of *voice_lines* that belong to any other recording.

    What a recording is named against: its own old rows would stand in
    the way of naming its new voices.
    """
    mine = set(id(row) for row in voice_lines_here(voice_lines, source))
    return [row for row in voice_lines or () if id(row) not in mine]


def voices_ignored_of(voice_lines, source=""):
    """The voices somebody set to "do not use", by their label.

    In the labels of the separation itself, not the keys the rows
    carry: this is held against a list of passages, where a voice is
    called SPEAKER_00.
    """
    return set(voice_key_parts(key)[1]
               for key, _nv, cv in voice_lines_here(voice_lines, source)
               if cv.get() == IGNORE_AUDIO)


def voice_names_of(named, voice_lines, source=""):
    """The names of the voices in use, with what was just typed in.

    A voice set to "do not use" has no name here: the name is what
    becomes a track and a speaker at auphonic.com. *named* and the
    answer are in one recording's labels, so *source* says whose rows
    are read.
    """
    ignored = voices_ignored_of(voice_lines, source)
    out = {k: v for k, v in dict(named or {}).items() if k not in ignored}
    for key, name_value, _cv in voice_lines_here(voice_lines, source):
        label = voice_key_parts(key)[1]
        if label not in ignored and name_value.get().strip():
            out[label] = name_value.get().strip()
    return out


def sheet_speaker_names(assign_lines=(), voice_lines=(), voiced=()):
    """Every speaker name the assignment sheet holds, in one list.

    One entry per person, whichever of the four ways they came in by. A
    recording whose voices stand under it says "several speakers" and
    not a name, so its voices speak for it; one set to "do not use"
    takes no part in the run and none here.
    """
    shown = set(path_key(p) for p in voiced or ())
    out = []
    for chain, name_value, camera_value in assign_lines or ():
        if camera_value.get() == IGNORE_AUDIO \
                or path_key(chain[0]) in shown:
            continue
        out.append(name_value.get())
    for _key, name_value, camera_value in voice_lines or ():
        if camera_value.get() != IGNORE_AUDIO:
            out.append(name_value.get().strip())
    return [n for n in out if n]


def names_used_twice(assign_lines=(), voice_lines=(), voiced=()):
    """The names standing more than once on the assignment sheet.

    A name is a person and a person is on the sheet once: two of one
    name reach the cut as one person, and their camera stands twice.
    """
    names = sheet_speaker_names(assign_lines, voice_lines, voiced)
    return sorted(set(n for n in names if names.count(n) > 1))


def voice_names_clashing(assign_lines=(), voice_lines=(), voiced=()):
    """The names of that sort a voice carries.

    Two recordings of one person merge into one track by design, so a
    name twice there is a question and not a refusal. A voice cannot
    merge with anything, so its name has to be its own.
    """
    twice = set(names_used_twice(assign_lines, voice_lines, voiced))
    return sorted(set(nv.get().strip() for _k, nv, cv in voice_lines or ()
                      if cv.get() != IGNORE_AUDIO
                      and nv.get().strip() in twice))


def speakers_on_window_axis(segments, offset, named=None):
    """The separation under its names, moved onto the shared axis.

    The offset and the widened edges are applied here, where it is
    used, so a later change of offset costs no measurement. Returns
    (speakers, how long the last of them runs).
    """
    out = [((named or {}).get(label) or label, parts)
           for label, parts in speaker_segments_on_axis(
               speaker_segments_polish(segments), offset)]
    return out, max((b for _n, parts in out for _a, b in parts),
                    default=0.0)


def track_recordings_of(assign_lines):
    """Which recording each track that still speaks was measured off.

    Every row but "do not use" -- a track with no camera of its own
    speaks too. The names are the ones speaker_measure gives, so both
    ends of the measurement agree without a second list.
    """
    out = {}
    for row, name_value, camera_value in assign_lines or ():
        if camera_value.get() == IGNORE_AUDIO:
            continue
        out.setdefault(name_value.get()
                       or os.path.basename(row[0]), []).append(row[0])
    return out


def speakers_window_all(voices, length, measured, where_from, separated=()):
    """The separations' voices and every track no separation covers.

    The same sum speakers_for_the_cut makes, so the preview shows the
    cut the run makes. *where_from* says which recording each measured
    track came off; one taken apart is in already, through its voices.
    """
    apart = set(path_key(p) for p in separated or () if p)
    out = list(voices or ())
    for name, parts in ((measured or {}).get("segments") or ()):
        # A name with no row behind it is nobody: set to "do not use"
        # after it was measured.
        paths = (where_from or {}).get(name)
        if paths and not any(path_key(p) in apart for p in paths if p):
            out.append((name, list(parts)))
    out = voices_merged(out)
    return out, max([length or 0.0]
                    + [b for _n, parts in out for _a, b in parts])


def tracks_awaiting_measure(where_from, measured, separated=()):
    """The tracks no separation covers and no measurement has reached.

    They are in the cut, but the preview cannot show them until the
    button has been pressed, so it names who is missing rather than
    showing a cut without them.
    """
    apart = set(path_key(p) for p in separated or () if p)
    heard = set(n for n, _p in ((measured or {}).get("segments") or ()))
    return sorted(name for name, paths in (where_from or {}).items()
                  if name not in heard
                  and not any(path_key(p) in apart for p in paths if p))


def speakers_all_on_window_axis(state, voice_lines, assign_lines,
                                offset_of):
    """Every separation the window holds, on the window's own axis.

    Each with the offset of its own recording, then folded by name: a
    preview computed from other voices than the run uses is worse than
    none. *offset_of* says where one recording lies on the axis.
    Returns (voices, how long the last of them runs).
    """
    begin = min([offset_of(row[0]) for row, _n, cv in assign_lines or ()
                 if cv.get() != IGNORE_AUDIO and os.path.exists(row[0])]
                or [0.0])
    out, length = [], 0.0
    for src, entry in sorted((state.get("speakers_by") or ByFile()).items()):
        if not voice_lines_here(voice_lines, src):
            continue
        rows, far = speakers_on_window_axis(
            voices_in_use(entry.get("segments") or (),
                          voices_ignored_of(voice_lines, src)),
            offset_of(src) - begin,
            voice_names_of(entry.get("names") or {}, voice_lines, src))
        out += rows
        length = max(length, far)
    return voices_merged(out), length


def speaker_segments_on_axis(segments, offset, t0=None, t1=None):
    """Move segments from the time of their file onto the common axis.

    *offset* is where that file begins. With *t0* and *t1* the result
    is cut to that window and counted from its start. Speech from
    before the episode falls out here, so the number of speakers shown
    is read off this result and not off the raw run.
    """
    out = []
    for label, parts in segments or ():
        kept = []
        for a, b in parts:
            a, b = a + offset, b + offset
            if t0 is not None:
                a, b = max(a, t0), min(b, t1 if t1 is not None else b)
            if b > a:
                kept.append((round(a - (t0 or 0.0), 3),
                             round(b - (t0 or 0.0), 3)))
        if kept:
            out.append((label, kept))
    return out


def voice_name_free(name, taken=()):
    """The name a voice shows: its own, or the first number nobody has.

    A name somebody typed stands, whatever else is on the sheet -- the
    field says so itself where two are the same. Only the numbered
    stand-in counts on, and it counts across every separation: to the
    cut, two voices of one name are one person.
    """
    name = str(name or "").strip()
    used = set(str(x).strip() for x in taken or () if str(x or "").strip())
    if name and not (is_stand_in_name(name) and name in used):
        return name
    n = 1
    while T('Speaker %d') % n in used:
        n += 1
    return T('Speaker %d') % n


def speaker_label_names(segments, called=None, taken=()):
    """Name the voices: whoever spoke most is the first one.

    A name given by hand stays, keyed by the model's label: renaming
    somebody is no reason to measure again. *taken* are the names
    already given elsewhere in the window, and the stand-in counts
    past them.
    """
    called = called or {}
    used = set(taken or ()) | set(called.values())
    out = []
    for label, _parts in segments or ():
        name = voice_name_free(called.get(label), used)
        used.add(name)
        out.append((label, name))
    return out


def segments_per_camera(segments, where_to, names=None):
    """Fold the speakers onto their cameras: either of them counts.

    Two people on one camera are one condition: a rule about that
    camera holds as soon as one of them speaks, so their segments merge
    into one series. *where_to* is {speaker name: camera}; a track left
    out contributes nothing. Returns [(camera, [(from, to), ...])].
    """
    names = dict(names or {})
    per = {}
    for label, parts in segments or ():
        who = names.get(label, label)
        camera = (where_to or {}).get(who)
        if not camera or camera == IGNORE_AUDIO:
            continue
        per.setdefault(camera, []).extend(parts)
    out = []
    for camera in sorted(per):
        joined = []
        for a, b in sorted(per[camera]):
            if joined and a <= joined[-1][1]:
                joined[-1] = (joined[-1][0], max(joined[-1][1], b))
            else:
                joined.append((a, b))
        out.append((camera, joined))
    return out


def speaker_split_wanted(asked):
    """May the separation run by itself? True, False, or unasked.

    On a Mac it runs unasked: the graphics unit does an hour of audio
    in two minutes. Elsewhere the answer is asked for once, on the line
    itself rather than in a dialogue, and then remembered in the
    project file; *asked* is that answer, None while nobody was asked.
    """
    if SPEAKER_SPLIT_OFF:
        return False
    if asked is not None:
        return bool(asked)
    return True if sys.platform == "darwin" else None


def split_line_write(line, words, never, wanted, busy, any_files,
                     note=None):
    """The line under the assignment table -- and mostly nothing at all.

    It speaks where this machine does not work the separation out on
    its own -- somebody said no, or nobody has been asked, and there
    the question and its button are the point of it -- and where a
    separation could not run: that reason belongs here, not in the
    cell it happened in, which is one line wide. Otherwise it says
    nothing, the state standing in each recording's own row.
    """
    if SPEAKER_SPLIT_OFF:
        line.setVisible(False)
        return
    # Everything below the note's first line. The cell takes the
    # first line; what does not fit there is what stands here.
    said = "\n".join((note[1] if note else "").split("\n")[1:]).strip()
    never.setVisible(wanted is None and not busy)
    if said:
        words.setText(said)
        words.setStyleSheet("color: %s" % note[2])
        line.setVisible(True)
        return
    if wanted is True:
        line.setVisible(False)
        return
    line.setVisible(bool(any_files))
    words.setStyleSheet("color: %s" % COLOURS["quiet"])
    words.setText(T('Speaker separation is switched off for this project.')
                  if wanted is False else
                  T('Who speaks when can be worked out on this machine, '
                    'from any one recording everybody is audible on.'))


def tc_column_write(rows, real_tc, axis, absolute):
    """Fill the timecode column of the assignment tree.

    The measurement stands there, having held every file against the
    others; only where nothing was measured does the timecode speak.
    *rows* is one entry per recording -- its row in the tree, the file,
    the plain caption -- and not one per row: a voice has no timecode.
    Returns False where the tree is gone, built again meanwhile.
    """
    import PySide6.QtGui as _qg
    for row, p, _plain in rows:
        if not p:
            continue
        t, kind = (axis or {}).get(path_key(p)), ""
        if t is not None:
            kind = T(' computed') if absolute else T(' virtual')
        else:
            t = real_tc(p)
        if t is None:
            text, colour = T('no timecode'), COLOURS["quiet"]
        else:
            text = timecode_string(t) + kind
            colour = COLOURS["value"] if not kind else COLOURS["heading"]
        try:
            row[3].setText(text)
            row[3].setForeground(_qg.QBrush(_qg.QColor(colour)))
        except RuntimeError:
            return False
    return True


def weak_decision(kind):
    """What became of a file with no place, in the words on the screen.

    The program moves such a file off content and the wide shot at the
    moment it finds it, so a line that only complains stands beside a
    row that already says something else, and the two read as a
    contradiction. *kind* is what the row says now.
    """
    if kind == TYPE_INTRO:
        return T('Set to %s; %s is one click away.') \
            % (label_of(TYPE_INTRO), label_of(TYPE_OUTRO))
    if kind == TYPE_IGNORED:
        return T('Left out, %s being taken already; %s is one click '
                 'away.') % (label_of(TYPE_INTRO), label_of(TYPE_OUTRO))
    return T('Its sound cannot be used.')


def weak_note(caption, placeless, kind=""):
    """What a file whose sound was not recognised says beside its name.

    Two ways lead to a place and one is enough: with a timecode only
    the second opinion is missing, without one there is no place at
    all and its sound is out of the run. Then the finding comes first
    and what was done about it under it.
    """
    if placeless:
        return T('%s\n   does not fit the other files: sound not '
                 'recognised, no timecode.\n   %s') \
            % (caption, weak_decision(kind))
    return T('%s\n   sound not recognised; placed by its timecode') \
        % caption


def weak_kind(kinds, path):
    """What the Kind field of that file says now, or "" where none does."""
    value = (kinds or ByFile()).get(path)
    return value.get() if value is not None else ""


def weak_colour(odd, placeless):
    """The colour a badly fitting file is written in."""
    if placeless:
        return COLOURS["error"]
    return COLOURS["warning"] if odd else COLOURS["text"]


def weak_nodes_mark(nodes, weak, no_place=(), kinds=None):
    """Mark the rows of the file list that do not fit the time axis.

    Usually picked by mistake, out of another recording. *no_place* are
    the ones no timecode places either: those are refused, the rest
    only warned about. *kinds* says what each was set to instead.
    Returns the rows that are gone.
    """
    import PySide6.QtGui as _qg
    nowhere = set(no_place or ())
    dropped = []
    for p, item in list(nodes.items()):
        placeless = path_key(p) in nowhere
        odd = path_key(p) in weak or placeless
        ink = _qg.QBrush(_qg.QColor(weak_colour(odd, placeless)))
        try:
            # Column 1 keeps the check mark: two inks in one cell
            # overwrite each other, whichever ran last.
            for column in (0, 2):
                item.setForeground(column, ink)
            if odd:
                item.setText(2, weak_note(os.path.dirname(p), placeless,
                                          weak_kind(kinds, p)))
        except RuntimeError:
            dropped.append(p)
    return dropped


def weak_marks_show(state, nodes):
    """Say on both sheets which files do not fit the time axis.

    One call for the two, so the file list and the assignment tree
    cannot say different things about one file. Returns the rows that
    are gone.
    """
    weak = state.get("weak") or ()
    nowhere = state.get("no_place") or ()
    # What the Kind field of each file says now, so the note can name
    # the decision the program has already taken on that file.
    kinds = state.get("clip_kinds")
    dropped = weak_nodes_mark(nodes, weak, nowhere, kinds)
    weak_rows_mark(state.get("file_rows") or (), weak, nowhere, kinds)
    return dropped


def weak_rows_mark(rows, weak, no_place=(), kinds=None):
    """The same mark on the recordings of the assignment tree.

    *rows* is (its row in the tree, the file, the plain caption), one
    per recording; the voices under it carry no mark, the question
    being about the recording. The camera rows carry none either: every
    note about a file stands on the first sheet, where the files are
    chosen, and repeating it here in red is an accusation, not news.
    """
    import PySide6.QtGui as _qg
    nowhere = set(no_place or ())
    for row, p, plain in rows:
        if not p:
            continue
        placeless = path_key(p) in nowhere
        odd = path_key(p) in weak or placeless
        ink = _qg.QBrush(_qg.QColor(weak_colour(odd, placeless)))
        try:
            for cell in row:
                cell.setForeground(ink)
            # Colour carries nothing to anybody who cannot see it, so
            # the first cell says it in words too. The plain caption
            # travels beside the row, or a second pass nests sentences.
            said = plain
            if odd:
                said = weak_note(plain, placeless, weak_kind(kinds, p))
            row[0].setText(said)
            # The column can be narrower than the sentence.
            row[0].setToolTip(said if odd else "")
        except RuntimeError:
            # The tree has been built again and its rows went with it.
            return


def separations_of(by_source, path):
    """What was separated out of that one recording, or nothing.

    *by_source* is the store the window keeps, one entry per recording
    taken apart. Asking by the recording is what keeps two of them
    apart, rather than the second emptying the first one's rows.
    """
    entry = (by_source or ByFile()).get(path or "") or {}
    return list(entry.get("segments") or ())


def speakers_stored(state, source):
    """One recording's separation as the window holds it.

    {"segments": …, "count": …, "names": …}, or nothing.
    """
    return (state.get("speakers_by") or ByFile()).get(
        source or "") or {}


def speakers_keep(state, source, segments, count, names):
    """Store what was heard in one recording, and put it in front.

    Every recording keeps its own: the names hang on the model's labels
    and cannot be put back by hand once they have been carried over to
    another recording's voices. In front is what the run and the
    preview read.
    """
    by = state.setdefault("speakers_by", ByFile())
    by[source] = {
        "segments": list(segments or ()),
        "count": int(count or 0), "names": dict(names or {})}
    state["speakers_source"] = source
    state["speakers_local"] = list(segments or ())
    state["speakers_count"] = int(count or 0)


def speakers_block_of(state, voice_lines=None):
    """Every separation the window holds, in the shape they travel in.

    The one in front stands where a single separation always stood, so
    a version that knows of one still opens the file; the others hang
    under it in "more". None where nothing was separated. With
    *voice_lines* only what stands on the sheet goes, without the
    voices set to "do not use" -- the run's view, not the file's.
    """
    by = state.get("speakers_by") or ByFile()
    front = state.get("speakers_source") or ""
    keep = [src for src in sorted(by) if by[src].get("segments")]
    if voice_lines is not None:
        # No rows: set to "do not use", or answered with a single
        # name. The separation stays stored, so switching it on again
        # is instant, and it is not in the run.
        keep = [src for src in keep if voice_lines_here(voice_lines, src)]
    if not keep:
        return None
    # The one the window calls the front, unless it is not among them.
    # Compared through path_key: two spellings of one file are unequal
    # as text.
    same = [src for src in keep if path_key(src) == path_key(front)]
    first = same[0] if same else keep[0]
    named = ((state.get("speakers_source") or "")
             if path_key(first) == path_key(front) else first)

    def block(src, e):
        segments, names = e["segments"], e.get("names") or {}
        if voice_lines is not None:
            segments = voices_in_use(segments,
                                     voices_ignored_of(voice_lines, src))
            names = voice_names_of(names, voice_lines, src)
        return speakers_for_project(src, segments, e.get("count") or 0,
                                    names)
    out = block(named, by[first])
    more = [block(src, by[src]) for src in keep if src != first]
    more = [m for m in more if m["segments"]]
    if more:
        out["more"] = more
    return out


def speakers_project_block(state):
    """Every separation the window holds, as the project file takes it."""
    return speakers_block_of(state)


def voices_merged(rows):
    """One entry per name: the same name twice is the same person.

    Whichever recording a voice was heard in, the name says who it is;
    two entries of one name reach the cut as two people, and their
    shared camera then stands twice in the same cut.
    """
    order, where = [], {}
    for name, parts in rows or ():
        if name in where:
            where[name].extend(parts)
        else:
            where[name] = list(parts)
            order.append(name)
    return [(name, sorted(where[name])) for name in order]


def separation_has_voices(given):
    """Whether any of the separations handed over heard anything."""
    given = given or {}
    return any((one or {}).get("segments")
               for one in [given] + list(given.get("more") or ()))


def voices_answer_kept(remembered, files, named):
    """Keep "several speakers" for every recording that shows voices.

    several_set writes it only when the entry is picked, so a project
    saved at any other moment comes back without it. Never over an
    answer of "one person": that answer and this arrive in the same
    round, and writing True back brings the voice rows straight in.
    """
    for p, _kind in files or ():
        here = os.path.abspath(p)
        if here not in named:
            continue
        for key in (p, here):
            if remembered.get("several:" + key) is not False:
                remembered["several:" + key] = True


def voice_names_by_source(voice_lines, fallback=""):
    """The names given in the rows, sorted under their recordings.

    One list for the whole window loses the names of the rows not on
    the screen and reads the rest back under another recording's
    voices.
    """
    out = ByFile()
    for key, name_value, _cv in voice_lines or ():
        src, _label = voice_key_parts(key)
        here = out.setdefault(src or fallback, {})
        if name_value.get().strip():
            here[voice_key_parts(key)[1]] = name_value.get().strip()
    return out


def voice_names_store(state, named):
    """Put each recording's names back under that recording."""
    for src, names in (named or {}).items():
        entry = (state.get("speakers_by") or ByFile()).get(src)
        if entry is not None:
            entry["names"] = names


def speakers_for_run(state, voice_lines):
    """Every separation the window holds, as the run is handed them.

    All of them: where a voice comes from makes no difference to the
    cut, and one of two leaves half the people off the screen. Voices
    set to "do not use" are left out here and kept in the window: they
    become no track and no speaker at auphonic.com.
    """
    return speakers_block_of(state, voice_lines)


def speakers_front_pick(state):
    """Put a separation that still holds in front, where none is.

    The recording the run was made of may have changed while another
    one's separation stands; without this the window would show voices
    and the run separate again.
    """
    if state.get("speakers_local") or not state.get("speakers_by"):
        return
    front = sorted(state["speakers_by"])[0]
    entry = state["speakers_by"][front]
    state["speakers_local"] = entry["segments"]
    state["speakers_source"] = front
    state["speakers_count"] = entry.get("count") or 0


def voice_keys_carry_source(remembered, source):
    """Give the voices of an older project the recording they are of.

    Such a project holds one separation, so a bare label belongs to the
    recording it separated; left bare, a second separation writes its
    own voices' names and cameras over them.
    """
    if not source:
        return
    for stem in ("voice:", "voicename:"):
        for api_key in [k for k in list(remembered)
                        if k.startswith(stem) and "\n" not in k]:
            fresh = stem + voice_key(source, api_key[len(stem):])
            remembered.setdefault(fresh, remembered.pop(api_key))


def split_cells_write(cells, busy, running, by_source, note):
    """Say in every recording's row how its separation stands.

    Only the recording being listened to offers a way out; the others
    have nothing to break off. Every row is asked about its own
    recording -- two can carry a separation at once, each with its own
    number. Returns False where the cells are gone, the table having
    been built again while this was on its way.
    """
    running = os.path.abspath(running) if running else ""
    for path, button, mark, _item in list(cells or ()):
        here = os.path.abspath(path)
        mine = busy and here == running
        found = separations_of(by_source, path)
        done = bool(found) and not mine
        try:
            button.setVisible(mine)
            if note and note[0] == here:
                # The first line of it and no more: the cell is one
                # line wide, and the rest stands under the table.
                mark.setText(note[1].split("\n")[0][:200])
                mark.setStyleSheet("color: %s" % note[2])
            elif mine:
                mark.setText(T('Separating ...'))
                mark.setStyleSheet("color: %s" % COLOURS["quiet"])
            elif done:
                mark.setText(TN(len(found), 'Separated: %s speaker',
                                'Separated: %s speakers')
                             % number_text(len(found), 0))
                mark.setStyleSheet("color: %s" % COLOURS["good"])
            else:
                mark.setText("")
        except RuntimeError:
            return False
    # After the texts and not between them: the rows have to be as
    # tall as what stands in them, and shorter again when it is gone.
    PROGRAM.cells_laid_out(cells)
    return True


def voices_under(path, said, by_source):
    """The voices to show under one recording, and none where not.

    *said* is the answer stored for this recording: True for several
    speakers, False for a single name, None where nobody has answered
    yet. Only an answer shows them; what was measured must not answer
    the question itself, and nothing is lost by that. Switching the
    separation off says "do not compute", not "do not look".
    """
    found = separations_of(by_source, path)
    return found if said and found else []


def longest_stretch(segments, label_name):
    """The longest stretch one voice speaks, in the source's time.

    The longest, because a name is read off what is heard and a two
    second scrap between two other people is the worst place to judge.
    """
    for label, parts in (segments or ()):
        if label == label_name and parts:
            return max(parts, key=lambda p: p[1] - p[0])
    return None


def audio_clock_of(file_path, clocks):
    """Return how fast this recorder ran against the common axis.

    The run rewrites every track with this, so the preview applies it
    too: without it the far end of an hour sits a tenth of a second
    out, and the last shots shown are not the ones the run makes.
    """
    b = (clocks or {}).get(path_key(file_path))
    return float(b) if b else 1.0


def audio_start_of(file_path, axis, unset=None):
    """Where an audio file starts: the measurement, else its timecode.

    A clock set by hand is set wrong -- measured, a recorder 2.35 s
    ahead of the cameras beside it -- and the axis outvotes it by the
    median of every timecode it was given. Where nothing was measured
    the timecode answers, except a clock never set; *unset* is that
    set, worked out from the axis where none is passed.
    """
    a = (axis or {}).get(path_key(file_path))
    if a is not None:
        return float(a)
    if unset is None:
        unset = clocks_not_set(list(axis or ()))
    if path_key(file_path) not in unset:
        try:
            t = file_timecode(file_path)
        except (OSError, ValueError, RuntimeError):
            t = None
        if t is not None:
            return float(t)
    return None


def camera_start_of(file_path):
    """Where a video file starts, from its timecode, or nothing."""
    try:
        info = video_facts(file_path)
    except (OSError, ValueError, RuntimeError):
        return None
    return timecode_seconds(info)


# How far apart two microphones must stand before measuring the tracks
# beats listening to them mixed: above this both name 99 % of the
# speech right, below it the mix leads by 9.5 points at 13 dB, 23 at 3.
MICROPHONES_APART_DB = 20.0


def speaker_mix_file(paths, made_of, folder=""):
    """Add the aligned recordings into the one file the separation hears.

    The bare sum names 97.6 % of the speech right against 37.5 % for
    measuring the same tracks. **Nothing is levelled first**: that
    costs 1.6 points, the recording levels being as large as the bleed.
    The name comes from *made_of*, or a mix redated every run costs the
    separation its key.
    """
    paths = [p for p in (paths or ()) if p]
    if len(paths) < 2:
        return ""
    folder = folder or cache_folder("speakers")
    if not folder:
        return ""
    mark = hashlib.sha1("\n".join([speaker_recipe_mark()]
                                  + [str(x) for x in made_of])
                        .encode("utf-8")).hexdigest()[:16]
    here = os.path.join(folder, "mix_%s.wav" % mark)
    if os.path.exists(here):
        return here
    parts, chains, markers = [], [], []
    for i, path in enumerate(paths):
        parts += ["-i", path]
        chains.append("[%d:a]aformat=channel_layouts=mono[m%d]" % (i, i))
        markers.append("[m%d]" % i)
    # A plain sum, then one gain over the finished mix so it cannot
    # clip: one gain over everything moves no track against another.
    fc = (";".join(chains) + ";" + "".join(markers)
          + "amix=inputs=%d:normalize=0:dropout_transition=0" % len(markers)
          + ",volume=%.6f[out]" % (1.0 / len(markers)))
    beside = ""
    try:
        fd, beside = tempfile.mkstemp(dir=folder, prefix=".vpm_",
                                      suffix=".wav")
        os.close(fd)
        run_ffmpeg_with_progress(
            ["ffmpeg", "-v", "error"] + parts
            + ["-filter_complex", fc, "-map", "[out]",
               "-ar", str(SPEAKER_SPLIT_RATE), "-ac", "1",
               "-c:a", "pcm_s16le", "-y", beside],
            sample_count(paths[0]) / float(SR),
            T('Mixing the tracks for the separation'))
        os.replace(beside, here)
    except Exception:
        if beside:
            remove_quietly(beside)
        return ""
    return here


def speaker_source_pick(audio_files, videos, own_cameras=(), chosen="",
                        camera_audio=False, placeless=(), length_of=None,
                        alone=False, apart_db=None, mix=None):
    """Say which file the separation should listen to.

    Microphones of their own MICROPHONES_APART_DB apart are measured
    instead; below that they name 37.5 % right and *mix* makes one file
    of them all. Only *placeless* files are left out; a run nobody
    asked for (*alone*) refuses a guess. Returns (path, why): chosen /
    one recording / camera track / microphones mixed / nothing, or,
    with an empty path, several microphones / several cameras.
    """
    nowhere = set(path_key(p) for p in (placeless or ()))

    def usable(p):
        return (p and os.path.exists(p)
                and path_key(p) not in nowhere)

    if chosen and usable(chosen):
        return chosen, "chosen"
    good = [p for p in (audio_files or ()) if usable(p)]
    if len(good) == 1:
        return good[0], "one recording"
    if len(good) > 1:
        if (mix is not None and apart_db is not None
                and apart_db < MICROPHONES_APART_DB):
            made = mix(good)
            if made:
                return made, "microphones mixed"
        return "", "several microphones"
    cameras = [p for p in (list(videos) if camera_audio
                           else list(own_cameras or ())) if usable(p)]
    if alone and len(cameras) > 1:
        return "", "several cameras"
    if cameras:
        how_long = length_of or media_seconds
        # The longest covers most of the episode; where none can be
        # measured the first stands.
        try:
            return max(cameras, key=how_long), "camera track"
        except OSError:
            return cameras[0], "camera track"
    return "", "nothing"


#----------------------------------- Who spoke, measured off the tracks

def speaker_statistics(d):
    """Return who speaks how much and how often.

    Same source as the cut: the handover file or the Auphonic statistics.
    Without them a share of wide shot cannot be judged.
    """
    out, total = [], 0.0
    for speaker in (d.get("speakers") or []):
        segs = [tuple(x) for x in (speaker.get("sections") or [])]
        total_sum = sum(b - a for a, b in segs)
        total += total_sum
        out.append({"name": speaker.get("name") or T('Track'), "seconds": total_sum,
                     "blocks": len(segs),
                     "mean": (total_sum / len(segs)) if segs else 0.0,
                     "longest_one": max((b - a for a, b in segs), default=0.0)})
    for e in out:
        e["share"] = 100.0 * e["seconds"] / (total or 1.0)
    out.sort(key=lambda e: -e["seconds"])
    # Silence: whatever is left when the speech blocks of all speakers
    # are laid on top of each other, so two at once count once here.
    every = sorted((a, b) for speaker in (d.get("speakers") or [])
                  for a, b in (speaker.get("sections") or []))
    merged = []
    for a, b in every:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    spoken = sum(b - a for a, b in merged)
    length = float(d.get("length_s") or 0.0) or (merged[-1][1]
                                                 if merged else 0.0)
    return out, total, max(0.0, length - spoken), length


def coupling_matrix(power, speech, faint=6.0, loud=10.0, at_least=3):
    """Return how loudly each voice arrives in the other microphones.

    ``c[i][j]`` is the power gain with which speaker j appears in
    microphone i, measured where j speaks alone; the diagonal is 1. No
    such moment leaves the entry 0. *power* is [track][block] on an axis.
    """
    n = len(power)
    c = np.eye(n)
    for j in range(n):
        # j speaks, everyone else is quiet against their own speech level.
        alone = power[j] > (speech[j] * (10 ** (-loud / 20.0))) ** 2
        for other in range(n):
            if other != j:
                alone &= power[other] < (speech[other]
                                         * (10 ** (-faint / 20.0))) ** 2
        blocks = np.where(alone)[0]
        if len(blocks) < at_least:
            continue
        for i in range(n):
            if i == j:
                continue
            own = power[j][blocks]
            c[i][j] = float(np.median(power[i][blocks] / np.maximum(own,
                                                                    1e-20)))
    return c


def unmix_levels(power, c, at_most=30.0):
    """Take the bleed out of the measured levels.

    What a microphone hears is its own speaker plus a share of every
    other: ``observed = c @ own``, solved once for all blocks. Returns
    (own, reason). Too strong a coupling to invert leaves the levels
    unchanged: better an unseparated measurement than an invented one.
    """
    if len(power) < 2:
        return power, ""
    highest = float(max(c[i][j] for i in range(len(c))
                        for j in range(len(c)) if i != j) if len(c) > 1
                    else 0.0)
    if highest >= 0.9:
        return power, T('the microphones hear each other almost as loudly '
                        'as their own speaker')
    try:
        if float(np.linalg.cond(c)) > at_most:
            return power, T('the tracks are too much alike to separate')
        own = np.linalg.solve(c, power)
    except np.linalg.LinAlgError as e:
        return power, str(e)
    return np.maximum(own, 0.0), ""


# The shortest sound that still counts as speech: below this a block is
# dropped before the pause search, so a short reaction reads as a pause.
# The floor is where passages stop being "mhm" and start being breath.
SPEECH_MIN_LEN_S = 0.2


def clock_on_axis(curve, clock):
    """Stretch a level curve from a recorder's own clock onto the axis.

    No two recorders run at exactly the same speed, so an hour on one is
    not an hour on the next. The run rewrites the audio; here the level
    curve is resampled. *clock* is the b of "recorder = a + b * axis".
    """
    if not len(curve) or abs(clock - 1.0) <= 1e-7:
        return curve
    long_enough = int(round(len(curve) / clock))
    if long_enough < 2:
        return curve
    return np.interp(np.arange(long_enough) * clock,
                     np.arange(len(curve)), curve)


def speakers_from_tracks(tracks, block=0.1, rate=8000, over_db=10.0,
                        gap=0.35, min_len=SPEECH_MIN_LEN_S,
                        report=None, separate=True,
                        note=None, grid=None):
    """Derive speech segments from the separate tracks.

    Each block is measured against the track's own noise floor, because
    recorders are set to different gains. With *separate* the bleed is
    taken out first; without it a neighbour's voice counts as that
    neighbour speaking. *tracks* is [(name, path, offset[, clock])];
    *grid* takes the levels as read, so no track is opened twice."""
    names, levels, shifts = [], [], []
    # Read a handful at a time, not all at once: an hour of audio is a
    # couple of hundred megabytes per track.
    step = max(2, min(4, how_many_processors()))
    read = {}
    for i, entry in enumerate(tracks):
        name, file_path, offset = entry[0], entry[1], entry[2]
        clock = float(entry[3]) if len(entry) > 3 else 1.0
        if i % step == 0:
            read = {}
            group = tracks[i:i + step]
            for entry, x in zip(group, parallel_map(
                    group, lambda t: decode_audio(t[1], rate=rate))):
                read[entry[1]] = x
        if report:
            report(T('Measuring %s (%s of %s)')
                   % (name, number_text(i + 1, 0),
                      number_text(len(tracks), 0)))
        x = read.pop(file_path, None)
        if x is None:
            x = decode_audio(file_path, rate=rate)
        nb = max(1, int(block * rate))
        count = len(x) // nb
        names.append(name)
        shifts.append(int(round(offset / block)))
        if count < 2:
            levels.append(np.zeros(0))
            continue
        levels.append(clock_on_axis(np.sqrt(
            (x[:count * nb].reshape(count, nb).astype(np.float64) ** 2
             ).mean(axis=1)), clock))

    # One grid for all: louder than another only means something on one axis.
    begin = min(shifts) if shifts else 0
    end = max((s + len(v) for s, v in zip(shifts, levels)), default=0)
    width = max(0, end - begin)
    level = np.zeros((len(levels), width))
    for i, (s, v) in enumerate(zip(shifts, levels)):
        if len(v):
            level[i][s - begin:s - begin + len(v)] = v
    # The reference has to land inside the speaking: the 90th percentile
    # does so above a tenth of the blocks, the 99th above a hundredth.
    # Below that it lands on the bleed and refuses the split untruly.
    speech = np.array([float(np.percentile(v[v > 0], 99))
                       if len(v) and len(v[v > 0]) else 0.0 for v in levels])
    if grid is not None:
        grid.append({"names": list(names), "level": level.copy(),
                     "block": block, "begin": begin * block})

    power = level ** 2
    reason = ""
    if separate and len(levels) > 1 and width:
        c = coupling_matrix(power, speech)
        power, reason = unmix_levels(power, c)
        if note:
            # c is a ratio of powers, so ten times the logarithm -- the
            # same figure the 3:1 check reports for amplitudes.
            far = [(10.0 * math.log10(1.0 / max(c[i][j], 1e-9)), names[j],
                    names[i]) for i in range(len(c)) for j in range(len(c))
                   if i != j and c[i][j] > 0]
            if reason:
                note(T('  Bleed not separable: %s') % reason)
            elif far:
                worst = min(far)
                note(T('  Bleed measured, %s in %s only %s dB quieter '
                       '-- taken out of the speech detection')
                     % (worst[1], worst[2],
                        number_text(worst[0], 1)))
                # Where a pair offers no moment of one voice alone, its
                # entry stays 0 and that bleed is left in: half a model
                # beats none, but silence here would look measured.
                pairs = len(c) * (len(c) - 1)
                if len(far) < pairs:
                    note(T('  Caution: only %s of %s pairs measurable. For '
                           'the rest no moment was found where exactly one '
                           'person speaks, so their bleed stays in -- the '
                           'speaker detection is unreliable here.')
                         % (number_text(len(far), 0), number_text(pairs, 0)))
            else:
                note(T('  No moment found where exactly one person speaks '
                       '-- the bleed stays in the speech detection.'))
    level = np.sqrt(power)

    out = []
    for i, name in enumerate(names):
        row = level[i]
        present = row[row > 0]
        if not len(present):
            out.append((name, []))
            continue
        # Noise floor: the lowest fifth of the blocks; above it is speech.
        floor = float(np.percentile(present, 20))
        threshold = max(floor * (10.0 ** (over_db / 20.0)),
                       float(np.percentile(present, 90)) * 0.08)
        loud = row > threshold
        segments, first = [], None
        for j, on in enumerate(loud):
            if on and first is None:
                first = j
            elif not on and first is not None:
                segments.append([first * block, j * block])
                first = None
        if first is not None:
            segments.append([first * block, len(row) * block])
        # Short pauses inside a sentence are not speaker changes.
        joined = []
        for a, b in segments:
            if joined and a - joined[-1][1] <= gap:
                joined[-1][1] = b
            else:
                joined.append([a, b])
        shift = begin * block
        out.append((name, [(round(a + shift, 2), round(b + shift, 2))
                            for a, b in joined if b - a >= min_len]))
    return out


#------------------------------------------- The voices get their names

# How many sentences a track must carry before its share of questions
# says anything. Under twenty it is arithmetic on nothing.
ROLE_MIN_SENTENCES = 20


def who_asks(tracks, words):
    """Rank the speakers by who does the asking -- a proposal, never more.

    The guest asks fewest questions per sentence and speaks longest, and
    that order holds; the distance varies too much for a threshold. It
    takes one voice per track, and holds the tracks against each other
    first to see that it has one. [(name, sentences, questions, speech_s)].
    """
    if not words or not tracks or len(tracks) < 2:
        return []
    # Counting per track means nothing where two of them carry the same
    # speech: the questions go to the loudest recorder, not to the asker.
    if not one_voice_each(tracks):
        return []
    held = {name: sum(b - a for a, b in segs) for name, segs in tracks}

    def talking_at(t):
        for name, segs in tracks:
            for a, b in segs:
                if a <= t < b:
                    return name
        return None

    said = {name: [0, 0] for name in held}
    for group in sentences_of(words):
        who = talking_at((group[0]["start"] + group[-1]["end"]) / 2.0)
        if who is None or who not in said:
            continue
        said[who][0] += 1
        text = (group[-1].get("word") or "").strip().rstrip(CLOSING_MARKS)
        if text.endswith("?"):
            said[who][1] += 1
    # Nothing is claimed about a track that hardly said anything.
    enough = [n for n in said if said[n][0] >= ROLE_MIN_SENTENCES]
    if len(enough) < 2:
        return []
    # Most questions per sentence first; the shorter speaking time
    # breaks a tie, because the one asking is the one talking less.
    return sorted(
        [(n, said[n][0], said[n][1], held[n]) for n in enough],
        key=lambda r: (-(r[2] / float(r[1])), r[3]))


def roles_report(order, tracks=()):
    """The proposal in words, or why there is none.

    Silence has one reason worth a line: the tracks carry each other's
    speech. Every other says nothing a person could act on.
    """
    if not order:
        if not one_voice_each(tracks):
            return [T('  Who asks -- not said here: two of the tracks carry '
                      'the same speech, so the questions would go to '
                      'whichever recorder was turned up loudest.')]
        return []
    out = [as_head(T('\nWHO ASKS -- a proposal, and nothing is set from it'))]
    for name, sentences, questions, held in order:
        out.append(T('  %-20s %s speaking, %s of %s sentences a question')
                   % (name, as_hms(held), number_text(questions, 0),
                      number_text(sentences, 0)))
    out.append(T('  The order carries, the distance between them does not: '
                 'measured over four episodes it never turned round, while '
                 'the distance between first and last changed fourfold. It '
                 'takes one voice per track; where two of them carry the '
                 'same speech nothing is said at all.'))
    return out


def is_stand_in_name(name):
    """Report whether this is a name the program made up itself.

    Either the separation's SPEAKER_00 upwards or the numbered stand-in
    the window puts in the field, in whatever language it was in.
    """
    text = (name or "").strip()
    if re.match(r"^SPEAKER_\d+$", text):
        return True
    forms = ["Speaker %d"] + [c.get("Speaker %d") for c in CATALOGUE.values()]
    for form in forms:
        if form and re.match(
                "^" + re.escape(form).replace("%d", r"\d+") + "$", text):
            return True
    return False


def voice_role_names(order):
    """Propose a name for each voice out of the ranking of who asks.

    The one who answers asks fewest questions and speaks longest, so the
    last of the ranking is the guest and the rest are named after asking.
    Too few sentences and a voice never reaches the ranking.
    """
    if len(order or ()) < 2:
        return {}
    asking = [row[0] for row in order[:-1]]
    out = {order[-1][0]: T('Guest')}
    for i, name in enumerate(asking):
        out[name] = T('Host') if len(asking) == 1 else T('Host %d') % (i + 1)
    return out


def voice_names_report(order):
    """The proposed names in words, or nothing where there is nothing."""
    named = dict((n, v) for n, v in voice_role_names(order).items()
                 if is_stand_in_name(n))
    if not named:
        return []
    out = [as_head(T('\nWHAT THE VOICES COULD BE CALLED -- a proposal'))]
    for row in order:
        if row[0] in named:
            out.append(T('  %-20s could be called %s')
                       % (row[0], named[row[0]]))
    out.append(T('  Only for voices still carrying the name the program gave '
                 'them; one somebody typed is never touched. The roles are '
                 'read off who asks and who answers, which holds for a '
                 'conversation with one guest and is a proposal, not a '
                 'setting.'))
    return out


def voice_window_order(tracks, words, offset, origin,
                       in_point="", out_point="", fps=30.0):
    """Who does the asking, worked out inside the time window alone.

    *tracks* are the voices on the shared axis, *words* the recognition
    in its own time, *offset* what moves them onto it. The window goes
    through apply_time_window, so preview and this can never disagree.
    """
    if not tracks or not words:
        return []
    length = max((b for _n, parts in tracks for _a, b in parts), default=0.0)
    if length <= 0:
        return []
    handover = {
        "speakers": [{"name": name, "sections": [list(p) for p in parts]}
                     for name, parts in tracks],
        "words": [[w["start"] + offset, w["end"] + offset, w["word"]]
                  for w in words],
        "length_s": length, "start_s": origin, "fps": fps}
    # Reached on the program and not bound above: apply_time_window
    # belongs to the cut, which the way in reads after this piece.
    cut, complaint = PROGRAM.apply_time_window(handover, in_point, out_point)
    if complaint:
        return []
    return who_asks(
        [(s["name"], s["sections"]) for s in cut["speakers"]],
        [speech_word(a, b, text) for a, b, text in cut["words"]])


def voice_proposals(order, labels):
    """The two proposals that follow from that ranking.

    A name for every voice that reached the ranking, "do not use" for
    every one that did not -- hardly speaking inside the window is the
    whole rule. Returns ({label: name}, [labels that hardly speak]).
    """
    if not order:
        return {}, []
    ranked = set(row[0] for row in order)
    return (voice_role_names(order),
            [label for label in labels if label not in ranked])


def voice_marks_of(state):
    """What the window remembers about its voice rows.

    Made on first use and kept over a rebuild of the table: the rows go
    and come again, and a mark going with them would overwrite an answer.
    """
    marks = state.get("voice_marks")
    if marks is None:
        marks = {"typed": set(), "said": {}, "name": {}, "camera": {}}
        state["voice_marks"] = marks
    return marks


def voice_row_marks(state, key, name_value, camera_value, field, box):
    """Note what a voice row was born with, and who answers in it.

    Only textEdited and activated say a person answered; they never fire
    for the program. *key* is recording and label together, because
    every separation calls its first voice SPEAKER_00.
    """
    marks = voice_marks_of(state)
    marks["name"].setdefault(key, name_value.get())
    marks["camera"].setdefault(key, camera_value.get())
    # The field itself, so a name already on somebody else can be
    # marked in it. Written over on every rebuild, never kept.
    marks.setdefault("field", {})[key] = field
    field.textEdited.connect(lambda *_: marks["typed"].add(key))
    box.activated.connect(lambda *_: marks["typed"].add(key))


def voice_proposal_apply(voice_lines, named, silent, marks, source=""):
    """Fill the fields that still carry what the program put there.

    A field belongs to the program while it holds what the row was born
    with or the last proposal, and stops the moment somebody answers --
    typing the stand-in back by hand counts. *source* keeps out the rows
    of other recordings; returns the labels that changed.
    """
    typed = marks.get("typed") or set()
    said = marks.setdefault("said", {})
    born = marks.get("name") or {}
    first = marks.get("camera") or {}
    moved = []
    for key, name_value, camera_value in voice_lines_here(voice_lines,
                                                          source):
        label = voice_key_parts(key)[1]
        if key in typed:
            continue
        text = name_value.get().strip()
        if not (is_stand_in_name(text) or text == said.get(key)):
            continue
        want = named.get(label) or born.get(key) or text
        # Never onto a name somebody else already carries: a proposal
        # making two voices one person is worse than none.
        if want in set(nv.get().strip()
                       for k, nv, _c in voice_lines if k != key):
            want = text
        if want != text:
            if named.get(label):
                said[key] = want
            else:
                said.pop(key, None)
            name_value.set(want)
            moved.append(label)
        picked, was = camera_value.get(), first.get(key)
        if label in silent:
            if picked == was and picked != IGNORE_AUDIO:
                camera_value.set(IGNORE_AUDIO)
                print(T('  %s hardly speaks inside the time window -- '
                        'proposed: do not use.') % label)
                moved.append(label)
        elif picked == IGNORE_AUDIO and was not in (None, IGNORE_AUDIO):
            camera_value.set(was)
            moved.append(label)
    return moved


def voice_axis_offset(state, assign_lines):
    """Where the separated recording lies on the shared axis.

    The separation and the words are both stored in the raw time of
    that one recording, so both have the same distance to travel.
    """
    axis = state.get("axis") or {}
    starts = [audio_start_of(row[0], axis) or 0.0
              for row, _nv, cv in assign_lines
              if cv.get() != IGNORE_AUDIO and os.path.exists(row[0])]
    source = state.get("speakers_source") or ""
    return (audio_start_of(source, axis) or 0.0) - min(starts or [0.0])


def voice_suggest_round(state, voice_lines, assign_lines, camera_lines,
                        in_point, out_point, language="", heard=None):
    """One round of the proposals, on the wait the preview runs on.

    A moved In point, a renamed voice and a changed camera all reach it
    and none costs a measurement. A voice set to "do not use" by hand
    stays out of the ranking for good; one the program put there does not.
    """
    if not (state.get("speakers_local") and state.get("speakers_source")):
        return []
    spoken = words_of_recording(state, state.get("speakers_source") or "")
    if spoken is None:
        speech_words_kick_off(state, language, heard)
        return []
    marks = voice_marks_of(state)
    # Of this recording's rows, in this recording's labels: another
    # recording's SPEAKER_00 says nothing about these passages.
    source = state.get("speakers_source") or ""
    by_hand = set(voice_key_parts(k)[1]
                  for k, _nv, cv in voice_lines_here(voice_lines, source)
                  if cv.get() == IGNORE_AUDIO and k in marks["typed"])
    offset = voice_axis_offset(state, assign_lines)
    tracks, length = speakers_on_window_axis(
        voices_in_use(state["speakers_local"], by_hand), offset)
    if not tracks:
        return []
    # On the program and not bound above, the same way: the zero point
    # is the cut's, and the cut is read after this piece.
    origin = PROGRAM.choose_zero_point(
        [audio_start_of(row[0], state.get("axis") or {})
         for row, _nv, cv in assign_lines
         if cv.get() != IGNORE_AUDIO and os.path.exists(row[0])],
        [camera_start_of(b) for b, _n, _own, _flag in camera_lines], length)
    order = voice_window_order(tracks, spoken, offset, origin,
                               in_point, out_point)
    named, silent = voice_proposals(order, [k for k, _p in tracks])
    return voice_proposal_apply(voice_lines, named, silent, marks, source)


# When two microphones can still be told apart: the share of the shorter
# one's speech that also falls inside the longer one. Above what talking
# at once produces, below what two clip-ons in one room share.
VOICE_TRACK_TOGETHER = 0.40


# How far the best microphone must be ahead of the second, as a share of
# the voice's own speech. Between the distance a right match keeps and
# the one a wrong match -- off the axis, no microphone -- ever reaches.
VOICE_TRACK_MARGIN = 0.40


# Under this much speech a voice says nothing about a microphone: below
# it the distance between the microphones collapses.
VOICE_MIN_SPEECH_S = 20.0


# How far the best microphone must stand ahead of the second once the
# recording level is out, in dB. Over a full interview the three margins
# were 6.0, 6.6 and 8.4 dB, so this refuses only a coin toss.
VOICE_LEVEL_MARGIN_DB = 1.0


def shared_seconds(one, other):
    """How long both of these lists of passages are running at once."""
    out, j = 0.0, 0
    other = sorted(other)
    for a, b in sorted(one):
        while j < len(other) and other[j][1] <= a:
            j += 1
        k = j
        while k < len(other) and other[k][0] < b:
            out += max(0.0, min(b, other[k][1]) - max(a, other[k][0]))
            k += 1
    return out


def one_voice_each(tracks):
    """Whether these lists of passages can be one voice apiece.

    Where clip-on microphones hear each other, every track carries the
    whole conversation and per-track counting lands on the loudest
    recorder. Measured as the shorter one's share inside the longer.
    """
    rows = list(tracks or ())
    for i, (_name, one) in enumerate(rows):
        for _other, two in rows[i + 1:]:
            floor = min(sum(b - a for a, b in one),
                        sum(b - a for a, b in two))
            if shared_seconds(one, two) > VOICE_TRACK_TOGETHER * floor:
                return False
    return True


def which_microphone(voices, tracks):
    """Match each separated voice to the microphone it was speaking into.

    Both are [(name, [(a, b), ...])] on one axis; returns [(voice,
    track, share, distance)] or []. A voice under a track's own name
    would claim it twice. Clip-ons are held against each other first.
    """
    own = set(name for name, _segs in tracks or ())
    voices = [(name, segs) for name, segs in voices or ()
              if name not in own]
    if len(voices) < 2 or len(tracks or ()) < 2:
        return []
    held = {name: sum(b - a for a, b in segs) for name, segs in tracks}
    if min(held.values()) <= 0:
        return []
    if not one_voice_each(tracks):
        return []
    picked = []
    for name, segs in voices:
        spoken = sum(b - a for a, b in segs)
        if spoken < VOICE_MIN_SPEECH_S:
            continue
        share = sorted(((shared_seconds(segs, t) / spoken, m)
                        for m, t in tracks), reverse=True)
        if share[0][0] - share[1][0] < VOICE_TRACK_MARGIN:
            continue
        picked.append((name, share[0][1], share[0][0],
                       share[0][0] - share[1][0]))
    # One microphone, one person: where two voices point at the same
    # one, neither is the answer -- one person cut in two, or two on
    # one microphone, and both mean this cannot name them.
    twice = set(t for i, (_, t, _s, _d) in enumerate(picked)
                for _n, u, _s2, _d2 in picked[i + 1:] if t == u)
    return [row for row in picked if row[1] not in twice]


def voices_by_level(voices, names, level, block=0.1, begin=0.0,
                    margin=VOICE_LEVEL_MARGIN_DB):
    """Name each separated voice after the microphone it spoke into.

    The voice says *when*, the microphones *who*. *level* is
    [microphone][block], *begin* where block zero sits. Not the loudest:
    a speaker stood louder in his neighbour's (-47.2 dB) than his own
    (-47.4 dB), 11 dB apart. Each microphone's mean out fixes that.
    """
    rows = [(name, list(segs)) for name, segs in (voices or ()) if segs]
    names = list(names or ())
    if len(rows) < 2 or len(names) < 2 or len(rows) > len(names):
        return []
    level = np.asarray(level, dtype=np.float64)
    if level.ndim != 2 or level.shape[0] != len(names) or not level.shape[1]:
        return []
    # Each microphone's own noise floor is the bottom of its column, or
    # a digitally silent track would drag its mean to minus infinity.
    floor = []
    for row in level:
        present = row[row > 0]
        floor.append(float(np.percentile(present, 20)) if len(present)
                     else 1e-7)
    table = []
    for _name, segs in rows:
        wanted = np.zeros(level.shape[1], dtype=bool)
        for a, b in segs:
            i = max(0, int(round((a - begin) / block)))
            j = min(level.shape[1], int(round((b - begin) / block)))
            if j > i:
                wanted[i:j] = True
        if not wanted.any():
            return []
        table.append([20.0 * math.log10(max(float(np.median(level[m][wanted])),
                                            floor[m], 1e-12))
                      for m in range(len(names))])
    # One number per microphone out of its own column: after this a
    # recorder turned up louder shifts nothing, only distance is left.
    middle = [sum(row[m] for row in table) / float(len(table))
              for m in range(len(names))]
    picked = []
    for (name, _segs), row in zip(rows, table):
        order = sorted(((row[m] - middle[m], names[m])
                        for m in range(len(names))), reverse=True)
        ahead = order[0][0] - order[1][0]
        if ahead >= margin:
            picked.append((name, order[0][1], round(order[0][0], 2),
                           round(ahead, 2)))
    # One microphone, one person -- which_microphone's rule. Where two
    # voices land on one, saying nothing beats naming an episode wrongly.
    twice = set(t for i, (_n, t, _l, _d) in enumerate(picked)
                for _n2, u, _l2, _d2 in picked[i + 1:] if t == u)
    return [row for row in picked if row[1] not in twice]


def microphones_report(rows):
    """The proposal in words, or nothing where there is nothing to say."""
    if not rows:
        return []
    out = [as_head(T('\nWHICH MICROPHONE -- a proposal, and nothing is set '
                     'from it'))]
    for voice, track, share, distance in rows:
        out.append(T('  %-20s sounds like %-20s %s %% of it inside that '
                     'track, %s points ahead of the next')
                   % (voice, track, number_text(round(100 * share), 0),
                      number_text(round(100 * distance), 0)))
    out.append(T('  It holds under one assumption: one microphone per '
                 'person, and each of them carrying only that person. '
                 'Where the tracks overlap too much to be told apart, or '
                 'two voices point at the same microphone, nothing is said '
                 'at all rather than something uncertain.'))
    return out


#------------------------------------------------------------- Storage

_SPEAKER_RECIPE = []


def speaker_recipe_mark():
    """A short mark of the way a separation is worked out.

    Without it a changed reckoning hands back yesterday's answer. Only
    what decides the *stored* segments goes in, not the widening and
    gap closing, which happen on use. Hashed, not counted: a number
    needs remembering, source changes by itself.
    """
    if not _SPEAKER_RECIPE:
        try:
            import inspect
            text = "%s|%d|%s" % (
                SPEAKER_SPLIT_WORKER, SPEAKER_SPLIT_RATE,
                "".join(inspect.getsource(f) for f in
                        (speaker_split_run, _speaker_split_talk,
                         speaker_segments_group, speaker_mix_file)))
        except Exception:
            # Nothing to read the source from. Coarser -- every
            # release throws the separations away -- but never wrong.
            text = VERSION
        _SPEAKER_RECIPE.append(
            hashlib.sha1(text.encode("utf-8")).hexdigest()[:12])
    return _SPEAKER_RECIPE[0]


def speaker_cache_key(path, model_mark="", num_speakers=0):
    """The name a stored separation lives under.

    Path, mtime and size say whether it is the same recording; the
    model, a number of speakers set by hand and the way the answer is
    worked out are inputs too. Not in it: the language, the time
    window, the offset, the names -- they change nothing measured.
    """
    mark = file_fingerprint(path)
    if not mark:
        return ""
    parts = ["%s|%d|%d" % (mark[0], mark[1], mark[2]),
             model_mark or "", str(int(num_speakers or 0)),
             speaker_recipe_mark()]
    return hashlib.sha1(
        "\n".join(parts).encode("utf-8")).hexdigest()[:16]


def speaker_cache_file(key):
    """Where a stored separation lives, or None."""
    folder = cache_folder("speakers")
    return os.path.join(folder, key + ".json") if folder and key else None


def speaker_cache_read(key):
    """Read a stored separation. None means: measure it again.

    Not tied to the program version: three minutes of computing are not
    thrown away because a number in the title bar changed. What decides
    is the model, and that is in the key.
    """
    file_path = speaker_cache_file(key)
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        with open(file_path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    return speaker_segments_group(d.get("segments") or [])


def speaker_cache_write(key, segments):
    """Store a separation so the next start need not repeat it."""
    file_path = speaker_cache_file(key)
    if not file_path:
        return
    d = {"when": time.time(), "version": VERSION,
         "model": SPEAKER_MODEL_NAME,
         "segments": [[label, a, b] for label, parts in segments
                      for a, b in parts]}
    try:
        fd, beside = tempfile.mkstemp(dir=os.path.dirname(file_path),
                                      prefix=".vpm_", suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        os.replace(beside, file_path)
    except OSError:
        pass


def speaker_split_stored(source, count=0):
    """A separation of this recording that is already on this machine.

    [] where none is, so whoever asks may say what a run would cost.
    """
    return speaker_cache_read(
        speaker_cache_key(source, speaker_model_mark(), count)) or []


def speaker_split_cached(source, count=0, report=None, stopping=None):
    """Separate one recording, or hand back what was stored before.

    The one road: the window and the run both take it, so minutes spent
    in the window are not spent again. Returns (segments, trouble).
    """
    stored = speaker_split_stored(source, count)
    if stored:
        return stored, ""
    segments, trouble = speaker_split_run(source, count, report=report,
                                          stopping=stopping)
    if segments:
        speaker_cache_write(
            speaker_cache_key(source, speaker_model_mark(), count),
            segments)
    return segments, trouble


def speaker_split_work(source, count, note, stopping, done):
    """One separation of one recording, in a thread of its own.

    Out here because it decides nothing and touches no widget: a file
    goes in, the passages come out, and the three callbacks -- *note*,
    *stopping*, *done* -- are the only way it says anything.
    """
    segments, trouble = [], ""
    try:
        # Asked from scratch every time one is started: the answer was
        # measured minutes ago at best, and something installed since
        # then must not go unnoticed until the window is restarted.
        if not speaker_split_available(deep=True):
            speaker_split_mend(note)
        if not speaker_split_available():
            trouble_log(speaker_split_why()
                        or speaker_split_missing())
            trouble = speaker_split_trouble()
        if not trouble:
            segments, trouble = speaker_split_cached(
                source, count, report=note, stopping=stopping)
    except Exception as e:
        trouble = T('The speaker separation reports: %s') % str(e)[:140]
    done((source, count, segments, trouble))


def speaker_measure_loop(tracks, bridge, bridge_emit):
    """Read off the tracks who speaks when, in a thread of its own."""
    try:
        out = speakers_from_tracks(
            tracks, report=bridge.speaker_note.emit)
        length = max((b for _n, segs in out for _a, b in segs), default=0.0)
        result = (out, length, "" if length > 0 else
                    T('Nothing was audible in the tracks.'))
    except Exception as e:
        result = ([], 0.0, T('Measuring not possible: %s') % str(e)[:140])
    bridge_emit(bridge.speakers_measured, result)


def speaker_split_loop(state, split_run, bridge, bridge_emit,
                       source, count, label_run):
    """The separation, with the window's own way of answering.

    Nothing is said back once the list this was started for has gone.
    """
    def still_wanted():
        return state.get("speakers_run") == label_run

    speaker_split_work(
        source, count,
        lambda t, s: still_wanted() and bridge_emit(
            bridge.speakers_split_note, t, s),
        lambda: split_run["stop"] or not still_wanted(),
        lambda r: still_wanted() and bridge_emit(bridge.speakers_split, r))


def speaker_split_begin(state, split_run, bridge, bridge_emit,
                        source, count, label_run, language=""):
    """Start the separation of one recording, and its words with it.

    The recognition runs beside the separation, not behind it: the two
    use different machinery, and the shorter costs nothing inside the
    longer. It inherits the separation's consent from this start.
    """
    threading.Thread(
        target=speaker_split_loop,
        args=(state, split_run, bridge, bridge_emit, source, count,
              label_run), daemon=True).start()
    speech_words_kick_off(state, language, lambda r: bridge_emit(
        bridge.speakers_heard, r), source)


def speakers_for_project(source, segments, num_speakers=0, called=None):
    """The separation as the project file carries it.

    Raw, in the time of the source file, so a machine that opens the
    project elsewhere does not pay the three minutes again.
    """
    mark = file_fingerprint(source) or [source, 0, 0]
    return {"source": mark[0], "mtime": mark[1], "size": mark[2],
            "model": SPEAKER_MODEL_NAME,
            "model_mark": speaker_model_mark(),
            "num_speakers": int(num_speakers or 0),
            "names": dict(called or {}),
            "segments": [[label, a, b] for label, parts in segments
                         for a, b in parts]}


def speakers_from_project(d, fingerprint=file_fingerprint):
    """Read a stored separation back, if it still fits its source.

    Returns (source, segments, names): a source that has been changed
    is measured again rather than carried on wrongly.
    """
    d = (d or {}).get("speakers") or {}
    source = d.get("source") or ""
    if not source:
        return "", [], {}
    mark = fingerprint(source)
    if not mark or mark[1] != d.get("mtime") or mark[2] != d.get("size"):
        return "", [], {}
    if d.get("model_mark") and speaker_model_mark() \
            and d["model_mark"] != speaker_model_mark():
        return "", [], {}
    return (source, speaker_segments_group(d.get("segments") or []),
            dict(d.get("names") or {}))


def speakers_all_from_project(d, fingerprint=file_fingerprint):
    """Every separation a project carries, by the recording it is of.

    More than one fits, each with its own voices. The block the run
    reads stands where a single separation stood, the others under it
    in "more". Each is tested on its own: one whose recording has
    changed falls out, the rest stand.
    """
    block = (d or {}).get("speakers") or {}
    out = ByFile()
    for one in [block] + list(block.get("more") or ()):
        source, segments, names = speakers_from_project(
            {"speakers": one}, fingerprint)
        if source and segments:
            out[source] = {
                "segments": segments, "names": names,
                "count": int(one.get("num_speakers") or 0)}
    return out


#------------------------------------------ A separation already stored

def read_separation_file(file_path):
    """Read a stored separation out of a project or assignment file.

    Returns the dict with source, segments and names, or {}.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        print(T('  %s cannot be read: %s') % (os.path.basename(file_path), e))
        return {}
    if not isinstance(d, dict):
        return {}
    for key in ("speakers_of", "speakers"):
        entry = d.get(key)
        if isinstance(entry, dict) and entry.get("segments"):
            return entry
    return d if d.get("segments") else {}


def voices_of_file(file_path):
    """Which camera each voice belongs to, out of a handed-over file.

    Only the interface knows this. Missing is the ordinary case and
    means every voice goes to the camera the run is built around.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return {}
    got = d.get("voices_of") if isinstance(d, dict) else None
    return dict(got) if isinstance(got, dict) else {}


def separation_on_axis(given, tracks, position, t0, t1):
    """Put every separation handed over onto the axis of this run.

    The one in front and the ones under "more", each with the offset of
    its own recording -- which recording a voice was heard in makes no
    difference to the cut. Voices of one name are folded together.
    Returns (segments, "") or ([], why not).
    """
    out, trouble = one_separation_on_axis(given, tracks, position, t0, t1)
    why = [trouble] if trouble else []
    for one in ((given or {}).get("more") or ()):
        more, trouble = one_separation_on_axis(one, tracks, position, t0, t1)
        out += more
        if trouble:
            why.append(trouble)
    if not out:
        return [], "; ".join(why) or T('no recording named')
    return voices_merged(out), ""


def one_separation_on_axis(given, tracks, position, t0, t1):
    """Put one stored separation onto the axis of this run.

    The segments are kept raw, in the time of the file they were measured
    in; where it sits is known, so this is arithmetic and no measurement.
    Returns (segments, "") or ([], why not).
    """
    if not (given or {}).get("source"):
        return [], T('no recording named')
    # Looked up by the real path: /tmp is a link to /private/tmp on
    # macOS, and the same file then carries two names.
    source = os.path.realpath(given["source"])
    where = ByFile()
    for track in tracks:
        blocks = track.get("blocks") or [track.get("source")]
        if blocks and blocks[0]:
            where[os.path.realpath(blocks[0])] = (track["a"], track["b"])
    for v, place in (position or {}).items():
        where[os.path.realpath(v)] = (place[0], place[1])
    if source not in where:
        return [], T('%s is not part of this run') % os.path.basename(source)
    a, b = where[source]
    if not b:
        return [], T('%s has no place on the axis') % os.path.basename(source)
    named = dict((given or {}).get("names") or {})
    # Only the recorder's own clock is undone here, an offset and a
    # divisor; the window and the rounding are speaker_segments_on_axis's,
    # so the two cannot drift apart. Measured over 18 cases with a
    # divisor of 1: the same answer in each, edges and empty input in.
    moved = [(named.get(label) or label,
              [((x - a) / b, (y - a) / b) for x, y in parts])
             for label, parts in speaker_segments_polish(
                 speaker_segments_group(
                     (given or {}).get("segments") or []))]
    out = speaker_segments_on_axis(moved, 0.0, t0, t1)
    if not out:
        return [], T('nothing of it falls inside the window')
    return out, ""


def microphones_apart_of_run(args, tracks):
    """How far apart the microphones of this run stand, in dB.

    Every recording against every other, both ways round, so it is the
    dearest question in this corner: asked once a run, the answer kept on
    *args*, None where there is nothing to compare. Two blocks of one
    recorder share no time, so the question goes to whole recordings.
    """
    if hasattr(args, "_microphones_apart"):
        return args._microphones_apart
    whole = []
    for track in tracks or ():
        p = track.get("source") or (track.get("blocks") or [""])[0]
        if p and p not in whole and os.path.exists(p):
            whole.append(p)
    apart = microphones_apart_db(whole) if len(whole) > 1 else None
    args._microphones_apart = apart
    return apart


def separation_source_of_run(args, tracks, video_paths, mixable=False,
                             window=()):
    """Which recording a run without a window takes apart by voice.

    The same rule the window follows, on the same function. Which cameras
    were ticked by hand is not on the command line, so all are offered.
    With *mixable* microphones that hear each other too well are added
    into one file, which becomes the source; *window* names it.
    """
    from_cameras = bool(getattr(args, "_camera_audio", None))
    recordings, of_track = [], {}
    for track in tracks or ():
        for p in (track.get("blocks") or [track.get("source")]):
            if p and p not in recordings:
                recordings.append(p)
                of_track[p] = track

    def mix(chosen):
        """Add up the tracks these recordings were aligned into."""
        picked, made_of, seen = [], [], set()
        for p in chosen:
            track = of_track.get(p)
            if track is None or id(track) in seen or not track.get("axis"):
                continue
            seen.add(id(track))
            picked.append(track["axis"])
            made_of.append("%s|%s|%.6f|%.9f"
                           % (path_key(p), file_fingerprint(p),
                              float(track.get("a") or 0.0),
                              float(track.get("b") or 1.0)))
        return speaker_mix_file(picked, made_of + [str(x) for x in window])

    apart = (microphones_apart_of_run(args, tracks)
             if mixable and not from_cameras else None)
    return speaker_source_pick([] if from_cameras else recordings,
                               video_paths or (),
                               camera_audio=from_cameras,
                               apart_db=apart,
                               mix=mix if mixable else None)


def voices_reported(segments):
    """Say who speaks how long, and in how many passages."""
    for name, segs in segments:
        print(TN(len(segs), '  %-20s %s in %s passage',
                 '  %-20s %s in %s passages')
              % (name, as_hms(sum(b - a for a, b in segs)),
                 number_text(len(segs), 0)))


def separation_for_run(args, tracks, position, t0, t1, video_paths=()):
    """Work out who speaks when, before the audio is processed.

    Four ways in, in order: handed over in the assignment file, named
    with --speakers-from, named with --speakers-local, or the one this
    run picks. Where the microphones hear each other too well, all are
    mixed instead. Returns (segments, where from) or ([], "").
    """
    given = getattr(args, "_speakers_of", None) or {}
    where_from = T('the interface') if given else ""
    if not given and getattr(args, "speakers_from", None):
        given = read_separation_file(args.speakers_from)
        where_from = os.path.basename(args.speakers_from)
    source, why, dropped = "", "", None
    if (getattr(args, "_speakers_of", None)
            and not SPEAKER_SPLIT_OFF
            and not getattr(args, "no_speakers_local", False)
            and not getattr(args, "speakers_local", None)
            and not getattr(args, "_camera_audio", None)
            and bool(getattr(args, "without_auphonic", False))
            and not getattr(args, "auphonic_done", None)):
        # The window picks its source without knowing how far the
        # microphones stand apart, so it takes one recording: below
        # MICROPHONES_APART_DB that names 37.5 % right against 97.6 %.
        apart = microphones_apart_of_run(args, tracks)
        if apart is not None and apart < MICROPHONES_APART_DB:
            source, why = separation_source_of_run(
                args, tracks, video_paths, mixable=True, window=(t0, t1))
            if source and why == "microphones mixed":
                dropped = apart
            else:
                # No mix came back, so what the window found still stands.
                source, why = "", ""
    if not given and not source and not getattr(args, "no_speakers_local",
                                                False):
        if getattr(args, "speakers_local", None):
            source = os.path.abspath(args.speakers_local)
        elif not SPEAKER_SPLIT_OFF:
            # Only where the recordings stay raw -- after auphonic.com
            # the bleed is already out of them.
            source, why = separation_source_of_run(
                args, tracks, video_paths,
                mixable=bool(getattr(args, "without_auphonic", False))
                and not getattr(args, "auphonic_done", None),
                window=(t0, t1))
    if source:
        print(as_head(T('\nSEPARATING THE SPEAKERS')))
        if dropped is not None:
            # Somebody is about to wait three minutes longer than the
            # window promised, and this is the only place to say why.
            print(as_warn(
                T('  What the window took apart is dropped: it listened '
                  'to one recording, and the microphones hear each other '
                  'so well that none of them stands out -- %s dB against '
                  'the %s dB one of them alone needs to say who is '
                  'speaking.')
                % (number_text(dropped, 1),
                   number_text(MICROPHONES_APART_DB, 1))))
        if why == "microphones mixed":
            args._speakers_mixed = True
            print(T('  The microphones hear each other too well to say who '
                    'is speaking, so the separation listens to all %s of '
                    'them at once, on this machine.')
                  % number_text(len(tracks), 0))
        else:
            print(T('  In %s, on this machine.') % os.path.basename(source))
        count = int(getattr(args, "speakers_count", 0) or 0)
        stored = speaker_split_stored(source, count)
        if stored:
            print(T('  Separated once already: read back, not measured '
                    'again.'))
        else:
            how_long = media_seconds(source)
            if how_long:
                print(T('  About %s of computing for %s of audio.')
                      % (as_hms(how_long / SPEAKER_SPLIT_SPEED),
                         as_hms(how_long)))
            if not speaker_split_available():
                print("  " + speaker_split_missing())
        # A separation already on this machine costs nothing to read, so
        # a dry run hands it on. Only a measurement is left undone.
        if getattr(args, "dry_run", False) and not stored:
            print(T('  (measuring only: nothing separated)'))
            return [], ""
        if not stored and not speaker_split_available():
            print("  %s" % speaker_split_missing())
            return [], ""
        segments, trouble = speaker_split_cached(
            source, count,
            report=lambda text, share: show_progress(text, share))
        print()
        if trouble:
            print("  %s" % trouble)
            return [], ""
        given = {"source": source,
                 "segments": [[label, a, b] for label, parts in segments
                              for a, b in parts]}
        where_from = T('the separation in this run')
    if not given:
        return [], ""
    # Which recordings were taken apart. Their tracks reach the cut
    # through their voices, the rest through speakers_for_the_cut.
    args._separated = separation_sources(given)
    if getattr(args, "_speakers_mixed", False):
        # The mix was written onto the axis over this window, so a moment
        # in it is a moment of the cut. Placing takes t0 off; -t0 undoes it.
        position = dict(position or {})
        position[source] = (-t0, 1.0)
    out, why_not = separation_on_axis(given, tracks, position, t0, t1)
    if not out:
        print(as_warn(T('  The speaker separation is not used: %s.')
                      % why_not))
        if getattr(args, "_speakers_mixed", False):
            # Whatever went wrong, the tracks are there and everybody is
            # on one. A mix that says nothing would empty the cut.
            args._speakers_mixed = False
            args._separated = []
        return [], ""
    if getattr(args, "_speakers_mixed", False):
        # The mix is made of every track, so every track is spoken for.
        # Without this everybody would stand in the cut twice.
        args._separated += [p for track in (tracks or ())
                            for p in (track.get("blocks")
                                      or [track.get("source")]) if p]
    if getattr(args, "dry_run", False):
        # A dry run stops before the cut is built, so what the voices
        # amount to is said here or nowhere.
        print(as_head(T('\nSPEAKERS -- SEPARATED BY VOICE')))
        voices_reported(out)
    return out, where_from


def separation_sources(given):
    """Every recording the separations handed over were made of."""
    given = given or {}
    return [one["source"] for one in [given] + list(given.get("more") or ())
            if (one or {}).get("source") and (one or {}).get("segments")]


def separated_already(track, separated=()):
    """Whether a separation was made of this very recording.

    Then the people in it are in the cut as its voices, and measuring the
    track as well would put them there twice. That is the only thing that
    keeps a track out of the measurement: one with no camera of its own
    is measured like any other and counts for the speaking shares.
    """
    apart = set(path_key(p) for p in separated or () if p)
    mine = list(track.get("blocks") or []) + [
        track.get("source") or "", track.get("from_camera") or ""]
    return any(path_key(p) in apart for p in mine if p)


def speakers_for_the_cut(args, tracks):
    """Say who speaks when, and put the origin in the log.

    Everybody is in it, whichever way they came in: the voices a
    separation found, and every track no separation covers, measured from
    its own microphone. Only "do not use" keeps somebody out. Whoever is
    not in it is named in the log instead of going quietly missing.
    """
    voices, where_from = getattr(args, "_speakers", None) or ([], "")
    left = [t for t in tracks
            if not separated_already(t, getattr(args, "_separated", None))]
    mics, box = [], []
    if left or (where_from and len(tracks) > 1):
        # One reading for both uses, over every track: a track left out
        # would hear its neighbour and count that as speech.
        try:
            mics = speakers_from_tracks(
                [(track["name"], track.get("ready") or track["axis"], 0.0)
                 for track in tracks], note=print, grid=box)
        except Exception as e:
            print(as_warn(T('  The tracks were not measured, so %s is in '
                            'the mix and not in the cut: %s')
                          % (", ".join(t["name"] for t in left) or "-",
                             str(e)[:140])))
            left = []
    named = []
    if voices and getattr(args, "_speakers_mixed", False):
        voices, named = name_voices_by_microphone(voices, box)
        if not voices:
            left = list(tracks)
            for line in named:
                print(line)
            named = []
    if voices:
        print(as_head(T('\nSPEAKERS -- SEPARATED BY VOICE')))
        print(TN(len(voices), '  From %s: %s voice.', '  From %s: %s voices.')
              % (where_from, number_text(len(voices), 0)))
        for line in named:
            print(line)
    if left:
        print(as_head(T('\nSPEAKERS -- MEASURED HERE')))
        print(T('  From the tracks themselves, one voice per track: %s.')
              % ", ".join(t["name"] for t in left))
        keep = set(t["name"] for t in left)
        voices = list(voices) + [(n, s) for n, s in mics if n in keep]
    segments = voices_merged(voices)
    voices_reported(segments)
    # A run that quietly holds fewer speakers than the sheet did costs
    # hours to find, so whoever is missing is named here.
    in_cut = set(name for name, _segs in segments)
    absent = [t["name"] for t in tracks if t["name"] not in in_cut]
    if absent:
        print(T('  Not in the cut: %s -- a separation speaks for the '
                'recording, or it was not measured.') % ", ".join(absent))
    if not any(segs for _, segs in segments):
        print(T('  Nothing was audible in the tracks -- no camera cut from '
                'this.'))
    if where_from and len(tracks) > 1:
        for line in name_the_voices(segments, mics):
            print(line)
    return segments


def name_voices_by_microphone(voices, box):
    """Give the voices of a mixed separation the names of the microphones.

    A voice out of a mix is SPEAKER_00, a name with no camera behind it,
    so the cut would stand on the wide shot throughout -- this is no
    proposal like the one below. *box* holds the levels
    speakers_from_tracks read, so the tracks are opened once.
    """
    grid = (box or [None])[0]
    rows = voices_by_level(voices, grid["names"], grid["level"],
                           grid["block"], grid["begin"]) if grid else []
    if not rows:
        # Nothing that could be hung on a camera, so the voices are let
        # go and the tracks answer -- worse, but everybody is somewhere.
        return [], [T('  Which voice belongs to which microphone could '
                      'not be told, so the tracks are measured instead.')]
    called = dict((voice, track) for voice, track, _level, _ahead in rows)
    lines = [T('  %-20s is %-20s %s dB ahead of the next microphone, '
               'the recording level taken out')
             % (voice, track, number_text(ahead, 1))
             for voice, track, _l, ahead in rows]
    return ([(called.get(name, name), segs) for name, segs in voices or ()],
            lines)


def name_the_voices(segments, mics):
    """What the microphones say about voices that came out unnamed.

    Only worth saying where the two are different things: a separation
    named the voices SPEAKER_00 upwards, and beside it there are tracks a
    person has named. The measurement comes in rather than being made
    here -- the one the cut is built from, not a second reading.
    """
    return microphones_report(which_microphone(segments, mics))


#-------------------------------- The box in the window, and its caption


def speakers_step_said(source):
    """What the line under the overall bar says while one is separated.

    The name and not the path: the bar stands in the window, not in the
    folder, and the line has one line's room.
    """
    return T('Separating speakers: %s') % os.path.basename(source)


def make_speaker_split(QtCore, state, bridge, bridge_emit, plan, files,
                       assign_lines, voice_lines, remembered, split_run,
                       split_line, split_label, split_never, axis_store):
    """Separate the speakers, locally, and say where that stands.

    A third source for the same thing: who speaks when. auphonic.com says
    it from its statistics, speakers_from_tracks measures it where every
    person has a microphone, and this works it out from one recording.
    Three names built in gui() come through *state*.
    """
    # A thread of its own and an entry of its own on the bar, and no
    # place in the prework count: axis_work_loop waits in "while
    # prework_busy()", and three minutes there hold up the time axis.
    def speaker_split_source(alone=False):
        """Which file the separation listens to, and why that one."""
        audio_files = [p for p, a in files if a == "audio"]
        videos = [p for p, a in files if a == "video"]
        # The derived answer, not the stored one: a camera whose sound is
        # the only sound there is was never clicked.
        return speaker_source_pick(
            audio_files, videos, state.get("own_cameras") or (),
            chosen=state.get("speakers_source_chosen") or "",
            placeless=state.get("no_place") or (), alone=alone)

    def speaker_split_show(text="", colour=None, where=""):
        """Say where the separation stands: in the row of its file.

        What is happening to a recording belongs in the line that shows
        it, so the state goes into the Speakers cell of the row. *where*
        names the recording a message belongs to.
        """
        state["split_note"] = ((os.path.abspath(where) if where else "",
                                text, colour or COLOURS["quiet"])
                               if text else None)
        split_line_write(split_line, split_label, split_never,
                         speaker_split_wanted(state.get("speakers_wanted")),
                         split_run["busy"], bool(files),
                         state.get("split_note"))
        split_cells_show()

    def split_cells_show():
        """Write the state of the separation into every file's row."""
        if SPEAKER_SPLIT_OFF:
            return
        if not split_cells_write(state.get("split_cells") or (),
                                 split_run["busy"],
                                 state.get("speakers_running") or "",
                                 state.get("speakers_by") or ByFile(),
                                 state.get("split_note")):
            state["split_cells"] = []

    def speaker_split_note(text, share):
        """Runs in the window thread: the row and the bar together."""
        source = state.get("speakers_running") or ""
        speaker_split_show(text, where=source)
        if source:
            # The caption travels with every report: pressing Start clears
            # the plan under a running separation, leaving the step bare.
            plan.report("speakers:" + source, share,
                        speakers_step_said(source))

    bridge.speakers_split_note.connect(speaker_split_note)

    def speaker_split_done(result):
        """The separation came back: keep it, store it, show it."""
        source, count, segments, trouble = result
        split_run["busy"] = False
        plan.done("speakers:" + source)
        state["speakers_running"] = ""
        if trouble:
            speaker_split_show(trouble, COLOURS["error"], where=source)
            return
        if not segments:
            speaker_split_show("", COLOURS["quiet"])
            return
        # The names are an assignment, not a measurement: a voice that
        # had one keeps it, and the stand-in counts past the sheet.
        called = dict(speakers_stored(state, source).get("names") or {})
        speakers_keep(state, source, segments, count, dict(
            speaker_label_names(segments, called, sheet_speaker_names(
                assign_lines, voice_lines_here_not(voice_lines, source),
                state.get("voiced") or ()))))
        axis_store(state.get("axis") or {})
        state["assignment_fresh"]()
        speaker_split_show()
        state["preview_soon"]()

    bridge.speakers_split.connect(speaker_split_done)
    bridge.speakers_heard.connect(
        lambda r: speech_words_done(state, r, state["preview_soon"]))

    def speaker_split_kick_off(fresh=False):
        """Start the separation where there is something to separate.

        Nothing is computed again for a moved time window, a new In point
        or a renamed speaker: those are arithmetic on what is stored. Only
        a changed source file or a hand-set number of speakers start it
        over. Without *fresh* nobody asked, so the source must be alone.
        """
        if split_run["busy"] or not files:
            return
        source, _why = speaker_split_source(alone=not fresh)
        if not source:
            speaker_split_show()
            return
        count = int(state.get("speakers_count") or 0)
        if not fresh:
            if speakers_stored(state, source).get("segments"):
                speaker_split_show()
                return
            if not speaker_split_wanted(state.get("speakers_wanted")):
                speaker_split_show()
                return
        state["speakers_wanted"] = True
        split_run["busy"] = True
        split_run["stop"] = False
        label_run = state.get("speakers_run", 0) + 1
        state["speakers_run"] = label_run
        state["speakers_running"] = source
        # Measured at 28 times real time on the graphics unit, so the
        # share of the bar is known rather than guessed.
        plan.add("speakers:" + source,
                 max(2.0, media_seconds(source) / SPEAKER_SPLIT_SPEED),
                 speakers_step_said(source))
        plan.begin("speakers:" + source, speakers_step_said(source))
        speaker_split_show()
        speaker_split_begin(state, split_run, bridge, bridge_emit,
                            source, count, label_run,
                            state["speech_language"].get())

    def split_stop(_source=""):
        """The one button left in a row: stop listening to it."""
        if not split_run["busy"]:
            return
        split_run["stop"] = True
        speaker_split_show(T('Stopping ...'),
                           where=state.get("speakers_running") or "")

    def voices_stored_for(path):
        """How many voices of this very recording are already here.

        It does not depend on what the row is showing: a row that says
        one person still carries what was measured on it.
        """
        return len(voices_under(path, True, state.get("speakers_by")))

    def voices_of(path):
        """The voices to show under this recording, if any."""
        return voices_under(path, remembered.get("several:" + path),
                            state.get("speakers_by"))

    def several_set(path, on):
        """The name field was answered: several speakers, or one again.

        Switching back hides the rows underneath and throws nothing
        away: what was measured stays in the project and in the cache.
        """
        remembered["several:" + path] = bool(on)
        if on and not voices_stored_for(path) and not SPEAKER_SPLIT_OFF:
            if state.get("speakers_source_chosen") != path:
                # A number of speakers set by hand belongs to the
                # recording it was set for, not to the next one.
                state["speakers_count"] = 0
            state["speakers_source_chosen"] = path
            QtCore.QTimer.singleShot(
                0, lambda: speaker_split_kick_off(fresh=True))
        QtCore.QTimer.singleShot(0, lambda: state["assignment_fresh"]())

    def speaker_split_never():
        """The other button: not on this machine, and remember it."""
        state["speakers_wanted"] = False
        axis_store(state.get("axis") or {})
        speaker_split_show()

    split_never.clicked.connect(speaker_split_never)

    return speaker_split_kick_off, split_stop, voices_of, several_set


#------------------------------ The rows, the marks and the speaking time


def speech_table_fill(Qt, QtGui, QtWidgets, table, d):
    """Write the speaker statistics into the table.

    It reaches into nothing of the window's own, so it stands beside
    what it counts rather than in the window. Returns the total speech
    time as a sentence, empty where no speaker is known.
    """
    lines, total, silence, length = (speaker_statistics(d) if d
                                      else ([], 0.0, 0.0, 0.0))
    table.setRowCount(len(lines) + (1 if length > 0 else 0))
    # The block count reaches four digits after nine minutes: a block
    # lasts at least 0.2 s and takes 0.35 s of silence to end it, so it
    # goes through the number helper like the columns beside it.
    for i, e in enumerate(lines):
        for column, text in ((0, e["name"]),
                             (1, PROGRAM.as_minutes(e["seconds"])),
                             (2, "%s %%" % number_text(e["share"], 1)),
                             (3, number_text(e["blocks"], 0)),
                             (4, "%s s" % number_text(e["mean"], 1))):
            p = QtWidgets.QTableWidgetItem(text)
            if column:
                p.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(i, column, p)
    if length > 0:
        i = len(lines)
        quiet_share = number_text(100.0 * silence / length, 1)
        for column, text in ((0, T('Silence')),
                             (1, PROGRAM.as_minutes(silence)),
                             (2, "%s %%" % quiet_share),
                             (3, ""), (4, "")):
            p = QtWidgets.QTableWidgetItem(text)
            p.setForeground(QtGui.QBrush(QtGui.QColor(COLOURS["quiet"])))
            if column:
                p.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(i, column, p)
    fix_table_width(table, most_rows=SPEAKER_ROWS_SHOWN)
    return (T('%s speech time') % PROGRAM.as_minutes(total) if lines else "")


def assignment_marks_show(audio_fields, assign_lines, video_fields,
                          camera_lines, multitrack_on, state,
                          voice_lines=()):
    """Mark the trouble spots red, and say beside the tables what they are.

    Three things are caught before they do damage: two recordings under
    one speaker name, which become a single track, a voice carrying a
    name that is on somebody else, and two cameras with the same output
    name, where the second overwrites the first.
    """
    voiced = state.get("voiced") or set()
    audio_reason, video_reason = (state.get("audio_reason"),
                                  state.get("video_reason"))
    # Every name on the sheet at once, both levels. A recording showing
    # its voices is left out: its field says "several speakers".
    twice = set(names_used_twice(assign_lines, voice_lines, voiced))
    used = [(f, v) for f, (r, v, cv) in zip(audio_fields, assign_lines)
               if cv.get() != IGNORE_AUDIO
               and os.path.abspath(r[0]) not in voiced] \
        if len(audio_fields) == len(assign_lines) else []
    names = [v.get() for _f, v in used]
    duplicate = set(n for n in names if n and names.count(n) > 1)
    for field, value in used:
        n = value.get()
        PROGRAM.mark_red(
            field, bool(n) and n in twice,
            T('This name occurs more than once. The recordings '
              'would become one track -- for Multitrack '
              'auphonic.com needs at least two different ones.'))
    fields = voice_marks_of(state).get("field") or {}
    for key, name_value, camera_value in voice_lines or ():
        n = name_value.get().strip()
        if fields.get(key) is not None:
            PROGRAM.mark_red(
                fields[key],
                bool(n) and n in twice
                and camera_value.get() != IGNORE_AUDIO,
                T('This name is on somebody else already. A name is '
                  'a person, and the cut puts a person on one '
                  'camera -- please give this voice its own.'))
    if audio_reason is not None:
        if duplicate and multitrack_on and len(set(names)) < 2:
            audio_reason.setText(
                T('✕  All recordings carry the same name. That makes '
                  'one track -- Multitrack needs at least two.'))
            audio_reason.setVisible(True)
        elif duplicate:
            audio_reason.setText(
                T('✕  %s occurs more than once. These recordings are '
                  'merged into one track and placed in sequence by '
                  'their timecode -- correct if recording was stopped '
                  'in between.') % ", ".join(sorted(duplicate)))
            audio_reason.setVisible(True)
        else:
            audio_reason.setVisible(False)

    if len(video_fields) == len(camera_lines):
        outputs = [v.get().strip() for _p, v, _k, _n in camera_lines]
        duplicate_video = set(n for n in outputs
                              if n and outputs.count(n) > 1)
        same_name = set(PROGRAM.camera_tracks_clashing(camera_lines))
        track_of = dict(PROGRAM.camera_tracks_of(camera_lines))
        for field, (p, value, _k, _n) in zip(video_fields, camera_lines):
            n = value.get().strip()
            # The file name first: of the two it is the one this field
            # can put right.
            same_file = bool(n) and n in duplicate_video
            PROGRAM.mark_red(
                field,
                same_file or track_of.get(p) in same_name,
                T('Two cameras would produce the same file. '
                  'The second would overwrite the first.')
                if same_file else
                T('Two cameras are one camera in the cut. Their '
                  'files carry the same name, so rename one of '
                  'them.'))
        if video_reason is not None:
            if duplicate_video:
                video_reason.setText(
                    T('✕  Two cameras would produce the same file '
                      '(%s). The second would overwrite the first.')
                    % ", ".join(sorted(duplicate_video)))
                video_reason.setVisible(True)
            elif same_name:
                video_reason.setText(
                    T('✕  Two cameras are one camera in the cut (%s). '
                      'Their files carry the same name, so rename one '
                      'of them.')
                    % ", ".join(sorted(same_name)))
                video_reason.setVisible(True)
            else:
                video_reason.setVisible(False)


def make_voice_rows(Qt, QtCore, assign_lines, camera_lines, voice_lines,
                    files, remembered, state, tree_open, multitrack, player,
                    assignment_check, player_load, speaker_split_kick_off,
                    voices_of):
    """The rows of the assignment tree, and the voices under them.

    None of it builds a widget -- the window's own objects go on being
    written through -- so it stands beside the voices it shows.
    `player` is a parameter on purpose: the module-level name player
    holds the piece read by beside(), and a free read here picks up
    the module, not the widget.
    """
    def assignment_state_show():
        """What the material allows: the cut box, and the tick's line.

        The camera cut needs speakers told apart, and whether they came
        of separate tracks or of one recording taken apart is no part of
        it. The widgets are looked up and not closed over: this runs
        while the window is still being built.
        """
        boxes = state.get("cut_boxes")
        if boxes:
            pairs = assignment_pairs(voice_lines, assign_lines)
            seen = len(camera_lines)
            on = bool(multitrack.get()) or cut_has_people(pairs, seen)
            boxes[0].setTitle(cut_box_title(pairs, multitrack.get(), seen))
            boxes[0].setVisible(on)
            boxes[1].setVisible(on)
            boxes[2].setVisible(not on)
        note = state.get("multitrack_note")
        if note is not None:
            used = [r for r in assign_lines if r[2].get() != IGNORE_AUDIO]
            note.setText(multitrack_state_note(
                len(used), sum(1 for _b, _nv, own, _n in camera_lines
                               if not own.get())))

    def voice_play(key):
        """Hand that voice to the player on the right.

        Without hearing it a name is a guess. The player on the right has
        the rail, the pause, the jumps and the boundaries. It jumps into
        the middle of the longest stretch: the first moment of a passage
        is often the tail of somebody else's word.
        """
        source, label = voice_key_parts(key)
        source = source or state.get("speakers_source") or ""
        stretch = longest_stretch(
            speakers_stored(state, source).get("segments"), label)
        if not source or not stretch:
            return
        length = min(8.0, stretch[1] - stretch[0])
        begin = stretch[0] + max(0.0, (stretch[1] - stretch[0] - length) / 2)
        player.load(source, seconds=begin, running=True)

    def assignment_row_show(tree):
        """A clicked row in the assignment tree, whichever level it is.

        The recording goes into the player like any other file. A voice
        has no file of its own, so the player opens the recording it was
        heard in and jumps to where that voice speaks longest -- which is
        the whole of what a Listen button would offer, so there is none.
        """
        row = tree_row_of(tree, tree.currentIndex())
        if row is None:
            return
        if row[0].data(Qt.UserRole + 2):
            voice_play(row[0].data(Qt.UserRole + 2))
        elif row[0].data(Qt.UserRole + 1):
            player_load(row[0].data(Qt.UserRole + 1))

    def folded_show(where):
        """Open, the voices carry the assignment; folded, the row sums up.

        The assignment has exactly one level: where the voices are on the
        screen the recording above shows nothing beside its name, because
        two answers one above the other can contradict each other.
        Folded, the row says their cameras -- not how many.
        """
        tree = state.get("assignment_tree")
        row = tree_row_of(tree, where) if tree is not None else None
        if row is None:
            return
        p, many = row[0].data(Qt.UserRole + 1), row[0].rowCount()
        if not p or not many:
            return
        open_now = tree.isExpanded(where)
        tree_open[p] = open_now
        tree_cell(row, 2, "" if open_now else folded_summary(tree, row),
                  COLOURS["quiet"])
        tree_rows_fit(tree, 266)

    def voice_add(source):
        """Say there is one more voice on that recording than was found.

        A row without segments would say nothing, so this is the input
        to a fresh separation rather than an entry in a list.
        """
        found = len(speakers_stored(state, source).get("segments") or ())
        state["speakers_source_chosen"] = source
        state["speakers_count"] = found + 1
        speaker_split_kick_off(fresh=True)

    def voices_build(tree, under, path, videos, targets, wide=None):
        """The voices heard in one recording, hung under its row.

        Everything counts per camera and not per speaker: two voices set
        to the same camera are one condition, which is why the camera
        sits on the voice and not on the file. *wide* is what
        wide_bar_of worked out. Returns how many voices there were.
        """
        wide = wide or PROGRAM.wide_bar_of(targets, (), False, {})
        barred = wide["barred"]
        found = voices_of(path)
        # The names of this recording, not of the window.
        called = dict(speakers_stored(state, path).get("names") or {})
        for label, _parts in found:
            key = voice_key(path, label)
            name_value = PROGRAM.SpeakerName(voice_name_free(
                remembered.get("voicename:" + key) or called.get(label),
                [nv.get() for _k, nv, _c in voice_lines]))
            picked, worked_out = camera_row_cameras(
                PROGRAM.camera_after_a_mark(
                    "voice:" + key, remembered.get("voice:" + key), wide,
                    name_value.get().strip() or label),
                wide["pickable"], name_value.get(), videos)
            camera_value = Value(MIX_ONLY if picked in barred else picked)
            camera_value.derived = worked_out
            # The first column says which of the two levels this row is,
            # the way the file list writes "4 channels" under a file.
            kid = tree_row(tree, under, [])
            tree_cell(kid, 0, T('Voice'), COLOURS["quiet"])
            kid[0].setData(key, Qt.UserRole + 2)
            field, box = PROGRAM.voice_row_cells(name_value, camera_value,
                                                 targets, name_value.get())
            PROGRAM.choices_shut(box, barred, wide["why"], COLOURS["quiet"])
            tree_field(tree, kid, 1, field)
            tree_field(tree, kid, 2, box)
            row_picker_watch(state["row_picker"], field, box)
            voice_row_marks(state, key, name_value, camera_value,
                            field, box)
            def voice_answered(*_):
                """Store it, mark it, and say the Kind column again.

                Name and camera both count: the wide shot is derived
                from the cameras nobody is assigned to.
                """
                PROGRAM.queue_once(QtCore, state, "voices", voices_remember)
                QtCore.QTimer.singleShot(0, assignment_check)
                PROGRAM.queue_once(QtCore, state, "kinds",
                                   state.get("kinds_refresh"))
                # The preview reads a handover older than this
                # answer, so it is told -- through the usual wait.
                soon = state.get("preview_soon")
                if soon:
                    soon()

            name_value.listen(voice_answered)
            camera_value.listen(voice_answered)
            voice_lines.append((key, name_value, camera_value))
        return len(found)

    def voices_remember():
        """Keep the names and cameras given to the voices."""
        if not voice_lines:
            # Switched back to a single name: the rows are hidden, and
            # what was measured and named must survive a mis-click.
            return
        # Each recording's names go back to that recording.
        named = voice_names_by_source(voice_lines,
                                      state.get("speakers_source") or "")
        voice_names_store(state, named)
        for k, nv, cv in voice_lines:
            # Only a real override: a camera the program worked out goes
            # back as nothing, so renaming a voice moves its camera too.
            remembered["voice:" + k] = camera_to_remember(
                cv.get(), getattr(cv, "derived", None))
            # The name as well: state alone does not reach the project
            # file, and the name is what auphonic.com puts on the track.
            said = nv.get().strip()
            if said:
                remembered["voicename:" + k] = said
            else:
                remembered.pop("voicename:" + k, None)
        voices_answer_kept(remembered, files, named)
        # A voice that has just been given a camera may be the second
        # one, and with it the camera cut becomes possible.
        assignment_state_show()
        # Bound in the window and not here, so it is reached the way
        # voice_answered above reaches it: through state.
        soon = state.get("preview_soon")
        if soon:
            soon()

    return (assignment_state_show, voice_play, assignment_row_show,
            folded_show, voice_add, voices_build, voices_remember)

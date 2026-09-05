# -*- coding: utf-8 -*-
"""Who speaks when, worked out here rather than fetched from anywhere.

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and every name this piece uses out of it is bound below, by name.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# separation reads as it did in the one file. Four are missing: np
# below, and is_stand_in_name, speakers_from_tracks and cells_laid_out,
# whose files are read after this one. Those three stay below.

ByFile = PROGRAM.ByFile
COLOURS = PROGRAM.COLOURS
IGNORE_AUDIO = PROGRAM.IGNORE_AUDIO
PIP_SOURCE = PROGRAM.PIP_SOURCE
SR = PROGRAM.SR
T = PROGRAM.T
TN = PROGRAM.TN
VERSION = PROGRAM.VERSION
as_hms = PROGRAM.as_hms
cache_folder = PROGRAM.cache_folder
clocks_apart = PROGRAM.clocks_apart
decode_audio = PROGRAM.decode_audio
ffprobe_json = PROGRAM.ffprobe_json
file_fingerprint = PROGRAM.file_fingerprint
file_timecode = PROGRAM.file_timecode
hashlib = PROGRAM.hashlib
https_context = PROGRAM.https_context
json = PROGRAM.json
os = PROGRAM.os
path_key = PROGRAM.path_key
remove_quietly = PROGRAM.remove_quietly
run_ffmpeg_with_progress = PROGRAM.run_ffmpeg_with_progress
running_from = PROGRAM.running_from
sample_count = PROGRAM.sample_count
speech_words_kick_off = PROGRAM.speech_words_kick_off
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
time = PROGRAM.time
timecode_seconds = PROGRAM.timecode_seconds
timecode_string = PROGRAM.timecode_string
trouble_log = PROGRAM.trouble_log
video_facts = PROGRAM.video_facts


# numpy is the one name here that the program has still to fetch:
# it holds a stand-in until the first sum asks, and binds the real
# module under its own name then -- which a copy taken up there
# would never see. So this asks the program once, the same way.
class LateNumpy:
    """Stands in for the program's numpy until a sum wants it."""

    def __getattr__(self, name):
        global np
        got = getattr(PROGRAM.np, name)
        np = PROGRAM.np
        return got


np = LateNumpy()


#---------------------------------------------- Local speaker separation

# =====================================================================
#  Local speaker separation
#  ------------------------
#  Who speaks when, out of one recording everybody is audible on --
#  not out of separate microphones, which is what
#  speakers_from_tracks does.
#
#  Measured over two whole interviews against the speech activity of
#  the clip-on microphones: 98.7 % of 45473 words land on the right
#  person, and three quarters of what is left sits in real overlap or
#  around a change of speaker. A raw recorder file separates as well
#  as a processed mix, so this runs before anything is uploaded.
# =====================================================================

# It runs in a process of its own, in an environment of its own, for
# two measured reasons: the packages pin versions the Python this
# program runs in should not have to follow, and a process can be
# broken off where a thread with a model inside it cannot.

SPEAKER_MODEL_NAME = "speaker-diarization-community-1"

# The waveform goes in at 16 kHz mono. That is what the model was
# trained on; anything else is resampled inside it anyway.
SPEAKER_SPLIT_RATE = 16000

# Widening every segment by 0.2 s and closing gaps below 0.25 s buys
# 4.2 points. 0.5 s is the F1 optimum for the boundaries themselves
# but doubles the words that fall to two speakers at once, so the
# smaller edge is the one taken. Both are applied when the segments
# are used, never when they are stored.
SPEAKER_MARGIN_S = 0.2

# How wide a hole inside one speaker is still that speaker breathing.
# Measured over nine values: 0.75 s shows whoever really talks 83.6 %
# of the time against 73.0 % at 0.25 s, for six words of 10 158 that
# go wrong; from 1.0 s both get worse. On a one-sided conversation.
SPEAKER_GAP_S = 0.75

# Measured on Apple Silicon with the graphics unit: an hour of audio
# in a little over two minutes. Used to give the step its share of the
# bar, so it need not be guessed.
SPEAKER_SPLIT_SPEED = 28.0

# From four processors upwards everything starts at once: measured,
# the different kinds of work do not slow each other down at all --
# the separation stays at 0 % beside speech recognition, ffmpeg and
# the prework together, which do not take two processors between them.
# Below that the prework is narrowed while the separation runs, since
# the one real brake is a full processor (+10 to +34 %).
SPEAKER_SPLIT_TOGETHER_CORES = 4

# One separation at a time. Two of them raise throughput by 12 % and
# charge 1.75 times the wait for the first answer plus 4.5 GB for the
# second process -- on a smaller machine that is where it starts
# swapping.
SPEAKER_SPLIT_TURN = threading.Semaphore(1)

# Where nothing may be fetched and nothing may compute for minutes
# without being asked -- a test suite, a machine on a metered line --
# this switches the separation off. It then never starts by itself;
# the button still starts it.
SPEAKER_SPLIT_OFF = bool(os.environ.get("VPM_NO_SPEAKER_SPLIT"))

# The mix auphonic.com writes is not offered as a source: measured, it
# separates no better than the raw recording, and it exists only after
# an upload. One name here rather than a rule spread over the file.
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

    The same question the first tab asks, through the same clocks_apart:
    the file whose timecode window overlaps none of the others. A file
    without a timecode is not in the result. Returns path_key names, so
    the answer can be held against the time axis without either side
    having to know which spelling the other was given.
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

    It travels with the program rather than being fetched: measured,
    a folder is all the pipeline needs -- with an empty HOME, without
    a Hugging Face cache and without a network.
    """
    # The model lies in the program's own folder, which is the
    # folder above this piece: running_from() is where the
    # program itself was loaded from.
    here = os.path.dirname(running_from())
    folder = os.path.join(here, "models", SPEAKER_MODEL_NAME)
    return folder if os.path.isfile(
        os.path.join(folder, "config.yaml")) else ""


# Where the model comes from when it is not there yet. The same
# repository the program itself comes from, so the two always match.
MODEL_BASE = ("https://raw.githubusercontent.com/Bascht74"
              "/videopodcast-magic/%s/videopodcast_magic/models/"
              + SPEAKER_MODEL_NAME + "/")
MODEL_MB = 33


def model_reference():
    """Which state of the repository the model is fetched from.

    The tag of this version, so a program and its model are never a
    version apart. Where there is no such tag -- a run straight off the
    main branch -- the branch is what there is.
    """
    return "v" + VERSION


def fetch_model(report=None, ref=""):
    """Fetch the separation model beside the program. "" when it worked.

    Every file is held against the SHA-256 sums that come with it, and
    one that does not match is not written. The sums are fetched first,
    so the list of files is not written down twice and cannot drift
    from what the model actually is.
    """
    # The model lies in the program's own folder, which is the
    # folder above this piece: running_from() is where the
    # program itself was loaded from.
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
            # No tag of that name: a run off the branch rather than off
            # a release. Say so rather than failing over a name.
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
            report(T('Fetching the model (about %d MB): %s')
                   % (MODEL_MB, name), 0.05 + 0.9 * done / len(sums))
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

    The plain format, digest and name separated by spaces, because
    that is the one shasum -c reads back. A comment block above it
    carries the sizes.
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

    Returns "" when all of them match. Otherwise the name of the first
    file that does not: weights that changed on the way are not put
    into a process that then decides who speaks.
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

    Taken from the checksum file, which names every weight and its
    digest: a different model or a different version of it gives a
    different mark without reading a gigabyte to find out.
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

def speaker_split_missing():
    """The one sentence for "it cannot run here", with the way back.

    One place, so the console, the window and the dry run cannot say
    three different things about the same fault. The way back is the
    same command that installed the program: pyannote stands on the
    list pip reads, so one command puts it back.
    """
    return T('The speaker separation is not installed here. This puts '
             'it back: %s') % ("pip3 install -U " + PIP_SOURCE)


def speaker_python():
    """The interpreter the separation runs in: this one.

    pyannote stands on the list pip reads, so it is here already and
    one command repairs both. The separate *process* is another
    matter and stays: the telemetry switch has to be thrown before
    anything else happens, and a crash inside torch must not take the
    window with it.
    """
    return sys.executable
def forget_speaker_split():
    """Ask again whether the separation can run."""
    PROGRAM._SPEAKER_READY, PROGRAM._SPEAKER_WHY = None, ""


def speaker_split_why():
    """What the import really said when it failed, or "".

    The one line that names the fault, out of whatever the other
    process wrote. Without it the window can only guess at a cause,
    and "not installed" was printed once for a program that was
    installed and whose import fell over a library beside it.
    """
    speaker_split_available()
    return PROGRAM._SPEAKER_WHY


def speaker_split_available(deep=False):
    """Say whether the separation can run. Measured, not assumed.

    The import is really done, in a process of its own: that is the
    only thing that answers the question, and a note left behind by an
    earlier run answers a different one. *deep* asks again from
    scratch rather than reading the answer kept in this run.
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
            # The last line of a traceback is the exception itself, and
            # that is the one line worth keeping: the frames above it
            # say where pyannote imports its own libraries, which
            # nobody reading this can do anything about.
            said = (p.stderr or b"").decode("utf-8", "replace").strip()
            PROGRAM._SPEAKER_WHY = "" \
                if PROGRAM._SPEAKER_READY or not said \
                else said.splitlines()[-1].strip()
        except OSError as e:
            PROGRAM._SPEAKER_READY, PROGRAM._SPEAKER_WHY = \
                False, str(e)
    return PROGRAM._SPEAKER_READY


#------------------------------------------------------- The worker

# What runs in the other process. Written to a file rather than passed
# on the command line so a failure has a line number to point at.
#
# The first thing it does, before any pipeline exists, is switch the
# telemetry off: pyannote 4 sends a trace to its own server on every
# pipeline it builds and every run it makes. No audio goes with it,
# but something goes out, and this program never sends anything by
# itself. Where the switch cannot be found the process refuses to run
# at all -- a separation is not worth breaking that rule for.
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

    The name carries a mark of its source, so a changed program does
    not run last week's worker.
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

    Returns (segments, ""), the segments raw and in the time of the
    file itself: [(label, [(from, to), ...])], without the widened
    edges and without the closed gaps. Storing them raw is what makes
    a later change of offset, of time window or of edge cost nothing.

    Returns ([], sentence) where it could not run. *stopping* is asked
    now and then and ends the run when it answers true.
    """
    folder = speaker_model_folder()
    if not folder:
        # Not there yet: fetch it once, beside the program, where it
        # then stays. Whoever asked for a separation has installed
        # pyannote and torch along with the program already; the 33 MB
        # of the model itself need no second question.
        if report:
            report(T('Fetching the model (about %d MB) ...') % MODEL_MB,
                   0.02)
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
    # Belt and braces: the folder branch of from_pretrained never asks
    # a server, and with this it could not if it wanted to.
    clean["HF_HUB_OFFLINE"] = "1"
    # Only one at a time. The graphics unit is nearly saturated by one
    # run, and a second one costs 4.5 GB for 12 % more throughput.
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
             '  Speaker separation (%s): %d speaker out of %s of audio',
             '  Speaker separation (%s): %d speakers out of %s of audio')
          % (device[-1] if device else "cpu", found, as_hms(seconds)))
    return speaker_segments_group(d["segments"]), ""


def speaker_segments_group(rows):
    """Turn [label, from, to] rows into [(label, [(from, to), ...])].

    In order of speaking time, the longest first: that is the order
    the voices are numbered in, and a name given by hand keeps its
    place because the label stays what it was.
    """
    per = {}
    for row in rows or ():
        # Read first, then filed: setting up the entry before the
        # numbers are known leaves a speaker behind who never spoke.
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

    Measured, this is worth 4.2 points on the assignment of words to
    people: a recogniser reports a word as beginning about a tenth of
    a second late, and the separation stops a moment before the sound
    dies away. Nothing moves before zero.

    It is arithmetic on the stored measurement, not a measurement, so
    it happens where the segments are used.
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

    That answer took the camera away and greyed the name, and there it
    stopped: the voice still became a track, a speaker at auphonic.com,
    a line in the transcript and one in the speaking shares. The case
    was a fourth voice a separation found where three people sat, and
    the rule it left: "do not use" makes a voice as good as not there.

    Taken out of the passages, not only of the names. With the passages
    gone nobody is speaking there, so the picture holds whoever it was
    on until the next voice that counts -- which is what he asked for.

    The separation itself stays whole in the project file: switching
    the voice back on must not cost the three minutes of computing
    again.
    """
    ignored = set(ignored or ())
    if not ignored:
        return list(segments)
    return [(label, parts) for label, parts in segments
            if label not in ignored]


def voice_key(source, label):
    """The name one voice is remembered under: recording and label.

    The model calls the first voice of every recording SPEAKER_00, so
    the label alone is not a name. With two recordings separated, a
    name and a camera given to a voice of the one were read back onto
    a voice of the other. A newline stands in no path and in no label,
    so the two parts always come apart again.
    """
    return "%s\n%s" % (os.path.abspath(source), label) if source else label


def voice_key_parts(key):
    """(recording, label) out of such a name.

    A bare label -- what a project written before this carries -- has
    no recording, and answers with the empty one.
    """
    source, _sep, label = str(key or "").rpartition("\n")
    return source, label


# What the assignment table remembers about one file, by the head of the
# key. The voices of a recording are remembered under the recording, so
# they are struck with it.
REMEMBERED_PER_FILE = ("audio", "kind", "own", "ownname", "several", "video")
REMEMBERED_PER_VOICE = ("voice", "voicename")


def remembered_forget(remembered, gone):
    """Strike what the table remembers about files that have left.

    The table is redrawn out of this store, and the project file is
    written out of it too. So a recording taken out of the list still
    stood in the saved project with an empty name, and one added again
    was "Intro" once more. *gone* are the paths that left.
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

    Without a recording named, all of them: a caller that knows of one
    separation only asks that way.
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

    What a recording is about to be named against: its own old rows
    would stand in the way of naming its own new voices.
    """
    mine = set(id(row) for row in voice_lines_here(voice_lines, source))
    return [row for row in voice_lines or () if id(row) not in mine]


def voices_ignored_of(voice_lines, source=""):
    """The voices somebody set to "do not use", by their label.

    Answered in the labels of the separation itself, not in the keys
    the rows carry: what this is held against is a list of passages,
    and there a voice is called SPEAKER_00.
    """
    return set(voice_key_parts(key)[1]
               for key, _nv, cv in voice_lines_here(voice_lines, source)
               if cv.get() == IGNORE_AUDIO)


def voice_names_of(named, voice_lines, source=""):
    """The names of the voices in use, with what was just typed in.

    A voice set to "do not use" has no name here: the name is what
    becomes a track and a speaker at auphonic.com, so leaving it out is
    half of leaving the voice out. *named* and the answer are in the
    labels of one recording's separation, so *source* says which
    recording's rows are read.
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

    One entry per person, whichever of the four ways they came in by:
    their own recording, a camera's sound, a channel of a recorder, or
    a voice a separation found. A recording whose voices stand under it
    says "several speakers" and not a name, so it is left out and its
    voices speak for it; one set to "do not use" takes no part in the
    run and none here.
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

    A name is a person and a person is on the sheet once. Two of one
    name reached the cut as one person on one camera, and that camera
    then stood twice at different places in the same cut.
    """
    names = sheet_speaker_names(assign_lines, voice_lines, voiced)
    return sorted(set(n for n in names if names.count(n) > 1))


def voice_names_clashing(assign_lines=(), voice_lines=(), voiced=()):
    """The names of that sort a voice carries.

    Two recordings of one person are merged into one track by design,
    so a name twice among the recordings is a question and not a
    refusal. A voice cannot be merged with anything: it is one person
    in one separation, so its name has to be its own.
    """
    twice = set(names_used_twice(assign_lines, voice_lines, voiced))
    return sorted(set(nv.get().strip() for _k, nv, cv in voice_lines or ()
                      if cv.get() != IGNORE_AUDIO
                      and nv.get().strip() in twice))


def speakers_on_window_axis(segments, offset, named=None):
    """The separation under its names, moved onto the shared axis.

    Stored raw and in the time of its own file. The offset and the
    widened edges are applied here, where it is used -- a later change
    of offset then costs this arithmetic and no measurement.

    Returns (speakers, how long the last of them runs).
    """
    out = [((named or {}).get(label) or label, parts)
           for label, parts in speaker_segments_on_axis(
               speaker_segments_polish(segments), offset)]
    return out, max((b for _n, parts in out for _a, b in parts),
                    default=0.0)


def track_recordings_of(assign_lines):
    """Which recording each track that still speaks was measured off.

    Every row the run has, which is every row but "do not use" -- a
    track with no camera of its own speaks too. The names are the ones
    speaker_measure gives, so the two ends of the measurement agree
    without a second list kept beside them.
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

    The same sum speakers_for_the_cut makes in the run, so the preview
    shows the cut the run makes. *where_from* says which recording each
    measured track came off; one whose recording was taken apart is in
    already, through its voices.
    """
    apart = set(path_key(p) for p in separated or () if p)
    out = list(voices or ())
    for name, parts in ((measured or {}).get("segments") or ()):
        # A name with no row behind it any more is nobody: the track
        # was set to "do not use" after it had been measured.
        paths = (where_from or {}).get(name)
        if paths and not any(path_key(p) in apart for p in paths if p):
            out.append((name, list(parts)))
    out = voices_merged(out)
    return out, max([length or 0.0]
                    + [b for _n, parts in out for _a, b in parts])


def tracks_awaiting_measure(where_from, measured, separated=()):
    """The tracks no separation covers and no measurement has reached.

    They are in the cut -- the run measures them itself -- and until
    the button here has been pressed the preview cannot show them. So
    it says who is missing rather than showing a cut without them.
    """
    apart = set(path_key(p) for p in separated or () if p)
    heard = set(n for n, _p in ((measured or {}).get("segments") or ()))
    return sorted(name for name, paths in (where_from or {}).items()
                  if name not in heard
                  and not any(path_key(p) in apart for p in paths if p))


def speakers_all_on_window_axis(state, voice_lines, assign_lines,
                                offset_of):
    """Every separation the window holds, on the window's own axis.

    Each with the offset of its own recording, and then folded by name.
    The run takes them all, so the preview beside it has to: a preview
    computed from other voices than the run uses is worse than none.
    *offset_of* says where one recording lies on the axis. Returns
    (voices, how long the last of them runs).
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

    *offset* is where that file begins on the axis. With *t0* and *t1*
    the result is cut to that window and counted from its start, the
    same arithmetic a finished handover gets when the window moves.

    A file that starts minutes before the episode does contain speech
    nobody will see; it falls out here rather than being kept out of
    the measurement, which is why the number of speakers shown has to
    be read off this result and not off the raw run.
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
    stand-in counts on, because it is the program's own and the program
    does not put one name on two voices. Counting from one per
    separation did: the second recording's first voice was a second
    "Speaker 1", and to the cut two voices of one name are one person.
    """
    name = str(name or "").strip()
    used = set(str(x).strip() for x in taken or () if str(x or "").strip())
    if name and not (PROGRAM.is_stand_in_name(name) and name in used):
        return name
    n = 1
    while T('Speaker %d') % n in used:
        n += 1
    return T('Speaker %d') % n


def speaker_label_names(segments, called=None, taken=()):
    """Name the voices: whoever spoke most is the first one.

    A name given by hand stays, keyed by the label the model used --
    renaming somebody is an assignment, not a reason to measure again.
    *taken* are the names already given elsewhere in the window; the
    stand-in counts past them.
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

    Two people assigned to one camera are one condition and not two.
    A rule about that camera -- how long it has been held, when it may
    be cut to -- holds as soon as one of the two speaks, so their
    segments are merged into one series rather than kept apart.

    *where_to* is {speaker name: camera}; a track set to be left out
    contributes nothing. Returns [(camera, [(from, to), ...])].
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

    On a Mac it runs without being asked: the graphics unit does an
    hour of audio in two minutes and nothing else is waiting on it.
    Elsewhere the answer is asked for once, with the two buttons on
    the line itself rather than in a dialogue, and then remembered in
    the project file. *asked* is that stored answer, None while
    nobody has been asked.
    """
    if SPEAKER_SPLIT_OFF:
        return False
    if asked is not None:
        return bool(asked)
    return True if sys.platform == "darwin" else None


def split_line_write(line, words, never, wanted, busy, any_files):
    """The line under the assignment table -- and mostly nothing at all.

    It used to carry an offer: "who speaks when can be worked out on
    this machine". On a machine that works it out by itself that was
    an offer for something long since done -- it was read on
    25.8.2026 while the table beside it already said "Separated: 4
    speakers". The sentence is left over from the time when the button
    sat down there and this was the state line; the state has stood in
    each recording's own row since that day.

    So the line speaks only where this machine does not work it out on
    its own: where somebody said no for this project, and where nobody
    has been asked yet -- there the question and its button are the
    whole point of the line. Where the answer is yes, it says nothing.
    """
    if SPEAKER_SPLIT_OFF or wanted is True:
        line.setVisible(False)
        return
    line.setVisible(bool(any_files))
    never.setVisible(wanted is None and not busy)
    words.setText(T('Speaker separation is switched off for this project.')
                  if wanted is False else
                  T('Who speaks when can be worked out on this machine, '
                    'from any one recording everybody is audible on.'))


# What a voice's row used to say, and no longer does. It carried one
# number that looked like a timestamp and was in truth the sum of that
# voice's speaking time; on 25.8.2026 the two were pulled apart into a
# duration and a position, which was the right answer to the wrong
# question. Read back on the result: the times matter for jumping
# to the right place, not for the person looking at the table, and the
# table grows too wide for them. So neither is written down any more.
# The longest passage is still worked out below -- it is where a click
# on the row takes the player.


def tc_column_write(rows, real_tc, axis, absolute):
    """Fill the timecode column of the assignment tree.

    What the measurement produced is what stands there: it has held
    every file against the others, while a clock can be seconds off.
    Only where nothing was measured does the timecode speak.

    *rows* is one entry per recording -- (its row in the tree, the
    file, the plain caption) -- and not one per row of the tree: the
    voices hang under their recording and carry no file, so there is
    nothing to number and nothing to skip. A timecode belongs to a
    recording, and a voice has none.

    Returns False where the tree is gone, which happens whenever it
    has been built again while this was on its way.
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


def weak_note(caption, placeless):
    """What a file whose sound was not recognised says beside its name.

    Two ways lead to a place and one of them is enough, so the sentence
    turns on which one is left. With a timecode the file still lies on
    the axis to the frame and only the second opinion is missing; with
    none there is no place at all, and its sound is out of the run.
    """
    if placeless:
        return T('%s\n   does not fit the other files: sound not '
                 'recognised, no timecode.\n   Its sound cannot be used.') \
            % caption
    return T('%s\n   sound not recognised; placed by its timecode') \
        % caption


def weak_colour(odd, placeless):
    """The colour a badly fitting file is written in."""
    if placeless:
        return COLOURS["error"]
    return COLOURS["warning"] if odd else COLOURS["text"]


def weak_nodes_mark(nodes, weak, no_place=()):
    """Mark the rows of the file list that do not fit the time axis.

    Usually those files were picked by mistake and belong to another
    recording. *no_place* are the ones no timecode places either: those
    are refused, the rest are only warned about. Returns the ones whose
    row is gone, for the caller to forget.
    """
    import PySide6.QtGui as _qg
    nowhere = set(no_place or ())
    dropped = []
    for p, item in list(nodes.items()):
        placeless = path_key(p) in nowhere
        odd = path_key(p) in weak or placeless
        ink = _qg.QBrush(_qg.QColor(weak_colour(odd, placeless)))
        try:
            # Column 1 stays with the check mark, or one overwrites the
            # green and red of the other depending on which ran last.
            for column in (0, 2):
                item.setForeground(column, ink)
            if odd:
                item.setText(2, weak_note(os.path.dirname(p), placeless))
        except RuntimeError:
            dropped.append(p)
    return dropped


def weak_marks_show(state, nodes):
    """Say on both sheets which files do not fit the time axis.

    One call for the two, so the file list and the assignment tree
    cannot end up saying different things about the same file.
    Returns the rows that are gone.
    """
    weak = state.get("weak") or ()
    nowhere = state.get("no_place") or ()
    dropped = weak_nodes_mark(nodes, weak, nowhere)
    weak_rows_mark(state.get("file_rows") or (), weak, nowhere)
    return dropped


def weak_rows_mark(rows, weak, no_place=()):
    """The same mark on the recordings of the assignment tree.

    *rows* is (its row in the tree, the file, the plain caption), one
    per recording. The voices under a recording are not marked: whether
    a recording fits the others is a question about the recording, and
    it is asked once, in its own row.

    The camera rows are not marked at all any more, and that is not an
    oversight. Every note about a file stands on the first sheet, where
    the files are chosen; by the time somebody is on the second sheet
    assigning speakers, the note has been read and accepted. Repeating
    it there in red -- over two lines, which widened the column with
    it -- was an accusation, not news.
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
            # the first cell says it in words too -- the same words the
            # first sheet uses. The plain caption travels beside the
            # row, or the second pass would write the sentence into the
            # sentence.
            said = plain
            if odd:
                said = weak_note(plain, placeless)
            row[0].setText(said)
            # The column can be narrower than the sentence.
            row[0].setToolTip(said if odd else "")
        except RuntimeError:
            # The tree has been built again and its rows went with it.
            return


def separations_of(by_source, path):
    """What was separated out of that one recording, or nothing.

    *by_source* is the store the window keeps: one entry per recording
    that has been taken apart. Asking it by the recording is what keeps
    two of them apart. With one entry for the whole window, separating
    a second recording emptied the first one's rows without a word.
    """
    entry = (by_source or ByFile()).get(path or "") or {}
    return list(entry.get("segments") or ())


def speakers_stored(state, source):
    """One recording's separation as the window holds it.

    {"segments": …, "count": …, "names": …}, or nothing where that
    recording has not been taken apart.
    """
    return (state.get("speakers_by") or ByFile()).get(
        source or "") or {}


def speakers_keep(state, source, segments, count, names):
    """Store what was heard in one recording, and put it in front.

    Every recording keeps its own. With room for one, taking a second
    recording apart emptied the first one's rows and carried its names
    over to the new voices -- names that hang on the model's labels and
    cannot be put back by hand. In front is what the run and the
    preview read: one first cut, out of one recording.
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
    under it in "more". None where nothing was separated.

    With *voice_lines* only what stands on the sheet goes, and without
    the voices set to "do not use" -- the run's view, not the file's.
    """
    by = state.get("speakers_by") or ByFile()
    front = state.get("speakers_source") or ""
    keep = [src for src in sorted(by) if by[src].get("segments")]
    if voice_lines is not None:
        # A recording whose sound was set back to "do not use", or
        # answered with a single name, has no rows. Its separation
        # stays stored -- switching it on again must be instant -- and
        # it is not in the run.
        keep = [src for src in keep if voice_lines_here(voice_lines, src)]
    if not keep:
        return None
    # The one the window calls the front, unless it is not among them.
    # keep holds the spellings the store was written under and front
    # the one the window kept, so they are compared in shape: a list
    # is not a ByFile, and two names of one file are unequal as text.
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

    Two entries of one name reached the cut as two people, and the
    camera they share then stood twice at different places in the same
    cut. Whichever recording a voice was heard in, the name says who it
    is.
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

    several_set writes it when the entry is picked, but only then: a
    project saved at any other moment came back without it and
    everybody was called "Speaker 1" again. Never over an answer of
    "one person" -- that answer and this arrive in the same round, and
    writing True back brings the voice rows straight in again.
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

    Written into one list for the whole window, the names of the rows
    that were not on the screen fell out of it, and the ones that were
    on it were read back under another recording's voices.
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

    All of them, each with the voices of the recording they were heard
    in: where a voice comes from makes no difference to the cut. One of
    two going in left half the people off the screen without a word.
    Voices set to "do not use" are left out here and kept in the
    window: they become no track and no speaker at auphonic.com.
    """
    return speakers_block_of(state, voice_lines)


def speakers_front_pick(state):
    """Put a separation that still holds in front, where none is.

    The recording the run was made of may have changed since the
    project was written while another one's separation stands. Without
    this the window would show voices and the run separate again.
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

    A voice was remembered under the model's label alone. Such a
    project holds one separation, so a bare label belongs to the
    recording it separated; left bare, a second separation would write
    its own voices' names and cameras over them.
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

    Only the recording being listened to offers a way out: the others
    have nothing to break off, and asking for one is answered in the
    name field of the row. Every row is asked about its own recording
    -- two can carry a separation at once, and each says its own
    number. Returns False where the cells are gone, which happens when
    the table has been built again while this was on its way.
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
                mark.setText(note[1])
                mark.setStyleSheet("color: %s" % note[2])
            elif mine:
                mark.setText(T('Separating ...'))
                mark.setStyleSheet("color: %s" % COLOURS["quiet"])
            elif done:
                mark.setText(TN(len(found), 'Separated: %d speaker',
                                'Separated: %d speakers') % len(found))
                mark.setStyleSheet("color: %s" % COLOURS["good"])
            else:
                mark.setText("")
        except RuntimeError:
            return False
    # After the texts and not between them: the rows have to be as
    # tall as what now stands in them, and a line shorter again when
    # that is cleared.
    PROGRAM.cells_laid_out(cells)
    return True


def voices_under(path, said, by_source):
    """The voices to show under one recording, and none where not.

    *said* is the answer stored for this recording: True for several
    speakers, False for a single name, None where nobody has answered
    yet. Only an answer shows them. What was measured used to decide
    while nobody had answered, and that put rows under a field which
    was then made to read "several speakers" so as not to contradict
    them -- the program answering its own question. Nothing measured is
    lost by this: the voices stay in the project and in the cache, and
    saying "several speakers" later brings them up without computing
    again.

    *by_source* holds one separation per recording, and this reads its
    own recording's. With room for one, the voices of a recording
    disappeared the moment a second one was taken apart.

    Whether this machine may run a separation has no bearing on this. A
    result that is already stored is shown either way: switching the
    separation off says "do not compute", not "do not look".
    """
    found = separations_of(by_source, path)
    return found if said and found else []


def longest_stretch(segments, label_name):
    """The longest stretch one voice speaks, in the source's time.

    The longest one, because a name is read off what is heard, and a
    two second scrap between two other people is the worst place to
    judge from.
    """
    for label, parts in (segments or ()):
        if label == label_name and parts:
            return max(parts, key=lambda p: p[1] - p[0])
    return None


def audio_clock_of(file_path, clocks):
    """Return how fast this recorder ran against the common axis.

    The run rewrites every track with this before it reads the speakers
    off it, so the preview applies it too: without it the far end of an
    hour sits a tenth of a second out, and the last shots shown are not
    the ones the run makes.
    """
    b = (clocks or {}).get(path_key(file_path))
    return float(b) if b else 1.0


def audio_start_of(file_path, axis, unset=None):
    """Where an audio file starts: the measurement, else its timecode.

    A clock is set by hand and is set wrong, and nothing here notices:
    measured, a recorder ran 2.35 s ahead of the cameras beside it. The
    axis is tied to the median of every timecode it was given, so one
    wrong clock is outvoted rather than believed -- asking a single one
    throws that away. Where nothing was measured the timecode answers,
    except the clock that was never set: clocks_not_set names those, and
    *unset* is that set, worked out from the axis where none is passed.
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


# How far apart two microphones have to stand before measuring the
# tracks beats listening to them mixed. Measured: above this both name
# 99 % of the speech right, below it the mix pulls ahead by 9.5 points
# at 13 dB and by 23 at 3 dB. The level route is the cheaper one.
MICROPHONES_APART_DB = 20.0


def speaker_mix_file(paths, made_of, folder=""):
    """Add the aligned recordings into the one file the separation hears.

    Measured, the bare sum names 97.6 % of the speech right against
    37.5 % for measuring the same tracks. **Nothing is levelled
    first**: that costs 1.6 points, the recording levels here being as
    large as the bleed. The name comes from *made_of* and not from the
    tracks, or a mix redated every run would cost the separation its key.
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
    # A plain sum, and then one gain over the finished mix so that it
    # cannot clip. One gain over everything moves no track against
    # another, which is the whole point of not levelling them.
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

    The separation is the way for one recording everybody is audible
    on. Where every person has a microphone of their own and those can
    be told apart, measuring the tracks is the better answer and this
    stays out. *apart_db* is how far apart they really stand and *mix*
    makes one file of several: below MICROPHONES_APART_DB the tracks
    no longer answer who is speaking -- measured, 37.5 % right -- and
    the separation listens to all of them at once instead.

    *placeless* are the files the measurement could place nowhere, and
    they are the only ones left out. Not the ones whose sound the
    alignment did not recognise: what a separation needs is a place on
    the axis, and a timecode is a place. Measured on a camera the old
    rule refused for a correlation of 0.44 -- mains hum on its loudness
    curve -- the separation found two speakers in 90 seconds.

    *alone*: a run nobody asked for may only start where the choice is
    no guess, three minutes being the price of a wrong one.

    Returns (path, why): "chosen", "one recording", "camera track",
    "microphones mixed", "several microphones" or "several cameras" --
    for the last two the path is empty -- or "nothing".
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
        # The longest of them, because it covers the most of the
        # episode; where none can be measured the first stands.
        try:
            return max(cameras, key=how_long), "camera track"
        except OSError:
            return cameras[0], "camera track"
    return "", "nothing"


#------------------------------------------------------------- Storage

_SPEAKER_RECIPE = []


def speaker_recipe_mark():
    """A short mark of the way a separation is worked out.

    Without it a changed reckoning hands back yesterday's answer, and
    eight minutes of computing is what nobody repeats to check. Only
    what decides the *stored* segments goes in -- not the whole file,
    and not the widening and gap closing, which happen on use. Hashed,
    not counted: a number needs remembering, source changes by itself.
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
            # Nothing to read the source from. Coarser -- every release
            # throws the separations away -- but it never hands back
            # one that some other reckoning wrote.
            text = VERSION
        _SPEAKER_RECIPE.append(
            hashlib.sha1(text.encode("utf-8")).hexdigest()[:12])
    return _SPEAKER_RECIPE[0]


def speaker_cache_key(path, model_mark="", num_speakers=0):
    """The name a stored separation lives under.

    Path, mtime and size say whether it is still the same recording;
    the model, a number of speakers set by hand and the way the answer
    is worked out are inputs to the measurement and belong in the key
    as well. What is not in it: the language, the time window, the
    offset and the names -- none of them change what was measured.
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

    Not tied to the program version: three minutes of computing are
    not thrown away because a number in the title bar changed. What
    decides is the model, and that is in the key.
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

    [] where none is, so whoever asks may print what it costs before
    starting one.
    """
    return speaker_cache_read(
        speaker_cache_key(source, speaker_model_mark(), count)) or []


def speaker_split_cached(source, count=0, report=None, stopping=None):
    """Separate one recording, or hand back what was stored before.

    The one road to a separation: the window and the run both take it,
    so minutes spent in the window are not spent again at the start of
    the run. Returns (segments, trouble) like speaker_split_run.
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

    Out here rather than inside the window because it decides nothing
    and touches no widget: a file goes in, the passages come out, and
    the three callbacks are the only way it says anything -- *note*
    for how far it has got, *stopping* for whether somebody pressed
    the button, *done* for the result.
    """
    segments, trouble = [], ""
    try:
        if not speaker_split_available():
            # The cell is one line wide in a table; the reason is a
            # traceback's last line and the way back is a pip3 command.
            # Both go where there is room for them, and the cell says
            # where that is.
            trouble_log(speaker_split_why()
                        or speaker_split_missing())
            trouble = T('Speaker separation not available. The log '
                        'says why.')
        if not trouble:
            segments, trouble = speaker_split_cached(
                source, count, report=note, stopping=stopping)
    except Exception as e:
        trouble = T('The speaker separation reports: %s') % str(e)[:140]
    done((source, count, segments, trouble))


def speaker_measure_loop(tracks, bridge, bridge_emit):
    """Read off the tracks who speaks when, in a thread of its own."""
    try:
        out = PROGRAM.speakers_from_tracks(
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

    Counted like the check and the time axis: nothing is said back
    once the list this was started for has gone.
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
    use different machinery, and the shorter of them costs nothing
    where it runs inside the longer. It inherits the separation's
    consent from this start rather than from its end.
    """
    threading.Thread(
        target=speaker_split_loop,
        args=(state, split_run, bridge, bridge_emit, source, count,
              label_run), daemon=True).start()
    speech_words_kick_off(state, language, lambda r: bridge_emit(
        bridge.speakers_heard, r), source)


def speakers_for_project(source, segments, num_speakers=0, called=None):
    """The separation as the project file carries it.

    It travels with the project so a machine that opens it somewhere
    else does not pay the three minutes again. Raw, in the time of the
    source file, exactly as it is stored in the cache.
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

    Returns (source, segments, names). The same test the time axis
    gets: a source that has been changed is measured again rather than
    carried on wrongly.
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

    More than one fits: an audio recording everybody is on and a
    camera whose sound is used are two recordings, each with its own
    voices. The block the run reads stands where a single separation
    stood and the others hang under it in "more". Each is tested on its
    own: one whose recording has changed falls out, the rest stand.
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



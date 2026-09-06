# -*- coding: utf-8 -*-
"""The workbench: what more than one piece of the program reaches for.

A piece of the program, read by beside(). It cannot import the file it
was cut out of -- that file is still being read -- so the program is
handed in and every name used out of it is bound below.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Read straight after the catalogue, so only what stands above that
# line can be bound here. AUDIO_SUFFIXES, RUN_STOP and ffprobe_json
# stand below it and are read through PROGRAM where they are used.
T = PROGRAM.T
TN = PROGRAM.TN
os = PROGRAM.os
re = PROGRAM.re
subprocess = PROGRAM.subprocess


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


#------------------------------------------------- Asked before a run

def only_reading(argv):
    """True where the command line only wants the switch list or the version.

    A question about the command line, asked where the command line is
    read. Reading it needs neither numpy nor ffmpeg.
    """
    return any(a in ("-h", "--help", "--version") for a in argv)


def count_process_starts(where):
    """Write one line per process this program starts, into a file.

    Process starts are what the Windows builder charges for, so the
    suite counts them per test. Off unless VPM_COUNT_STARTS names a
    file. Only Popen is wrapped -- subprocess.run builds one itself,
    and wrapping both counted every run twice.
    """
    was_popen = subprocess.Popen

    def note(argv):
        first = argv if isinstance(argv, str) else (argv[0] if argv else "?")
        try:
            with open(where, "a", encoding="utf-8") as f:
                f.write("%s\n" % os.path.basename(str(first)))
        except OSError:
            return

    class Popen(was_popen):
        def __init__(self, *a, **k):
            note(a[0] if a else k.get("args") or [])
            was_popen.__init__(self, *a, **k)

    subprocess.Popen = Popen

#--------------------------------------------------- Saying it in numbers

def number_text(number, places=1, plus=False):
    """Group the thousands and set the decimal mark, as the language does.

    Not in two passes over the finished text: one language's thousands
    mark is another's decimal mark, and on German the second pass reads
    what the first wrote -- "1,234,5". *places* None writes as many
    places as the number needs, and *plus* signs a positive one.
    """
    # French and Russian group with a space, so nothing here may look
    # for a particular character: the cut is made at the point "%f"
    # wrote, while both halves are still plain digits.
    text = ("%g" % float(number) if places is None
            else "%.*f" % (max(0, int(places)), float(number)))
    ahead = "-" if text.startswith("-") else ("+" if plus else "")
    # "inf" and "nan" carry no digits to group, and int() stops the run
    # over them. A fit with no spread of its own reports its error as
    # inf, so this is reachable, and the word is handed on whole.
    if not text.lstrip("-")[:1].isdigit():
        return ahead + text.lstrip("-")
    whole, _, rest = text.lstrip("-").partition(".")
    # Over a million "%g" writes "1e+06", and int() stops over that too.
    if whole.isdigit():
        whole = format(int(whole), ",d").replace(",", T(","))
    return ahead + whole + (T(".") + rest if rest else "")


def channel_text(count):
    """Say a channel count the way a person would.

    One and two have names; above that the number does the work. An
    unreadable file has no count at all, and then a guess would be worse
    than saying so.
    """
    try:
        count = int(count)
    except (TypeError, ValueError):
        return T('channel count unknown')
    return {1: "mono", 2: "stereo"}.get(
        count, TN(count, '%s channel', '%s channels') % number_text(count, 0))


#--------------------------------------------------------- Running a tool

def safe_filename(name):
    return re.sub(r"[^A-Za-z0-9_.+-]", "_", name) or "track"


def shell_quote(cmd):
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode("utf-8", "replace")[-2000:])
    return p


#----------------------------------------------------- Two recordings in step

PHAT_BAND = (300.0, 3500.0)


def gcc_phat_offset(x, y, rate, max_ms=120.0):
    """Return by how many milliseconds y arrives later than x.

    GCC-PHAT: the cross spectrum is normalised to magnitude one across
    the speech band so only the phase counts. Against reverberation and
    different microphones that beats a plain cross correlation, and it
    measures to a fraction of a sample. Returns (ms, peak sharpness).
    """
    n = 1 << int(np.ceil(np.log2(len(x) + len(y))))
    X, Y = np.fft.rfft(x, n), np.fft.rfft(y, n)
    R = np.conj(X) * Y
    f = np.fft.rfftfreq(n, 1.0 / rate)
    band = (f >= PHAT_BAND[0]) & (f <= PHAT_BAND[1])
    W = np.zeros_like(R)
    W[band] = R[band] / np.maximum(np.abs(R[band]), 1e-12)
    r = np.fft.irfft(W, n)
    size = int(max_ms / 1000.0 * rate)
    corr_window = np.concatenate([r[-size:], r[:size + 1]])
    k = int(np.argmax(corr_window))
    peak = float(corr_window[k])
    if 0 < k < len(corr_window) - 1:
        a, b, c = corr_window[k - 1], corr_window[k], corr_window[k + 1]
        denominator = a - 2 * b + c
        fine = 0.5 * (a - c) / denominator if abs(denominator) > 1e-12 else 0.0
    else:
        fine = 0.0
    return ((k - size + fine) / rate * 1000.0,
            peak / (float(np.std(corr_window)) + 1e-12))


#--------------------------------------------------------------- Video data

def video_facts(path, fps_default=None, tc_default_value=None):
    d = PROGRAM.ffprobe_json(path)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), None)
    if v is None:
        raise RuntimeError(T('no video track in %s') % os.path.basename(path))
    a = [s for s in d.get("streams", []) if s.get("codec_type") == "audio"]
    fps = fps_default
    if not fps:
        r = v.get("avg_frame_rate") or v.get("r_frame_rate") or "30/1"
        try:
            num, the_one = (int(x) for x in r.split("/"))
            fps = num / the_one if the_one else 30.0
        except Exception:
            fps = 30.0
    tc = tc_default_value
    if tc is None:
        # The tracks before the file, for the reason in file_timecode:
        # the track is the camera's clock, the file level is ffmpeg's
        # reading of it, and the camera wins where they disagree.
        for source in [s.get("tags", {}) or {} for s in d.get("streams", [])] +\
                      [d.get("format", {}).get("tags", {})]:
            if source.get("timecode"):
                tc = source["timecode"]
                break
    dur = float(d.get("format", {}).get("duration") or v.get("duration") or 0.0)
    label_text = 0.0
    try:
        num, the_one = (float(x) for x in str(v.get("r_frame_rate")
                                          or "0/0").split("/"))
        label_text = num / the_one if the_one else 0.0
    except Exception:
        label_text = 0.0
    return {"fps": fps, "tc": tc, "duration": dur, "audio": a, "video": v,
            "width": v.get("width"), "height": v.get("height"),
            "nominal": label_text or fps,
            "tags": (d.get("format") or {}).get("tags") or {}}


#--------------------------------------------- What a folder holds already

def finished_tracks_find(base):
    """Report whether processed tracks from Auphonic are already there.

    After a run the output folder holds a subfolder with the single
    tracks, and choosing it again usually means reassembling rather
    than uploading, so that is offered.
    """
    if not base or not os.path.isdir(base):
        return None
    for name in ("auphonic-tracks",):
        p = os.path.join(base, name)
        if os.path.isdir(p) and any(
                os.path.splitext(f)[1].lower() in PROGRAM.AUDIO_SUFFIXES
                for f in os.listdir(p)):
            return p
    return None


#---------------------------------------------------- Breaking a run off

class Stopped(Exception):
    """The run was broken off from the window."""

def stop_wanted():
    """Whether somebody has asked for the run to stop."""
    return bool(PROGRAM.RUN_STOP["wanted"])

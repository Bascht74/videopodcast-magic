# -*- coding: utf-8 -*-
"""The herald: what the run says of itself, and what it starts.

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and every name this piece uses out of it is bound below, by name.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that these
# read as they did in the one file. Three names are missing, and the
# block under the list says which and why.

BAD_MARK = PROGRAM.BAD_MARK
T = PROGRAM.T
THREAD_BUFFER = PROGRAM.THREAD_BUFFER
THREAD_SHARE = PROGRAM.THREAD_SHARE
VERSION = PROGRAM.VERSION
_LOG_ASIDE = PROGRAM._LOG_ASIDE
atexit = PROGRAM.atexit
contextlib = PROGRAM.contextlib
group_text = PROGRAM.group_text
log_aside = PROGRAM.log_aside
log_path = PROGRAM.log_path
os = PROGRAM.os
outside_flush = PROGRAM.outside_flush
outside_say = PROGRAM.outside_say
platform = PROGRAM.platform
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
threading = PROGRAM.threading
time = PROGRAM.time


# Two of the three are bent while the run goes on, and a copy taken
# here would answer with the value of the run before: the window sets
# OUTPUT_SINK and PROGRESS_SINK on the program object, which is a
# write the pieces are never told about. Both stay over there.

# python_note is the third. It comes out of the material, which is read
# further down than this piece, so a copy taken here would find
# nothing. It is read as PROGRAM.python_note where the log header
# wants it.


def show_progress(text, share=None):
    # Where this thread runs inside a parallel batch, its progress goes into
    # the shared bar rather than onto a line of its own -- three bars above
    # each other would be unreadable.
    own_flag = THREAD_SHARE.get(threading.get_ident())
    if own_flag is not None:
        own_flag.report(0.0 if share is None else share, text)
        return
    step_report(share)
    draw_progress_bar(text, share)


def progress_from_line(line, duration):
    """Extract the progress fraction from a line of "ffmpeg -progress".

    Returns a number between 0 and 0.999, or None if the line says nothing
    about progress. Four places read this output and should read it the same
    way.
    """
    if isinstance(line, bytes):
        line = line.decode("utf-8", "replace")
    line = line.strip()
    if not line.startswith("out_time_ms=") or not duration or duration <= 0:
        return None
    try:
        return min(0.999, int(line.split("=")[1]) / 1e6 / float(duration))
    except ValueError:
        return None


def draw_progress_bar(text, share=None):
    """Write one progress line, directly."""
    if share is None:
        line = "\r  %s" % text
    else:
        line = "\r  %s [%-30s] %3.0f %%" % (text, "#" * int(share * 30),
                                             share * 100)
    if PROGRAM.OUTPUT_SINK:
        PROGRAM.OUTPUT_SINK(line)
    else:
        sys.stdout.write(line + " " * 6)
        sys.stdout.flush()


class SharedProgressBar(object):
    """One progress bar for everything running at once.

    Every file reports its own share and the average is displayed. Because
    each share can only rise, the bar never jumps back.
    """

    def __init__(self, text, how_many):
        self.text, self.how_many = text, max(1, how_many)
        self.status, self.lock = {}, threading.Lock()
        self.last_time = -1.0
        self.stream = None      # the real output, past the buffer

    def show(self, share):
        line = "\r  %s [%-30s] %3.0f %%" % (
            T('%s (%s files)') % (self.text, group_text(self.how_many)),
            "#" * int(share * 30), share * 100)
        if PROGRAM.OUTPUT_SINK:
            PROGRAM.OUTPUT_SINK(line)
            return
        # Past the buffer: the bar belongs on the real output, otherwise it
        # only appears once the file is finished.
        stream = self.stream or sys.stdout
        try:
            stream.write(line + " " * 6)
            stream.flush()
        except Exception:
            pass

    def report(self, who, share):
        with self.lock:
            self.status[who] = share
            total = sum(self.status.values()) / float(self.how_many)
            # At most 99 % while the run is not through. The last file reports
            # itself done before its report leaves the buffer, and a bar at 100
            # % with something still arriving below looks like a hang.
            total = min(0.99, total)
            if abs(total - self.last_time) < 0.005:
                return          # nothing new, so no second line
            self.last_time = total
        # The bar in the footer wants the joint figure, not each file's:
        # several threads reporting one at a time would make it jump to
        # whichever file happens to be furthest along.
        step_report(total)
        self.show(total)

    def stop(self):
        self.show(1.0)
        write_through("\n")


class Share(object):
    """The progress of one file, assembled from sections.

    The sections are roughly weighted: measure, write, verify. Within a
    section the ffmpeg progress is passed through. It never goes back.
    """

    def __init__(self, progress_bar, who):
        self.progress_bar, self.who = progress_bar, who
        self.begins, self.until, self.highest = 0.0, 1.0, 0.0
        self.done = set()

    def segment(self, begins, until):
        self.begins, self.until = begins, until
        self.report(0.0)

    def report(self, share, text=None):
        # The bar itself runs jointly; every step still enters this file's
        # report as soon as it is through. Otherwise the lines one knows from a
        # sequential run would be missing there.
        if text and share >= 0.999 and text not in self.done:
            self.done.add(text)
            write_through("  %s [%s] 100 %%\n" % (text, "#" * 30))
        value = self.begins + (self.until - self.begins) * max(0.0, min(1.0, share))
        if value > self.highest:
            self.highest = value
        self.progress_bar.report(self.who, self.highest)


# Which stage the run is in, for the line the bar carries.
_STEP = {"name": ""}


def step_begin(name):
    """Say that the run has reached a stage. Ends the one before it."""
    _STEP["name"] = name
    if PROGRAM.PROGRESS_SINK:
        try:
            PROGRAM.PROGRESS_SINK(name, None)
        except Exception:
            pass


def step_report(share):
    """Say how far the current stage is, 0 to 1."""
    if PROGRAM.PROGRESS_SINK and _STEP["name"] and share is not None:
        try:
            PROGRAM.PROGRESS_SINK(_STEP["name"], float(share))
        except Exception:
            pass


def run_stages(multitrack, cameras, auphonic, speakers=None):
    """The stages of a run and what share of the bar each is worth.

    The weights are proportions measured on real jobs, not guesses at a
    clock: writing the camera files reads and re-encodes every camera in
    full and takes longer than everything before it together, so it gets
    most of the bar. Pulling the audio out of the cameras is the other
    long one. A stage that will not happen is not in the list.
    """
    cameras = max(0, int(cameras))
    out = [("plan", 1.0, T('Reading the plan'))]
    # Only the multitrack path pulls the audio out of the cameras; the
    # simple path aligns against them and leaves them alone. Listed for
    # both, the bar held a fifth of itself for a stage that never
    # reported, and then jumped that fifth in one go when the next one
    # began.
    if cameras and multitrack:
        out.append(("camera audio", 5.0 * cameras,
                    T('Audio out of the cameras')))
    out.append(("time base", 4.0, T('Common time axis')))
    if auphonic:
        out.append(("auphonic", 8.0, T('Processing at auphonic.com')))
    else:
        out.append(("loudness", 4.0, T('Loudness and levels')))
    if multitrack if speakers is None else speakers:
        out.append(("speakers", 3.0, T('Who speaks when')))
    if cameras:
        out.append(("cameras", 12.0 * cameras,
                    T('Writing the camera files')))
    out.append(("result", 1.0, T('Handover and result')))
    return out


class ProgressPlan(object):
    """One bar for a job whose steps take very different lengths.

    Each step carries a weight, and the bar is the weighted sum of what
    the steps report. Three things make it readable rather than merely
    correct:

    It never goes back. A step added while the job runs lowers the
    arithmetic, and a bar jumping backwards reads as a fault even though
    nothing was lost.

    A step that cannot say how far it is creeps towards its own end
    instead of standing still. The creep slows as it approaches and
    never reaches the boundary, so the bar keeps moving without ever
    claiming a step is further along than it is.

    Long steps get room in proportion to how long they take. Pulling the
    audio out of an hour of 4K and reading a wav file are one step each,
    and giving them the same share of the bar would make it useless.
    """

    def __init__(self):
        self.order = []
        self.weight = {}
        self.share = {}
        self.real = {}
        self.caption = {}
        self.began = set()
        self.highest = 0.0

    def clear(self):
        self.__init__()

    def add(self, name, weight=1.0, caption=""):
        """Announce a step. Announcing it twice changes nothing."""
        if name not in self.weight:
            self.order.append(name)
            self.weight[name] = max(0.01, float(weight))
            self.share[name] = 0.0
        if caption:
            self.caption[name] = caption

    def begin(self, name, caption="", weight=1.0):
        """Mark a step as under way without claiming a figure for it.

        For work that reports nothing at all until it is finished. Such
        a step may creep the whole way to its ceiling; one that does
        report stays close to what it reported.
        """
        self.add(name, weight, caption)
        self.began.add(name)

    def report(self, name, share, caption=""):
        """Say how far one step is. Unknown steps count as weight 1."""
        self.begin(name, caption)
        value = max(0.0, min(1.0, float(share)))
        self.real[name] = max(self.real.get(name, 0.0), value)
        self.share[name] = max(self.share[name], value)

    def done(self, name):
        self.report(name, 1.0)

    def drop(self, names):
        """Forget steps whose work was called off.

        A step left standing half way is neither finished nor being
        worked on, and it holds the bar up for ever. Marking it done
        instead would put the bar at the end of work nobody did.
        """
        for name in list(names):
            if name not in self.weight:
                continue
            self.order.remove(name)
            del self.weight[name]
            del self.share[name]
            self.real.pop(name, None)
            self.caption.pop(name, None)
            self.began.discard(name)
        if not self.order:
            self.highest = 0.0

    def creep(self, seconds, reach=0.93, half_life=30.0, lead=0.12,
              beyond=0.99, slower=10.0):
        """Let the running steps drift on, but not into a lie.

        Asymptotic: half the remaining distance every half_life. A step
        that has reported a figure may only creep a little past it --
        otherwise the bar would sit near the end of a step that is a
        tenth of the way through. A step that reports nothing at all has
        nothing to be held to and may creep the whole way.

        Past the ceiling it goes on at a tenth of the speed, up to
        *beyond*. Something that runs far longer than expected should
        still show life; at a tenth of the pace that reads as "nearly
        there, still working" rather than as a promise.
        """
        if seconds <= 0 or half_life <= 0:
            return
        part = 1.0 - 0.5 ** (float(seconds) / float(half_life))
        crawl = 1.0 - 0.5 ** (float(seconds) / (float(half_life) * slower))
        for name in self.began:
            here = self.share[name]
            top = (reach if name not in self.real
                   else min(reach, self.real[name] + lead))
            # A hair short of the ceiling counts as at it. The approach
            # is asymptotic and would otherwise never cross, so the slow
            # stretch past it could never be reached at all.
            if here < top - 0.001:
                self.share[name] = here + (top - here) * part
            elif top >= reach and here < beyond:
                here = max(here, top)
                self.share[name] = here + (beyond - here) * crawl

    def total(self):
        """The whole job as one number, 0 to 1, and never falling."""
        weight = sum(self.weight.values())
        if not weight:
            return self.highest
        now = sum(self.weight[n] * self.share[n] for n in self.order) / weight
        self.highest = max(self.highest, now)
        return self.highest

    def busy(self):
        """Report whether anything is still outstanding."""
        return any(self.share[n] < 0.999 for n in self.order)

    def running(self):
        """The steps under way, in the order they were announced."""
        return [n for n in self.order
                if n in self.began and self.share[n] < 0.999]

    def line(self):
        """One line for beside the bar: what is being worked on."""
        busy = self.running()
        if not busy:
            return ""
        first = self.caption.get(busy[0]) or busy[0]
        if len(busy) == 1:
            return first
        return T('%s and %s more') % (first, group_text(len(busy) - 1))


def write_through(text):
    """Print text; buffer it first when running in a parallel thread."""
    p = THREAD_BUFFER.get(threading.get_ident())
    if p is not None:
        p.append(text)
        return
    if PROGRAM.OUTPUT_SINK:
        PROGRAM.OUTPUT_SINK(text)
    else:
        sys.stdout.write(text)
        sys.stdout.flush()


class ThreadOutput(object):
    """Stand-in for sys.stdout while several threads are writing."""

    def __init__(self, real):
        self.real = real

    def write(self, text):
        p = THREAD_BUFFER.get(threading.get_ident())
        if p is not None:
            p.append(text)
            return len(text)
        return self.real.write(text)

    def flush(self):
        try:
            self.real.flush()
        except Exception:
            pass


def running_from():
    """Which copy of the script this is.

    Not sys.argv[0]: the restart after an update and the call out of
    DaVinci Resolve both set it to something else. __file__ is the file
    that was really loaded.
    """
    try:
        return os.path.abspath(PROGRAM.__file__)
    except Exception:
        return "?"


# The mark the window's own lines carry, so they can be picked out of a
# log that also holds what ffmpeg and Qt write: grep for it.
GUI_MARK = "[GUI]"


# What a speaker reading leaves behind in the state. Cleared together,
# or a reading of one project is read back in the next.
SPEAKER_STATE = ("measure_failed", "speakers_measured", "speakers_measuring")


def speakers_still_wanted(state):
    """Whether the speakers still have to be worked out.

    Not while one run is under way and not after one failed -- it would
    fail the same way and cost the same minutes. And not where a
    finished run already knows them: measuring again would relabel its
    preview as measured from the raw recordings.
    """
    return not (state.get("speakers_measured")
                or state.get("speakers_measuring")
                or state.get("measure_failed")
                or state.get("cut_basis") in ("run", "auphonic"))


# How close a player has to be to a jump before it counts as arrived.
# One second: a seek lands on the key frame before the mark, and with
# long GOPs on 4K material that is most of a second away.
SPOT_ARRIVED_MS = 1000

# Waiting for a jump to land, as the cut player's Seeker does -- which
# is why that one switches cameras cleanly. Measured on 18 and 27 GB
# files: a file falls back to its front 18 to 88 ms after reporting
# itself loaded. A seek is a request, not a command.
SEEK_HIT_MS = 350
SEEK_AGAIN_MS = 120
SEEK_PATIENCE_S = 5.0
SEEK_SETTLE_S = 0.5


def gui_log(text):
    """Write down what the window just did.

    A window tells nobody afterwards what it was showing, where it
    stood, or which of the two reckonings a position came out of. The
    log is what somebody can send along with a complaint. It lands in
    the file: redirect_console has the descriptors by then.
    """
    print("%s %s  %s" % (GUI_MARK, time.strftime("%H:%M:%S"), text))


def outside_what(cmd):
    """The tool and the file one call to another program is about."""
    parts = [str(x) for x in ([cmd] if isinstance(cmd, str) else (cmd or []))]
    if not parts:
        return "", ""
    tool = os.path.basename(parts[0])
    # A python of its own runs the speaker separation, and "python3"
    # says nothing about what is taking the minutes. The script it is
    # given is the name worth printing.
    if tool.startswith("python") and len(parts) > 1:
        tool = os.path.basename(parts[1]).replace(".py", "") or tool
    for i, one in enumerate(parts):
        if one == "-i" and i + 1 < len(parts):
            return tool, os.path.basename(parts[i + 1])
    # ffprobe takes its file last and without a switch in front of it.
    tail = parts[-1]
    return tool, os.path.basename(tail) if not tail.startswith("-") else ""


# Otherwise the last run of identical calls is never written: nothing
# different comes after it to push it out.
atexit.register(outside_flush)


def outside_log(cmd, seconds=None):
    """Write down one call to a program outside this one.

    Every call is here because subprocess is wrapped once below, so a
    new call site cannot forget to say so.
    """
    tool, about = outside_what(cmd)
    if tool:
        outside_say(tool, about, seconds)


@contextlib.contextmanager
def outside_work(tool, about):
    """Time work that runs in this process but costs like an outside call.

    The models are not subprocesses, so the wrapper below does not see
    them -- and they are the longest thing a run does. Said even where
    it fails: work that broke off after four minutes still took them.
    """
    began = time.monotonic()
    try:
        yield
    finally:
        outside_say(tool, about, time.monotonic() - began)


_subprocess_run, _subprocess_popen = subprocess.run, subprocess.Popen


# run() opens a Popen of its own, so without this every call it makes
# would be said twice. Per thread: the window runs its prework in
# several at once, and one counter for all of them would silence the
# wrong lines.
_in_run = threading.local()


def run_outside(cmd, *rest, **named):
    """subprocess.run, with the call and how long it took written down."""
    began = time.monotonic()
    _in_run.here = getattr(_in_run, "here", 0) + 1
    try:
        return _subprocess_run(cmd, *rest, **named)
    finally:
        _in_run.here -= 1
        outside_log(cmd, time.monotonic() - began)


class SaysWhenDone(_subprocess_popen):
    """A Popen that says how long it ran when somebody waits for it.

    Started and finished are two lines because a long call is
    interesting while it runs -- and without the second one a process
    that took four minutes cannot be told from one that took four
    seconds.
    """

    def __init__(self, cmd, *rest, **named):
        self._began = time.monotonic()
        self._said = False
        self._cmd = cmd
        _subprocess_popen.__init__(self, cmd, *rest, **named)

    def _say_done(self):
        if not self._said:
            self._said = True
            outside_log(self._cmd, time.monotonic() - self._began)

    def wait(self, *rest, **named):
        try:
            return _subprocess_popen.wait(self, *rest, **named)
        finally:
            self._say_done()

    def communicate(self, *rest, **named):
        try:
            return _subprocess_popen.communicate(self, *rest, **named)
        finally:
            self._say_done()


def popen_outside(cmd, *rest, **named):
    """subprocess.Popen, saying both when it started and when it ended."""
    if getattr(_in_run, "here", 0):
        return _subprocess_popen(cmd, *rest, **named)
    outside_log(cmd)
    return SaysWhenDone(cmd, *rest, **named)


def watch_outside_calls():
    """Route every call to another program past the log.

    Wrapped here rather than at the 46 call sites: what is asked of a
    call site is forgotten by the next one somebody writes. Called from
    main(), where somebody has asked for a run -- done while the file
    is read, the replacement would reach into whoever imported it, and
    their processes have nothing to do with a run.
    """
    subprocess.run = run_outside
    subprocess.Popen = popen_outside


def trouble_log(text):
    """Write down what the window is showing in red.

    A red mark in the window is gone the moment the row is drawn
    again, and the complaint about it arrives hours later. In the log
    it keeps, with the time beside it.
    """
    said = " ".join(str(text or "").split())
    if said:
        log_aside("%s %s  %s"
                  % (BAD_MARK, time.strftime("%H:%M:%S"), said[:200]))


def redirect_console():
    """Redirect everything that would go to the terminal into a file.

    Not only our own messages: the file descriptors themselves are
    redirected so that what Qt and ffmpeg write underneath Python comes
    along. One backup of the previous run is kept.
    """
    file_path = log_path()
    if not file_path:
        return None
    # The aside handle may already stand open on the file about to be
    # renamed -- the tool check runs a process before this, and every
    # outside call is written down. Left alone, the whole run's aside
    # lines would land in the previous run's log. Measured 4.9.2026.
    while _LOG_ASIDE:
        kept = _LOG_ASIDE.pop()
        try:
            if kept is not None:
                kept.close()
        except Exception:
            kept = None
    # The backup is called ..._1.log rather than ....log.1 --
    # otherwise Finder does not know the extension and will not open it.
    before_value = os.path.splitext(file_path)[0] + "_1.log"
    try:
        old = file_path + ".1"
        if os.path.exists(old):
            os.unlink(old)          # from older versions
    except OSError:
        pass
    try:
        if os.path.exists(file_path):
            os.replace(file_path, before_value)
        file = open(file_path, "w", buffering=1, encoding="utf-8",
                     errors="replace")
        # Header: version, time, machine -- and which copy of the
        # script this was. Several runnable copies of the same version
        # are the normal case here: the snapshot the test suite runs
        # against, the one pip installed, a checkout somebody started
        # by its path. They share one log file, and without the path
        # nobody can tell later why one run came out different from
        # another.
        file.write("Video Podcast Magic %s   %s   %s %s   %s\n%s\n\n"
                    % (VERSION,
                       time.strftime("%Y-%m-%d %H:%M:%S"),
                       platform.system(), platform.release(),
                       PROGRAM.python_note(), running_from()))
        os.dup2(file.fileno(), 1)
        os.dup2(file.fileno(), 2)
        # The aside lines go through this same handle from now on: two
        # handles on one file keep two write positions, and whichever
        # is behind writes over what the other put there. Measured
        # 5.9.2026 -- a line came out as "rogram list is settled".
        _LOG_ASIDE.append(file)
    except Exception:
        return None
    return file_path

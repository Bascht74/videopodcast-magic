# -*- coding: utf-8 -*-
"""What auphonic.com puts around the sound sent is cut from what it returns.

auphonic.com is never spoken to: curl is replaced by a stand-in whose
reply is the sound sent with a jingle in front and a tone behind, as
the free plan hands it back. In order: a single production returned as
WAV keeps a file as long as what was sent, lined up with it to the
sample, and the log says what was cut at each end; the same returned
as MP3, to within a frame; a multitrack production cuts every track; a
reply no longer than what was sent is left untouched, and one in which
the sound sent cannot be found is left as it came, and said. Where the
file lines up is measured by a plain cross-correlation, not the
program's own measurement.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import time
import numpy as np
import the_program

SCRIPT = the_program.SCRIPT
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
SR = vpm.SR
D = tempfile.mkdtemp(prefix="jingle_")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


SENT_S = 20.0      # what goes up
FRONT_S = 6.4      # the jingle put in front, as measured on 27.9.2026
BEHIND_S = 2.0     # and a tone put behind
SAMPLE_S = 1.0 / SR
# A lossy file is cut by copying whole frames, so it may keep up to one
# MP3 frame (24 ms at 48 kHz) more than was sent, and its decoder adds
# its own priming: within one picture frame at 25 fps.
LOSSY_S = 0.04


def speech_like(seconds, seed):
    """Voiced syllables of changing pitch with pauses between them."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    x = np.zeros(n)
    t = 0
    while t < n - SR:
        length = int(rng.uniform(0.3, 1.2) * SR)
        f0 = rng.uniform(90, 190)
        k = np.arange(length)
        piece = sum(np.sin(2 * np.pi * f0 * h * k / SR) / h
                    for h in range(1, 12))
        x[t:t + length] += 0.3 * piece * np.hanning(length)
        t += length + int(rng.uniform(0.1, 0.8) * SR)
    return x + 0.001 * rng.normal(size=n)


def tone(seconds, hz):
    k = np.arange(int(round(seconds * SR)))
    return 0.2 * np.sin(2 * np.pi * hz * k / SR) \
        * (1 + np.sin(2 * np.pi * 3 * k / SR)) / 2


def write(path, x):
    """Samples into a file of the kind the name says, by ffmpeg."""
    raw = path + ".f32"
    np.asarray(x, dtype=np.float32).tofile(raw)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR),
                    "-ac", "1", "-i", raw, "-y", path], check=True)
    os.unlink(raw)
    return path


def samples(path):
    """The file decoded by ffmpeg itself, not through the program.

    Nothing to decode is no samples, so a crashed step reaches its check.
    """
    if not path or not os.path.isfile(path):
        return np.zeros(0)
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le",
                          "-ac", "1", "-ar", str(SR), "-"],
                         stdout=subprocess.PIPE).stdout
    return np.frombuffer(out, dtype=np.float32).astype(np.float64)


def lag_of(sent, kept):
    """Seconds into *kept* where *sent* begins, by one cross-correlation."""
    n = 1 << int(np.ceil(np.log2(len(sent) + len(kept))))
    cc = np.fft.irfft(np.fft.rfft(kept, n) * np.conj(np.fft.rfft(sent, n)), n)
    k = int(np.argmax(cc))
    return (k if k < n // 2 else k - n) / float(SR)


def digest(path):
    if not path or not os.path.isfile(path):
        return "no file"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


class Server:
    """curl, answering from a table; a download copies a prepared reply."""

    def __init__(self, replies):
        self.replies = replies      # file name at auphonic.com -> local file

    def __call__(self, key, arguments, output_binary=False, progress=False):
        if "-o" in arguments:
            url = arguments[-1]
            shutil.copyfile(self.replies[url.rsplit("/", 1)[1]],
                            arguments[arguments.index("-o") + 1])
            return ""
        if any("simple/productions" in a for a in arguments):
            return json.dumps({"status_code": 200, "data": {"uuid": "U1"}})
        return json.dumps({"status_code": 200, "data": {
            "uuid": "U1", "status": 3, "status_string": "Done",
            "output_files": [
                {"filename": name,
                 "download_url": "https://auphonic.com/download/" + name}
                for name in self.replies]}})


def single(sent_path, reply_path, name):
    """One single production through the stand-in: (kept file, log)."""
    vpm._curl_call = Server({name: reply_path})
    log = io.StringIO()
    kept = None
    with contextlib.redirect_stdout(log):
        try:
            kept = vpm.run_single_production(
                sent_path, "P", "the preset", "FAKEKEY-0000",
                os.path.join(D, "back_" + os.path.splitext(name)[1][1:]),
                wait_s=60)
        except Exception as e:
            print("the production raised: %s" % " ".join(str(e).split())[:200])
    return kept, log.getvalue()


def said(line, name, seconds):
    return vpm.T(line) % (name, vpm.number_text(seconds, 1))


START = '  %s: auphonic.com added %s s at the start -- cut away'
END = '  %s: auphonic.com added %s s at the end -- cut away'

sent = speech_like(SENT_S, seed=3)
sent_path = write(os.path.join(D, "Guest.wav"), sent)
with_jingle = np.concatenate([tone(FRONT_S, 660), 0.8 * sent,
                              tone(BEHIND_S, 440)])

print("A single production returned as WAV")
kept, log = single(sent_path, write(os.path.join(D, "reply.wav"),
                                    with_jingle), "Guest.wav")
got = samples(kept)
check("a WAV comes back as long as the sound that was sent",
      abs(len(got) / float(SR) - SENT_S) <= SAMPLE_S,
      "%.4f s kept against %.4f s sent, %.4f s came back"
      % (len(got) / float(SR), SENT_S, FRONT_S + SENT_S + BEHIND_S))
lag = lag_of(sent, got)
check("the sound sent begins where the WAV kept begins",
      abs(lag) <= SAMPLE_S,
      "it begins %+.4f s into the file kept, 0 wanted" % lag)
check("the log says how much was cut at the start",
      said(START, "Guest.wav", FRONT_S) in log,
      "wanted %r, the log said: %s" % (said(START, "Guest.wav", FRONT_S),
                                       " / ".join(log.split("\n")[-4:])))
check("the log says how much was cut at the end",
      said(END, "Guest.wav", BEHIND_S) in log,
      "wanted %r, the log said: %s" % (said(END, "Guest.wav", BEHIND_S),
                                       " / ".join(log.split("\n")[-4:])))

print("\nThe same returned as MP3")
kept, log = single(sent_path, write(os.path.join(D, "reply.mp3"),
                                    with_jingle), "Guest.mp3")
got = samples(kept)
check("an MP3 comes back as long as the sound sent, within a frame",
      abs(len(got) / float(SR) - SENT_S) <= LOSSY_S,
      "%.4f s kept against %.4f s sent, %.2f s allowed"
      % (len(got) / float(SR), SENT_S, LOSSY_S))
lag = lag_of(sent, got)
check("the sound sent begins where the MP3 kept begins, within a frame",
      abs(lag) <= LOSSY_S,
      "it begins %+.4f s into the file kept, %.2f s allowed" % (lag, LOSSY_S))
check("the log reads an MP3's length and names what was cut behind it",
      said(END, "Guest.mp3", BEHIND_S) in log,
      "wanted %r, the log said: %s" % (said(END, "Guest.mp3", BEHIND_S),
                                       " / ".join(log.split("\n")[-4:])))

print("\nA multitrack production")
second = speech_like(SENT_S, seed=5)
tracks = [{"name": "Host", "axis": sent_path},
          {"name": "Guest", "axis": write(os.path.join(D, "Guest2.wav"),
                                          second)}]
zipped = {"Host": write(os.path.join(D, "reply_host.wav"), with_jingle),
          "Guest": write(os.path.join(D, "reply_guest.wav"), np.concatenate(
              [tone(FRONT_S, 660), 0.8 * second, tone(BEHIND_S, 440)]))}


def fetched(key, p, names, target_folder, base):
    """What download_results hands back, without a ZIP to unpack."""
    os.makedirs(target_folder, exist_ok=True)
    out = {}
    for name in names:
        out[name] = os.path.join(target_folder, name + ".wav")
        shutil.copyfile(zipped[name], out[name])
    return out


class MultiServer:
    def __call__(self, key, arguments, output_binary=False, progress=False):
        joined = " ".join(arguments)
        if "/api/productions.json" in joined or "upload.json" in joined:
            return json.dumps({"status_code": 200, "data": {
                "uuid": "U2", "multi_input_files": [
                    {"id": t["name"], "input_file": "x"} for t in tracks]}})
        return json.dumps({"status_code": 200, "data": {
            "uuid": "U2", "status": 3, "status_string": "Done"}})


vpm._curl_call = MultiServer()
vpm.read_preset = lambda key, uuid: {"is_multitrack": True}
vpm.find_production_by_title = lambda key, title: None
vpm.build_multitrack_request = lambda *a, **k: {}
vpm.download_results = fetched
log = io.StringIO()
result = None
with contextlib.redirect_stdout(log):
    try:
        result = vpm.run_multitrack_production(
            "FAKEKEY-0000", "PRESET", "Episode", tracks,
            os.path.join(D, "multi"), wait_s=60)
    except Exception as e:
        print("the production raised: %s" % " ".join(str(e).split())[:200])
lengths = dict((n, len(samples(p)) / float(SR))
               for n, p in (result or {}).items())
check("every track of a multitrack production is cut to what was sent",
      sorted(lengths) == ["Guest", "Host"]
      and all(abs(s - SENT_S) <= SAMPLE_S for s in lengths.values()),
      "kept %s against %.4f s sent each%s"
      % (", ".join("%s %.4f s" % kv for kv in sorted(lengths.items()))
         or "nothing", SENT_S, "" if result else
         " -- " + " / ".join(log.getvalue().split("\n")[-3:])))

print("\nA reply with nothing added, and one that is not the sound sent")
plain = write(os.path.join(D, "plain.wav"), 0.8 * sent)
before = digest(plain)
kept, log = single(sent_path, plain, "Plain.wav")
check("a reply no longer than what was sent is left untouched",
      digest(kept) == before and "cut away" not in log,
      "file %s against %s before%s" % (digest(kept), before,
                                       ", and the log says it cut"
                                       if "cut away" in log else ""))
stranger = write(os.path.join(D, "stranger.wav"),
                 speech_like(SENT_S + FRONT_S, seed=9))
before = digest(stranger)
kept, log = single(sent_path, stranger, "Stranger.wav")
check("a reply the sound sent cannot be found in is left as it came",
      digest(kept) == before,
      "file %s against %s before, %.3f s long"
      % (digest(kept), before, len(samples(kept)) / float(SR)))
wanted = vpm.T('  %s came back %s s longer than it went up, and where the '
               'sound sent\n  begins in it could not be measured -- left as '
               'it came.').split("%s")[-1].strip()
check("a reply that cannot be placed is said, not cut in silence",
      wanted in log,
      "wanted %r, the log said: %s" % (wanted,
                                       " / ".join(log.split("\n")[-4:])))

shutil.rmtree(D, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)

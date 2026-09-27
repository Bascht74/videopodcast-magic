# -*- coding: utf-8 -*-
"""A free account's long Multitrack production is refused, and the reason said.

Against auphonic.com itself, and it may spend credit: two tracks of an
hour each, made by ffmpeg -- VPM_LIVE_MINUTES sets another length --
through the account's first multitrack preset. auphonic.com lets a free
account try Multitrack only for productions shorter than twenty
minutes; the program says so as a hint, tries anyway, and leaves the
answer to auphonic.com. The test prints what the program said, reads
the production back by its title -- status, error_code, error_message
-- and deletes it.

Leaves itself out on a paying account, where the limit does not hold
and the run would spend two hours of credit. The checks: the account is
free; auphonic.com refused the production at its start and the run did
not come back with tracks; auphonic.com's own message stands in what
the program said; no credit was spent; the production is gone at the
end. A step that throws is a failed judgement and not a traceback.
"""
PLATFORM_BOUND = True
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import auphonic_ground as ground

ground.gate(spends=True)

began = time.time()
done = 0
bad = []
SECONDS = int(float(os.environ.get("VPM_LIVE_MINUTES", "60")) * 60)
# auphonic.com's status for a production it gave up on.
ERROR = 2
# What credit may move without anything being charged: auphonic.com
# charges whole minutes, so a thousandth of an hour is less than one.
SLACK_H = 0.001


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def said(e):
    """An exception as one short line."""
    return " ".join(str(e).split())[:300]


def a_track(path, pitch, seed):
    """SECONDS of a tone that rises and falls, mono MP3."""
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "sine=frequency=%d:duration=%d:sample_rate=16000" % (pitch, SECONDS),
         "-af", "tremolo=f=%.1f:d=0.8,volume=0.5" % (2.5 + seed * 0.7),
         "-ac", "1", "-b:a", "48k", path], check=True)
    return path


vpm = ground.program()
key, origin = ground.the_key(vpm)
account = vpm.account_credit(key) or {}
print("0. The account: paying = %r, credit %.4f h"
      % (account.get("paying"), account.get("hours") or 0))
if account.get("paying") is not False:
    ground.leave_out("the account is not a free one (is_paying_user = %r), "
                     "so the twenty-minute limit does not hold for it"
                     % account.get("paying"))
check("the account is a free one", account.get("paying") is False,
      "is_paying_user = %r" % account.get("paying"))

preset = ground.a_preset(vpm, key, multitrack=True)
folder = tempfile.mkdtemp(prefix="vpm_auphonic_live_")
title = ground.a_test_title("limit")
uuid = None
try:
    tracks = [{"name": name, "axis": a_track(
        os.path.join(folder, "%s.mp3" % name.lower()), pitch, i)}
        for i, (name, pitch) in enumerate((("Guest", 140),
                                           ("Presenter", 110)))]
    print("   two tracks of %d s made, %s"
          % (SECONDS, ", ".join("%s %.1f s" % (t["name"], ground.measured(
              t["axis"])[0]) for t in tracks)))

    print("\n1. The run, as a run does it -- what the program says")
    out = io.StringIO()
    result, why = None, ""
    t0 = time.time()
    try:
        with contextlib.redirect_stdout(out):
            result = vpm.run_multitrack_production(
                key, preset, title, tracks, os.path.join(folder, "back"),
                wait_s=5400)
    except Exception as e:
        why = said(e)
    took = time.time() - t0
    for line in out.getvalue().splitlines():
        print("   | " + vpm.strip_marks(line))
    print("   ended after %.0f s with: %s"
          % (took, ("error: " + why) if why else "tracks %r"
             % sorted((result or {}).keys())))

    print("\n2. The production read back by its title")
    for t, u in ground.productions(vpm, key):
        if t == title:
            uuid = u
    print("   production found: %s" % ("yes" if uuid else "no"))
    info = {}
    if uuid:
        d = vpm._parse_json(vpm._curl_call(
            key, [vpm.AUPHONIC + "/api/production/%s.json" % uuid]))
        info = d.get("data") or {}
        for k in ("status", "status_string", "error_code", "error_message",
                  "warning_message", "length", "used_credits"):
            print("   %-20s %r" % (k, info.get(k)))
    check("auphonic.com refused the production at its start",
          info.get("status") == ERROR,
          "status %r (%r), wanted %d" % (info.get("status"),
                                         info.get("status_string"), ERROR))
    check("the run does not come back with tracks as if all were well",
          bool(why) and not result, why or "came back %r" % (result,))
    message = (info.get("error_message") or "").strip()
    check("auphonic.com's own message is in what the program said",
          bool(message) and " ".join(message.split())[:60] in
          " ".join((why + " " + out.getvalue()).split()),
          "auphonic.com: %r" % message[:200])
except Exception as e:
    bad.append("the test stopped half way [%s: %s]"
               % (type(e).__name__, said(e)))
finally:
    shutil.rmtree(folder, ignore_errors=True)

print("\n3. What it cost, and what is left behind")
after = vpm.account_credit(key) or {}
before_h, after_h = account.get("hours"), after.get("hours")
print("   credit before %r h, after %r h" % (before_h, after_h))
check("no credit was spent on the refused production",
      before_h is not None and after_h is not None
      and after_h >= before_h - SLACK_H,
      "before %r h, after %r h" % (before_h, after_h))
check("the production is deleted at the end",
      bool(uuid) and ground.delete(vpm, key, uuid),
      "production %s" % (uuid or "not found by its title"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)

# -*- coding: utf-8 -*-
"""Two voices, two cameras, and a curl that writes down where it was sent.

The material of a whole multitrack run that finishes on this machine,
built here once so that the tests starting such a run stand on the same
ground instead of on copies of it. Beside it the stand-in curl: the one
program that could reach auphonic.com, replaced on the search path.

Nothing in this file prints; run.sh would count a line against the test.
"""
import json
import os
import subprocess
import wave

import numpy as np

# The program refuses a common range under 30 seconds, and the second
# camera starts CAM_LATE late: the window is LENGTH - CAM_LATE, 2.5 s over.
RATE, LENGTH, CAM_LATE = 48000, 34.0, 1.5
# Five turns of 5 s with a second of quiet around each. Under a fifth
# quiet, the noise floor lands inside the neighbour's bleed and a build
# without the separation passes; 5 s stays clear of MIN_EDIT_DURATION_S.
TURNS = {"Host": [(2, 7), (15, 20), (28, 33)],
         "Guest": [(8.5, 13.5), (21.5, 26.5)]}
# A port nothing listens on: a real curl started past the stand-in
# reaches no server, whatever it was handed.
NOWHERE = "http://127.0.0.1:9"


def voice(turns, seed):
    """Speech-like noise in the turns given, silence around them."""
    rng = np.random.default_rng(seed)
    x = np.zeros(int(LENGTH * RATE))
    for a, b in turns:
        n = int((b - a) * RATE)
        env = 0.3 + 0.7 * np.abs(np.sin(np.linspace(0, 50, n)))
        x[int(a * RATE):int(a * RATE) + n] = rng.normal(0, 0.25, n) * env
    return x


def write(path, x):
    """One mono track as 16-bit WAV at RATE."""
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


def build(folder, file_format):
    """Write the material into `folder`; hands back the assignment's path.

    Host.wav and Guest.wav each hear the other 8 dB down, under the 3:1
    rule on purpose. The cameras are colour bars at ultrafast: the run
    reads packet times and copies the picture, so it only has to exist.
    One ffmpeg call writes both; the -ss is an output option for the second.
    """
    host, guest = voice(TURNS["Host"], 1), voice(TURNS["Guest"], 2)
    bleed = 10 ** (-8.0 / 20)
    noise = np.random.default_rng(9).normal(0, 0.0004, len(host))
    write(folder + "/Host.wav", host + bleed * guest + noise)
    write(folder + "/Guest.wav", guest + bleed * host + noise)
    write(folder + "/room.wav", 0.6 * host + 0.6 * guest + noise)
    camera = ["-map", "0:v", "-map", "1:a", "-c:v", "libx264",
              "-preset", "ultrafast", "-pix_fmt", "yuv420p",
              "-c:a", "pcm_s16le", "-shortest"]
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "smptebars=size=320x180:rate=25:duration=%.1f" % LENGTH,
         "-i", folder + "/room.wav"] + camera + [folder + "/CamHost.mov",
         "-ss", "%.2f" % CAM_LATE] + camera + [folder + "/CamGuest.mov"],
        check=True)
    plan = {"format": file_format, "created_by": "test", "production": "WA",
            "tracks_of": [
                {"audio": folder + "/Host.wav",
                 "blocks": [folder + "/Host.wav"], "speakers": "Host",
                 "camera": folder + "/CamHost.mov", "camera_audio": False},
                {"audio": folder + "/Guest.wav",
                 "blocks": [folder + "/Guest.wav"], "speakers": "Guest",
                 "camera": folder + "/CamGuest.mov", "camera_audio": False}],
            "cameras": [{"video": folder + "/CamHost.mov", "name": "CamHost"},
                        {"video": folder + "/CamGuest.mov",
                         "name": "CamGuest"}]}
    with open(folder + "/assign.json", "w", encoding="utf-8") as f:
        json.dump(plan, f)
    return folder + "/assign.json"


def watched_curl(folder, env):
    """A stand-in curl first on env's search path: (calls, watched).

    It writes down every call and refuses, and the proxies in env point
    nowhere, so nothing leaves the machine whatever is broken. `calls()`
    hands back the calls, oldest first. `watched` is asked, not assumed:
    Windows starts no #!/bin/sh file, the real curl answers, and a
    judgement resting on the stand-in would be green having seen nothing.
    """
    os.makedirs(folder, exist_ok=True)
    written = os.path.join(folder, "curl_calls.txt")
    standin = os.path.join(folder, "curl")
    with open(standin, "w") as f:
        f.write("#!/bin/sh\nprintf '%s\\n' \"$*\" >> '" + written
                + "'\nexit 1\n")
    os.chmod(standin, 0o755)
    env["PATH"] = folder + os.pathsep + env.get("PATH", "")
    for name in ("https_proxy", "http_proxy", "all_proxy",
                 "HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY"):
        env[name] = NOWHERE
    for name in ("no_proxy", "NO_PROXY"):
        env.pop(name, None)

    def calls():
        """What the stand-in was called with, oldest first."""
        try:
            with open(written) as f:
                return [x.strip() for x in f if x.strip()]
        except OSError:
            return []

    try:
        subprocess.run(["curl", "--version"], capture_output=True, env=env)
    except OSError:
        pass
    watched = calls() == ["--version"]
    open(written, "w").close()
    return calls, watched

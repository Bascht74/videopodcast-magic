# -*- coding: utf-8 -*-
"""The transcript is ours: auphonic.com's is neither asked for nor fetched.

Nothing here talks to auphonic.com. In order: a Multitrack request
and a Singletrack one built from a preset with speech recognition on
both leave it out and keep the rest of the preset, the Singletrack one
asking for none of the text it would write either; a single
production's text outputs are fetched without auphonic.com's three
transcript formats, held against a stand-in that notes the address
instead of opening it; and the preflight says in one line that speech
recognition is on, the same line for both kinds of production, and
says nothing where it is off. The shape of an "off" preset is the API
description's, not one seen in an answer.
"""
PLATFORM_BOUND = False
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program
SCRIPT = the_program.SCRIPT
import shutil, tempfile, time

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Auphonic Whisper: the block without a service id, as the API
# description shows it; an outside service carries its id.
LISTENS = {"speech_recognition": {"language": "en", "keywords": []},
           "algorithms": {"leveler": True, "normloudness": True,
                          "loudnesstarget": -16},
           "multi_input_files": [{"id": "Speaker",
                                  "algorithms": {"denoise": True}}],
           "is_multitrack": True, "preset_name": "Podcast_Multitrack"}

print("1. Neither kind of request asks for speech recognition")
request = vpm.build_multitrack_request(LISTENS, "Episode",
                                       ["Guest", "Presenter"], "Episode")
check("speech recognition is not in the request",
      "speech_recognition" not in request,
      "request keys %s" % sorted(request))
check("the preset's switches go along as they stand",
      request.get("algorithms") == LISTENS["algorithms"],
      "sent %r, preset %r" % (request.get("algorithms"),
                              LISTENS["algorithms"]))
check("and the preset itself is left as it was read",
      "speech_recognition" in LISTENS,
      "preset keys %s" % sorted(LISTENS))
# A Singletrack preset that listens carries the text outputs of its
# recognition beside the audio, by the three formats the API names.
SINGLE = dict(LISTENS, is_multitrack=False, multi_input_files=[],
              output_files=[{"format": "wav", "ending": "wav"},
                            {"format": "subtitle", "ending": "srt"},
                            {"format": "transcript", "ending": "txt"},
                            {"format": "chaps", "ending": "chapters.txt"}])
single_request = vpm.build_single_request(SINGLE, "Episode")
check("the Singletrack request leaves speech recognition out too",
      "speech_recognition" not in single_request,
      "request keys %s" % sorted(single_request))
asked = [f.get("format") for f in single_request.get("output_files") or []]
check("and asks for none of the text the recognition would write",
      asked == ["wav", "chaps"], "asked for %s, wanted wav and chaps" % asked)

print("\n2. A single production's text comes without the transcript")
folder = tempfile.mkdtemp(prefix="vpm_text_")
asked = []
real = vpm._curl_call
files = [{"filename": "show.wav", "format": "wav", "download_url": "u1"},
         {"filename": "show.chapters.txt", "format": "chaps",
          "download_url": "u2"},
         {"filename": "show_stats.json", "format": "stats",
          "download_url": "u3"},
         {"filename": "show.srt", "format": "subtitle", "download_url": "u4"},
         {"filename": "show_speech.json", "format": "speech",
          "download_url": "u5"},
         {"filename": "show.txt", "format": "transcript",
          "download_url": "u6"}]
try:
    vpm._curl_call = lambda key, arguments, **k: asked.append(arguments) or b""
    vpm.fetch_text_outputs("K", files, folder, skip=files[0])
finally:
    vpm._curl_call = real
    shutil.rmtree(folder, ignore_errors=True)
got = sorted(a[-1] for a in asked)
check("chapter marks and statistics are fetched",
      "u2" in got and "u3" in got,
      "%d fetched: %s, wanted u2 and u3 among them" % (len(got), got))
check("auphonic.com's three transcript formats are not",
      not set(got) & {"u4", "u5", "u6"},
      "%d fetched: %s, none of u4 u5 u6 may be" % (len(got), got))

print("\n3. The preflight says it in one line")


def said_for(preset, multitrack):
    """The preflight's findings on speech recognition for one preset."""
    vpm.read_preset = lambda key, uuid: preset
    return [b for b in vpm.check_preset("key", "uuid", "Podcast", -16.0,
                                        multitrack)
            if b.field == vpm.T('Speech recognition')]


multi = said_for(LISTENS, True)
check("a Multitrack preset that listens is said once",
      len(multi) == 1, "%d lines: %s" % (len(multi), [b.text for b in multi]))
check("and it holds nothing up",
      all(b.kind != "abort" for b in multi), [b.kind for b in multi])
single = said_for(dict(LISTENS, is_multitrack=False,
                       speech_recognition={"uuid": "SERVICEID",
                                           "language": "en-US"}), False)
check("a single preset with an outside service is said once",
      len(single) == 1,
      "%d lines: %s" % (len(single), [b.text for b in single]))
check("and that holds nothing up either",
      all(b.kind != "abort" for b in single), [b.kind for b in single])
check("both kinds are told the same line",
      [(b.kind, b.text) for b in single] == [(b.kind, b.text) for b in multi],
      "single %s against multitrack %s"
      % ([(b.kind, b.text) for b in single],
         [(b.kind, b.text) for b in multi]))
quiet = (said_for(dict(LISTENS, speech_recognition=None), True)
         + said_for(dict(LISTENS, speech_recognition={}), True)
         + said_for({k: v for k, v in LISTENS.items()
                     if k != "speech_recognition"}, True))
check("a preset without it says nothing about it",
      not quiet, "%d lines: %s" % (len(quiet), [b.text for b in quiet]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)

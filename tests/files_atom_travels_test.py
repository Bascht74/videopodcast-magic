# -*- coding: utf-8 -*-
"""A logs atom lost by ffmpeg's copy is put back into the new file.

The source is built here and the atom written into its video sample
description by hand, the way a camera writes it -- so the program's own
reader has to find the moov box and that description first. Then in
order: the source carries the atom and ffprobe still reads it, copying
with -c:v copy drops it, copy_mov_atoms names what it put back and the
atom is there again, the file stays readable and decodable, and a
second run adds nothing and leaves the atom as it stood.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, shutil, struct, subprocess, sys, tempfile, time
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
m = importlib.util.module_from_spec(spec); sys.modules["vpm"] = m
spec.loader.exec_module(m)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_logs_")
raw = os.path.join(folder, "raw.mov")
# A precondition of the material, not a judgement about the program:
# without a source file there is nothing to test at all.
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "testsrc=size=320x180:rate=30:duration=2",
                "-f", "lavfi", "-i", "sine=frequency=300:duration=2",
                "-c:v", "hevc", "-tag:v", "hvc1",
                "-pix_fmt", "yuv420p10le",
                "-c:a", "pcm_s16le", "-colorspace", "bt2020nc",
                raw], check=True)

# Write a logs atom into the hvc1 description by hand -- the way the
# iPhone does it.
CONTENT = b"com.apple.apple-wide-gamut.apple-log"
atom = struct.pack(">I4s", 8 + len(CONTENT), b"logs") + CONTENT


def insert(file_path):
    """Put the atom into the video sample description of a file.

    Getting there is the program's own reader, so the two steps down are
    judged rather than asserted; False means the rest cannot follow.
    """
    above = m._top_level_boxes(file_path)
    last = above[-1][0].decode("latin1", "replace") if above else "nothing"
    check("the reader finds a moov box at the end of the source",
          bool(above) and above[-1][0] == b"moov",
          "%d top-level boxes, last of them %s, wanted moov"
          % (len(above), last))
    if not above or above[-1][0] != b"moov":
        return False
    pos, size = above[-1][1], above[-1][2]
    with open(file_path, "rb") as f:
        f.seek(pos); moov = bytearray(f.read(size))
    chain = m._video_track_chain(moov, 0, len(moov), 8)
    check("the reader reaches the video sample description",
          bool(chain), "%d boxes down from moov, wanted 7"
          % len(chain or []))
    if not chain:
        return False
    e_i, _ = chain[-1]
    e_size = struct.unpack(">I", moov[e_i:e_i + 4])[0]
    for i, _k in chain:
        box = struct.unpack(">I", moov[i:i + 4])[0]
        struct.pack_into(">I", moov, i, box + len(atom))
    moov = moov[:e_i + e_size] + atom + moov[e_i + e_size:]
    with open(file_path, "r+b") as f:
        f.seek(pos); f.write(moov); f.truncate(pos + len(moov))
    return True


def logs_of(file_path):
    """The contents of the video track logs atom, or None."""
    above = m._top_level_boxes(file_path)
    mo = next(((p, n) for a, p, n in above if a == b"moov"), None)
    if not mo:
        return None
    with open(file_path, "rb") as f:
        f.seek(mo[0]); moov = f.read(mo[1])
    chain = m._video_track_chain(moov, 0, len(moov), 8)
    if not chain:
        return None
    e_i, _ = chain[-1]
    e_size = struct.unpack(">I", moov[e_i:e_i + 4])[0]
    for i, size, kind, head in m._atom_boxes(moov, e_i + 8 + 78,
                                             e_i + e_size):
        if kind == b"logs":
            return moov[i + 8:i + size]
    return None


def one_line(text):
    """A tool's complaint on a single line, short enough to read.

    The evidence of a FAIL only counts where the runner finds it, and it
    greps whole lines: a newline in the middle hides the rest.
    """
    return " ".join(text.decode("latin1", "replace").split())[:110]


def probe(file_path, *more):
    """ffprobe's answer as a dictionary, plus why it is empty."""
    p = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json",
                        "-show_streams"] + list(more) + [file_path],
                       capture_output=True)
    if p.returncode != 0:
        return {}, "ffprobe: " + one_line(p.stderr)
    try:
        return json.loads(p.stdout or b"{}"), ""
    except ValueError as e:
        return {}, "unreadable answer: %s" % str(e)[:80]


if insert(raw):
    found = logs_of(raw)
    check("the source carries the logs atom", found == CONTENT,
          (found or b"nothing").decode("latin1", "replace"))

    data, why = probe(raw)
    names = [s.get("codec_name") for s in data.get("streams", [])]
    check("ffprobe reads the prepared source",
          len(names) == 2 and "hevc" in names, why or ", ".join(names))

    # This is how the script copies -- with -c:v copy
    target = os.path.join(folder, "target.mov")
    subprocess.run(["ffmpeg", "-v", "error", "-i", raw, "-map", "0",
                    "-c:v", "copy", "-c:a", "pcm_s24le",
                    "-map_metadata", "0",
                    "-movflags", "+write_colr+use_metadata_tags", "-y",
                    target], check=True)
    dropped = logs_of(target)
    check("ffmpeg's copy drops the atom", dropped is None,
          "gone" if dropped is None
          else "kept %s" % dropped.decode("latin1", "replace"))

    out = m.copy_mov_atoms(raw, target)
    check("copy_mov_atoms names the atom it added", out == ["logs"],
          "returned %r" % (out,))
    back = logs_of(target)
    # Only a copy into a file that had lost the atom proves anything: had
    # ffmpeg kept it, the atom would be there without anything copying it.
    check("the atom is back in the new file",
          dropped is None and back == CONTENT,
          (back or b"nothing").decode("latin1", "replace"))

    # Is the file still sound?
    data, why = probe(target, "-show_format")
    tracks = len(data.get("streams", []))
    seconds = float(data.get("format", {}).get("duration") or 0.0)
    check("the file is still readable",
          tracks == 2 and 1.5 < seconds < 2.5,
          why or "tracks %d, %.2f s" % (tracks, seconds))

    # And can it still be decoded?
    played = subprocess.run(["ffmpeg", "-v", "error", "-i", target,
                             "-f", "null", "-"], capture_output=True)
    check("the file is still decodable", played.returncode == 0,
          "return code %d %s" % (played.returncode,
                                 one_line(played.stderr)))

    # Adding twice must not duplicate anything
    again = m.copy_mov_atoms(raw, target)
    still = logs_of(target)
    check("a second run adds nothing", again == [],
          "returned %r" % (again,))
    check("and the atom stands unchanged", still == CONTENT,
          (still or b"nothing").decode("latin1", "replace"))
else:
    print("  the source was never prepared, so the checks below "
          "could not run")

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)

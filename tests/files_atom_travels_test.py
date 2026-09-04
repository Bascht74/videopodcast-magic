# -*- coding: utf-8 -*-
"""Atoms lost by ffmpeg's copy are put back into the new file.

The source is built here and the atoms written into its video sample
description by hand, the way a camera writes them -- so the program's
own reader has to find the moov box and that description first. Then in
order: the source carries the atom and ffprobe still reads it, copying
with -c:v copy drops it, copy_mov_atoms names what it put back and the
atom is there again, the file stays readable and decodable, and a
second run adds nothing and leaves the atom as it stood. Last the
others on the list -- the older gamma and both Dolby Vision boxes --
and the one that is deliberately not on it: a 3D box beside the one
ffmpeg writes itself leaves a file nothing will open.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import json, shutil, struct, subprocess, sys, tempfile, time
m = the_program.load()

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

    # --- the others on the list, and the one that is not -------------
    # gama holds the curve of older QuickTime recordings, dvcC and dvvC
    # the Dolby Vision set. st3d says how a 3D picture is packed and is
    # deliberately absent from the list.
    def box(kind, payload):
        return struct.pack(">I4s", 8 + len(payload), kind) + payload

    MORE = {b"gama": box(b"gama", struct.pack(">I", 144179)),
            b"dvcC": box(b"dvcC", bytes([1, 0, 10, 53] + [0] * 20)),
            b"dvvC": box(b"dvvC", bytes([1, 0, 16, 37] + [0] * 20)),
            b"st3d": box(b"st3d", b"\x00\x00\x00\x00\x02")}

    def sub_boxes(file_path):
        """The kinds of the video sample description's sub-boxes."""
        above = m._top_level_boxes(file_path)
        mo = next(((p, n) for a, p, n in above if a == b"moov"), None)
        if not mo:
            return []
        with open(file_path, "rb") as f:
            f.seek(mo[0]); moov = f.read(mo[1])
        chain = m._video_track_chain(moov, 0, len(moov), 8)
        if not chain:
            return []
        e_i, _ = chain[-1]
        e_size = struct.unpack(">I", moov[e_i:e_i + 4])[0]
        return [bytes(k) for _i, _s, k, _h
                in m._atom_boxes(moov, e_i + 8 + 78, e_i + e_size)]

    def prepared(name, kinds):
        """A source carrying those atoms, and a target written from it."""
        src = os.path.join(folder, "src_%s.mov" % name)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-map", "0",
                        "-c", "copy", "-movflags", "+write_colr", src],
                       check=True)
        atoms = b"".join(MORE[k] for k in kinds)
        above = m._top_level_boxes(src)
        pos, size = above[-1][1], above[-1][2]
        with open(src, "rb") as f:
            f.seek(pos); moov = bytearray(f.read(size))
        chain = m._video_track_chain(moov, 0, len(moov), 8)
        e_i, _ = chain[-1]
        e_size = struct.unpack(">I", moov[e_i:e_i + 4])[0]
        for i, _k in chain:
            struct.pack_into(">I", moov, i,
                             struct.unpack(">I", moov[i:i + 4])[0] + len(atoms))
        moov = moov[:e_i + e_size] + atoms + moov[e_i + e_size:]
        with open(src, "r+b") as f:
            f.seek(pos); f.write(moov); f.truncate(pos + len(moov))
        dst = os.path.join(folder, "dst_%s.mov" % name)
        subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-map", "0",
                        "-c:v", "copy", "-c:a", "pcm_s24le",
                        "-map_metadata", "0",
                        "-movflags", "+use_metadata_tags", "-y", dst],
                       check=True)
        return src, dst

    wanted = [b"gama", b"dvcC", b"dvvC"]
    src, dst = prepared("more", wanted)
    have = sub_boxes(src)
    check("the source carries the gamma and both Dolby Vision boxes",
          all(k in have for k in wanted),
          "found %r, wanted %r among them"
          % ([k.decode("latin1") for k in have],
             [k.decode("latin1") for k in wanted]))
    lost = [k for k in wanted if k not in sub_boxes(dst)]
    check("ffmpeg's copy drops all three of them", lost == wanted,
          "dropped %r, wanted all three dropped"
          % ([k.decode("latin1") for k in lost],))
    got = m.copy_mov_atoms(src, dst)
    check("all three are on the list and are put back",
          sorted(got) == sorted(k.decode("latin1") for k in wanted),
          "put back %r, wanted %r"
          % (sorted(got), sorted(k.decode("latin1") for k in wanted)))
    read = subprocess.run(["ffprobe", "-v", "error", "-show_streams",
                           "-select_streams", "v:0", dst],
                          capture_output=True)
    check("and the file with them in it still opens",
          read.returncode == 0 and b"DOVI" in read.stdout,
          "return code %d, Dolby Vision read back %s %s"
          % (read.returncode, b"DOVI" in read.stdout,
             one_line(read.stderr)))

    # The 3D box: ffmpeg writes one of its own into the target, and the
    # two beside each other make a file nothing will open. Copying it
    # back would trade a lost packing for a lost file.
    src3, dst3 = prepared("st3d", [b"st3d"])
    check("a 3D source makes ffmpeg write a box of its own",
          b"vexu" in sub_boxes(dst3),
          "the new file carries %r, wanted vexu among them"
          % ([k.decode("latin1") for k in sub_boxes(dst3)],))
    # Why it is not on the list stands in the source beside the list,
    # and is not checked here: it is a fault of the writer's, and a
    # check that held ffmpeg to it would go red the day ffmpeg mended
    # it -- red at somebody who had broken nothing.
    # Once, into a name: copying twice would put the atom in on the
    # first call and find it there on the second, and the failure line
    # would then report the second answer for the first one's fault.
    put = m.copy_mov_atoms(src3, dst3)
    check("the 3D box is not on the list and is not put back", put == [],
          "put back %r, wanted nothing" % (put,))
else:
    print("  the source was never prepared, so the checks below "
          "could not run")

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)

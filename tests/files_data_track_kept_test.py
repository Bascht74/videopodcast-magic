# -*- coding: utf-8 -*-
"""A camera's data track is carried over only where ffmpeg writes it whole.

Sources are built here: ffmpeg cannot encode a data stream, so a
timecode track is written and its handler and sample entry renamed --
four bytes each, no size and no offset moves. Then in order: a gpmd
track is asked for and reaches the new file, a mebx track is not asked
for at all, the timecode track is never asked for because copying it
makes ffmpeg throw away the timecode this program worked out, and the
report names what was left behind instead of losing it silently.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import argparse, io, json, shutil, struct, subprocess
import sys, tempfile, time
m = the_program.load()
m.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_dtrack_")
CONTAINERS = (b"moov", b"trak", b"mdia", b"minf", b"stbl")


def walk(data, start, end):
    """The boxes of one MOV level: (offset, size, kind, header length)."""
    i = start
    while i + 8 <= end:
        size = struct.unpack(">I", data[i:i + 4])[0]
        kind = bytes(data[i + 4:i + 8])
        head = 8
        if size == 1:
            size = struct.unpack(">Q", data[i + 8:i + 16])[0]
            head = 16
        elif size == 0:
            size = end - i
        if size < head or i + size > end:
            return
        yield i, size, kind, head
        i += size


def rename_track(data, start, end, old, hdlr, entry):
    """Rename a track's handler type and its sample entry, in place."""
    for i, size, kind, head in walk(data, start, end):
        if kind == b"hdlr" and size >= head + 12:
            if bytes(data[i + head + 8:i + head + 12]) == old:
                data[i + head + 8:i + head + 12] = hdlr
        elif kind == b"stsd":
            for e, es, ek, eh in walk(data, i + head + 8, i + size):
                if ek == old:
                    data[e + 4:e + 8] = entry
        elif kind in CONTAINERS:
            rename_track(data, i + head, i + size, old, hdlr, entry)


def tags_of(path):
    """The codec tags of the file's data tracks, straight from ffprobe."""
    p = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json",
                        "-show_streams", path], capture_output=True)
    try:
        d = json.loads(p.stdout or b"{}")
    except ValueError:
        return []
    return [(s.get("codec_tag_string") or "?").strip()
            for s in d.get("streams", []) if s.get("codec_type") == "data"]


def video_timecode(path):
    """The timecode the video track carries, or ""."""
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream_tags=timecode",
                        "-of", "csv=p=0", path], capture_output=True)
    return (p.stdout or b"").decode("latin1", "replace").strip().strip(",")


def build(name, entry):
    """A camera file with one data track of the given kind. "" on failure."""
    raw = os.path.join(folder, "raw_%s.mov" % name)
    out = os.path.join(folder, "src_%s.mov" % name)
    p = subprocess.run(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=25:duration=2",
         "-f", "lavfi", "-i", "sine=frequency=300:duration=2",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
         "-shortest", "-timecode", "01:00:00:00", raw], capture_output=True)
    if p.returncode != 0:
        return ""
    data = bytearray(open(raw, "rb").read())
    rename_track(data, 0, len(data), b"tmcd", b"meta", entry)
    open(out, "wb").write(bytes(data))
    return out


def one_line(text):
    """A tool's complaint on one line: the runner greps whole lines."""
    return " ".join(text.decode("latin1", "replace").split())[:110]


guest = os.path.join(folder, "Guest.wav")
made = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                       "sine=frequency=440:duration=2", "-c:a", "pcm_s24le",
                       "-ar", "48000", "-ac", "1", guest], capture_output=True)
# A precondition of the material, not a judgement about the program.
assert made.returncode == 0, one_line(made.stderr)


def written(source, target):
    """Run the program's own camera writer. The ffmpeg complaint on failure."""
    info = m.video_facts(source)
    args = argparse.Namespace(no_camera_audio=False, speech_language=None,
                              speech_language_camera=None,
                              name_camera="Camera Original")
    try:
        m.write_camera_file(source, info, [("Guest", guest)], target,
                            0.0, 1.0, False, args)
    except Exception as e:
        # On one line: the runner greps whole lines, and a newline in
        # the middle of the evidence hides the rest of it.
        return " ".join(str(e).split())[:90]
    return ""


# ---------------------------------------------------------------- gpmd
gpmd = build("gpmd", b"gpmd")
check("a source with a motion data track can be built",
      bool(gpmd) and tags_of(gpmd) == ["gpmd"],
      "tags %r, wanted ['gpmd']" % (tags_of(gpmd) if gpmd else "no file",))
if gpmd and tags_of(gpmd) == ["gpmd"]:
    check("the motion data track is asked for",
          m.data_track_maps(gpmd) == ["-map", "0:d:0"],
          "asked for %r, wanted ['-map', '0:d:0']" % (m.data_track_maps(gpmd),))
    out = os.path.join(folder, "out_gpmd.mov")
    why = written(gpmd, out)
    check("the file with a motion data track is written", why == "", why)
    if not why:
        after = tags_of(out)
        check("the motion data track reaches the new file", "gpmd" in after,
              "data tracks in the new file %r, wanted gpmd among them" % (after,))
        # A track ffmpeg could not describe arrives with an empty sample
        # description, and ffprobe then reads the next box as its name.
        check("and it arrives under its own name, not a stray box",
              after and after[0] == "gpmd",
              "first data track %r, wanted 'gpmd'"
              % (after[0] if after else "none",))

# ---------------------------------------------------------------- mebx
mebx = build("mebx", b"mebx")
check("a source with a phone's metadata track can be built",
      bool(mebx) and tags_of(mebx) == ["mebx"],
      "tags %r, wanted ['mebx']" % (tags_of(mebx) if mebx else "no file",))
if mebx and tags_of(mebx) == ["mebx"]:
    check("a track ffmpeg cannot write is not asked for",
          m.data_track_maps(mebx) == [],
          "asked for %r, wanted nothing" % (m.data_track_maps(mebx),))
    out = os.path.join(folder, "out_mebx.mov")
    why = written(mebx, out)
    check("the file with a phone's metadata track is written", why == "", why)
    if not why:
        # Not "mebx is absent": a track ffmpeg could not describe arrives
        # with an empty sample description, and ffprobe then reads the
        # next box as its name -- so the name it went in under proves
        # nothing about whether it came along.
        check("that track does not reach the new file", tags_of(out) == [],
              "data tracks in the new file %r, wanted none of them"
              % (tags_of(out),))
        said = io.StringIO()
        keep, sys.stdout = sys.stdout, said
        try:
            m.check_data_tracks(mebx, out)
        finally:
            sys.stdout = keep
        text = said.getvalue()
        check("what was left behind is named, not dropped quietly",
              "mebx" in text,
              "the report said %r, wanted mebx named in it" % text.strip()[:70])

# ------------------------------------------------------------ the timecode
tc = build("tc", b"tmcd")     # renamed back to itself: a plain timecode track
if tc:
    tc_src = os.path.join(folder, "src_plain.mov")
    shutil.copy(tc, tc_src)
    check("the timecode track is never asked for",
          m.data_track_maps(tc_src) == [],
          "asked for %r, wanted nothing -- copying it makes ffmpeg drop "
          "the timecode this program worked out"
          % (m.data_track_maps(tc_src),))
    out = os.path.join(folder, "out_cut.mov")
    info = m.video_facts(tc_src)
    args = argparse.Namespace(no_camera_audio=False, speech_language=None,
                              speech_language_camera=None,
                              name_camera="Camera Original")
    wanted = m.camera_stamp(info, 1.0, None)
    why = ""
    try:
        m.write_camera_file(tc_src, info, [("Guest", guest)], out,
                            0.0, 1.0, False, args, cut_at=1.0, keep_s=0.8)
    except Exception as e:
        why = " ".join(str(e).split())[:90]
    check("a camera cut at the front is written", why == "", why)
    if not why:
        check("the timecode the program worked out is the one in the file",
              video_timecode(out) == wanted and wanted != info["tc"],
              "file says %r, program worked out %r, source had %r"
              % (video_timecode(out), wanted, info["tc"]))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)

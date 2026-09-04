# -*- coding: utf-8 -*-
"""Colour tags, metadata keys and named audio tracks reach the result.

The simple path writes its camera file with write_camera_file. What the
source carries has to come out the other side: the three colour tags,
the colour box byte for byte, every metadata key and not only the Apple
ones, the camera's own audio beside the track that was added, and each
track under the name it was given. And the other way round -- a source
with no colour box must not come out with one invented for it, and a
camera that writes no Apple key at all must still get a line.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import io, subprocess, sys, json, tempfile, time
vpm = the_program.load()

began = time.time()
done = 0
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))


T = tempfile.mkdtemp(prefix="simple_")
# A video with colour tags and one QuickTime key
video = os.path.join(T, "camera.mov")
# Two passes on purpose: ffmpeg 9 no longer carries -color_primaries and
# -color_trc into the file. The encoder's own parameters put them in the
# bitstream, and repacking with -c:v copy gets them into the colr box.
raw = os.path.join(T, "raw.mov")
subprocess.run(["ffmpeg","-v","error","-y",
                "-f","lavfi",
                "-i","testsrc=size=320x180:rate=30:duration=5",
                "-f","lavfi","-i","sine=frequency=300:duration=5",
                "-c:v","libx264","-pix_fmt","yuv420p",
                "-x264opts",
                "colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc",
                "-c:a","pcm_s16le", raw],
               check=True)
subprocess.run(["ffmpeg","-v","error","-y","-i", raw,
                "-c","copy",
                "-metadata","com.apple.proapps.testkey=hello",
                "-movflags","+write_colr+use_metadata_tags", video],
               check=True)
audio = os.path.join(T, "audio.wav")
subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi",
                "-i","sine=frequency=800:duration=5",
                "-ac","1","-c:a","pcm_s24le", audio], check=True)
KEY = "com.apple.proapps.testkey"
class Args: pass
args = Args(); args.name = "Audio"; args.name_camera = "Camera Original"
args.speech_language = ""; args.speech_language_camera = ""
args.no_camera_audio = False
info = vpm.video_facts(video)
target = os.path.join(T, "done.mov")
# The writer that both paths use.
vpm.write_camera_file(video, info, [(args.name, audio)], target,
                      0.0, 1.0, False, args)


def parts(p):
    """The video stream, the audio streams and the container's tags."""
    d = json.loads(subprocess.run(
        ["ffprobe","-v","error","-show_streams","-show_format",
         "-of","json",p],capture_output=True,text=True).stdout)
    vs = [s for s in d["streams"] if s["codec_type"]=="video"][0]
    tracks = [s for s in d["streams"] if s["codec_type"]=="audio"]
    return vs, tracks, d.get("format",{}).get("tags",{})


def track_name(stream):
    """The name a player shows for one audio track.

    A MOV keeps it in the track's own name box rather than in a title
    tag, so ffprobe hands it back under "name" or as the handler name.
    """
    tags = stream.get("tags", {})
    for key in ("title", "name", "handler_name"):
        if tags.get(key):
            return tags[key]
    return None


def show(p, what):
    vs, audio, tags = parts(p)
    print("%-10s primaries=%s trc=%s space=%s  audio tracks=%d"
          "  apple keys=%s"
          % (what, vs.get("color_primaries"), vs.get("color_transfer"),
             vs.get("color_space"), len(audio),
             [k for k in tags if "apple" in k.lower()] or "none"))
show(video, "Source")
show(target, "Result")

source_video, source_audio, source_tags = parts(video)
result_video, result_audio, result_tags = parts(target)
names = [track_name(s) for s in result_audio]
print("Track names:", names)
print()

# The source is asked first and the result is held against it: a value
# written into the test would go stale the day ffmpeg names it
# differently, and then the test would be about ffmpeg's spelling.
carried = ("color_transfer", "color_primaries", "color_space")
check("the source itself carries the three colour tags",
      all(source_video.get(k) for k in carried),
      " ".join("%s=%s" % (k, source_video.get(k)) for k in carried))
for tag, what in (("color_transfer", "transfer characteristics"),
                  ("color_primaries", "primaries"),
                  ("color_space", "matrix")):
    check("colour %s as in the source" % what,
          result_video.get(tag) == source_video.get(tag),
          "%s -> %s" % (source_video.get(tag), result_video.get(tag)))
was, now = source_tags.get(KEY), result_tags.get(KEY)
check("the QuickTime key came along",
      was is not None and now == was,
      "%s=%r -> %r" % (KEY, was, now))
expected = len(source_audio) + 1
check("the camera's audio and the added one",
      len(result_audio) == expected,
      "%d found, %d expected" % (len(result_audio), expected))
check("both tracks under the name they were given",
      names == [args.name, args.name_camera],
      "%r, expected %r" % (names, [args.name, args.name_camera]))

# --- the colour box itself, not ffprobe's name for it ----------------
# The names above can agree while the box differs; the promise is that
# the box travels unchanged, so the numbers in it are read directly.
before, after = vpm.mov_colour_tags(video), vpm.mov_colour_tags(target)
check("the colour box arrives with the same numbers in it",
      before is not None and after == before,
      "source %r, new file %r" % (before, after))

# --- and a source that has none keeps none ---------------------------
# ffmpeg can be asked to write a colour box whatever the source said,
# and it then puts "unspecified" -- 2/2/2 -- into a file that had
# nothing. Nothing is gained by that and the check above it then
# reports a difference the writing itself made.
bare = os.path.join(T, "bare.mov")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                "-i", "testsrc=size=320x180:rate=30:duration=2",
                "-f", "lavfi", "-i", "sine=frequency=300:duration=2",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "pcm_s16le", "-shortest", bare], check=True)
check("the source without a colour box really has none",
      vpm.mov_colour_tags(bare) is None,
      "read %r, wanted nothing" % (vpm.mov_colour_tags(bare),))
bare_out = os.path.join(T, "bare_done.mov")
bare_info = vpm.video_facts(bare)
vpm.write_camera_file(bare, bare_info, [(args.name, audio)], bare_out,
                      0.0, 1.0, False, args)
check("a source without a colour box does not gain an invented one",
      vpm.mov_colour_tags(bare_out) is None,
      "the new file says %r, wanted nothing -- 2/2/2 is "
      "\"unspecified\" and was never in the source"
      % (vpm.mov_colour_tags(bare_out),))

# --- every metadata key, not only the Apple ones ---------------------
plain = os.path.join(T, "plain.mov")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-c", "copy",
                "-metadata", "artist=Presenter",
                "-metadata", "model=WideCam One",
                "-metadata", "description=a camera that writes no Apple key",
                "-movflags", "+write_colr+use_metadata_tags", plain],
               check=True)
keys = vpm.file_metadata(plain)
check("a camera that writes no Apple key still carries keys",
      keys and not [k for k in keys if k.startswith("com.")],
      "read %d keys, %d of them Apple ones"
      % (len(keys), len([k for k in keys if k.startswith("com.")])))
check("what the container says about itself is not counted as camera data",
      not [k for k in keys if k in ("major_brand", "minor_version",
                                    "compatible_brands", "encoder")],
      "counted %r among the camera keys"
      % ([k for k in keys if k in ("major_brand", "minor_version",
                                   "compatible_brands", "encoder")],))
plain_out = os.path.join(T, "plain_done.mov")
vpm.write_camera_file(plain, vpm.video_facts(plain), [(args.name, audio)],
                      plain_out, 0.0, 1.0, False, args)
gone = [k for k in keys if k not in vpm.file_metadata(plain_out)]
check("a plain key reaches the new file as an Apple one does",
      not gone, "missing from the new file: %r of %d" % (gone, len(keys)))

# The line itself: a camera with no Apple key used to get none at all,
# neither good nor bad, and a loss there was reported by nobody.
said = io.StringIO()
keep_out, sys.stdout = sys.stdout, said
try:
    vpm.check_camera_metadata(plain, plain_out)
finally:
    sys.stdout = keep_out
check("and it gets a line of its own, where it used to get none",
      "%d" % len(keys) in said.getvalue(),
      "the report said %r, wanted the %d keys named in it"
      % (said.getvalue().strip()[:70], len(keys)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)

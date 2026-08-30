"""The simple path: does it now carry colour and metadata along?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, subprocess, sys, json, tempfile
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
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
class Args: pass
args = Args(); args.name = "Audio"; args.name_camera = "Camera Original"
args.speech_language = ""; args.speech_language_camera = ""
args.no_camera_audio = False
info = vpm.video_facts(video)
target = os.path.join(T, "done.mov")
# The writer that both paths use.
vpm.write_camera_file(video, info, [(args.name, audio)], target,
                      0.0, 1.0, False, args)

def show(p, what):
    d = json.loads(subprocess.run(
        ["ffprobe","-v","error","-show_streams","-show_format",
         "-of","json",p],capture_output=True,text=True).stdout)
    vs = [s for s in d["streams"] if s["codec_type"]=="video"][0]
    audio = [s for s in d["streams"] if s["codec_type"]=="audio"]
    tags = d.get("format",{}).get("tags",{})
    print("%-10s primaries=%s trc=%s space=%s  audio tracks=%d"
          "  apple keys=%s"
          % (what, vs.get("color_primaries"), vs.get("color_transfer"),
             vs.get("color_space"), len(audio),
             [k for k in tags if "apple" in k.lower()] or "none"))
show(video, "Source")
show(target, "Result")
d = json.loads(subprocess.run(
    ["ffprobe","-v","error","-show_streams","-of","json",target],
    capture_output=True,text=True).stdout)
audio_streams = [s for s in d["streams"] if s["codec_type"]=="audio"]
print("Track names:",
      [s.get("tags",{}).get("title") for s in audio_streams])
vs = [s for s in d["streams"] if s["codec_type"]=="video"][0]
assert vs.get("color_transfer") == "arib-std-b67", "colour tags lost!"
print("\nOK: colour tags and camera audio came along.")

"""Does the logs atom move from the source into the new file?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, subprocess, struct, json
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
m = importlib.util.module_from_spec(spec); sys.modules["vpm"] = m
spec.loader.exec_module(m)

D = fixture("logsatom"); os.makedirs(D, exist_ok=True)
raw = "%s/raw.mov" % D
if os.path.exists(raw): os.remove(raw)
subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i",
                "testsrc=size=320x180:rate=30:duration=2",
                "-f","lavfi","-i","sine=frequency=300:duration=2",
                "-c:v","hevc","-tag:v","hvc1","-pix_fmt","yuv420p10le",
                "-c:a","pcm_s16le","-colorspace","bt2020nc",
                raw], check=True)

# Write a logs atom into the hvc1 description by hand -- the way the
# iPhone does it.
CONTENT = b"com.apple.apple-wide-gamut.apple-log"
atom = struct.pack(">I4s", 8 + len(CONTENT), b"logs") + CONTENT
def insert(file_path):
    above = m._top_level_boxes(file_path)
    assert above[-1][0] == b"moov", above
    pos, size = above[-1][1], above[-1][2]
    with open(file_path,"rb") as f:
        f.seek(pos); moov = bytearray(f.read(size))
    chain = m._video_track_chain(moov, 0, len(moov), 8)
    assert chain, "no video track found"
    e_i, _ = chain[-1]
    e_size = struct.unpack(">I", moov[e_i:e_i+4])[0]
    for i, _k in chain:
        box = struct.unpack(">I", moov[i:i+4])[0]
        struct.pack_into(">I", moov, i, box + len(atom))
    moov = moov[:e_i+e_size] + atom + moov[e_i+e_size:]
    with open(file_path,"r+b") as f:
        f.seek(pos); f.write(moov); f.truncate(pos+len(moov))
insert(raw)

def logs_of(file_path):
    above = m._top_level_boxes(file_path)
    mo = next(((p,n) for a,p,n in above if a==b"moov"), None)
    if not mo: return None
    with open(file_path,"rb") as f:
        f.seek(mo[0]); moov = f.read(mo[1])
    chain = m._video_track_chain(moov, 0, len(moov), 8)
    if not chain: return None
    e_i,_ = chain[-1]; e_size = struct.unpack(">I", moov[e_i:e_i+4])[0]
    for i,size,kind,head in m._atom_boxes(moov, e_i+8+78, e_i+e_size):
        if kind == b"logs":
            return moov[i+8:i+size]
    return None

print("source carries logs:", logs_of(raw))
assert logs_of(raw) == CONTENT
# Still readable?
d = json.loads(subprocess.run(["ffprobe","-v","error","-print_format","json",
     "-show_streams", raw], capture_output=True).stdout)
print("ffprobe reads the prepared source:",
      [s["codec_name"] for s in d["streams"]])

# This is how the script copies -- with -c:v copy
target = "%s/target.mov" % D
if os.path.exists(target): os.remove(target)
subprocess.run(["ffmpeg","-v","error","-i",raw,"-map","0","-c:v","copy",
                "-c:a","pcm_s24le","-map_metadata","0",
                "-movflags","+write_colr+use_metadata_tags","-y",target],
               check=True)
print("target after copying:", logs_of(target))
assert logs_of(target) is None, "did ffmpeg keep it this time?"

out = m.copy_mov_atoms(raw, target)
print("added afterwards:", out)
print("target after that: ", logs_of(target))
assert logs_of(target) == CONTENT, "logs still missing"

# Is the file still sound?
p = subprocess.run(["ffprobe","-v","error","-print_format","json",
                    "-show_format","-show_streams", target],
                   capture_output=True)
assert p.returncode == 0, p.stderr[:300]
d = json.loads(p.stdout)
print("ffprobe after adding: %d tracks, %s s"
      % (len(d["streams"]), d["format"]["duration"]))
# And can it still be decoded?
p2 = subprocess.run(["ffmpeg","-v","error","-i",target,"-f","null","-"],
                    capture_output=True)
assert p2.returncode == 0, p2.stderr[:400]
print("fully decodable: yes")

# Adding twice must not duplicate anything
out2 = m.copy_mov_atoms(raw, target)
print("second run:", out2)
assert out2 == []
print("\nall good")

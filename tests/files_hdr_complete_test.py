# -*- coding: utf-8 -*-
"""#65: Does a finished file carry everything that marks it as HDR?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, time, importlib.util
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

D = fixture("hdrtest")
FOREIGN = fixture("foreign")
began = time.time()
done = 0
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))

def field(findings, name):
    return next((finding for finding in findings
                 if finding.field == name), None)

print("1. HDR10 with everything")
findings = vpm.hdr_findings(D + "/hdr10.mp4")
check("primaries good", field(findings, "Primaries").kind == "good")
check("curve good and PQ", field(findings, "Curve").kind == "good"
        and "PQ" in field(findings, "Curve").text,
        field(findings, "Curve").text)
check("matrix good", field(findings, "Matrix").kind == "good")
check("bit depth good", field(findings, "Bit depth").kind == "good",
        field(findings, "Bit depth").text)
check("codec profile good", field(findings, "Codec profile").kind == "good",
        field(findings, "Codec profile").text)
check("static metadata complete",
        field(findings, "Static metadata").kind == "good",
        field(findings, "Static metadata").text)
check("nothing to fault",
        not [x for x in findings if x.kind != "good"])

print("\n2. HLG -- static metadata is no fault there")
findings = vpm.hdr_findings(D + "/hlg.mp4")
check("curve good and HLG", field(findings, "Curve").kind == "good"
        and "HLG" in field(findings, "Curve").text,
        field(findings, "Curve").text)
check("static metadata no fault",
        field(findings, "Static metadata").kind == "good",
        field(findings, "Static metadata").text)
check("nothing to fault", not [x for x in findings if x.kind != "good"])

print("\n3. PQ without static metadata -- a hint, not an abort")
findings = vpm.hdr_findings(D + "/nostatic.mp4")
check("curve good", field(findings, "Curve").kind == "good")
check("static metadata as a hint",
        field(findings, "Static metadata").kind == "hint")
check("no abort", not [x for x in findings if x.kind == "abort"])

print("\n4. SDR -- falls through")
findings = vpm.hdr_findings(D + "/sdr.mp4")
check("curve not good", field(findings, "Curve").kind != "good",
        field(findings, "Curve").text)
check("bit depth as an abort", field(findings, "Bit depth").kind == "abort",
        field(findings, "Bit depth").text)
check("codec instead of codec profile", field(findings, "Codec") is not None)

print("\n5. The 14 is not an HDR curve")
findings = vpm.hdr_findings(D + "/wrongcurve.mp4")
check("curve 14 is faulted", field(findings, "Curve").kind == "hint",
        field(findings, "Curve").text)
check("but primaries and matrix are good",
        field(findings, "Primaries").kind == "good"
        and field(findings, "Matrix").kind == "good")

print("\n6. Return value of check_hdr")
import io as _io, contextlib
def quiet(file_path):
    buffer = _io.StringIO()
    with contextlib.redirect_stdout(buffer):
        return vpm.check_hdr(file_path)
check("HDR10 -> 0", quiet(D + "/hdr10.mp4") == 0)
check("HLG -> 0", quiet(D + "/hlg.mp4") == 0)
check("without static -> 0 (a note only)", quiet(D + "/nostatic.mp4") == 0)
check("SDR -> 1", quiet(D + "/sdr.mp4") == 1)
check("wrong curve -> 1", quiet(D + "/wrongcurve.mp4") == 1)

print("\n7. Foreign and missing files")
for file_path in (D + "/doesnotexist.mp4", FOREIGN + "/text.txt",
             FOREIGN + "/audio.wav", FOREIGN + "/folder", ""):
    try:
        findings = vpm.hdr_findings(file_path)
        check("no crash on %s" % (os.path.basename(file_path) or "empty"),
                isinstance(findings, list) and bool(findings))
    except Exception as e:
        check("no crash on %s" % (os.path.basename(file_path) or "empty"),
                False, "%s: %s" % (type(e).__name__, str(e)[:40]))

print("\n8. hdr_kind_from_project reads instead of guessing")
class P(object):
    def __init__(self, settings): self.settings = settings
    def GetSetting(self, k=""):
        return dict(self.settings) if k == "" else None
for value, want in (("Rec.2100 ST2084", "pq"), ("Rec.2100 HLG", "hlg"),
                   ("Rec.709 Gamma 2.4", None), ("", None)):
    kind, reason = vpm.hdr_kind_from_project(P({"colorSpaceOutput": value}))
    check("%-20s -> %s" % (repr(value), want), kind == want, str(kind))
kind, _reason = vpm.hdr_kind_from_project(P({}))
check("without a setting -> None", kind is None, str(kind))
class Blind(object):
    def GetSetting(self, k=""): raise RuntimeError("nothing")
check("Resolve does not answer -> None",
        vpm.hdr_kind_from_project(Blind())[0] is None)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)

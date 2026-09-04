# -*- coding: utf-8 -*-
"""#65: Does a finished file carry everything that marks it as HDR?"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import sys, time
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture
vpm = the_program.load()

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

def spell(findings):
    """Field, kind and text of every finding given, for a failure line."""
    return "; ".join("%s %s %r" % (x.field, x.kind, x.text)
                     for x in findings) or "none"

def seen(findings, name, want):
    """One field as it came back, beside what was wanted of it.

    repr and not str, because the interesting case is the empty one: a
    kind or a text that is "" has to stay visible in the line, and a
    field that is not there at all says so and names what is.
    """
    finding = field(findings, name)
    if finding is None:
        return "no %r among %s -- wanted %s" % (
            name, [str(x.field) for x in findings], want)
    return "%s: kind %r, text %r -- wanted %s" % (
        name, finding.kind, finding.text, want)

def written(findings, pick, label):
    """How many findings `pick` keeps, of how many, and which ones."""
    got = [x for x in findings if pick(x)]
    return "%d of %d findings %s: %s" % (len(got), len(findings), label,
                                         spell(got))

print("1. HDR10 with everything")
findings = vpm.hdr_findings(D + "/hdr10.mp4")
check("primaries good", field(findings, "Primaries").kind == "good",
        seen(findings, "Primaries", "good -- HDR needs 9 (BT.2020)"))
check("curve good and PQ", field(findings, "Curve").kind == "good"
        and "PQ" in field(findings, "Curve").text,
        seen(findings, "Curve", "good with PQ in it -- HDR10 needs 16"))
check("matrix good", field(findings, "Matrix").kind == "good",
        seen(findings, "Matrix", "good -- HDR needs 9 (BT.2020)"))
check("bit depth good", field(findings, "Bit depth").kind == "good",
        seen(findings, "Bit depth", "good -- 10 bit or more"))
check("codec profile good", field(findings, "Codec profile").kind == "good",
        seen(findings, "Codec profile", "good -- HEVC with Main 10"))
check("static metadata complete",
        field(findings, "Static metadata").kind == "good",
        seen(findings, "Static metadata", "good -- mdcv and clli both there"))
check("nothing to fault",
        not [x for x in findings if x.kind != "good"],
        written(findings, lambda x: x.kind != "good", "not good"))

print("\n2. HLG -- static metadata is no fault there")
findings = vpm.hdr_findings(D + "/hlg.mp4")
check("curve good and HLG", field(findings, "Curve").kind == "good"
        and "HLG" in field(findings, "Curve").text,
        seen(findings, "Curve", "good with HLG in it -- HLG is 18"))
check("static metadata no fault",
        field(findings, "Static metadata").kind == "good",
        seen(findings, "Static metadata", "good -- HLG asks for none"))
check("nothing to fault", not [x for x in findings if x.kind != "good"],
        written(findings, lambda x: x.kind != "good", "not good"))

print("\n3. PQ without static metadata -- a hint, not an abort")
findings = vpm.hdr_findings(D + "/nostatic.mp4")
check("curve good", field(findings, "Curve").kind == "good",
        seen(findings, "Curve", "good -- 16 (PQ)"))
check("static metadata as a hint",
        field(findings, "Static metadata").kind == "hint",
        seen(findings, "Static metadata", "hint -- neither good nor abort"))
check("no abort", not [x for x in findings if x.kind == "abort"],
        written(findings, lambda x: x.kind == "abort", "aborting"))

print("\n4. SDR -- falls through")
findings = vpm.hdr_findings(D + "/sdr.mp4")
check("curve not good", field(findings, "Curve").kind != "good",
        seen(findings, "Curve", "any kind but good -- 1 is BT.709"))
check("bit depth as an abort", field(findings, "Bit depth").kind == "abort",
        seen(findings, "Bit depth", "abort -- under 10 bit"))
check("codec instead of codec profile", field(findings, "Codec") is not None,
        "fields back: %s -- wanted a 'Codec' among them, not a 'Codec profile'"
        % ([str(x.field) for x in findings],))

print("\n5. The 14 is not an HDR curve")
findings = vpm.hdr_findings(D + "/wrongcurve.mp4")
check("curve 14 is faulted", field(findings, "Curve").kind == "hint",
        seen(findings, "Curve", "hint -- 14 is not an HDR curve"))
check("but primaries and matrix are good",
        field(findings, "Primaries").kind == "good"
        and field(findings, "Matrix").kind == "good",
        "%s; %s" % (seen(findings, "Primaries", "good"),
                    seen(findings, "Matrix", "good")))

print("\n6. Return value of check_hdr")
import io as _io, contextlib
def quiet(file_path):
    """What check_hdr returned, and the verdict line it printed."""
    buffer = _io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = vpm.check_hdr(file_path)
    said = [line.strip() for line in buffer.getvalue().splitlines()
            if line.strip()]
    return code, said[-1] if said else "(printed nothing)"
code, said = quiet(D + "/hdr10.mp4")
check("HDR10 -> 0", code == 0,
        "returned %r, wanted 0 -- said %r" % (code, said))
code, said = quiet(D + "/hlg.mp4")
check("HLG -> 0", code == 0,
        "returned %r, wanted 0 -- said %r" % (code, said))
code, said = quiet(D + "/nostatic.mp4")
check("without static -> 0 (a note only)", code == 0,
        "returned %r, wanted 0 -- said %r" % (code, said))
code, said = quiet(D + "/sdr.mp4")
check("SDR -> 1", code == 1,
        "returned %r, wanted 1 -- said %r" % (code, said))
code, said = quiet(D + "/wrongcurve.mp4")
check("wrong curve -> 1", code == 1,
        "returned %r, wanted 1 -- said %r" % (code, said))

print("\n7. Foreign and missing files")
for file_path in (D + "/doesnotexist.mp4", FOREIGN + "/text.txt",
             FOREIGN + "/audio.wav", FOREIGN + "/folder", ""):
    try:
        findings = vpm.hdr_findings(file_path)
        back = ("%d findings: %s" % (len(findings), spell(findings))
                if isinstance(findings, list) else
                "%s, not a list: %r" % (type(findings).__name__, findings))
        check("no crash on %s" % (os.path.basename(file_path) or "empty"),
                isinstance(findings, list) and bool(findings),
                "%r gave %s -- wanted a list with at least one finding"
                % (file_path, back))
    except Exception as e:
        check("no crash on %s" % (os.path.basename(file_path) or "empty"),
                False, "%r raised %s %r -- wanted a list of findings"
                % (file_path, type(e).__name__, str(e)))

print("\n8. hdr_kind_from_project reads instead of guessing")
class P(object):
    def __init__(self, settings): self.settings = settings
    def GetSetting(self, k=""):
        return dict(self.settings) if k == "" else None
for value, want in (("Rec.2100 ST2084", "pq"), ("Rec.2100 HLG", "hlg"),
                   ("Rec.709 Gamma 2.4", None), ("", None)):
    kind, reason = vpm.hdr_kind_from_project(P({"colorSpaceOutput": value}))
    check("%-20s -> %s" % (repr(value), want), kind == want,
            "colorSpaceOutput %r gave %r, wanted %r -- reason %r"
            % (value, kind, want, reason))
kind, reason = vpm.hdr_kind_from_project(P({}))
check("without a setting -> None", kind is None,
        "no colour setting at all gave %r, wanted None -- reason %r"
        % (kind, reason))
class Blind(object):
    def GetSetting(self, k=""): raise RuntimeError("nothing")
blind = vpm.hdr_kind_from_project(Blind())
check("Resolve does not answer -> None", blind[0] is None,
        "a GetSetting that raises gave %r, wanted (None, '')" % (blind,))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)

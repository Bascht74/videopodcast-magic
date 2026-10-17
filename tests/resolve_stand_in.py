# -*- coding: utf-8 -*-
"""One Resolve for the tests to talk to, and never the real one.

The scripting interface as far as the program uses it: a Resolve that
hands out a project manager, projects with their settings, colour
groups and render queue, a media pool with its clips, and timelines
with tracks and items. Every object writes down what was asked of it,
so a test can judge what the program asked for and not only what it
printed.

**Strict where the real one is strict, and stricter where nobody knows.**
A setting that is not in the project's list is refused; a colour group
or a project whose name is taken is refused; a track that is not there
has no items and cannot be named; a clip colour outside Resolve's
sixteen is refused; a colour group the project did not make is not
taken. What the real Resolve would refuse and this one accepted would
let a test pass where the program fails -- the counter-proof skill,
"does it invent what the real thing refuses?".

**Each refusal is a switch, off by default**: `refuse` names the calls
that answer no, `throw` the calls that raise. A test turns on the one it
is about and leaves the rest as Resolve answers on a good day.

`script_module(folder)` lays a `DaVinciResolveScript` beside a library
file in a folder of the test's own, so `connect_to_resolve` can be run
whole without the real module: its `scriptapp` answers out of `ANSWER`
here and writes down every call in `ASKED`.

Nothing in this file prints; run.sh would count a line against the test.
"""
import os

# What the stand-in module's scriptapp hands back, by the name asked for,
# and every name it was asked for, in order.
ANSWER = {}
ASKED = []

# The sixteen clip colours Resolve 18 and later offer. A name outside
# them is refused, as Resolve refuses it.
CLIP_COLOURS = ("Orange", "Apricot", "Yellow", "Lime", "Olive", "Green",
                "Teal", "Navy", "Blue", "Purple", "Violet", "Pink", "Tan",
                "Beige", "Brown", "Chocolate")


class Refusing(object):
    """The two switches every stand-in object carries.

    `refuse` holds method names that answer no -- False, None or an
    empty list, whatever that call answers when it fails -- and
    `throw` holds method names that raise. Both are sets of names, and
    a test changes them between calls.
    """

    def __init__(self, refuse=(), throw=()):
        self.refuse = set(refuse)
        self.throw = set(throw)
        self.calls = []

    def asked(self, name, *args):
        """Write the call down; raise if that call is set to throw."""
        self.calls.append((name,) + args)
        if name in self.throw:
            raise RuntimeError("stand-in %s refused by raising" % name)
        return name in self.refuse

    def count(self, name):
        """How often this call was made."""
        return len([c for c in self.calls if c[0] == name])


class Resolve(Refusing):
    """What the scripting module hands back when asked for Resolve."""

    def __init__(self, pm=None, product="DaVinci Resolve Studio",
                 version="21.0.4", **switches):
        Refusing.__init__(self, **switches)
        self.pm = pm if pm is not None else ProjectManager()
        self.product, self.version = product, version

    def GetProductName(self):
        self.asked("GetProductName")
        return self.product

    def GetVersionString(self):
        self.asked("GetVersionString")
        return self.version

    def GetProjectManager(self):
        if self.asked("GetProjectManager"):
            return None
        return self.pm


class ProjectManager(Refusing):
    """Projects by name in the current folder; a taken name is refused.

    The open one cannot be deleted, as in Resolve.
    """

    def __init__(self, names=(), refuse_names=(), **switches):
        Refusing.__init__(self, **switches)
        self.projects = dict((n, Project(n)) for n in names)
        self.refuse_names = set(refuse_names)
        self.made, self.current = [], None

    def GetProjectListInCurrentFolder(self):
        self.asked("GetProjectListInCurrentFolder")
        return list(self.projects)

    def CreateProject(self, name):
        if (self.asked("CreateProject", name) or name in self.projects
                or name in self.refuse_names):
            return None
        self.projects[name] = self.current = Project(name)
        self.made.append(name)
        return self.current

    def LoadProject(self, name):
        if (self.asked("LoadProject", name) or name not in self.projects
                or name in self.refuse_names):
            return None
        self.current = self.projects[name]
        return self.current

    def GetCurrentProject(self):
        return self.current

    def DeleteProject(self, name):
        # Resolve deletes none that is open, measured in
        # resolve/live/resolve_ground.py, and none that is not there.
        if (self.asked("DeleteProject", name) or name not in self.projects
                or self.projects[name] is self.current):
            return False
        del self.projects[name]
        return True


class ColourGroup(object):
    def __init__(self, name, owner):
        self.name, self.owner = name, owner

    def GetName(self):
        return self.name


class Project(Refusing):
    """Settings, colour groups, timelines and the render queue.

    `settings` is the list GetSetting("") hands out; a key not in it is
    refused on setting. `accepts` narrows a key to the values Resolve
    takes for it, and `reads_back` makes a key read back something other
    than what was set -- both the shapes a real Resolve has shown.
    Values come back as text, as Resolve hands them out.
    `refuse_groups` names the colour groups AddColorGroup answers no to.
    """

    def __init__(self, name="Stand-in", settings=None, accepts=None,
                 reads_back=None, formats=None, codecs=None,
                 render_refuses=(), refuse_groups=(), **switches):
        Refusing.__init__(self, **switches)
        self.name = name
        self.refuse_groups = set(refuse_groups)
        self.settings = dict((k, str(v)) for k, v in
                             (settings or {}).items())
        self.accepts = dict(accepts or {})
        self.reads_back = dict(reads_back or {})
        self.groups = []
        self.timelines, self.timeline = [], None
        self.pool = MediaPool(self)
        self.formats = formats if formats is not None else {
            "MP4": "mp4", "QuickTime": "mov"}
        self.codecs = codecs if codecs is not None else {
            "mp4": {"H.264": "H264", "H.265": "H265"}}
        # Keys SetRenderSettings will not take: a dictionary holding one
        # is refused whole, as Resolve refuses an unknown key.
        self.render_refuses = set(render_refuses)
        self.render, self.format_codec, self.mode, self.jobs = (
            None, None, None, [])

    def GetName(self):
        return self.name

    # -- settings
    def GetSetting(self, key=""):
        self.asked("GetSetting", key)
        if key == "":
            return dict(self.settings)
        if key in self.reads_back:
            return self.reads_back[key]
        return self.settings.get(key, "")

    def SetSetting(self, key, value):
        if self.asked("SetSetting", key, value) or key not in self.settings:
            return False
        if key in self.accepts and str(value) not in self.accepts[key]:
            return False
        self.settings[key] = str(value)
        return True

    # -- colour groups
    def GetColorGroupsList(self):
        self.asked("GetColorGroupsList")
        return list(self.groups)

    def AddColorGroup(self, name):
        if (self.asked("AddColorGroup", name) or name in self.refuse_groups
                or name in [g.name for g in self.groups]):
            return None
        group = ColourGroup(name, self)
        self.groups.append(group)
        return group

    # -- timelines
    def GetMediaPool(self):
        return self.pool

    def GetTimelineCount(self):
        return len(self.timelines)

    def GetTimelineByIndex(self, i):
        return self.timelines[i - 1] if 1 <= i <= len(self.timelines) \
            else None

    def SetCurrentTimeline(self, tl):
        if self.asked("SetCurrentTimeline", tl) or tl not in self.timelines:
            return False
        self.timeline = tl
        return True

    def GetCurrentTimeline(self):
        return self.timeline

    # -- the render page
    def GetRenderFormats(self):
        self.asked("GetRenderFormats")
        return dict(self.formats)

    def GetRenderCodecs(self, format_id):
        self.asked("GetRenderCodecs", format_id)
        return dict(self.codecs.get(format_id, {}))

    def SetCurrentRenderFormatAndCodec(self, format_id, codec_id):
        if (self.asked("SetCurrentRenderFormatAndCodec", format_id, codec_id)
                or codec_id not in self.codecs.get(format_id, {}).values()):
            return False
        self.format_codec = (format_id, codec_id)
        return True

    def SetCurrentRenderMode(self, mode):
        if self.asked("SetCurrentRenderMode", mode):
            return False
        self.mode = mode
        return True

    def SetRenderSettings(self, settings):
        if (self.asked("SetRenderSettings", dict(settings))
                or set(settings) & self.render_refuses):
            return False
        self.render = dict(settings)
        return True

    def AddRenderJob(self):
        if self.asked("AddRenderJob") or self.render is None:
            return ""
        self.jobs.append(dict(self.render))
        return "job%d" % len(self.jobs)


class Clip(Refusing):
    """A media pool clip: a file, its properties, its audio mapping."""

    def __init__(self, path, properties=None, mapping=None, frames=None,
                 **switches):
        Refusing.__init__(self, **switches)
        self.path = path
        self.properties = dict(properties or {})
        self.properties.setdefault("File Path", path)
        self.mapping = mapping
        self.frames = frames

    def GetName(self):
        return os.path.basename(self.path)

    def GetClipProperty(self, key=None):
        self.asked("GetClipProperty", key)
        if key is None:
            return dict(self.properties)
        return self.properties.get(key, "")

    def GetAudioMapping(self):
        self.asked("GetAudioMapping")
        return self.mapping


class Item(Refusing):
    """A piece on a timeline track, cut out of a clip."""

    def __init__(self, name, frames=0, clip=None, **switches):
        Refusing.__init__(self, **switches)
        self.name, self.frames, self.clip = name, frames, clip
        self.colour, self.group = "", None
        self.start = self.end = None

    def GetName(self):
        self.asked("GetName")
        return self.name

    def GetDuration(self):
        return self.frames

    def GetClipColor(self):
        self.asked("GetClipColor")
        return self.colour

    def SetClipColor(self, name):
        if self.asked("SetClipColor", name) or name not in CLIP_COLOURS:
            return False
        self.colour = name
        return True

    def ClearClipColor(self):
        self.asked("ClearClipColor")
        self.colour = ""
        return True

    def AssignToColorGroup(self, group):
        if (self.asked("AssignToColorGroup", group)
                or not isinstance(group, ColourGroup)):
            return False
        self.group = group
        return True


class Timeline(Refusing):
    """Tracks of items, a name per track, and a start timecode.

    A new timeline has one video and one audio track, as Resolve makes
    it. `moves_start_to` makes the start read back as another timecode
    than the one set, as Resolve does with a timecode it rounds.
    """

    def __init__(self, name, moves_start_to=None, **switches):
        Refusing.__init__(self, **switches)
        self.name = name
        self.tracks = {"video": [[]], "audio": [[]]}
        self.names = {"video": [""], "audio": [""]}
        self.start = "01:00:00:00"
        self.moves_start_to = moves_start_to

    def GetName(self):
        return self.name

    def GetTrackCount(self, kind):
        return len(self.tracks.get(kind, []))

    def GetItemListInTrack(self, kind, i):
        tracks = self.tracks.get(kind, [])
        if not 1 <= i <= len(tracks):
            return None
        return list(tracks[i - 1])

    def AddTrack(self, kind):
        if self.asked("AddTrack", kind) or kind not in self.tracks:
            return False
        self.tracks[kind].append([])
        self.names[kind].append("")
        return True

    def SetTrackName(self, kind, i, name):
        if (self.asked("SetTrackName", kind, i, name)
                or not 1 <= i <= len(self.tracks.get(kind, []))):
            return False
        self.names[kind][i - 1] = name
        return True

    def GetTrackName(self, kind, i):
        return self.names[kind][i - 1] \
            if 1 <= i <= len(self.names.get(kind, [])) else ""

    def SetStartTimecode(self, tc):
        if self.asked("SetStartTimecode", tc):
            return False
        self.start = self.moves_start_to or tc
        return True

    def GetStartTimecode(self):
        self.asked("GetStartTimecode")
        return self.start

    def lay(self, kind, track, item):
        """Put an item on a track, making the track if it is the next one."""
        while len(self.tracks[kind]) < track:
            self.tracks[kind].append([])
            self.names[kind].append("")
        self.tracks[kind][track - 1].append(item)


class Folder(object):
    """A media pool bin: its clips, and the bins inside it."""

    def __init__(self):
        self.clips = []
        self.folders = []

    def GetClipList(self):
        return list(self.clips)

    def GetSubFolderList(self):
        return list(self.folders)


class MediaPool(Refusing):
    """Clips imported from files, and timelines made and filled.

    `takes` limits how many pieces one AppendToTimeline lays -- Resolve
    lays fewer than it was sent and says nothing about it -- and
    `refuse_media` names the media types (1 picture, 2 sound) it lays
    none of.
    """

    def __init__(self, project=None, takes=None, refuse_media=(),
                 **switches):
        Refusing.__init__(self, **switches)
        self.project = project
        self.root = Folder()
        self.takes = takes
        self.refuse_media = set(refuse_media)
        self.sent = []

    def GetRootFolder(self):
        return self.root

    def ImportMedia(self, paths):
        if self.asked("ImportMedia", list(paths)):
            return []
        fresh = [Clip(p) for p in paths if os.path.exists(p)]
        self.root.clips.extend(fresh)
        return fresh

    def CreateEmptyTimeline(self, name):
        taken = [t.GetName() for t in self.project.timelines]
        if self.asked("CreateEmptyTimeline", name) or name in taken:
            return None
        tl = Timeline(name)
        self.project.timelines.append(tl)
        self.project.timeline = tl
        return tl

    def DeleteTimelines(self, timelines):
        if self.asked("DeleteTimelines", list(timelines)):
            return False
        for tl in timelines:
            if tl in self.project.timelines \
                    and tl is not self.project.timeline:
                self.project.timelines.remove(tl)
        return True

    def AppendToTimeline(self, entries):
        """Lay pieces on the current timeline; hand back what was laid."""
        entries = list(entries)
        self.sent.append(entries)
        if self.asked("AppendToTimeline", entries):
            return []
        tl = self.project.timeline
        laid = []
        for e in entries:
            if self.takes is not None and len(laid) >= self.takes:
                break
            if not isinstance(e, dict) or tl is None:
                continue
            kind = e.get("mediaType")
            if kind in self.refuse_media:
                continue
            clip = e.get("mediaPoolItem")
            first, last = e.get("startFrame", 0), e.get("endFrame")
            if last is None:
                last = clip.frames if clip is not None and clip.frames \
                    else first
            item = Item(clip.GetName() if clip is not None else "",
                        frames=last - first, clip=clip)
            item.start, item.end = first, e.get("endFrame")
            item.record = e.get("recordFrame")
            for kind_name, number in (("video", 1), ("audio", 2)):
                if kind in (None, number):
                    tl.lay(kind_name, e.get("trackIndex", 1), item)
            laid.append(item)
        return laid


def script_module(folder):
    """Lay a scripting module and a library file; return (api, lib).

    The module is a file of its own, as the real one is, so the import
    connect_to_resolve makes is a real import. Its scriptapp answers out
    of ANSWER in this file and writes every call into ASKED.
    """
    modules = os.path.join(folder, "Modules")
    if not os.path.isdir(modules):
        os.makedirs(modules)
    with open(os.path.join(modules, "DaVinciResolveScript.py"), "w") as f:
        f.write("import resolve_stand_in as _stand_in\n\n\n"
                "def scriptapp(app):\n"
                "    _stand_in.ASKED.append(app)\n"
                "    return _stand_in.ANSWER.get(app)\n")
    lib = os.path.join(folder, "fusionscript.so")
    open(lib, "w").close()
    return folder, lib

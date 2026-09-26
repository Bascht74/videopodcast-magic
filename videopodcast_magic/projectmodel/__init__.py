# -*- coding: utf-8 -*-
"""What a production is, held in one place: ProjectModel.

A piece of the program, read in by beside() from the window. It holds
no widget and imports no Qt: the files, the settings and the
assignment, which the project file writes and reads and the run is
built from. Those two read it here instead of being handed each part
as an argument of its own. The program is handed in, bound by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program, bound once.
ByFile = PROGRAM.ByFile
FileSet = PROGRAM.FileSet
TYPE_CONTENT = PROGRAM.TYPE_CONTENT
Value = PROGRAM.Value
as_hms = PROGRAM.as_hms
os = PROGRAM.os
parse_time_point = PROGRAM.parse_time_point


class ProjectModel(object):
    """One production's data, apart from the widgets that show it.

    Made once with the window and never replaced: the widgets bind to
    its Values and the tables are redrawn around its lists, so every
    part of the window reaches the same object. project_new empties
    it, project_open fills it, project_write and the run read it. A
    setting stays a Value, which is already watched.
    """

    def __init__(self, lufs, speech_language):
        """Everything empty; the two defaults a window starts with come in."""
        self.files = []                  # [(path, "audio"|"video")]
        self.out_folder = Value("")
        self.production = Value("")
        self.in_point = Value("")
        self.out_point = Value("")
        self.project_type = Value("")    # "cut", "sync", or not asked
        self.multitrack = Value(False)
        self.edge_on = Value(True)       # the wide shot at both edges
        self.lufs = Value(lufs)
        self.speech_language = Value(speech_language)
        # {command line name: Value}, and the auphonic.com key and the
        # folder of finished tracks: each made by the box showing it,
        # which puts it here, so they stand empty until then.
        self.cut = {}
        self.key = None
        self.done_folder = None
        self.clip_kinds = ByFile()       # video file -> Value of its Kind
        # One value per video file, shown twice -- file list and player.
        # Not a second store: the same object both times.
        self.audio_use = ByFile()
        self.channel_choice = ByFile()   # file -> {pair: stereo yes/no}
        # Which blocks make up which recording. The channels are judged
        # over the whole recording, not its first block -- blocks_facts.
        self.blocks_of = ByFile()
        self.recording_of = ByFile()
        # file -> [(track file, label)]. An empty list means looked at and
        # whole; a missing entry means not looked at yet.
        self.split_files = ByFile()
        # Blocks taken out of a recording by hand stand on their own from
        # then on. Only removing the whole recording clears its marks.
        self.no_join = FileSet()
        # Files put into a recording by hand: {file: the recording it
        # joins}. The counterpart to no_join, stored in the project alike.
        self.join_to = ByFile()
        self.assign_lines = []   # [(chain, name_value, camera_value)]
        self.camera_lines = []   # [(path, name_value, own, own_name)]
        # One row per voice a separation heard, hanging under the
        # recording it was heard in: a tree says the level by the place.
        self.voice_lines = []    # [(key, name_value, camera_value)]
        self.remembered = {}     # survives a redraw of the table

    def commonest_folder(self):
        """Return the folder most of the chosen files come from."""
        counter = {}
        for p, _ in self.files:
            folder = os.path.dirname(os.path.abspath(p))
            counter[folder] = counter.get(folder, 0) + 1
        return max(counter, key=counter.get) if counter else None

    def together_now(self):
        """The by-hand groupings, as group_recording_parts wants them."""
        return [[target, source]
                for source, target in sorted(self.join_to.items())
                if target and target != source]

    def files_for_run(self):
        """The file list a run is given, with tracks in place of sources.

        Only here, not in the list the project stores: that one keeps the
        files as they lie on disc. The tracks are cut afresh each time.
        """
        out = []
        for p, kind in self.files:
            pieces = (self.split_files.get(p) or []
                      if kind == "audio" else [])
            if pieces:
                out += [(x, "audio") for x, _label in pieces]
            else:
                out.append((p, kind))
        return out

    def window_length(self):
        """Return the length of the window, empty if none is set."""
        try:
            a, _ = parse_time_point(self.in_point.get(), 30.0)
            b, _ = parse_time_point(self.out_point.get(), 30.0)
        except Exception:
            return ""
        if a is None or b is None or b <= a:
            return ""
        return as_hms(b - a)

    def clip_kind_value(self, path):
        """One video file's Kind -- one value, and two places show it."""
        return self.clip_kinds.setdefault(
            path, Value(self.remembered.get("kind:" + path) or TYPE_CONTENT))

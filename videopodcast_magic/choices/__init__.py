# -*- coding: utf-8 -*-
"""The values that are stored and shown at once, and what they are called.

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and the one name this piece uses out of it is bound below, by name.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses. One name, and it stands
# above the seam, so it is a copy of what was there and not read late.
T = PROGRAM.T


# =====================================================================
#  What is stored, and what it is called on screen
#  -----------------------------------------------

# Values that are stored and shown at the same time. The value is fixed so
# a project file keeps its meaning in any language; what appears on screen
# comes from CHOICE_LABELS and goes through T().
MIX_ONLY = "mix-only"            # audio track without a camera of its own
IGNORE_AUDIO = "ignore-audio"    # audio track stays out entirely
# The answer "I do not know, go and measure" to the name field's
# question of who is to be heard: a typed name claims one person, this
# says there are several and the machine is to tell them apart.
SEVERAL_SPEAKERS = "several-speakers"
PRESET_NONE = "no-auphonic"      # list entry, not a preset name
TYPE_CONTENT, TYPE_INTRO, TYPE_OUTRO = "content", "intro", "outro"
# The camera nobody sits in front of. A value of the Kind field rather
# than something derived, so it is an answer somebody gives instead of
# a guess -- and it travels in the project file and on the switch.
TYPE_WIDE = "wide-shot"
TYPE_IGNORED = "ignore-video"    # video file stays out entirely
CLIP_TYPES = (TYPE_CONTENT, TYPE_WIDE, TYPE_INTRO, TYPE_OUTRO,
              TYPE_IGNORED)
# Which kinds are a camera in the run. The wide shot is one like any
# other -- aligned, rendered, cut to; the mark says only that no
# speaker belongs to it. Named once here rather than at every place
# that asks "is this a camera".
CAMERA_TYPES = (TYPE_CONTENT, TYPE_WIDE)
# Whether a video file's sound is material for the run. It cannot be
# measured: a radio microphone recorded into the video track looks like
# a room microphone, so only whoever was there knows. Synchronising is
# untouched by it; this decides only whether the sound counts as content.
AUDIO_UNUSED = "audio-unused"
AUDIO_MATERIAL = "audio-material"
AUDIO_USE = (AUDIO_UNUSED, AUDIO_MATERIAL)
# Two names that are easy to confuse: "do not use" leaves the audio out
# entirely, "no camera of its own" only keeps the person off camera.
# The fuller wording is twice as wide as the column allows, so the rest
# of it lives in the tooltip.
CHOICE_LABELS = {MIX_ONLY: "no camera of its own",
                 IGNORE_AUDIO: "do not use",
                 SEVERAL_SPEAKERS: "several speakers",
                 PRESET_NONE: "work without Auphonic",
                 TYPE_CONTENT: "Content", TYPE_INTRO: "Intro",
                 # The same words the cut band, the legend and the four
                 # cut rules use. A second name for one thing would
                 # read as a second thing.
                 TYPE_WIDE: 'Wide shot',
                 TYPE_OUTRO: "Outro", TYPE_IGNORED: "ignore this video",
                 AUDIO_UNUSED: "do not use the audio",
                 AUDIO_MATERIAL: "use the audio"}


def label_of(value):
    """Return what a stored value is called on screen."""
    return T(CHOICE_LABELS[value]) if value in CHOICE_LABELS else value


def fill_choices(box, values, chosen=None):
    """Fill a combo box: it stores the value and shows the label."""
    box.clear()
    for v in values:
        box.addItem(label_of(v), v)
    if chosen is not None:
        pick_choice(box, chosen)


def pick_choice(box, value):
    """Select the entry that stands for this value; first one if unknown."""
    i = box.findData(value)
    box.setCurrentIndex(i if i >= 0 else 0)

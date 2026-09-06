# -*- coding: utf-8 -*-
"""The values that are stored and shown at once, and what they are called.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam, so it is a copy and not read late.
T = PROGRAM.T


# =====================================================================
#  What is stored, and what it is called on screen
#  -----------------------------------------------

# The value is fixed so a project file keeps its meaning in any
# language; what is shown comes from CHOICE_LABELS, through T().
MIX_ONLY = "mix-only"            # audio track without a camera of its own
IGNORE_AUDIO = "ignore-audio"    # audio track stays out entirely
# The name field's "I do not know, go and measure": a typed name
# claims one person, this says several and asks the machine to tell.
SEVERAL_SPEAKERS = "several-speakers"
PRESET_NONE = "no-auphonic"      # list entry, not a preset name
TYPE_CONTENT, TYPE_INTRO, TYPE_OUTRO = "content", "intro", "outro"
# The camera nobody sits in front of. A value of the Kind field, not
# something derived, so it is an answer given rather than a guess.
TYPE_WIDE = "wide-shot"
TYPE_IGNORED = "ignore-video"    # video file stays out entirely
CLIP_TYPES = (TYPE_CONTENT, TYPE_WIDE, TYPE_INTRO, TYPE_OUTRO,
              TYPE_IGNORED)
# Which kinds are a camera in the run. The wide shot is one like any
# other -- aligned, rendered, cut to; only no speaker belongs to it.
CAMERA_TYPES = (TYPE_CONTENT, TYPE_WIDE)
# Whether a video file's sound is material. It cannot be measured: a
# radio microphone in the video track looks like a room microphone.
# Synchronising is untouched; this decides only what counts as content.
AUDIO_UNUSED = "audio-unused"
AUDIO_MATERIAL = "audio-material"
AUDIO_USE = (AUDIO_UNUSED, AUDIO_MATERIAL)
# Two names easy to confuse: "do not use" leaves the audio out
# entirely, "no camera of its own" only keeps the person off camera.
CHOICE_LABELS = {MIX_ONLY: "no camera of its own",
                 IGNORE_AUDIO: "do not use",
                 SEVERAL_SPEAKERS: "several speakers",
                 PRESET_NONE: "work without Auphonic",
                 TYPE_CONTENT: "Content", TYPE_INTRO: "Intro",
                 # The same words the cut band, the legend and the cut
                 # rules use; a second name reads as a second thing.
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

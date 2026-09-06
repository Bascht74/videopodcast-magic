# -*- coding: utf-8 -*-
"""The dials the cut is set with, and the value a dial holds.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in. Nothing is bound below.
"""

# Put here by beside() before this file is read; no line reads it.
PROGRAM = PROGRAM


# =====================================================================
#  The dials of the cut
#  --------------------

class Value(object):
    """A value several observers can watch.

    Qt binds a value to its input widget, but the assignment table is
    rebuilt on every change: the widgets go, the values must not.
    """

    def __init__(self, value=""):
        self._value = value
        self._listeners = []

    def get(self):
        return self._value

    def typed(self):
        """Only the answer given here, with nothing standing in for it.

        get() is the plain reading; this is for the two places that must
        tell an answer from a guess -- what a widget shows, and what the
        project file saves. Only on a name field do the two differ.
        """
        return self._value

    def set(self, value):
        if value == self._value:
            return
        self._value = value
        for f in list(self._listeners):
            try:
                f()
            except Exception:
                pass

    def listen(self, f):
        self._listeners.append(f)
        return f

# What is shown where "whoever speaks is on screen" gives no answer.
SHOT_WIDE = "wide"
SHOT_LISTENER = "listener"
SHOT_ALTERNATE = "alternate"
SHOT_HOLD = "hold"
SHOT_HOLD_BRIEF = "hold-brief"
SHOT_OFF = "off"
SHOT_ANSWER = "answer"

SHOT_NAMES = {
    SHOT_WIDE: 'Wide shot',
    SHOT_LISTENER: 'Listener',
    SHOT_ALTERNATE: 'Alternating',
    SHOT_HOLD: 'No camera change',
    # Holding without an end is a different answer from holding a
    # breath, so the seconds stand in a field of their own.
    SHOT_HOLD_BRIEF: 'Hold a short gap',
    # Named after what does not happen: in a row labelled "Question"
    # the picture going early is the only thing to leave alone.
    SHOT_OFF: 'do not go early',
    SHOT_ANSWER: 'Answering speaker',
}

# The shortest a shot may stand: a camera changing faster than the
# viewer can settle on a face reads as nervous. One value for all.
MIN_EDIT_DURATION_S = 3.0

# Up to here a gap with nobody in it is a breath, not an end. At one
# second nothing stands on a silent person past 4.0 s; at two, the
# first over five appear.
SILENCE_HOLD_S = 1.0

# How fine the camera cut turns out. Per entry: switch, label,
# default, unit, short explanation beside it, longer in the tooltip.
CUT_FIELDS = (
    ("min-edit-duration", 'Minimum Edit Duration',
     "%.1f" % MIN_EDIT_DURATION_S, "s",
     'shorter shots are merged in',
     'Shorter shots fall into the following one.'),
    ("min-speech-to-switch", 'Speaks at least', "1.5", "s",
     'below this the camera does not follow',
     ('A short "yes" does not move the picture. Without this a block of '
      'half a second draws the camera over, and the minimum edit '
      'duration then holds it there for seconds.')),
    ("silence-hold", 'Short gap up to', "%.1f" % SILENCE_HOLD_S, "s",
     'so long a silence leaves the picture alone',
     ('Only where "Nobody speaks" is set to hold a short gap. A gap up '
      'to this long changes nothing, a longer one goes to the wide '
      'shot. Above two seconds the picture begins to stand on someone '
      'silent for over five seconds.')),
    # Resolve's own name for it, in the German window as well, so it stays
    # English. The double quotes are the mark: this one is not translated.
    ("edit-change-delay", "Edit Change Delay", "0.3", "s",
     'the picture changes this much later than the sound',
     'A negative value makes the picture lead the sound.'),
    ("reaction-lead", 'Answer on screen earlier', "1.5", "s",
     'before the question ends',
     ('Zero is where the asker stops, not where the answer starts: the '
      'pause between them belongs to the question. Applies only where '
      '"After a question" asks for it, and the Edit Change Delay is '
      'not added again.')),
    ("wide-after", 'Wide shot after', "70", "s",
     'from here on a good moment for it is looked for',
     ('The soft limit of the pair: from here the program waits for a '
      'sentence boundary and puts the wide shot there, not on the '
      'clock. 0 turns it off. "Wide shot at the latest" is the hard '
      'limit, where it cuts without one.')),
    ("wide-latest", 'Wide shot at the latest', "120", "s",
     'and here it is cut, good moment or not',
     ('The hard limit of the pair: where no sentence boundary has '
      'turned up since "Wide shot after", the longest speech pause '
      'stands in for one, and at this point the cut happens whatever '
      'is being said.')),
    ("wide-length", 'Wide shot at least', "5", "s",
     'so long the inserted wide shot stands at least',
     ('It then runs to the end of the sentence. Below five seconds the '
      'look reads as a twitch.')),
    ("wide-most", 'Wide shot at most', "15", "s",
     'and at most this long',
     ('Where the end of the sentence lies beyond it, the last clause '
      'break before it ends the shot -- it is not cut off mid-sentence.')),
)

# Where the speech does not say whom to show. Per entry: switch,
# label, default, the values it takes, short explanation, tooltip.
CUT_CHOICES = (
    # Directly under "Answer on screen earlier": one question, one place.
    ("on-question", 'After a question', SHOT_ANSWER,
     (SHOT_OFF, SHOT_ANSWER, SHOT_LISTENER),
     'the picture goes to the answer before it starts',
     ('Only after a question that is not the main speaker\'s, when '
      'somebody else takes over at once and keeps the floor.\n"do not '
      'go early" means no early camera change: the picture follows '
      'the sound here as it does everywhere else.')),
    ("on-monologue", 'Long monologue', SHOT_ALTERNATE,
     (SHOT_WIDE, SHOT_LISTENER, SHOT_ALTERNATE, SHOT_HOLD),
     'one person holds the floor past "Wide shot after"',
     ('"Alternating" remembers what the last break of this monologue '
      'showed. The listener only gets the picture when someone on that '
      'camera was heard in the last 20 seconds; otherwise the wide '
      'shot.')),
    ("on-together", 'Several speak at once', SHOT_WIDE,
     (SHOT_WIDE, SHOT_LISTENER, SHOT_ALTERNATE, SHOT_HOLD),
     'and no camera shows exactly them',
     'Cutting into a jumble looks frantic.'),
    # Directly above "Recognition uncertain", easily taken for it:
    # nobody speaking is not recognition being unsure, and this case
    # decides a fifth of the running time against three thousandths.
    ("on-silence", 'Nobody speaks', SHOT_WIDE,
     (SHOT_WIDE, SHOT_HOLD_BRIEF, SHOT_HOLD),
     'no voice is heard at all here',
     ('A breath in the middle of a sentence and the end of a thought '
      'are both silence, and the program cannot tell them apart. Only '
      'the length can: "Short gap up to" says how long a silence may '
      'be and still count as a breath.')),
    ("on-uncertain", 'Recognition uncertain', SHOT_WIDE,
     (SHOT_WIDE, SHOT_LISTENER, SHOT_ALTERNATE, SHOT_HOLD),
     'the speaker recognition frays or leaves a heap behind',
     ('Guessing puts the wrong person on screen for seconds; the wide '
      'shot is right in every case. Somebody is speaking here -- where '
      'nobody is, "Nobody speaks" decides.')),
)

# Third-party components

This program is a Python package: the folder `videopodcast_magic/`, installed
with pip3. It contains no third-party code. What it leans on is installed
beside it by pip, or started as a separate program, and each is named here
with its licence, as `pip3 show` reports it.

## Installed with it

pip3 installs every one of these, always, because `pyproject.toml` names
them. None is optional and none is fetched later:

  numpy          BSD-3-Clause          the measurements
  PySide6        LGPL-3.0 (or GPL)     the window and the player in it
  certifi        MPL-2.0               the certificates an HTTPS
                                       download is verified against
  faster-whisper MIT                   speech recognition
  pyannote.audio MIT                   speaker separation
  torchvision    BSD-3-Clause          named so that pyannote.audio can
                                       be imported; it would come anyway

## Pulled in by those

These are not named by the program, but pip brings them, and they are
the largest part of an installation:

  torch          BSD-3-Clause, parts   brought by pyannote.audio and
                 Apache-2.0, MIT,      torchvision
                 BSL-1.0
  torchaudio     BSD-2-Clause          brought by pyannote.audio
  onnxruntime    MIT                   brought by faster-whisper; its
                                       reporting to Microsoft is
                                       switched off before it loads

They bring further packages of their own. `pip3 show <name>` names each
one and its licence.

## Started as separate programs

  ffmpeg/ffprobe LGPL-2.1+ or GPL      the system's own, when it has one

Where the system brings none -- Windows, or a Linux whose own is older
than the program needs -- the program offers to fetch a built one:
the "gpl" build from https://github.com/BtbN/FFmpeg-Builds, under the
GPL, as its file name says. It is fetched only when the user agrees, from
that address straight onto the user's machine, into the program's own
folder. Nothing of it is in this repository.

## For the test suite only

  pyspellchecker MIT                   named in requirements-dev.txt;
                                       the program never imports it

## Shipped from here: the speaker model

One thing is redistributed here, and it is not code: the pretrained model
files under `videopodcast_magic/models/`.

  speaker-diarization-community-1  CC BY 4.0  the models under models/

PySide6 is used through an ordinary Python import, which is dynamic linking.
The LGPL permits this without placing its own terms on the importing work,
provided the user can replace the library -- and the user can, because
PySide6 is installed separately by pip and never shipped from here.

ffmpeg and ffprobe are executed as separate programs over the command line.
Running a program does not place its licence on the caller. Nothing from
either is copied into this repository.

pyannote.audio is not shipped from here either. pip installs it with the
program, and the program runs it as its own process.

The models it runs are shipped from here, in
`videopodcast_magic/models/speaker-diarization-community-1/`: the pretrained
pipeline `speaker-diarization-community-1` by pyannoteAI and Hervé Bredin,
published under CC BY 4.0. They are in the repository, not in what pip
installs; the program fetches them from this repository the first time it
separates speakers. CC BY 4.0 allows passing them on, and asks for
attribution in return -- so the licence text, the authors' own model card
and the three papers they ask to have cited travel in the same folder, as
`LICENSE-CC-BY-4.0.txt`, `MODEL_CARD.md` and `NOTICE.md`. The files are the
authors' files, byte for byte: nothing was retrained, converted, renamed or
repacked, and `SHA256SUMS.txt` in that folder is what proves it. The
official source is https://hf.co/pyannote/speaker-diarization-community-1;
it asks for a free account and a read token, and it stays the recommended
way to get the models.

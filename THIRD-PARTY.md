# Third-party components

This program is one Python file. It does not contain, bundle or redistribute
any third-party code. What it uses, it uses at run time:

  numpy          BSD-3-Clause          imported for the measurements
  PySide6        LGPL-3.0 (or GPL)     imported for the window
  pyspellchecker MIT                   imported by the test suite only
  pyannote.audio MIT                   imported for speaker diarization
  ffmpeg/ffprobe LGPL-2.1+ or GPL      started as separate programs

The program installs three more by itself, each only where it is needed,
and each named here because a user who did not ask for it should still
be able to find out what it is:

  certifi        MPL-2.0               the certificates an HTTPS
                                       download is verified against,
                                       fetched where this Python brings
                                       none of its own
  faster-whisper MIT                   speech recognition where the
                                       system brings none -- everywhere
                                       but macOS 26 and newer
  static-ffmpeg  BSD-3-Clause          ffmpeg builds inside a Python
                                       package, the last resort where
                                       no package manager has one

One thing is redistributed here, and it is not code: the pretrained model
files under `models/`.

  speaker-diarization-community-1  CC BY 4.0  the models under models/

PySide6 is used through an ordinary Python import, which is dynamic linking.
The LGPL permits this without placing its own terms on the importing work,
provided the user can replace the library -- and the user can, because
PySide6 is installed separately with pip and never shipped from here.

ffmpeg and ffprobe are executed as separate programs over the command line.
Running a program does not place its licence on the caller. Nothing from
either is copied into this repository.

pyannote.audio is not shipped from here either. It is installed with pip
into a separate environment when the user asks for speaker diarization, and
it is run as its own process.

The models it runs are shipped from here, in
`models/speaker-diarization-community-1/`: the pretrained pipeline
`speaker-diarization-community-1` by pyannoteAI and Hervé Bredin, published
under CC BY 4.0. CC BY 4.0 allows passing them on, and asks for attribution
in return -- so the licence text, the authors' own model card and the three
papers they ask to have cited travel in the same folder, as
`LICENSE-CC-BY-4.0.txt`, `MODEL_CARD.md` and `NOTICE.md`. The files are the
authors' files, byte for byte: nothing was retrained, converted, renamed or
repacked, and `SHA256SUMS.txt` in that folder is what proves it. The
official source is https://hf.co/pyannote/speaker-diarization-community-1;
it asks for a free account and a read token, and it stays the recommended
way to get the models.

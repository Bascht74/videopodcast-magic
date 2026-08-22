# Third-party components

This program is one Python file. It does not contain, bundle or redistribute
any third-party code. What it uses, it uses at run time:

  numpy          BSD-3-Clause          imported for the measurements
  PySide6        LGPL-3.0 (or GPL)     imported for the window
  pyspellchecker MIT                   imported by the test suite only
  ffmpeg/ffprobe LGPL-2.1+ or GPL      started as separate programs

PySide6 is used through an ordinary Python import, which is dynamic linking.
The LGPL permits this without placing its own terms on the importing work,
provided the user can replace the library -- and the user can, because
PySide6 is installed separately with pip and never shipped from here.

ffmpeg and ffprobe are executed as separate programs over the command line.
Running a program does not place its licence on the caller. Nothing from
either is copied into this repository.

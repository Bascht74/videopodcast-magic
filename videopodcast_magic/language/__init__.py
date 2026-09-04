# -*- coding: utf-8 -*-
"""The translations, one file per language, keyed by the English text.

Nothing imports these as modules: `texts_of_language` reads each one
from its path, because a test loads the program from an absolute path
under the name `vpm`, and `videopodcast_magic.language` is not
importable then.

This file exists so that pip ships the folder. Without it setuptools
sees loose data and leaves it behind, and an installed copy speaks
English only.
"""

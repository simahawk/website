# -*- coding: utf-8 -*-

import mimetypes
MTYPES = mimetypes.types_map.values()
IMAGE_TYPES = [x for x in MTYPES if x.startswith('image/')]
AUDIO_TYPES = [x for x in MTYPES if x.startswith('audio/')]
VIDEO_TYPES = [x for x in MTYPES if x.startswith('video/')]


class AttrDict(dict):
    """A smarter dict."""

    def __getattr__(self, k):
        """Well... get and return given attr."""
        return self[k]

    def __setattr__(self, k, v):
        """Well... set given attr."""
        self[k] = v

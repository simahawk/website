# -*- coding: utf-8 -*-

import time
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




def timeit(method):
    """Decorates methods to measure time."""

    def timed(*args, **kw):

        print 'START', method.__name__
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print 'STOP', method.__name__

        print 'TIME %r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te - ts)
        return result

    return timed

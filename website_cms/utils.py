# -*- coding: utf-8 -*-


class AttrDict(dict):
    """A smarter dict."""

    def __getattr__(self, k):
        """Well... get and return given attr."""
        return self[k]

    def __setattr__(self, k, v):
        """Well... set given attr."""
        self[k] = v

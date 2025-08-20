class WordnikError(Exception):
    """Base class for all Wordnik library exceptions."""


class FailedToRefetchResult(WordnikError):
    pass


class Unauthorized(WordnikError):
    """Raised when we fail to auth with Wordnik."""

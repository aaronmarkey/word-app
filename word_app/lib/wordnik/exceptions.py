class WordnikError(Exception):
    """Base class for all Wordnik library exceptions."""


class FailedToRefetchResult(WordnikError):
    pass

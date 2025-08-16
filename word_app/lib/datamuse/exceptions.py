class DatamuseError(Exception):
    """Base class for all Datamuse library exceptions."""


class FailedToRefetchResult(DatamuseError):
    pass

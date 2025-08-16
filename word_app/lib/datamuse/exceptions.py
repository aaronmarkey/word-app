class DatamuseError(Exception):
    """Base class for all DatamuseClient exceptions."""


class FailedToRefetchResult(DatamuseError):
    pass

class SEWError(Exception):
    """Base class for SEW exceptions."""


class InvalidPathOrPixels(SEWError):
    """Throw this exception when an the user gives an invalid path_or_pixels object."""


class SourceExtractorExecutableError(SEWError):
    """Throw this exception when there is an error finding/running SExtractor."""
    
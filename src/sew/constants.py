import os
from pathlib import Path

from .errors import SourceExtractorExecutableError

__all__ = [
    "PACKAGE_PATH",
    "REPO_PATH",
    "SE_EXECUTABLE",
]


PACKAGE_PATH = Path(__file__).parent
REPO_PATH = PACKAGE_PATH.parent.parent
SE_EXECUTABLE = os.getenv("SE_EXECUTABLE")

if SE_EXECUTABLE is None:
    raise SourceExtractorExecutableError(
        "SE_EXECUTABLE env variable not set -> set this env variable to your local SExtractor executable"
    )

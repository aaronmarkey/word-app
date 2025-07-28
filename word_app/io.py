"""IO utilities for the Word App."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path


class ApplicationPath:
    class Location(StrEnum):
        ROOT = ""
        USER = "usr"

    def _get_application_root(self) -> Path:
        """Get the path to the application directory."""
        return Path(__file__).parent

    def get_path_for(self, *, location: ApplicationPath.Location) -> Path:
        root = self._get_application_root()
        return root / location.value if location.value else root

    @property
    def usr(self) -> Path:
        return self.get_path_for(location=ApplicationPath.Location.USER)

    @property
    def root(self) -> Path:
        return self.get_path_for(location=ApplicationPath.Location.ROOT)

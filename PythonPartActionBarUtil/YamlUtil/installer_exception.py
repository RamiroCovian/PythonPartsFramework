"""Custom Exceptions for Allep Installer."""

class PackageExtractionError(Exception):
    """Error raised during Package Extraction."""


class InstallRequirementsError(Exception):
    """Error raised during requirements installation."""


class CreateActionBarError(Exception):
    """Error raised during creating actb and npd file."""

class MinimumAllplanVersionError(Exception):
    """Error raised when versions dont match"""
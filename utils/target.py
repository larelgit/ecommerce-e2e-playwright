"""A distinct error for target availability failures in navigation/preflight."""


class TargetUnavailableError(RuntimeError):
    """The target cannot serve the application to this test runner."""

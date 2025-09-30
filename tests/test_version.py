"""Tests for uuid_forge._version module."""

from uuid_forge import _version


class TestVersion:
    """Test version module functionality."""

    def test_version_is_string(self):
        """Test that version is a string."""
        assert isinstance(_version.__version__, str)

    def test_version_not_empty(self):
        """Test that version is not empty."""
        assert len(_version.__version__) > 0

    def test_version_format(self):
        """Test that version follows expected format."""
        # Should be something like "0.1.0" or "0.1.0.dev0"
        version = _version.__version__
        parts = version.split(".")
        assert len(parts) >= 2  # At least major.minor
        assert parts[0].isdigit()  # Major version should be numeric
        assert parts[1].isdigit()  # Minor version should be numeric

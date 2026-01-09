"""Tests for version module"""
import pytest
from core.version import __version__
from core.__version__ import __version__ as version_alt


class TestVersion:
    """Tests for version information"""
    
    def test_version_format(self):
        """Version should be in semver format"""
        parts = __version__.split(".")
        assert len(parts) >= 3
        # Major and minor should be integers
        assert parts[0].isdigit()
        assert parts[1].isdigit()
    
    def test_version_consistency(self):
        """Both version files should have same version"""
        assert __version__ == version_alt
    
    def test_version_not_empty(self):
        """Version should not be empty"""
        assert __version__
        assert len(__version__) > 0

"""Tests for uuid_forge.__init__ module."""

import uuid_forge


class TestImports:
    """Test that all public imports work correctly."""

    def test_import_core_functions(self):
        """Test that core functions can be imported."""
        assert hasattr(uuid_forge, "generate_uuid_only")
        assert hasattr(uuid_forge, "generate_uuid_with_prefix")
        assert hasattr(uuid_forge, "extract_uuid_from_prefixed")
        assert hasattr(uuid_forge, "generate_salt")

    def test_import_classes(self):
        """Test that classes can be imported."""
        assert hasattr(uuid_forge, "IDConfig")
        assert hasattr(uuid_forge, "UUIDGenerator")

    def test_version_available(self):
        """Test that version is available."""
        assert hasattr(uuid_forge, "__version__")
        assert isinstance(uuid_forge.__version__, str)

    def test_module_docstring(self):
        """Test that module has proper docstring."""
        assert uuid_forge.__doc__ is not None
        assert "UUID-Forge" in uuid_forge.__doc__


class TestBasicFunctionality:
    """Test basic functionality works through module imports."""

    def test_generate_uuid_only_works(self):
        """Test that generate_uuid_only works when imported from module."""
        config = uuid_forge.IDConfig(salt="test-salt")
        result = uuid_forge.generate_uuid_only("test", config=config, key="value")
        assert isinstance(result, uuid_forge.core.uuid_module.UUID)

    def test_generate_with_prefix_works(self):
        """Test that generate_uuid_with_prefix works when imported from module."""
        config = uuid_forge.IDConfig(salt="test-salt")
        result = uuid_forge.generate_uuid_with_prefix(
            "test", prefix="TST", config=config, key="value"
        )
        assert isinstance(result, str)
        assert result.startswith("TST-")

    def test_id_config_works(self):
        """Test that IDConfig works when imported from module."""
        config = uuid_forge.IDConfig(salt="test-salt")
        assert config.salt == "test-salt"

    def test_uuid_generator_works(self):
        """Test that UUIDGenerator works when imported from module."""
        config = uuid_forge.IDConfig(salt="test-salt")
        generator = uuid_forge.UUIDGenerator(config)
        result = generator.generate("test", key="value")
        assert isinstance(result, uuid_forge.core.uuid_module.UUID)

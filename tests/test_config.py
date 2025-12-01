"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from toulmini.config import (
    Config,
    ConfigurationError,
    get_config,
    reset_config,
    set_config_value,
)


# === Fixtures ===


@pytest.fixture(autouse=True)
def reset_config_cache():
    """Reset config cache before and after each test."""
    reset_config()
    yield
    reset_config()


# === Default Configuration Tests ===


def test_default_config():
    """Test default configuration values when no environment variables are set."""
    with patch.dict(os.environ, {}, clear=True):
        reset_config()
        config = get_config()

        # Feature toggles
        assert config.enable_council is True

        # Circuit breakers
        assert config.strict_mode is True
        assert config.fail_on_weak_warrant is True
        assert config.fail_on_weak_backing is True

        # Debugging
        assert config.debug is False
        assert config.log_level == "INFO"


def test_config_is_singleton():
    """Test that get_config() returns the same instance (cached)."""
    config1 = get_config()
    config2 = get_config()

    # Should be the exact same object due to lru_cache
    assert config1 is config2


def test_config_dataclass_properties():
    """Test that Config is a properly structured dataclass."""
    config = get_config()

    assert isinstance(config, Config)
    assert hasattr(config, "enable_council")
    assert hasattr(config, "strict_mode")
    assert hasattr(config, "fail_on_weak_warrant")
    assert hasattr(config, "fail_on_weak_backing")
    assert hasattr(config, "debug")
    assert hasattr(config, "log_level")


# === Boolean Environment Variable Parsing ===


@pytest.mark.parametrize(
    "env_value,expected",
    [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("yes", True),
        ("Yes", True),
        ("1", True),
        ("on", True),
        ("anything", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("no", False),
        ("No", False),
        ("0", False),
        ("off", False),
        ("Off", False),
    ],
)
def test_env_bool_parsing(env_value, expected):
    """Test boolean environment variable parsing handles various formats."""
    with patch.dict(os.environ, {"TOULMINI_ENABLE_COUNCIL": env_value}):
        reset_config()
        config = get_config()
        assert config.enable_council is expected


def test_env_bool_with_whitespace():
    """Test boolean parsing handles leading/trailing whitespace."""
    with patch.dict(os.environ, {"TOULMINI_STRICT_MODE": "  false  "}):
        reset_config()
        config = get_config()
        assert config.strict_mode is False


# === String Environment Variable Parsing ===


@pytest.mark.parametrize(
    "env_value,expected",
    [
        ("DEBUG", "DEBUG"),
        ("debug", "DEBUG"),
        ("Info", "INFO"),
        ("WARNING", "WARNING"),
        ("ERROR", "ERROR"),
    ],
)
def test_env_str_parsing_log_level(env_value, expected):
    """Test string environment variable parsing (log level normalization)."""
    with patch.dict(os.environ, {"TOULMINI_LOG_LEVEL": env_value}):
        reset_config()
        config = get_config()
        assert config.log_level == expected


def test_invalid_log_level_raises_error():
    """Test that invalid log level raises ConfigurationError."""
    with patch.dict(os.environ, {"TOULMINI_LOG_LEVEL": "INVALID"}):
        reset_config()
        with pytest.raises(ConfigurationError) as exc_info:
            get_config()

        assert "TOULMINI_LOG_LEVEL" in str(exc_info.value)
        assert "INVALID" in str(exc_info.value)


# === Multiple Environment Variables ===


def test_all_env_vars_together():
    """Test setting all environment variables together."""
    with patch.dict(
        os.environ,
        {
            "TOULMINI_ENABLE_COUNCIL": "false",
            "TOULMINI_STRICT_MODE": "0",
            "TOULMINI_FAIL_ON_WEAK_WARRANT": "no",
            "TOULMINI_FAIL_ON_WEAK_BACKING": "off",
            "TOULMINI_DEBUG": "true",
            "TOULMINI_LOG_LEVEL": "DEBUG",
        },
    ):
        reset_config()
        config = get_config()

        assert config.enable_council is False
        assert config.strict_mode is False
        assert config.fail_on_weak_warrant is False
        assert config.fail_on_weak_backing is False
        assert config.debug is True
        assert config.log_level == "DEBUG"


def test_partial_env_vars_with_defaults():
    """Test that unset env vars use defaults."""
    with patch.dict(
        os.environ,
        {
            "TOULMINI_ENABLE_COUNCIL": "false",
            "TOULMINI_DEBUG": "true",
        },
        clear=True,
    ):
        reset_config()
        config = get_config()

        # Explicitly set
        assert config.enable_council is False
        assert config.debug is True

        # Should use defaults
        assert config.strict_mode is True
        assert config.fail_on_weak_warrant is True
        assert config.fail_on_weak_backing is True
        assert config.log_level == "INFO"


# === Runtime Configuration Updates ===


def test_set_config_value_updates_attribute():
    """Test that set_config_value updates config attributes."""
    config = get_config()
    original_strict_mode = config.strict_mode

    set_config_value("strict_mode", False)
    config = get_config()
    assert config.strict_mode is False

    # Restore original
    set_config_value("strict_mode", original_strict_mode)


def test_set_config_value_invalid_key_raises_error():
    """Test that setting an invalid key raises AttributeError."""
    with pytest.raises(AttributeError) as exc_info:
        set_config_value("invalid_key_that_does_not_exist", "value")

    assert "invalid_key_that_does_not_exist" in str(exc_info.value)


def test_set_config_value_multiple_attributes():
    """Test setting multiple config values in sequence."""
    set_config_value("enable_council", False)
    set_config_value("debug", True)
    set_config_value("log_level", "ERROR")

    config = get_config()
    assert config.enable_council is False
    assert config.debug is True
    assert config.log_level == "ERROR"


# === Cache Behavior ===


def test_reset_config_clears_cache():
    """Test that reset_config() clears the cached config."""
    config1 = get_config()
    reset_config()
    config2 = get_config()

    # Should be different objects after reset
    assert config1 is not config2


def test_config_persists_across_calls_without_reset():
    """Test that config values persist across multiple get_config() calls."""
    set_config_value("strict_mode", False)

    config1 = get_config()
    config2 = get_config()

    # Same object, same value
    assert config1 is config2
    assert config1.strict_mode is False
    assert config2.strict_mode is False


def test_env_change_requires_reset():
    """Test that environment variable changes require reset to take effect."""
    # Start with default
    with patch.dict(os.environ, {}, clear=True):
        reset_config()
        config1 = get_config()
        assert config1.strict_mode is True

    # Change env var
    with patch.dict(os.environ, {"TOULMINI_STRICT_MODE": "false"}):
        # Without reset, old value persists (cached)
        config2 = get_config()
        assert config2.strict_mode is True  # Still cached value

        # After reset, new value takes effect
        reset_config()
        config3 = get_config()
        assert config3.strict_mode is False  # New value from env


# === Initial Environment Snapshot ===


def test_initial_env_snapshot_stored():
    """Test that initial environment variables are stored in _initial_env."""
    with patch.dict(
        os.environ,
        {
            "TOULMINI_ENABLE_COUNCIL": "false",
            "TOULMINI_DEBUG": "true",
        },
        clear=True,
    ):
        reset_config()
        config = get_config()

        assert config._initial_env["TOULMINI_ENABLE_COUNCIL"] == "false"
        assert config._initial_env["TOULMINI_DEBUG"] == "true"
        assert config._initial_env["TOULMINI_STRICT_MODE"] is None


def test_initial_env_snapshot_reflects_unset_vars():
    """Test that unset vars are stored as None in snapshot."""
    with patch.dict(os.environ, {}, clear=True):
        reset_config()
        config = get_config()

        for key in config._initial_env:
            assert config._initial_env[key] is None


# === Integration Scenarios ===


def test_debug_mode_scenario():
    """Test realistic debug mode configuration."""
    with patch.dict(
        os.environ,
        {
            "TOULMINI_STRICT_MODE": "false",
            "TOULMINI_DEBUG": "true",
            "TOULMINI_LOG_LEVEL": "DEBUG",
        },
    ):
        reset_config()
        config = get_config()

        assert config.strict_mode is False  # Circuit breakers off
        assert config.debug is True
        assert config.log_level == "DEBUG"


def test_production_mode_scenario():
    """Test realistic production configuration (all defaults)."""
    with patch.dict(os.environ, {}, clear=True):
        reset_config()
        config = get_config()

        assert config.enable_council is True
        assert config.strict_mode is True
        assert config.fail_on_weak_warrant is True
        assert config.fail_on_weak_backing is True
        assert config.debug is False
        assert config.log_level == "INFO"


def test_council_disabled_scenario():
    """Test scenario where Council is disabled but validation is strict."""
    with patch.dict(os.environ, {"TOULMINI_ENABLE_COUNCIL": "false"}):
        reset_config()
        config = get_config()

        assert config.enable_council is False
        assert config.strict_mode is True  # Still strict


# === Edge Cases ===


def test_empty_string_env_var_treated_as_true():
    """Test that empty string environment variable is treated as True."""
    with patch.dict(os.environ, {"TOULMINI_ENABLE_COUNCIL": ""}):
        reset_config()
        config = get_config()
        # Empty string is not in {"0", "false", "no", "off"}, so it's True
        assert config.enable_council is True


def test_config_repr_does_not_include_internal_state():
    """Test that _initial_env is excluded from repr (repr=False in field)."""
    config = get_config()
    repr_str = repr(config)

    # Should NOT include _initial_env (due to repr=False)
    assert "_initial_env" not in repr_str

    # Should include actual config fields
    assert "enable_council" in repr_str
    assert "strict_mode" in repr_str


# === Error Handling ===


def test_configuration_error_is_runtime_error():
    """Test that ConfigurationError is a RuntimeError subclass."""
    with pytest.raises(RuntimeError):
        raise ConfigurationError("Test error")


def test_configuration_error_message():
    """Test ConfigurationError message formatting."""
    error = ConfigurationError("Custom error message")
    assert str(error) == "Custom error message"


# === Module Exports ===


def test_module_exports_all_public_apis():
    """Test that __all__ includes all public APIs."""
    from toulmini import config

    assert hasattr(config, "Config")
    assert hasattr(config, "ConfigurationError")
    assert hasattr(config, "get_config")
    assert hasattr(config, "set_config_value")
    assert hasattr(config, "reset_config")

    # Verify __all__ matches
    expected_exports = {
        "Config",
        "ConfigurationError",
        "get_config",
        "set_config_value",
        "reset_config",
    }
    assert set(config.__all__) == expected_exports

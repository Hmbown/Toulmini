"""Environment-driven configuration for Toulmini.

Provides singleton configuration with type-safe environment variable parsing.
Adapted from Hegelion's config pattern for Toulmini's feature toggle needs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Dict


class ConfigurationError(RuntimeError):
    """Raised when configuration is invalid or misconfigured."""


def _get_env_bool(name: str, default: bool) -> bool:
    """Parse boolean from environment variable.

    Treats '0', 'false', 'no', 'off' (case-insensitive) as False.
    All other non-empty values are treated as True.

    Args:
        name: Environment variable name
        default: Default value if variable not set

    Returns:
        Parsed boolean value
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def _get_env_str(name: str, default: str) -> str:
    """Get string from environment variable.

    Args:
        name: Environment variable name
        default: Default value if variable not set

    Returns:
        Environment variable value or default
    """
    return os.getenv(name, default)


def _get_env_int(name: str, default: int) -> int:
    """Parse integer from environment variable with validation.

    Args:
        name: Environment variable name
        default: Default value if variable not set

    Returns:
        Parsed integer value

    Raises:
        ConfigurationError: If value cannot be parsed as integer
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigurationError(
            f"Environment variable {name} must be an integer. Got: {raw}"
        ) from exc


@dataclass
class Config:
    """Mutable runtime configuration for Toulmini.

    All configuration is driven by environment variables with sensible defaults.
    The config is cached as a singleton using @lru_cache on get_config().

    Environment Variables:
        TOULMINI_ENABLE_COUNCIL: Enable/disable Council of Experts (default: True)
        TOULMINI_STRICT_MODE: Master switch for all circuit breakers (default: True)
        TOULMINI_FAIL_ON_WEAK_WARRANT: Terminate on weak warrant (default: True)
        TOULMINI_FAIL_ON_WEAK_BACKING: Terminate on weak backing (default: True)
        TOULMINI_DEBUG: Enable debug mode (default: False)
        TOULMINI_LOG_LEVEL: Logging level (default: "INFO")
    """

    # Feature toggles
    enable_council: bool
    """Enable or disable the Council of Experts feature."""

    # Circuit breaker controls
    strict_mode: bool
    """Master switch for all circuit breakers. False = skip validation (debug mode)."""

    fail_on_weak_warrant: bool
    """Terminate if warrant strength is 'weak' or 'irrelevant'. Only active when strict_mode=True."""

    fail_on_weak_backing: bool
    """Terminate if backing strength is 'weak' or 'irrelevant'. Only active when strict_mode=True."""

    # Debugging & logging
    debug: bool
    """Enable debug mode with verbose logging."""

    log_level: str
    """Logging level: DEBUG, INFO, WARNING, ERROR."""

    # Internal state (not configurable via env vars)
    _initial_env: Dict[str, Any] = field(default_factory=dict, repr=False)
    """Snapshot of initial environment variables for testing/debugging."""


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Return the global configuration singleton.

    This function is cached, so it returns the same Config instance
    throughout the process lifetime. Config values are read from
    environment variables on first call.

    Returns:
        Cached Config instance

    Examples:
        >>> config = get_config()
        >>> if config.enable_council:
        ...     # Council is enabled
        ...     pass

        >>> # Override for testing
        >>> set_config_value("strict_mode", False)
        >>> config = get_config()
        >>> assert config.strict_mode is False
    """
    config = Config(
        # Feature toggles
        enable_council=_get_env_bool("TOULMINI_ENABLE_COUNCIL", True),

        # Circuit breaker controls
        strict_mode=_get_env_bool("TOULMINI_STRICT_MODE", True),
        fail_on_weak_warrant=_get_env_bool("TOULMINI_FAIL_ON_WEAK_WARRANT", True),
        fail_on_weak_backing=_get_env_bool("TOULMINI_FAIL_ON_WEAK_BACKING", True),

        # Debugging
        debug=_get_env_bool("TOULMINI_DEBUG", False),
        log_level=_get_env_str("TOULMINI_LOG_LEVEL", "INFO").upper(),
    )

    # Store initial environment snapshot for debugging
    config._initial_env = {
        "TOULMINI_ENABLE_COUNCIL": os.getenv("TOULMINI_ENABLE_COUNCIL"),
        "TOULMINI_STRICT_MODE": os.getenv("TOULMINI_STRICT_MODE"),
        "TOULMINI_FAIL_ON_WEAK_WARRANT": os.getenv("TOULMINI_FAIL_ON_WEAK_WARRANT"),
        "TOULMINI_FAIL_ON_WEAK_BACKING": os.getenv("TOULMINI_FAIL_ON_WEAK_BACKING"),
        "TOULMINI_DEBUG": os.getenv("TOULMINI_DEBUG"),
        "TOULMINI_LOG_LEVEL": os.getenv("TOULMINI_LOG_LEVEL"),
    }

    # Validate log level
    valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if config.log_level not in valid_log_levels:
        raise ConfigurationError(
            f"TOULMINI_LOG_LEVEL must be one of {valid_log_levels}. Got: {config.log_level}"
        )

    return config


def set_config_value(key: str, value: Any) -> None:
    """Update a value in the global configuration.

    This is primarily for testing. After updating a value, the config
    cache is cleared to ensure the next call to get_config() returns
    a fresh instance.

    Args:
        key: Config attribute name
        value: New value to set

    Raises:
        AttributeError: If key is not a valid config attribute

    Examples:
        >>> set_config_value("strict_mode", False)
        >>> config = get_config()
        >>> assert config.strict_mode is False

        >>> # Restore to default
        >>> get_config.cache_clear()
        >>> config = get_config()
        >>> assert config.strict_mode is True  # Back to default
    """
    config = get_config()
    if not hasattr(config, key):
        raise AttributeError(
            f"'{type(config).__name__}' object has no attribute '{key}'"
        )

    setattr(config, key, value)
    # Clear cache so next call to get_config() will re-read env vars
    # (unless the value was set programmatically, in which case it persists)
    # Note: This doesn't re-read env vars, it just clears the cache


def reset_config() -> None:
    """Clear the configuration cache.

    Forces get_config() to re-read environment variables on next call.
    Useful for testing different configurations.

    Examples:
        >>> import os
        >>> os.environ["TOULMINI_STRICT_MODE"] = "false"
        >>> reset_config()
        >>> config = get_config()
        >>> assert config.strict_mode is False
    """
    get_config.cache_clear()


__all__ = [
    "Config",
    "ConfigurationError",
    "get_config",
    "set_config_value",
    "reset_config",
]

"""Configuration loader with environment variable substitution."""

import os
import re
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

# Try to import streamlit for secrets support (optional)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def _has_streamlit_secrets() -> bool:
    """Check if Streamlit secrets are available."""
    if not HAS_STREAMLIT:
        return False
    try:
        # Try to access secrets - will fail if not on Streamlit Cloud
        _ = st.secrets
        return True
    except (AttributeError, FileNotFoundError):
        return False


def _get_default_config() -> Dict[str, Any]:
    """Get default configuration for Streamlit Cloud deployment."""
    return {
        'anthropic': {
            'api_key': '${ANTHROPIC_API_KEY}',
            'model': 'claude-sonnet-4-5-20250929',
            'max_tokens': 4000,
            'temperature': 0.3
        },
        'search': {
            'engine': 'duckduckgo',
            'provider': 'auto',  # auto | duckduckgo | google
            'max_results_per_query': 5,
            'google_api_key': '${GOOGLE_API_KEY}',
            'google_cse_id': '${GOOGLE_CSE_ID}'
        },
        'fetching': {
            'max_content_length': 5000,
            'timeout_seconds': 10,
            'retry_attempts': 2
        },
        'agent': {
            'max_subqueries': 5,
            'min_subqueries': 3,
            'facts_per_source': 5
        },
        'output': {
            'report_dir': 'data/reports',
            'save_intermediate': False
        },
        'logging': {
            'level': 'INFO',
            'file': 'logs/research.log',
            'console': True
        }
    }


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file with environment variable substitution.
    Falls back to default config if running on Streamlit Cloud without config.yaml.

    Args:
        config_path: Path to config file. Defaults to project root config.yaml

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist (except on Streamlit Cloud)
        ValueError: If required API key is missing
    """
    # Load .env file if it exists
    load_dotenv()

    # Default to config.yaml in project root
    if config_path is None:
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config.yaml"

    config_file = Path(config_path)

    # If config file doesn't exist, use default config (for Streamlit Cloud)
    if not config_file.exists():
        # Check if we're on Streamlit Cloud (has secrets)
        if HAS_STREAMLIT and _has_streamlit_secrets():
            config = _get_default_config()
        else:
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                f"Copy config.yaml.template to config.yaml and set your API key."
            )
    else:
        # Load YAML
        with open(config_file) as f:
            config = yaml.safe_load(f)

    # Substitute environment variables
    config = _substitute_env_vars(config)

    # Validate required fields
    _validate_config(config)

    return config


def _get_secret(key: str) -> str:
    """
    Get secret from Streamlit secrets or environment variable.

    Args:
        key: Secret key name

    Returns:
        Secret value or None
    """
    # Try Streamlit secrets first (for Streamlit Cloud deployment)
    if HAS_STREAMLIT:
        try:
            return st.secrets.get(key)
        except (KeyError, FileNotFoundError):
            pass

    # Fall back to environment variable
    return os.getenv(key)


def _substitute_env_vars(obj: Any) -> Any:
    """
    Recursively substitute ${VAR_NAME} patterns with environment variables.

    Args:
        obj: Configuration object (dict, list, str, etc.)

    Returns:
        Object with environment variables substituted
    """
    if isinstance(obj, dict):
        return {key: _substitute_env_vars(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_substitute_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        # Match ${VAR_NAME} pattern
        pattern = r'\$\{([^}]+)\}'
        matches = re.findall(pattern, obj)

        for var_name in matches:
            # Try Streamlit secrets first, then environment
            env_value = _get_secret(var_name)
            if env_value is not None:
                obj = obj.replace(f"${{{var_name}}}", env_value)

        return obj
    else:
        return obj


def _validate_config(config: Dict[str, Any]) -> None:
    """
    Validate required configuration fields.

    Args:
        config: Configuration dictionary

    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Check Anthropic API key
    api_key = config.get('anthropic', {}).get('api_key', '')
    if not api_key or api_key.startswith('${'):
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Set it as an environment variable:\n"
            "  export ANTHROPIC_API_KEY='your-key-here'\n"
            "Or set it directly in config.yaml"
        )

    # Validate API key format
    if not api_key.startswith('sk-ant-'):
        raise ValueError(
            f"Invalid Anthropic API key format. Expected format: sk-ant-..."
        )

    # Check required sections exist
    required_sections = ['search', 'agent', 'output', 'logging']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")


def get_api_key() -> str:
    """
    Quick helper to get Anthropic API key from environment or config.

    Returns:
        Anthropic API key
    """
    # Try Streamlit secrets first
    api_key = _get_secret('ANTHROPIC_API_KEY')
    if api_key:
        return api_key

    # Try loading from config
    try:
        config = load_config()
        return config['anthropic']['api_key']
    except (FileNotFoundError, KeyError, ValueError):
        raise ValueError(
            "ANTHROPIC_API_KEY not found in Streamlit secrets, environment, or config.yaml"
        )

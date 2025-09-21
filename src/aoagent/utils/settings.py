"""File containing the single-source-of-truth for the project.

Contains ssot's for:
   - Paths
   - External Source Configurations
"""

from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
CONFIG_DIR = PROJECT_ROOT / "config"
ENV_FILE_PATH = CONFIG_DIR / ".env"

def set_env_vars():
    """Set environment variables.

    Loads environment variables from .env file and validates that at least
    one provider API key is configured.

    Raises:
        FileNotFoundError: If .env file doesn't exist
        ValueError: If no provider keys are found in environment
    """

    provider_keys = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY",
    ]

    # Check if .env file exists
    if not ENV_FILE_PATH.exists():
        raise FileNotFoundError(f"Environment file not found: {ENV_FILE_PATH}")

    # Load environment variables
    success = load_dotenv(dotenv_path=ENV_FILE_PATH, override=False)
    if not success:
        raise RuntimeError(f"Failed to load environment variables from {ENV_FILE_PATH}")

    # Validate that at least one provider key is set
    found_keys = []
    for key in provider_keys:
        value = os.getenv(key)
        if value and value.strip():  # Check for non-empty, non-whitespace values
            found_keys.append(key)

    if not found_keys:
        available_keys = ", ".join(provider_keys)
        raise ValueError(
            f"No provider API keys found in environment. "
            f"At least one of the following must be set: {available_keys}"
        )


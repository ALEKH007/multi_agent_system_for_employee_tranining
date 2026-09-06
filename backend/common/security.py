import os
import secrets
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_secret(name: str) -> str:
    """
    Multi-tiered secret resolution as per secure coding guidelines.
    Resolution order:
    1. Environment variable
    2. Local file query (.secrets directory)
    3. Random generation + Severe warning log (only in development)
    """
    # 1. Check environment variables
    secret_value = os.getenv(name)
    if secret_value:
        return secret_value

    # 2. Check local file (useful for Docker secrets)
    secrets_dir = Path('/run/secrets')
    if not secrets_dir.exists():
        secrets_dir = Path(__file__).resolve().parent.parent.parent / '.secrets'
        
    secret_file = secrets_dir / name
    if secret_file.exists() and secret_file.is_file():
        try:
            with open(secret_file, 'r') as f:
                return f.read().strip()
        except IOError:
            logger.error(f"Failed to read secret file {secret_file}")

    # 3. Handle missing secret
    is_production = not os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    
    if is_production:
        # Never fallback in production
        raise RuntimeError(f"Secret '{name}' is required in production but was not found!")
    
    # Fallback to ephemeral secret for development ONLY
    logger.warning(f"CRITICAL: Generating ephemeral secret for '{name}'. Instance-isolated! Horizontal scaling will fail.")
    return secrets.token_urlsafe(64)

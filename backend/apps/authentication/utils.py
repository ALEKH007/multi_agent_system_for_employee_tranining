import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from common.security import get_secret

ALGORITHM = "HS256"

def generate_jwt_token(payload_data: Dict[str, Any], expires_in_minutes: int = 60 * 24) -> str:
    """
    Generates a JWT token securely.
    - Uses hardcoded HS256 algorithm.
    - Sets explicit 'exp' claim.
    - Uses securely resolved secret key.
    """
    secret_key = get_secret('JWT_SECRET_KEY')
    
    # Copy payload to avoid mutating original
    payload = payload_data.copy()
    
    # Enforce expiration claim
    expire = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    payload.update({"exp": expire})
    
    encoded_jwt = jwt.encode(payload, secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifies a JWT token.
    - Hardcodes algorithms=["HS256"] to reject 'none' or 'RS256' attacks.
    - Requires and validates 'exp' claim automatically via PyJWT.
    """
    secret_key = get_secret('JWT_SECRET_KEY')
    try:
        # PyJWT automatically verifies expiration when 'exp' is present
        payload = jwt.decode(
            token, 
            secret_key, 
            algorithms=[ALGORITHM],
            options={"require": ["exp"]}
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

import re
from django.core.exceptions import ValidationError

def validate_password_strength(password: str) -> None:
    """
    Validates password strength according to security guidelines:
    - Minimum 8 characters
    - No upper limit (handled implicitly or safely up to reasonable limits)
    - All chars allowed
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if len(password) > 128:
        raise ValidationError("Password is too long (max 128 characters).")

def validate_no_xss(text: str) -> str:
    """
    Basic input validation to reject scripts.
    We also rely on output escaping, but catching it here is good defense-in-depth.
    """
    if not text:
        return text
        
    xss_patterns = [
        r'<script.*?>',
        r'javascript:',
        r'onload=',
        r'onerror=',
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValidationError("Invalid characters or script detected in input.")
            
    return text

def validate_department_name(name: str) -> str:
    """
    Allow-list validation for department names.
    Only allows letters, spaces, hyphens, and ampersands.
    """
    if not name:
        raise ValidationError("Department name cannot be empty.")
        
    if not re.match(r'^[a-zA-Z0-9\s\-&]+$', name):
        raise ValidationError("Department name contains invalid characters.")
        
    return name

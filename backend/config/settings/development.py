from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CORS for development
CORS_ALLOW_ALL_ORIGINS = False
env_origins = [o.strip() for o in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()]
CORS_ALLOWED_ORIGINS = list(set([
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
] + env_origins))
CORS_ALLOW_CREDENTIALS = True

# Overriding session cookies for local dev without HTTPS
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# CSRF trusted origins for cross-origin requests from Vite dev server
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# We use ephemeral secrets if not provided, but log a warning (enforced in security.py)

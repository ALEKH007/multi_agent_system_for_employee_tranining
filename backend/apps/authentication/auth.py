from rest_framework import authentication
from rest_framework import exceptions
from .models import User
from .utils import verify_jwt_token
import logging

logger = logging.getLogger(__name__)

class JWTCookieAuthentication(authentication.BaseAuthentication):
    """
    Custom DRF authentication class that reads the JWT from an HttpOnly cookie
    and authenticates the User via MongoEngine.
    """
    def authenticate(self, request):
        # In a real scenario, we might use __Host- prefix for strict security
        token = request.COOKIES.get('auth_token')
        
        if not token:
            return None
            
        payload = verify_jwt_token(token)
        if not payload:
            # Return None instead of raising so that views with
            # permission_classes=[] (login, register) still work when a
            # stale / expired cookie is present.  Protected views are
            # guarded by IsAuthenticated which checks request.user.
            logger.warning('Invalid or expired JWT cookie encountered.')
            return None
            
        user_id = payload.get('user_id')
        if not user_id:
            logger.warning('JWT payload missing user_id.')
            return None
            
        try:
            user = User.objects.get(user_id=user_id)
            if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
                self.enforce_csrf(request)
            return (user, token)
        except User.DoesNotExist:
            logger.warning(f'JWT references non-existent user: {user_id}')
            return None

    @staticmethod
    def enforce_csrf(request):
        """Apply Django's CSRF validation to unsafe cookie-authenticated requests."""
        from rest_framework.authentication import CSRFCheck

        check = CSRFCheck(lambda request: None)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise exceptions.PermissionDenied(f'CSRF Failed: {reason}')

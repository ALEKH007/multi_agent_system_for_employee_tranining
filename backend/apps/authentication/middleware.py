from django.conf import settings

class SecurityHeadersMiddleware:
    """
    Adds advanced security headers that Django's built-in SecurityMiddleware 
    might not cover by default, such as Permissions-Policy and CSP.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Disable unused browser features
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), usb=()'
        
        # Build CSP from settings if available
        if hasattr(settings, 'CSP_DEFAULT_SRC'):
            csp = [
                f"default-src {' '.join(settings.CSP_DEFAULT_SRC)}",
                f"script-src {' '.join(settings.CSP_SCRIPT_SRC)}",
                f"style-src {' '.join(settings.CSP_STYLE_SRC)}",
                f"img-src {' '.join(settings.CSP_IMG_SRC)}",
                f"font-src {' '.join(settings.CSP_FONT_SRC)}",
                f"connect-src {' '.join(settings.CSP_CONNECT_SRC)}",
                f"object-src {' '.join(settings.CSP_OBJECT_SRC)}",
                f"base-uri {' '.join(settings.CSP_BASE_URI)}",
                f"form-action {' '.join(settings.CSP_FORM_ACTION)}",
                f"frame-ancestors {' '.join(settings.CSP_FRAME_ANCESTORS)}",
            ]
            response['Content-Security-Policy'] = '; '.join(csp)
            
        return response

from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.core.exceptions import ValidationError as DjangoValidationError
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF to ensure DB/internal errors 
    are not leaked to the frontend, while logging detailed diagnostics securely.
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # If the exception is a Django ValidationError, convert it
    if isinstance(exc, DjangoValidationError):
        return Response({'detail': exc.messages}, status=400)

    # For unhandled exceptions (500s)
    if response is None:
        # Log the full stack trace securely on the server
        logger.error(
            f"Unhandled exception in {context['view'].__class__.__name__}: {str(exc)}",
            exc_info=True
        )
        # Return generic error to client
        return Response({
            'detail': 'An internal server error occurred. Please try again later.'
        }, status=500)

    return response

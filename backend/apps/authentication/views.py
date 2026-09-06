from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.middleware.csrf import get_token
from .models import User
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .utils import generate_jwt_token
from common.validators import validate_password_strength
import logging

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    """
    Creates an unlinked employee account only. HR, manager, and system-admin
    accounts must be provisioned through an authenticated admin workflow.
    """
    permission_classes = [] # Allow any for now to bootstrap
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            password = serializer.validated_data['password']
            
            # Check if user exists
            if User.objects(email=email).first():
                return Response({'detail': 'Email already registered.'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Validate password strength securely
            try:
                validate_password_strength(password)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
            # Create user
            user = User(email=email, role='employee')
            user.set_password(password)
            user.save()
            
            logger.info(f"New employee account registered: {user.user_id}")
            return Response({'detail': 'Registration successful.'}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [] # Allow any
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            password = serializer.validated_data['password']
            
            user = User.objects(email=email).first()
            if not user or not user.check_password(password):
                # We return generic error to avoid user enumeration
                return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
                
            # Generate JWT
            payload = {
                'user_id': str(user.user_id),
                'role': user.role,
                'employee_id': user.employee_id
            }
            token = generate_jwt_token(payload)
            
            response = Response({
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
            # Set Secure HttpOnly cookie
            response.set_cookie(
                key='auth_token',
                value=token,
                max_age=settings.SESSION_COOKIE_AGE,
                secure=settings.SESSION_COOKIE_SECURE,
                httponly=settings.SESSION_COOKIE_HTTPONLY,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )
            get_token(request)
            logger.info(f"User {user.user_id} logged in.")
            return response
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        response = Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        # Clear the authentication cookie
        response.delete_cookie(
            key='auth_token',
            samesite=settings.SESSION_COOKIE_SAMESITE
        )
        return response

class MeView(APIView):
    # Relies on the default permission classes (IsAuthenticated) set in settings.py
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        email = request.data.get('email')
        password = request.data.get('password')
        
        if email:
            email = email.lower()
            existing = User.objects(email=email).first()
            if existing and str(existing.user_id) != str(user.user_id):
                return Response({'detail': 'Email already registered.'}, status=status.HTTP_400_BAD_REQUEST)
            user.email = email
            
        if password:
            try:
                validate_password_strength(password)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password)
            
        user.save()
        
        # Generate new JWT with updated payload
        payload = {
            'user_id': str(user.user_id),
            'role': user.role,
            'employee_id': user.employee_id
        }
        token = generate_jwt_token(payload)
        
        response = Response({
            'detail': 'Profile updated successfully.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key='auth_token',
            value=token,
            max_age=settings.SESSION_COOKIE_AGE,
            secure=settings.SESSION_COOKIE_SECURE,
            httponly=settings.SESSION_COOKIE_HTTPONLY,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )
        logger.info(f"User {user.user_id} updated profile email")
        return response

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    # path('admin/', admin.site.urls), # Admin panel disabled since we use MongoDB directly without Django ORM
    path('health/', health_check, name='health_check'),
    
    # API Endpoints
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/employees/', include('apps.employees.urls')),
    path('api/v1/assessments/', include('apps.assessments.urls')),
    path('api/v1/recommendations/', include('apps.recommendations.urls')),
    path('api/v1/training/', include('apps.training.urls')),
    # path('api/v1/progress/', include('apps.progress.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
]

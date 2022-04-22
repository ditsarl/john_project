"""test_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings

from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from rapidsms.backends.kannel.views import KannelBackendView
from rapidsms.views import dashboard
import rapidsms
admin.site.site_header = settings.ADMIN_SITE_HEADER

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from john_app import views

router = routers.DefaultRouter()
router.register(r'api-auth/users', views.UserViewSet)
router.register(r'api-auth/groups', views.GroupViewSet)
router.register(r'abonnement', views.AbonnementViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/signup/', views.CreateUserView.as_view(),name='signup'),
    path('api/login/', views.LoginView.as_view(), name='login'),

    path('rapidsms/', rapidsms.views.dashboard),#, name='rapidsms-dashboard')
    path('', include('john_app.urls')),
    path('accounts/', include('rapidsms.urls.login_logout')),
    # RapidSMS contrib app URLs
    path('httptester/', include('rapidsms.contrib.httptester.urls')),
    path('messagelog/', include('rapidsms.contrib.messagelog.urls')),
    path('messaging/', include('rapidsms.contrib.messaging.urls')),
    path('registration/', include('rapidsms.contrib.registration.urls'))
    
]

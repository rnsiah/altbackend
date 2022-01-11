"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf.urls import include
from django.urls import re_path
from django.conf import settings

from django.urls import path
import Alt, StripeAPI
from rest_framework.authtoken.views import obtain_auth_token
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^api/', include('api.urls')),
    re_path(r'^auth/', include('rest_auth.urls')),
    path('secure/', obtain_auth_token),
    re_path(r'^auth/registration/', include('rest_auth.registration.urls')),
    path('', include('Alt.urls')),
    re_path(r'^payments/', include('StripeAPI.urls', namespace='StripeAPI')),
    path('accounts/', include('allauth.urls')),
    path('verification/', include('verify_email.urls')),
 

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

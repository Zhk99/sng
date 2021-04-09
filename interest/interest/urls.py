"""interest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from reg import views as users_views_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', users_views_api.LoginView.as_view(), name='login'),
    path('api/logout/', users_views_api.LogoutView.as_view(), name='logout'),
    path('api/user-create/', users_views_api.UserRegistrationView.as_view(), name='user-create'),
    path('api/user-activate/<uidb64>/<token>/', users_views_api.ActivationUserView.as_view(), name='user_activation'),
    path('api/verify_phone/<int:sms_code>', users_views_api.ActivationUumber.as_view(), name='phone-activation'),
]

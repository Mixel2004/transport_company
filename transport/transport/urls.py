"""
URL configuration for transport project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls.conf import include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views 
from .views import *

router = DefaultRouter()
# router.register(r'admins', admin.site.urls)
router.register(r'customers', CustomerViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'waitingtimes', WaitingTimeViewSet)
router.register(r'trucks', TruckViewSet)
router.register(r'branches', BranchViewSet)
router.register(r'consignments', ConsignmentViewSet)
router.register(r'managers', ManagerViewSet)
router.register(r'branchmanagers', BranchManagerViewSet)
router.register(r'logout', LogoutCustomerViewSet, basename='customer-logout')

# router.register(r'customer/login', LoginCustomerViewSet, basename='customer-login')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginViewSet.as_view({'post': 'create'}), name='login'),  
    path('checklogin/', CheckLoginViewSet.as_view({'get': 'get'}), name='checklogin'),
]   




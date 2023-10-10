"""
URL configuration for src project.

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
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
# from .api import RegisterApi
# from src.Calendar.views import hello
from .views import *

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'events', views.EventViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view()),
    path('event_day_report/', List_Events_By_Day.as_view()),
    path('event_month_report/', List_Events_By_Day_In_Month.as_view()),
    # path('api/event/', EventViewSet.as_view()),
    # path('api/view/', token_view),
    # path('admin/', admin.site.urls),
    # path('cal/', CalendarView.as_view(), name="cal"),
    # path('day/<int:year>/<int:month>/<int:day>/', view_day, name="day"),
    # path('add_event/', event_form, name="add_event"),
]

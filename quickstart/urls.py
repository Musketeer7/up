from django.conf.urls import url
from django.conf.urls import include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('profile', views.UserProfileViewSet)
router.register('login', views.LoginViewSet, base_name='login')


urlpatterns = [
    url(r'', include(router.urls)),
]


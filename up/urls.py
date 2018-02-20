"""
from django.conf.urls import url, include
from rest_framework import router
from quickstart import views
from django.contrib import admin


# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'admin/', admin.site.urls),
]
"""

from django.conf.urls import url, include
from rest_framework import routers
from quickstart import views
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from quickstart.views import Register
from quickstart.views import verify_and_create


router = routers.DefaultRouter()
router.register(r'users', views.UserProfileViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'login', views.LoginViewSet, base_name='login')
router.register(r'transaction', views.TransactionViewSet, base_name='transaction')
# router.register('verification', views.VerificationViewSet, base_name='verification')
router.register(r'register', Register, base_name='register')


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	# url(r'^signup/', include('register.urls')),
	url(r'^register/$',Register),
	url(r'^verify/$', verify_and_create),
]
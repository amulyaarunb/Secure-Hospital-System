from re import template
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin

from app import views
from django_registration.backends.one_step.views import RegistrationView

urlpatterns = [
    path('', views.index, name="index"),
    path('admin/', admin.site.urls),
    path('accounts/register/',
         RegistrationView.as_view(success_url='/'),
         name='django_registration_register'),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from re import template
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin

from app import views
from django_registration.backends.activation.views import RegistrationView


urlpatterns = [
    path('', views.index, name="index"),
    path('admin/', admin.site.urls),
    path('administrator/', views.admin, name="administrator"),
    path('accounts/register/',
         views.CustomRegistrationView.as_view(success_url='/'),
         name='django_registration_register'),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('hospital_staff_appointments/', views.hospital_appointment, name='hospital_staff_appointments'),
    path('hospital_staff_create_payment/', views.hospital_transaction, name='hospital_staff_create_payment'),
    path('hospital_search_patients/', views.hospital_search, name='hospital_search_patients'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin

from app.models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    pass

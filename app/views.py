import re
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth.models import Group

from app.decorators import check_view_permissions


@login_required
def index(request):
    if request.user.groups.filter(name='patient').exists():
        # return patient stuff
        return render(request, "home.html")
    if request.user.groups.filter(name='doctor').exists():
            # return patient stuff
        return render(request, "home.html")
    if request.user.groups.filter(name='hospital_staff').exists():
            # return patient stuff
        return render(request, "home.html")
    if request.user.groups.filter(name='lab_staff').exists():
            # return patient stuff
        return render(request, "home.html")
    if request.user.groups.filter(name='insurance_staff').exists():
        # return patient stuff
        return render(request, "home.html")
    if request.user.groups.filter(name='admin').exists():
        return redirect('/administrator')


class CustomRegistrationView(RegistrationView):
    def register(self, form):
        user =  super().register(form)
        patient_group = Group.objects.get(name='patient')
        patient_group.user_set.add(user)


@login_required
@check_view_permissions("admin")
def admin(request):
    return render(request=request, template_name="admin/index.html", context={'hello': "hello"})
    
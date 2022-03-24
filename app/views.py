import re
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth.models import Group
from django.http import HttpResponse
from . models import Diagnosis,Test
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

''' Lab Staff View Starts Here'''


@login_required
@check_view_permissions("lab_staff")
def admin(request):
    return render(request=request, template_name="admin/index.html", context={'hello': "hello"})
    
    
@login_required
@check_view_permissions("lab_staff")
def viewDiagnosis(request,pk):
    obj = Diagnosis.objects.filter(id=pk)
    return HttpResponse(obj)

@login_required
@check_view_permissions("lab_staff")  
def updateRecord(request,pk,record):
    if request.method =='PUT':
        obj = Test.objects.filter(id=pk)
        obj.status = 'completed'
        obj.results = record
        obj.save()
    return HttpResponse("Succesfully Created/Updated Test")

@login_required
@check_view_permissions("lab_staff")
def denyTestRequest(request,pk):
    obj = Test.objects.filter(id=pk)
    obj.status = 'deny'
    obj.save()
    return HttpResponse("Successfully Denied Request")
    
    
'''Lab Staff View Ends Here'''
    
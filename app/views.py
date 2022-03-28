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
    print(request.user.groups)
    if request.user.groups.filter(name='patient').exists():
        # return patient stuff
        return render(request, "home.html")
    if request.user.groups.filter(name='doctor').exists():
            # return patient stuff
        return render(request, "home.html")
    if request.user.groups.filter(name='hospital_staff').exists():
            # return patient stuff
        return render(request, "hospital_staff_home.html")
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
    

''' Lab Staff View Starts Here'''

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

'''Hospital Staff View ''' 
@login_required
@check_view_permissions("hospital_staff")
def hospital_appointment_view(request):
    return render(request,'hospital_staff_appointments.html')

#To show appointments to hospital staff for approval
@login_required
@check_view_permissions("hospital_staff")
def hospital_appointment(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status='initiated')
    return render(request,'hospital_staff_appointments.html',{'appointments':appointments})

@login_required
@check_view_permissions("hospital_staff")
def hospital_appointment_approve(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status='approved'
    appointment.save()
    return HttpResponse("Approved appointment")

@login_required
@check_view_permissions("hospital_staff")
def hospital_appointment_reject(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status='rejected'
    appointment.save()
    return HttpResponse("Rejected appointment")

def hospital_search(request):
    # whatever user write in search box we get in query
    query = request.GET['query']
    patients=models.Patient.objects.all().filter(Q(patientID__icontains=query)|Q(name__icontains=query))
    return render(request,'hospital_search_patients.html',{'patients':patients})

def hospital_patient_details(request,pID):
    patient_details = model.Patient.objects.get(patientID = pID)
    appointment_details=models.Appointment.objects.get(patientID=pID)
    test_details = models.Test.objects.get(patientID = pID)
    return render(request,'hospital_search_patients.html',{'patient_details':patient_details,'appointment_details':appointment_details,'test_details':test_details})
'''
def hospital_patient_diagnosis(request, appointmentID):
    patient_diagnosis = models.Diagnosis.objects.get(appointmentID=appointmentID)
    pdiag = {
        'diagnosisID': i.diagnosisID,
        'doctorID': i.doctorID,
        'patientID': i.patientID,
        'appointmentID': i.appointmentID,
        'diagnosis': i.diagnosis,
        'test_recommendation': i.test_recommendation,
        'prescription': i.prescription
    }
    return HttpResponse(pdiag)
'''
def update_patient_record(request,patientID):
    patient=models.Patient.objects.get(id=patientID)
    patientForm=forms.PatientForm(request.POST,request.FILES)
    if request.method=='POST':
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if  patientForm.is_valid():
            patient=patientForm.save(commit=False)
            patient.save()
    return HttpResponse("Updated")


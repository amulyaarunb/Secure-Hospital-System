import re
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth.models import Group
from django.http import HttpResponse
from . models import Diagnosis,Test,Insurance,Payment,Appointment,Patient
from app.decorators import check_view_permissions
from . import forms, models

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

'''Insurance Staff View starts here'''
@login_required
@check_view_permissions("insurance_staff")
def denyClaim(request,pk):
    obj = Insurance.objects.filter(id=pk)
    obj.status = 'denied'
    return("Successfully Denied Request")
@login_required
@check_view_permissions("insurance_staff")
def approveClaim(request,pk):
    obj = Insurance.objects.filter(id=pk)
    obj.status = 'approved'
    return("Successfully Approved Request")
@login_required
@check_view_permissions("insurance_staff")
def authorizeFund(request,pk):
    obj = Insurance.objects.filter(id=pk)
    obj1 = Payment.objects.filter(id=obj.paymentID)
    obj1.status = 'completed'
    return("Funds authorized and approved")
@login_required
@check_view_permissions("insurance_staff")
def viewClaim(request):
    obj = Insurance.objects.filter(status='initiated')
    return obj
@login_required
@check_view_permissions("insurance_staff")
def validate(request,pk):
    obj = Payment.objects.filter(id=pk)
    return obj
'''Insurance Staff View ends here'''

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
    appointments=Appointment.objects.all().filter(status='initiated')
    return render(request,'hospital_staff_appointments.html',{'appointments':appointments})

@login_required
@check_view_permissions("hospital_staff")
def hospital_appointment_approve(request,pk):
    appointment=Appointment.objects.get(id=pk)
    appointment.status='approved'
    appointment.save()
    return HttpResponse("Approved appointment")

@login_required
@check_view_permissions("hospital_staff")
def hospital_appointment_reject(request,pk):
    appointment=Appointment.objects.get(id=pk)
    appointment.status='rejected'
    appointment.save()
    return HttpResponse("Rejected appointment")

def hospital_search(request):
    # whatever user write in search box we get in query
    query = request.GET['query']
    patients=Patient.objects.all().filter(Q(patientID__icontains=query)|Q(name__icontains=query))
    return render(request,'hospital_search_patients.html',{'patients':patients})

def hospital_patient_details(request,pID):
    patient_details = Patient.objects.get(patientID = pID)
    appointment_details=Appointment.objects.get(patientID=pID)
    test_details = Test.objects.get(patientID = pID)
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
    patient=Patient.objects.get(id=patientID)
    patientForm=forms.PatientForm(request.POST,request.FILES)
    if request.method=='POST':
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if  patientForm.is_valid():
            patient=patientForm.save(commit=False)
            patient.save()
    return HttpResponse("Updated")


# ---------------------------------------------------------------------------------
# ------------------------ PATIENT RELATED VIEWS START ------------------------------
# ---------------------------------------------------------------------------------



# @app.route("/diagnosis")
@login_required
@check_view_permissions("patient")
def patient_diagnosis_details(request, patientID):
    patient_diagnosis_details = models.Diagnosis.objects.all().filter(patientID=patientID)
    d={}
    for i in patient_diagnosis_details:
        mydict = {
        'diagnosisID': i.diagnosisID,
        'doctorID': i.doctorID,
        'patientID': i.patientID,
        'appointmentID': i.appointmentID,
        'diagnosis': i.diagnosis,
        'test_recommendation': i.test_recommendation,
        'prescription': i.prescription
        }
        d[i]=mydict
    return HttpResponse(d)

@login_required
@check_view_permissions("patient")
def patient_details(request, patientID):
     patient = models.Patient.objects.get(patientID=patientID)
     mydict = {
         'patientID': patientID,
         'name': patient.name,
         'age': patient.age,
         'gender': patient.gender,
         'height': patient.height,
         'weight': patient.weight,
         'insuranceID': patient.insuranceID,
     }
     return HttpResponse(mydict)

@login_required
@check_view_permissions("patient")
def patient_payments_details(request,patientID):
    patient_payments_details = models.Payment.objects.all().filter(patientID=patientID)
    d={}
    for i in patient_payments_details:
        mydict = {
        'paymentID': i.paymentID,
        'method': i.method,
        'type':i.type,
        'mode':i.mode,
        'amount':i.amount,
        'status':i.status,
        'patientID': i.patientID,
        'testID':i.testID,
        'appointmentID': i.appointmentID,
        'created_on':i.created_on
        }
        d[i]=mydict
    return HttpResponse(d)

@login_required
@check_view_permissions("patient")
def request_test(request):
    if request.method=='POST':
        testform=forms.RequestLabTestForm(request.POST)
        if  testform.is_valid():
            test=testform.save(commit=False)
            test.status='requested'
            test.save()
    return HttpResponse("Requested lab test")

@login_required
@check_view_permissions("patient")
def update_patient_record(request,patientID):
    patient=models.Patient.objects.get(patientID=patientID)
    patientForm=forms.PatientForm(request.POST,request.FILES)
    if request.method=='POST':
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if  patientForm.is_valid():
            patient=patientForm.save(commit=False)
            patient.save()
    return HttpResponse("Updated")

@login_required
@check_view_permissions("patient")
def patient_book_appointment_view(request,patientID):
    appointmentForm=forms.PatientAppointmentForm()
    patient=models.Patient.objects.get(patientID=patientID) 
    if request.method=='POST':
        appointmentForm=forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.status='initiated'
            appointment.save()
    return HttpResponse("Appointment request initiated")


@login_required
@check_view_permissions("patient")
def make_payment(request):
    if request.method=='POST':
        payform=forms.MakePaymentForm(request.POST)
        if  payform.is_valid():
            pay=payform.save(commit=False)
            pay.status='initiated'
            pay.save()
    return HttpResponse("Payment")


@login_required
@check_view_permissions("patient")
def view_lab_report(request,diagnosisID):
    lab_test_details=models.Test.objects.get(diagnosisID=diagnosisID)
    mydict={
        'result':lab_test_details.result
    }
    return HttpResponse(mydict)

   

# ------------------------ PATIENT RELATED VIEWS END ------------------------------
# ---------------------------------------------------------------------------------

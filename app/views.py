import re
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django_registration.backends.one_step.views import RegistrationView
from django.contrib.auth.models import Group
from django.http import HttpResponse
from . models import Diagnosis,Test,Insurance,Payment,Appointment,Patient,Doctor
from app.decorators import check_view_permissions
from . import forms, models
from .BotMain import chatgui # Botmain is chatbot directory

@login_required
def index(request):
    print(request.user.groups)
    if request.user.groups.filter(name='patient').exists():
        # return patient stuff
        return redirect('/patient')
    if request.user.groups.filter(name='doctor').exists():
            # return patient stuff
        return redirect('/doctor')
        # return render(request, "home.html")
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
    return render(request=request, template_name="administrator/index.html", context={'hello': "hello"})
    

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
    obj.status = 'denied'
    obj.save()
    return HttpResponse("Successfully Denied Request")
    
@login_required
@check_view_permissions("lab_staff")   
def approveTest(request,pk):
    obj = Test.objects.filter(id=pk)
    obj.status = 'approved'
    obj.save()
    return HttpResponse("Successfully Approved Request")
    
@login_required
@check_view_permissions("lab_staff") 
def deleteTestReport(request,pk):
    obj = Test.objects.filter(id=pk)
    obj.results = ""
    obj.save()
    return HttpResponse("Succesfully Deleted Report")
    
    
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

'''------------------Hospital Staff View------------------- ''' 
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
    appt=[]
    for i in appointments:
        patient = Patient.objects.get(patientID = i.patientID.patientID)
        doctor = Doctor.objects.get(doctorID = i.doctorID.doctorID)
        mydict = {
        'appointmentID': i.appointmentID,
        'date': i.date,
        'time': i.time,
        'type': i.type,
        'patientID': i.patientID,
        'doctorID': i.doctorID,
        'patientName':patient.name,
        'doctorName':doctor.name,
        'status': i.status,
		'diagnosisID': i.diagnosisID,
		'testID': i.testID,
		'paymentID':i.paymentID,
		'created_on': i.created_on
        }
        appt.append(mydict)
    return render(request,'hospital_staff_appointments.html',{'appointments':appt})
    

@login_required
@check_view_permissions("hospital_staff")
def hospital_appointment_approve(request,ID):
    appointment=Appointment.objects.get(appointmentID=ID)
    appointment.status='approved'
    appointment.save()
    patient = Patient.objects.get(patientID = appointment.patientID.patientID)
    if(patient.name == ''):
        return render(request,'hospital_update_patients.html',{'patient':patient})
    return redirect('/hospital_staff_appointments')

@login_required
@check_view_permissions("hospital_staff")
def hospital_appointment_reject(request,ID):
    appointment=Appointment.objects.get(appointmentID=ID)
    appointment.status='rejected'
    appointment.save()
    return redirect('/hospital_staff_appointments')

@login_required
@check_view_permissions("hospital_staff")
def hospital_update_patients(request):
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = forms.PatientUpdateForm(request.POST)
            if form.is_valid():
                obj = Patient() #gets new object
                obj.name = form.cleaned_data['PatientName']
                obj.age = form.cleaned_data['Age']
                obj.gender = form.cleaned_data['Gender']
                obj.height = form.cleaned_data['Height']
                obj.weight = form.cleaned_data['Weight']
                obj.insuranceID = form.cleaned_data['InsuranceID']
                obj.save()
                return HttpResponseRedirect('/thanks/')

        # if a GET (or any other method) we'll create a blank form
        else:
            form = forms.PatientUpdateForm()
        return render(request, 'hospital_update_patients.html', {'form': form})

@login_required
@check_view_permissions("hospital_staff")
def hospital_transaction(request,ID):
    return('/hospital_staff_appointments')

@login_required
@check_view_permissions("hospital_staff")
def hospital_search(request):
    # whatever user write in search box we get in query
    query = '12345'
    print(request)
    patients=Patient.objects.all().filter(Q(patientID__icontains=query)|Q(name__icontains=query))
    return render(request,'hospital_search_patients.html',{'patients':patients})

@login_required
@check_view_permissions("hospital_staff")
def hospital_patient_details(request,pID):
    patient_details = Patient.objects.get(patientID = pID)
    appointment_details=Appointment.objects.get(patientID=pID)
    test_details = Test.objects.get(patientID = pID)
    return render(request,'hospital_search_patients.html',{'patient_details':patient_details,'appointment_details':appointment_details,'test_details':test_details})



'''---------------Hospital end-------------'''

# ---------------------------------------------------------------------------------
# ------------------------ PATIENT RELATED VIEWS START ------------------------------
# ---------------------------------------------------------------------------------


@login_required
@check_view_permissions("patient")
def patient(request):
    return render(request, 'Patient/patient.html', {"user": request.user})

# @app.route("/diagnosis")
@login_required
@check_view_permissions("patient")
def patient_diagnosis_details(request, patientID):
    patient_diagnosis_details = models.Diagnosis.objects.all().filter(patientID=patientID)
    print(patient_diagnosis_details)
    return render(request,'Patient/diagnosis.html',{'patient_diagnosis_details':patient_diagnosis_details})

#patient details views
@login_required
@check_view_permissions("patient")
def patient_details(request, patientID):
     patient = models.Patient.objects.filter(patientID=patientID)
     return render(request,'Patient/patient_details.html',{'patient':patient, "user": request.user})

def update_patient_record(request,patientID):
    patient=Patient.objects.get(patientID=patientID)
    print(patient)
    # patientForm=forms.PatientForm(request.POST,request.FILES)
    patientForm=forms.PatientForm(request.POST)
    print(patientForm)
    if request.method=='POST':
        print("Hi from POST")
        # patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        print(patientForm.errors)
        # patientForm['patientID'] 
        # if  patientForm.is_valid():
        print("patientForm is valid")
        patient=patientForm.save(commit=True)
        patient.save(force_update=True)
        return redirect('patient_details',patient.patientID)
    mydict={'patientForm':patientForm}
    return render(request,'Patient/update_patient_details.html', context=mydict)

# Lab views
@login_required
@check_view_permissions("patient")
def patient_labtest_view(request,patientID):
     return render(request, 'Patient/labtest/labtest.html',{"user": request.user})

@login_required
@check_view_permissions("patient")
def request_test(request):
    if request.method=='POST':
        testform=forms.RequestLabTestForm(request.POST)
        if  testform.is_valid():
            test=testform.save(commit=False)
            test.status='requested'
            test.save()
    mydict={"testform":testform}
    return render(request,'Patient/labtest/request_labtest.html', context=mydict)

@login_required
@check_view_permissions("patient")
def view_lab_report(request,diagnosisID):
    lab_test_details=models.Test.objects.get(diagnosisID=diagnosisID)
    return render(request, 'Patient/labtest/patient_view_lab_report.html',{"user": request.user})

#Chatbot Views
@login_required
@check_view_permissions("patient")
def get_bot_response(request):
    d = request.GET
    userText = d['msg']
    result = chatgui.chatbot_response(userText)
    return HttpResponse(result, content_type="text/plain")


# Appointment Views
@login_required
@check_view_permissions("patient")
def patient_appointment_view(request):
     return render(request, 'Patient/Appointment/appointment.html')

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


# Payment and Transaction views
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
def patient_payments_details(request,patientID):
    patient_payments_details = models.Payment.objects.all().filter(patientID=patientID)
    return render(request,'Patient/', patient_payments_details)
   

# ------------------------ PATIENT RELATED VIEWS END ------------------------------
# ---------------------------------------------------------------------------------


# -------------------------Doctor View---------------------------------------------

@login_required
@check_view_permissions("doctor")
def doctor(request):
    return render(request,'Doctor/doctorhome.html', {"user": request.user})

@login_required
@check_view_permissions("doctor")
def doctor_view_appointment_view(request):
    appointments=models.Appointment.objects.all().filter(doctorID=request.user.id)
    l=[]
    for i in appointments:
        mydict = {
        'appointmentID': i.appointmentID,
        'date': i.date,
        'time': i.time,
        'type': i.type,
        'patientID': i.patientID,
        'doctorID': i.doctorID,
        'status': i.status,
		'diagnosisID': i.diagnosisID,
		'testID': i.testID,
		'paymentID':i.paymentID,
		'created_on': i.created_on
        }
        l[i]=mydict
    return render(request,'Doctor/doctor_view_appointment_view.html', {'appointments':l})

@login_required
@check_view_permissions("doctor")
def doctor_book_appointment(request,ID):
    patient_details=models.Patient.objects.all().get(patientID=patientID)
    return render(request, "Doctor/doctor_book_appointment.html", {"profile": patient_details})
    
    #patient records button views start here
@login_required
@check_view_permissions("doctor")
def doctor_view_patientlist(request):
    # patients=models.Patient.objects.all().filter(doctorId=doctorID)
    return render(request, 'Doctor/doctor_view_patientlist.html')

@login_required
@check_view_permissions("doctor")
def doctor_appointmentID_search_view(request):
    # query stores the input given in search bar
    query = request.GET['query']
    #patients=models.Patient.objects.all().filter(doctorId=request.user.id).filter(Q(patientID__icontains=query)|Q(name__icontains=query))
    appointments=models.Appointment.objects.all().filter(doctorId=request.user.id).filter(Q(patientID__icontains=query)|Q(appointmentID__icontains=query)|Q(date__icontains=query))
    return render(request,'Doctor/doctor_view_appointment_view.html',{'appointments':appointments})

@login_required
@check_view_permissions("doctor")
def doctor_createpatientdiagnosis_view(request,ID):
    diagnosis=models.Diagnosis.objects.all().get(appointmentID=ID)
    if request.method=='POST':
        form=createDiagnosisForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/record modified/')
        else:
            form=createDiagnosisForm()
    return render(request, 'Doctor/doctor_createpatientdiagnosis_view.html', {'form': form})

@login_required
@check_view_permissions("doctor")
def doctor_create_prescription_view(request,ID):
    prescription=models.Diagnosis.objects.all().get(appointmentID=ID)
    #diag=models.Diagnosis.objects.all().get(diagnosisID=diagnosis.diagnosisID)
    if request.method=='POST':
        form=createprescriptionForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/record updated/')
        else:
            form=createprescriptionForm()
    return render(request, 'Doctor/doctor_create_prescription.html', {'form': form})

@login_required
@check_view_permissions("doctor")
def doctor_search_view(request):
    if request.method == "POST":
        searched = request.POST['searched']
        patients = Patient.objects.filter(patientID__contains = searched)

        return render(request, 'Doctor/doctor_search.html', {'searched':searched, 'patients':patients})
    else:
        return render(request, 'Doctor/doctor_search.html', {})
		
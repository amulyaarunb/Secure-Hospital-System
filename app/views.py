import re
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django_registration.backends.one_step.views import RegistrationView
from django_registration.forms import RegistrationForm
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpResponseRedirect
from . models import Diagnosis, Test, Insurance, Payment, Appointment, Patient, Doctor
from app.decorators import check_view_permissions
from . import forms, models
from .BotMain import chatgui  # Botmain is chatbot directory
from django_otp.decorators import otp_required
from django.contrib.auth import logout
from django.views.generic.edit import FormView


@login_required(redirect_field_name="two_factor")
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
        return redirect('/insurance_staff')
    if request.user.groups.filter(name='admin').exists():
        return redirect('/admin')


class Register(RegistrationView):
    form_class = RegistrationForm
    success_url = None
    template_name = "django_registration/registration_form.html"

    def register(self, form):
        new_user = form.save()
        patient_group = Group.objects.get(name='patient')
        patient_group.user_set.add(new_user)


@login_required
@check_view_permissions("admin")
def admin(request):
    return render(request=request, template_name="administrator/index.html", context={'hello': "hello"})
    

''' Lab Staff View Starts Here'''

@login_required
@check_view_permissions("lab_staff")
def viewDiagnosis(request,pk):
    obj = Diagnosis.objects.get(diagnosisID=pk)
    return HttpResponse(obj)

@login_required
@check_view_permissions("lab_staff")  
def updateRecord(request,pk,record):
    if request.method =='PUT':
        obj = Test.objects.get(testID=pk)
        obj.status = 'completed'
        obj.results = record
        obj.save()
    return HttpResponse("Succesfully Created/Updated Test")

@login_required
@check_view_permissions("lab_staff")
def denyTestRequest(request,pk):
    obj = Test.objects.get(testID=pk)
    obj.status = 'denied'
    obj.save()
    return HttpResponse("Successfully Denied Request")
    
@login_required
@check_view_permissions("lab_staff")   
def approveTest(request,pk):
    obj = Test.objects.get(testID=pk)
    obj.status = 'approved'
    obj.save()
    return HttpResponse("Successfully Approved Request")
    
@login_required
@check_view_permissions("lab_staff") 
def deleteTestReport(request,pk):
    obj = Test.objects.get(testID=pk)
    obj.results = ""
    obj.save()
    return HttpResponse("Succesfully Deleted Report")
    
    
'''Lab Staff View Ends Here'''

'''Insurance Staff View starts here'''
@login_required
@check_view_permissions("insurance_staff")
def denyClaim(request,pk):
    obj = Insurance.objects.get(request_id=pk)
    obj.status = 'denied'
    obj.save()
    return redirect('/insurance_staff')
    
@login_required
@check_view_permissions("insurance_staff")
def approveClaim(request,pk):
    obj = Insurance.objects.get(request_id=pk)
    obj.status = 'approved'
    obj.save()
    return redirect('/insurance_staff')
    
@login_required
@check_view_permissions("insurance_staff")
def authorizeFund(request,pk):
    obj = Insurance.objects.get(request_id=pk)
    obj1 = Payment.objects.get(paymentID=obj.paymentID.paymentID)
    obj1.status = 'completed'
    obj1.save()
    return redirect('/insurance_staff_review')

@login_required
@check_view_permissions("insurance_staff")
def claimDisb(request):
    obj = Insurance.objects.all().filter(status='approved')
    arr = []
    for i in obj:
        obj1 = Patient.objects.get(patientID=i.patientID.patientID)
        obj2 = Payment.objects.get(paymentID=i.paymentID.paymentID)
        if(obj2.status!='completed'):
            dict = {
                'patientName':obj1.name,
                'insuranceID':obj1.insuranceID,
                'amount':obj2.amount,
                'requestID' :i.request_id
            }
        if(obj2.status!='completed'): arr.append(dict)

    return render(request,'insurance_staff_review.html',{'disbursal':arr})


@login_required
@check_view_permissions("insurance_staff")
def viewClaim(request):
    obj = Insurance.objects.all().filter(status='initiated')
    arr = []
    for i in obj:
        obj1 = Patient.objects.get(patientID=i.patientID.patientID)
        obj2 = Payment.objects.get(paymentID=i.paymentID.paymentID)
        dict = {
            'patientName':obj1.name,
            'insuranceID':obj1.insuranceID,
            'amount':obj2.amount,
            'requestID' :i.request_id
        }
        arr.append(dict)

    return render(request,'insurance/insurance_staff.html',{'claims':arr})

    
'''Insurance Staff View ends here'''


'''------------------Hospital Staff View------------------- ''' 
'''------------------Hospital Staff View------------------- ''' 
@login_required
@check_view_permissions("hospital_staff")
def hospital_appointment_view(request):
    return render(request,'hospital_staff_appointments.html')

# To show appointments to hospital staff for approval
@login_required
@check_view_permissions("hospital_staff")
def hospital_appointment(request):
    # those whose approval are needed
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
    patient = Patient.objects.get(patientID = appointment.patientID.patientID)
    appointment.status='approved'
    appointment.save()
    if(patient.name == ''):
        request.session['_patient_id'] = patient.patientID
        return HttpResponseRedirect('/hospital_update_patients')
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
        # print(request.session)
        pID = request.session.get('_patient_id')
        print(pID)
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = forms.PatientUpdateForm(request.POST)
            if form.is_valid():
                obj = Patient.objects.get(patientID = pID) 
                # obj = Patient()
                obj.name = form.cleaned_data['PatientName']
                obj.age = form.cleaned_data['Age']
                obj.gender = form.cleaned_data['Gender']
                obj.height = form.cleaned_data['Height']
                obj.weight = form.cleaned_data['Weight']
                obj.insuranceID = form.cleaned_data['InsuranceID']
                obj.save()
                return HttpResponseRedirect('/hospital_staff_appointment/')

        # if a GET (or any other method) we'll create a blank form
        else:
            form = forms.PatientUpdateForm()
        return render(request, 'hospital_update_patients.html', {'form': form})

@login_required
@check_view_permissions("hospital_staff")
def hospital_approved_appointment(request):
    # those whose approval are needed
    appointments=Appointment.objects.all().filter(status='approved')
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
        'status': i.status
        }
        appt.append(mydict)
    return render(request,'hospital_staff_create_payment.html',{'appointments':appt})

@login_required
@check_view_permissions("hospital_staff")
def hospital_complete_appointment(request,ID):
    appointment=Appointment.objects.get(appointmentID=ID)
    appointment.status='completed'
    appointment.save()
    request.session['_appointment_id'] = ID
    return HttpResponseRedirect('/hospital_transaction')

@login_required
@check_view_permissions("hospital_staff")
def hospital_transaction(request):
    apptID = request.session.get('_appointment_id')
    print(apptID)
    if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = forms.CreatePaymentForm(request.POST)
            if form.is_valid():
                apptID = Appointment.objects.get(appointmentID = apptID)
                print(apptID)
                pID = apptID.patientID
                obj = Payment()
                obj.amount = form.cleaned_data['Amount']
                # obj.appointmentID = apptID
                # obj.patientID =pID
                # obj.status= 'initiated'
                obj.save()
                return HttpResponseRedirect('/hospital_staff_create_payment/')

        # if a GET (or any other method) we'll create a blank form
            else:
                form = forms.CreatePaymentForm()
            return render(request, 'hospital_update_amount.html', {'form': form})

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
    return render(request,'hospital_view_patient_details.html',{'patient_details':patient_details,'appointment_details':appointment_details,'test_details':test_details})



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
    # print(patient_diagnosis_details)
    return render(request,'Patient/diagnosis.html',{'patient_diagnosis_details':patient_diagnosis_details})

# patient details views
@login_required
@check_view_permissions("patient")
def patient_details(request, patientID):
     patient = models.Patient.objects.filter(patientID=patientID)
     return render(request,'Patient/patient_details.html',{'patient':patient, "user": request.user})

def update_patient_record(request,patientID):
    patient=Patient.objects.get(patientID=patientID)
    # print(patient)
    # patientForm=forms.PatientForm(request.POST,request.FILES)
    patientForm=forms.PatientForm(request.POST)
    
    if request.method=='POST':
        # print("Hi from POST")
        # print(patientForm.data['age'])
        patient.name=patientForm.data['name']
        patient.age=patientForm.data['age']
        patient.gender=patientForm.data['gender']
        patient.height=patientForm.data['height']
        patient.weight=patientForm.data['weight']
        patient.insuranceID=patientForm.data['insuranceID']
        patient.save()
        
        # patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        # print(patientForm.errors)
        # patientForm['patientID'] 
        if  patientForm.is_valid():
            print("patientForm is valid")
            patient=patientForm.save(commit=True)
            patient.save(force_update=True)

        patient=Patient.objects.get(patientID=patientID)   
        # return redirect("{% url 'patient_details' patient.patientID %}")
        return redirect("patient_details", patient.patientID)

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
def view_lab_report(request,patientID):
    lab_test_details=models.Test.objects.all().filter(patientID=patientID)
    return render(request,'Patient/labtest/patient_view_lab_report.html',{'lab_test_details':lab_test_details})

@login_required
@check_view_permissions("patient")
def view_one_lab_report(request,testID):
    lab_test_details=models.Test.objects.all().filter(testID=testID)
    return render(request,'Patient/labtest/patient_view_lab_report.html',{'lab_test_details':lab_test_details})



# Chatbot Views
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
def patient_previous_appointment_view(request,patientID):
    patient_prev_appointments = models.Appointment.objects.all().filter(patientID=patientID)
    # print(patient_diagnosis_details)
    return render(request, 'Patient/Appointment/view-appointment.html',{'patient_prev_appointments':patient_prev_appointments})

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
    return render(request, 'Patient/Appointment/book-appointment.html')


# Payment and Transaction views
@login_required
@check_view_permissions("patient")
def make_payment(request, patientID):
    patient_payments = models.Payment.objects.all().filter(patientID=patientID)
    if request.method=='POST':
        payform=forms.MakePaymentForm(request.POST)
        if  payform.is_valid():
            pay=payform.save(commit=False)
            pay.status='initiated'
            pay.save()
        return redirect("patient_payments", patient_payments.patientID)

    # mydict={'MakePaymentForm': payform}
    return render(request,'Patient/payments_and_transactions/make_payment.html', {"patient_payments":patient_payments})

@login_required
@check_view_permissions("patient")
def patient_payments_details(request,patientID):
    patient_payments = models.Payment.objects.all().filter(patientID=patientID)
    return render(request,'Patient/payments_and_transactions/patient_payments.html', {"patient_payments":patient_payments})
   

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
    appointments=models.Appointment.objects.all().filter(doctorID=request.user.username)
    l=[]
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
        l.append(mydict)
    return render(request,'Doctor/doctor_view_appointment_view.html', {'appointments':l})

@login_required
@check_view_permissions("doctor")
def doctor_book_appointment(request,patinetID):
    patient_details=models.Patient.objects.all().get(patientID=patientID)
    return render(request, "Doctor/doctor_book_appointment.html", {"profile": patient_details})
    
# patient records button views start here
@login_required
@check_view_permissions("doctor")
def doctor_view_patientlist(request):
    appointments=models.Appointment.objects.all().filter(doctorID=request.user.username)
    # patients=models.Patient.objects.all().filter(patientID=appointments.patientID)
    l=[]
    for p in appointments:
        i=models.Patient.objects.get(patientID=p.patientID.patientID)
        # doctor = Doctor.objects.get(doctorID = i.doctorID.doctorID)
        mydict = {
        'name': i.name,
        'age': i.age,
        'gender': i.gender,
        'patientID': i.patientID,
        'doctorID': p.doctorID,
        'height': i.height,
		'weight': i.weight
        }
        l.append(mydict)
    return render(request, 'Doctor/doctor_view_patientlist.html',{'patients':l})

@login_required
@check_view_permissions("doctor")
def doctor_appointmentID_search_view(request):
    # query stores the input given in search bar
    query = request.GET['query']
    # patients=models.Patient.objects.all().filter(doctorId=request.user.id).filter(Q(patientID__icontains=query)|Q(name__icontains=query))
    appointments=models.Appointment.objects.all().filter(doctorId=request.user.id).filter(Q(patientID__icontains=query)|Q(appointmentID__icontains=query)|Q(date__icontains=query))
    return render(request,'Doctor/doctor_view_appointment_view.html',{'appointments':appointments})

@login_required
@check_view_permissions("doctor")
def doctor_createpatientdiagnosis_view(request):
    diagnosis=models.Diagnosis.objects.all().get(doctorID=request.user.username)
    l=[]
    for i in diagnosis:
        mydict = {
        'appointmentID': i.appointmentID,
        'patientID': i.patientID,
        'doctorID': i.doctorID,
		'diagnosisID': i.diagnosisID,
		'diagnosis': i.diagnosis,
        'test_recommendation': i.test_recommendation,
        'prescription': i.prescription
        }
        l.append(mydict)
    if request.method=='POST':
        form=createDiagnosisForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/record modified/')
        else:
            form=createDiagnosisForm()
    return render(request, 'Doctor/doctor_createpatientdiagnosis_view.html', {'form': form, 'diagnosis': l})

@login_required
@check_view_permissions("doctor")
def doctor_create_prescription_view(request,ID):
    prescription=models.Diagnosis.objects.all().get(appointmentID=ID)
    # diag=models.Diagnosis.objects.all().get(diagnosisID=diagnosis.diagnosisID)
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


@login_required
@check_view_permissions("doctor")
def doctor_view_labreport_view(request):
    appointments=models.Appointment.objects.all().filter(doctorID=request.user.username)
    l=[]
    for i in appointments:
        j=models.Test.objects.get(patientID=i.patientID.patientID)
        mydict = {
        'testID': j.testID,
        'date': j.date,
        'time': j.time,
        'type': j.type,
        'patientID': j.patientID,
        'status': j.status,
        'result': j.result,
        'diagnosisID': j.diagnosisID,
		'paymentID': j.paymentID
        }
        l.append(mydict)
    return render(request,'Doctor/doctor_view_labreport.html',{'labtestreport':l})
		


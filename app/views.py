from typing_extensions import Self
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django_registration.backends.one_step.views import RegistrationView
from django_registration.forms import RegistrationForm
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpResponseRedirect
from . models import Diagnosis, Test, Insurance, Payment, Appointment, Patient, Doctor
from app.decorators import check_view_permissions
from . import forms, models
from .BotMain import chatgui  # Botmain is chatbot directory
from django_otp.decorators import otp_required


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
        return redirect('/hospital_staff_appointments')
        # return render(request, "/hospital_staff_home.html")
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

    return render(request,'insurance_staff.html',{'claims':arr})

    
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
        #print(request.session)
        pID = request.session.get('_patient_id')
        print(pID)
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = forms.PatientUpdateForm(request.POST)
            if form.is_valid():
                obj = Patient.objects.get(patientID = pID) 
                #obj = Patient()
                obj.name = form.cleaned_data['PatientName']
                obj.age = form.cleaned_data['Age']
                obj.gender = form.cleaned_data['Gender']
                obj.height = form.cleaned_data['Height']
                obj.weight = form.cleaned_data['Weight']
                obj.insuranceID = form.cleaned_data['InsuranceID']
                obj.save()
                return HttpResponseRedirect('/hospital_staff_appointments/')

        # if a GET (or any other method) we'll create a blank form
        else:
            form = forms.PatientUpdateForm()
        return render(request, 'hospital_update_patients.html', {'form': form})

@login_required
@check_view_permissions("hospital_staff")
def hospital_approved_appointment(request):
    #those whose approval are needed
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
    print(appointment.appointmentID)
    request.session['_appointment_id'] = appointment.appointmentID
    appointment.status='completed'
    appointment.save()
    
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
                pID = apptID.patientID
                obj = Payment()
                obj.amount = form.cleaned_data['Amount']
                obj.appointmentID = apptID
                obj.patientID =pID
                obj.status= 'initiated'
                obj.save()
                return HttpResponseRedirect('/hospital_staff_create_payment/')

        # if a GET (or any other method) we'll create a blank form
    else:
                form = forms.CreatePaymentForm()
    return render(request, 'hospital_staff_amount.html', {'form': form})

@login_required
@check_view_permissions("hospital_staff")
def hospital_search(request):
    # whatever user write in search box we get in query
    query = request.GET.get('search',False)
    patients=Patient.objects.all().filter(Q(patientID__icontains=query)|Q(name__icontains=query))
    return render(request,'hospital_search_patients.html',{'patients':patients})

@login_required
@check_view_permissions("hospital_staff")
def hospital_view_patients(request):
    patients=Patient.objects.all()
    return render(request,'hospital_search_patients.html',{'patients':patients})

@login_required
@check_view_permissions("hospital_staff")
def hospital_patient_details(request,pID):
    patient_details = Patient.objects.get(patientID = pID)
    appointments=Appointment.objects.all().filter(patientID=pID)
    appt=[]
    for i in appointments:
        doctor = Doctor.objects.get(doctorID = i.doctorID.doctorID)
        if i.diagnosisID is None:
            mydict = {
            'appointmentID': i.appointmentID,
            'date': i.date,
            'time': i.time,
            'type': i.type,
            'doctorName':doctor.name,
            'status': i.status,
            'diagnosis': '',
            'prescription':'',
            'created_on':i.created_on
            }
        else:
            diagnosis = Diagnosis.objects.get(diagnosisID = i.diagnosisID.diagnosisID)
            mydict = {
            'appointmentID': i.appointmentID,
            'date': i.date,
            'time': i.time,
            'type': i.type,
            'doctorName':doctor.name,
            'status': i.status,
            'diagnosis': diagnosis.diagnosis,
            'prescription':diagnosis.prescription,
            'created_on':i.created_on
            }
        appt.append(mydict)
    test_details = Test.objects.all().filter(patientID = pID)
    test =[]
    for i in test_details:
        doctor = Doctor.objects.get(doctorID = i.doctorID.doctorID)
        mydict = {
        'testID':i.testID,
        'date': i.date,
        'time': i.time,
        'type': i.type,
        'status':i.status,
        'result': i.result,
        }
        test.append(mydict)
    return render(request,'hospital_view_patient_details.html',{'patient_details':patient_details,'appointment_details':appt,'test_details':test})

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
def request_test(request,patientID):
    testform=forms.RequestLabTestForm(request.POST)
    print(testform.data)
    patient=models.Patient.objects.get(patientID=patientID) 
    if request.method=='POST':
        Test.date=testform.data['date']
        Test.time=testform.data['time']
        Test.type=testform.data['type']
        Test.diagnosisID=2
        # test.diagnosisID=testform.data['diagnosisID']
        Test.patientID=patientID
        Test.status='requested'
        Test.save()
        # Test.save(self)        
        if  testform.is_valid():
            test=testform.save(commit=False)
            test.status='requested'
            test.save()
        return redirect('patient_labtest',patientID)
    mydict={"testform":testform}
    return render(request,'Patient/labtest/request_labtest.html', {"patient":patient})

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
def patient_appointment_view(request, patientID):
     return render(request, 'Patient/Appointment/appointment.html')

@login_required
@check_view_permissions("patient")
def patient_previous_appointment_view(request,patientID):
    patient_prev_appointments = models.Appointment.objects.all().filter(patientID=patientID)
    # print(patient_diagnosis_details)
    return render(request, 'Patient/Appointment/view-appoitnment.html',{'patient_prev_appointments':patient_prev_appointments})

@login_required
@check_view_permissions("patient")
def patient_book_appointment_view(request,patientID):
    appointmentForm=forms.PatientAppointmentForm() 
    print(appointmentForm.data)
    if request.method=='POST':
        Appointment.date=appointmentForm.data['date']
        Appointment.time=appointmentForm.data['time']
        # Appointment.type=appointmentForm.data['type']
        Appointment.doctorID=appointmentForm.data['doctorID']
        Appointment.patientID=patientID
        Appointment.status='requested'
        Appointment.save()
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.status='initiated'
            appointment.save()
        return redirect('patient-view-appointment',patientID)
    return render(request, 'Patient/Appointment/book-appointment.html',{"user": request.user})


# Payment and Transaction views
@login_required
@check_view_permissions("patient")
def make_payment(request, paymentID):
    patient_payments = models.Payment.objects.get(paymentID=paymentID)
    patientID=patient_payments.patientID
    print(patientID.patientID)
    payform=forms.MakePaymentForm(request.POST)
    if request.method=='POST':
        #print(payform.data)
        patient_payments.method=payform.data['method']
        #print(payform.data['method'])
        if patient_payments.method=='Insurance':
            patient_payments.status='initiated'
        else:
            patient_payments.status='completed'

        patient_payments.save()
        if  payform.is_valid():
            pay=payform.save(commit=False)
            pay.status='initiated'
            pay.save()
        #print(patient_payments.amount)
        return redirect("patient_payments", patientID.patientID)

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
        d = Diagnosis.objects.get(patientID=p.patientID.patientID)
        mydict = {
        'name': i.name,
        'age': i.age,
        'gender': i.gender,
        'patientID': i.patientID,
        'doctorID': p.doctorID,
        'height': i.height,
		'weight': i.weight,
        'diagnosis': d.diagnosis,
        'test_recommendation': d.test_recommendation,
        'prescription': d.prescription
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
def doctor_create_prescription_view(request, ID):
    d=models.Diagnosis.objects.get(patientID=ID)
    CreatePrescription=forms.CreatePrescription(request.POST)
    
    if request.method=='POST':
        d.prescription=CreatePrescription.data['prescription']
        d.save() 
        if  CreatePrescription.is_valid():
            print("CreatePrescription is valid")
            d=CreatePrescription.save(commit=True)
            d.save(force_update=True)

        d=Diagnosis.objects.get(patientID=patientID)   
        return redirect("prescription", d.patientID)

    mydict={'CreatePrescription':CreatePrescription}
    return render(request, 'Doctor/doctor_create_prescription.html', context=mydict)     

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


@login_required
@check_view_permissions("doctor")
def doctor_recommend_labtest_view(request, ID):
    d=models.Diagnosis.objects.get(patientID=ID)
    RecommendLabTest=forms.RecommendLabTest(request.POST)
    
    if request.method=='POST':
        d.test_recommendation=RecommendLabTest.data['test_recommendation']
        d.save() 
        if  RecommendLabTest.is_valid():
            print("RecommendLabTest is valid")
            d=RecommendLabTest.save(commit=True)
            d.save(force_update=True)

        d=Diagnosis.objects.get(patientID=patientID)   
        return redirect("test_recommendation", d.patientID)

    mydict={'RecommendLabTest':RecommendLabTest}
    return render(request, 'Doctor/doctor_recommendlabtest.html', context=mydict)     

@login_required
@check_view_permissions("doctor")
def doctor_patient_diagnosis_view(request):
    return render(request, 'Doctor/doctor_patient_diagnosis.html', {'diagnosis': l}) 

# @login_required
# @check_view_permissions("doctor")
# def patient_diagnosis_details(request, patientID):
#     patient_diagnosis_details = models.Diagnosis.objects.all().filter(patientID=patientID)
#     return render(request,'Doctor/doctor_patient_diagnosis.html',{'patient_diagnosis_details':patient_diagnosis_details})

def doctor_createpatientdiagnosis_view(request, ID):
    d=models.Diagnosis.objects.get(patientID=ID)
    EditDiagnosisForm=forms.EditDiagnosisForm(request.POST)
    
    if request.method=='POST':
        d.diagnosis=EditDiagnosisForm.data['diagnosis']
        d.save() 
        if  EditDiagnosisForm.is_valid():
            print("EditDiagnosisForm is valid")
            d=EditDiagnosisForm.save(commit=True)
            d.save(force_update=True)

        d=Diagnosis.objects.get(patientID=patientID)   
        return redirect("diagnosis", d.patientID)

    mydict={'EditDiagnosisForm':EditDiagnosisForm}
    return render(request, 'Doctor/doctor_createpatientdiagnosis_view.html', context=mydict)     
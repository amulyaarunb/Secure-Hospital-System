from django import forms
#from django.contrib.auth.models import User
from . import models

class PatientForm(forms.ModelForm):
    class Meta:
        model=models.Patient
        fields=['patientID','name','age','gender','height','weight','insuranceID']


class PatientAppointmentForm(forms.ModelForm):
    class Meta:
        model=models.Appointment
        fields=['date','time','type','patientID','doctorID']


class RequestLabTestForm(forms.ModelForm):
    class Meta:
        model=models.Test
        fields=['type','date','time','diagnosisID']

class MakePaymentForm(forms.ModelForm):
    class Meta:
        model=models.Payment
        # fields=['method','type','mode','patientID','testID','appointmentID']
        fields=['method']

class PatientUpdateForm(forms.Form):
    PatientName = forms.CharField(label = 'Patient Name', max_length=100)
    Age = forms.CharField(label = 'Age', max_length=100)
    Gender = forms.CharField(label = 'Gender', max_length = 50)
    Height = forms.CharField(label = 'Height')
    Weight = forms.CharField(label = 'Weight')
    InsuranceID = forms.CharField(label = 'Insurance ID', max_length= 10)

class CreatePaymentForm(forms.Form):
    Amount = forms.CharField(label = 'Amount', max_length = 50)
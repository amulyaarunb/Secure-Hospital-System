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
        fields=['type','patientID','diagnosisID']

class MakePaymentForm(forms.ModelForm):
    class Meta:
        model=models.Payment
        fields=['method','type','mode','patientID','testID','appointmentID']
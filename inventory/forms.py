from django import forms
from .models import Enquiry
class EnquiryForm(forms.ModelForm):
 token=forms.CharField(widget=forms.HiddenInput)
 website=forms.CharField(required=False,widget=forms.HiddenInput)
 consent=forms.BooleanField(label='I agree that the dealership may contact me about this enquiry. I have read the privacy notice.')
 class Meta:
  model=Enquiry
  fields=['name','email','phone','message','consent']
  widgets={'message':forms.Textarea(attrs={'rows':5}),'name':forms.TextInput(attrs={'autocomplete':'name'}),'email':forms.EmailInput(attrs={'autocomplete':'email'}),'phone':forms.TextInput(attrs={'autocomplete':'tel'})}

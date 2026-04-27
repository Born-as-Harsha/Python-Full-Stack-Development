from django import forms
from captcha.fields import CaptchaField

class RegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    captcha = CaptchaField()

from django import forms
from captcha.fields import CaptchaField

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField()
    captcha = CaptchaField()

from django import forms
from captcha.fields import CaptchaField

class RegisterForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField(max_length=10)
    password = forms.CharField(widget=forms.PasswordInput)
    captcha = CaptchaField()
from django import forms
from .models import Customers
from django.contrib.auth.hashers import make_password


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = Customers
        fields = ["name", "email", "phone_number"]

    def clean_password2(self):
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return p2

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.password = make_password(self.cleaned_data["password"])
        if commit:
            obj.save()
        return obj


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

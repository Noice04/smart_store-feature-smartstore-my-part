from django import forms
from .models import Customers, Products, InventoryReceived

from django import forms
from django.contrib.auth.hashers import make_password
from .models import Customers

class CustomerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = Customers
        fields = ["name", "email", "phone_number"]

    def clean_password2(self):
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("password2")
        if p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return p2

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.password = make_password(self.cleaned_data["password"])
        if commit:
            instance.save()
        return instance

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['name', 'category', 'price', 'epc', 'upc', 'producer_company', 'expiry_date']

class InventoryForm(forms.ModelForm):
    class Meta:
        model = InventoryReceived
        fields = ['product_id', 'date_received', 'quantity_received']
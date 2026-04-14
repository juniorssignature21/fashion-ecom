from django import forms
from store import models as store_models

class AddressForm(forms.ModelForm):
    class Meta:
        model = store_models.Address
        fields = ['delivery_address','city', 'state', 'postal_code', 'country', 'phone', 'email', "set_as_default"]
        exclude = ['user', 'created_at', 'updated_at']

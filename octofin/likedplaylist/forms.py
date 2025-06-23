from django import forms
from .models import JellyfinAccount

class JellyfinAccountForm(forms.ModelForm):
    class Meta:
        model = JellyfinAccount
        fields = ['server', 'username', 'password']
        widgets = {'password': forms.PasswordInput(render_value=True)}

class AccountToggleForm(forms.Form):
    account_id = forms.IntegerField(widget=forms.HiddenInput())
    is_active = forms.BooleanField(required=False)

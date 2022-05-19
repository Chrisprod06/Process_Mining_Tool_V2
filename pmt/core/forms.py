from django import forms


class ChangePasswordForm(forms.Form):
    """Form used for changing user password"""
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

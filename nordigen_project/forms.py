from django import forms


class NameForm(forms.Form):
    id_input = forms.CharField(label='Your ID', max_length=100)
    secret_input = forms.CharField(label='Your Secret', max_length=100)
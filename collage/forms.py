from django import forms

class zoektermForm(forms.Form):
    zoekterm = forms.CharField(required=True)
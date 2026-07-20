from django import forms

class StudentUploadForm(forms.Form):
    file = forms.FileField(
        label="Select Excel or CSV File"
    )
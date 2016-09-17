from django import forms

class sheetNameForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': "fish",
            'class': "u-full-width",
        }
    )
)
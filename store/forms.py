from django import forms


class ContactForm(forms.Form):
    INTENT_CHOICES = [
        ("request", "Ask for a service"),
        ("offer", "Offer a service"),
    ]

    intent = forms.ChoiceField(choices=INTENT_CHOICES, widget=forms.RadioSelect)
    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))

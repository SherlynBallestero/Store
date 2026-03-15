from django import forms
from .models import Customer


class ContactForm(forms.Form):
    INTENT_CHOICES = [
        ("request", "Ask for a service"),
        ("offer", "Offer a service"),
    ]

    intent = forms.ChoiceField(choices=INTENT_CHOICES, widget=forms.RadioSelect)
    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))


class CustomerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    user_email = forms.EmailField(label="Email")

    class Meta:
        model = Customer
        fields = ["name", "phone", "address", "preferred_address"]
        labels = {
            "name": "Full Name",
            "phone": "Phone",
            "address": "Address",
            "preferred_address": "Preferred Delivery Address (optional)",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

        if self.user is not None:
            self.fields["first_name"].initial = self.user.first_name
            self.fields["last_name"].initial = self.user.last_name
            self.fields["user_email"].initial = self.user.email

    def clean_user_email(self):
        email = self.cleaned_data["user_email"]
        existing = Customer.objects.filter(email=email).exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError("This email is already in use by another account.")
        return email

    def save(self, commit=True):
        customer = super().save(commit=False)

        if self.user is not None:
            self.user.first_name = self.cleaned_data["first_name"]
            self.user.last_name = self.cleaned_data["last_name"]
            self.user.email = self.cleaned_data["user_email"]
            if commit:
                self.user.save()

            customer.email = self.user.email

        if commit:
            customer.save()

        return customer


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone (optional)"}),
    )
    delivery_address = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Street, city, state, ZIP"}),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Special delivery instructions (optional)"}),
    )

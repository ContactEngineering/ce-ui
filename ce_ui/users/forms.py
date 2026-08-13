from allauth.account.forms import SignupForm
from django import forms


class SignupFormWithName(SignupForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bounded to match `User.name`, so an over-long value is a field error
        # on the form rather than a database error on save
        self.fields['name'] = forms.CharField(max_length=255, label="Full name")

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class RegisterForm(UserCreationForm):
  email = forms.EmailField(
    required=True,
    widget=forms.EmailInput(attrs={"placeholder": "Email address"}),
  )

  class Meta(UserCreationForm.Meta):
    fields = ("username", "email", "password1", "password2")

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields["username"].widget.attrs.update({"placeholder": "Username"})
    self.fields["password1"].widget.attrs.update({"placeholder": "Password"})
    self.fields["password2"].widget.attrs.update({"placeholder": "Confirm password"})

  def save(self, commit=True):
    user = super().save(commit=False)
    user.email = self.cleaned_data["email"]
    if commit:
      user.save()
    return user


class LoginForm(AuthenticationForm):
  username = forms.CharField(
    widget=forms.TextInput(attrs={"placeholder": "Username", "autofocus": True})
  )
  password = forms.CharField(
    widget=forms.PasswordInput(attrs={"placeholder": "Password"})
  )

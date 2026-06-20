from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import LoginForm, RegisterForm


def register(request):
  if request.user.is_authenticated:
    return redirect("chat:rooms")

  if request.method == "POST":
    form = RegisterForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      messages.success(request, "Account created successfully. Welcome!")
      return redirect("chat:rooms")
  else:
    form = RegisterForm()

  return render(request, "accounts/register.html", {"form": form})


class UserLoginView(LoginView):
  template_name = "accounts/login.html"
  authentication_form = LoginForm
  redirect_authenticated_user = True

  def form_valid(self, form):
    messages.success(self.request, f"Welcome back, {form.get_user().username}!")
    return super().form_valid(form)


class UserLogoutView(LogoutView):
  next_page = reverse_lazy("accounts:login")

  def dispatch(self, request, *args, **kwargs):
    if request.user.is_authenticated:
      messages.info(request, "You have been logged out.")
    return super().dispatch(request, *args, **kwargs)

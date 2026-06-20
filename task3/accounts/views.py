from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import StyledUserCreationForm


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def register(request):
    if request.user.is_authenticated:
        return redirect('projects:dashboard')
    if request.method == 'POST':
        form = StyledUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('projects:dashboard')
    else:
        form = StyledUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

from django.shortcuts import redirect, render
from django.views import View
from accounts.forms import CustomUserCreationForm, ProfileCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
def RegisterView(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = ProfileCreationForm(request.POST, request.FILES)
        username = request.POST.get('username')
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('accounts:login')  # Redirect to login page after successful registration
    else:
        user_form = CustomUserCreationForm()
        profile_form = ProfileCreationForm()
    
    return render(request, 'accounts/register.html', {'user_form': user_form, 'profile_form': profile_form})

def LoginView(request):
    if request.user.is_authenticated:
        messages.info(request, "Already logged in!!")
        url = request.META.get('HTTP_REFERER', 'accounts:login')  # Get the referring URL or default to login page
        return redirect(url)
        # return redirect('accounts:')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)  # Redirect to the next page if specified
            return redirect('store:home')  # Redirect to home page after successful login
        else:
            messages.error(request, 'Invalid username or password.')
                
    return render(request, 'accounts/login.html')
    
def LogoutView(request):
    
    logout(request)
    messages.success(request, 'You have been logged out.')
    url = request.META.get('HTTP_REFERER', 'accounts:login')  # Get the referring URL or default to login page
    return redirect(url)  # Redirect to the referring page or login page after 
    

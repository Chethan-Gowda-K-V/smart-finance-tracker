from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import SignUpForm, CustomLoginForm
from expenses.models import Account, Category

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Set is_verified True for simplicity in local dev (can verify via token later)
            user.is_verified = True
            user.save()
            
            # Auto-create a default Cash Wallet and Bank Account
            Account.objects.create(user=user, name='Cash Wallet', balance=0.00, account_type='cash')
            Account.objects.create(user=user, name='Main Bank Account', balance=0.00, account_type='bank')
            
            # Create default expense and income categories
            default_categories = [
                # Expenses
                ('Food & Dining', 'expense', 'bi-cart', '#ef4444'),
                ('Rent & Housing', 'expense', 'bi-house-door', '#f59e0b'),
                ('Transport & Travel', 'expense', 'bi-car-front', '#3b82f6'),
                ('Shopping & Fashion', 'expense', 'bi-bag', '#ec4899'),
                ('Entertainment & Leisure', 'expense', 'bi-controller', '#8b5cf6'),
                ('Utilities & Bills', 'expense', 'bi-lightning', '#06b6d4'),
                
                # Incomes
                ('Salary & Wage', 'income', 'bi-cash-stack', '#10b981'),
                ('Freelance & Side Hustles', 'income', 'bi-laptop', '#14b8a6'),
                ('Investments', 'income', 'bi-graph-up-arrow', '#84cc16'),
            ]
            for name, cat_type, icon, color in default_categories:
                Category.objects.get_or_create(user=user, name=name, type=cat_type, defaults={'icon': icon, 'color': color})
            
            login(request, user)
            messages.success(request, "Registration successful! Welcome to your Smart Finance Tracker.")
            return redirect('dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'authentication/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have logged out successfully.")
    return redirect('login')

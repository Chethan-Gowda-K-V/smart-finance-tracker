import decimal
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta, date, datetime
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Account, Category, Transaction, Budget, SavingsGoal
from .serializers import (
    AccountSerializer, CategorySerializer, TransactionSerializer,
    BudgetSerializer, SavingsGoalSerializer
)
from notifications.models import Notification

# =====================================================================
# TEMPLATE VIEWS (Renders HTML templates with server-side context)
# =====================================================================

@login_required
def dashboard_view(request):
    user = request.user
    
    # Calculate Total Balance across all accounts
    accounts = Account.objects.filter(user=user)
    total_balance = accounts.aggregate(Sum('balance'))['balance__sum'] or 0.00
    
    # Calculate current month's expenses and income
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    
    monthly_expenses = Transaction.objects.filter(
        user=user, type='expense', date__gte=start_of_month, date__lte=today
    ).aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    monthly_income = Transaction.objects.filter(
        user=user, type='income', date__gte=start_of_month, date__lte=today
    ).aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    # Recent Transactions
    recent_transactions = Transaction.objects.filter(user=user).select_related('category', 'account')[:6]
    
    # Categories
    categories = Category.objects.filter(user=user)
    
    # Active Savings Goals
    savings_goals = SavingsGoal.objects.filter(user=user, is_completed=False)[:3]
    
    # Active Budgets
    budgets = Budget.objects.filter(user=user, start_date__lte=today, end_date__gte=today)
    budget_alerts = []
    
    # Check budget alerts dynamically
    for b in budgets:
        if b.category:
            spent = Transaction.objects.filter(
                user=user, type='expense', category=b.category, date__gte=b.start_date, date__lte=b.end_date
            ).aggregate(Sum('amount'))['amount__sum'] or 0.00
        else:
            spent = Transaction.objects.filter(
                user=user, type='expense', date__gte=b.start_date, date__lte=b.end_date
            ).aggregate(Sum('amount'))['amount__sum'] or 0.00
        
        spent = Decimal(spent or 0)
        budget_amount = Decimal(b.amount or 0)

        pct = (spent / budget_amount) * Decimal(100) if budget_amount > 0 else Decimal(0)

        if pct >= 80:
            msg = f"Alert: You have spent {pct:.1f}% of your {'global' if not b.category else b.category.name} budget!"

            budget_alerts.append({
                'category': b.category.name if b.category else 'Global',
                'spent': spent,
                'limit': b.amount,
                'percentage': pct,
                'message': msg
            })
            # Log notification if not exists
            Notification.objects.get_or_create(
                user=user,
                title=f"Budget Alert: {b.category.name if b.category else 'Global'}",
                message=msg,
                type='budget_alert'
            )
    notifications = Notification.objects.filter(user=user, is_read=False)[:5]

    monthly_income = Decimal(monthly_income or 0)
    monthly_expenses = Decimal(monthly_expenses or 0)
    income_goal = Decimal(user.monthly_income_goal or 0)

    if income_goal > 0:
        income_progress = (monthly_income / income_goal) * Decimal(100)
    else:
        income_progress = Decimal(0)

    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'monthly_expenses': monthly_expenses,
        'monthly_income': monthly_income,
        'recent_transactions': recent_transactions,
        'categories': categories,
        'savings_goals': savings_goals,
        'budget_alerts': budget_alerts,
        'notifications': notifications,
        'income_goal': income_goal,
        'income_progress': income_progress
    }

    return render(request, 'expenses/dashboard.html', context)
            
@login_required
def transactions_page_view(request):
    user = request.user
    accounts = Account.objects.filter(user=user)
    categories = Category.objects.filter(user=user)
    
    # Initial filters
    tx_filter = Q(user=user)
    
    # Search
    q = request.GET.get('q', '')
    if q:
        tx_filter &= Q(description__icontains=q) | Q(category__name__icontains=q)
        
    # Date filters
    period = request.GET.get('period', 'all')
    today = date.today()
    if period == 'daily':
        tx_filter &= Q(date=today)
    elif period == 'weekly':
        start_of_week = today - timedelta(days=today.weekday())
        tx_filter &= Q(date__gte=start_of_week)
    elif period == 'monthly':
        start_of_month = date(today.year, today.month, 1)
        tx_filter &= Q(date__gte=start_of_month)
        
    transactions = Transaction.objects.filter(tx_filter).select_related('category', 'account').order_by('-date', '-created_at')
    
    # Handle Form Submission via AJAX/normal post
    if request.method == 'POST':
        action_type = request.POST.get('action')
        if action_type == 'add_transaction':
            acc_id = request.POST.get('account')
            cat_id = request.POST.get('category')
            tx_type = request.POST.get('type')
            amt = float(request.POST.get('amount', 0))
            desc = request.POST.get('description', '')
            dt_str = request.POST.get('date') or today.strftime('%Y-%m-%d')
            dt = datetime.strptime(dt_str, '%Y-%m-%d').date()
            
            acc = get_object_or_404(Account, id=acc_id, user=user)
            cat = get_object_or_404(Category, id=cat_id, user=user)
            
            tx = Transaction.objects.create(
                user=user, account=acc, category=cat, type=tx_type,
                amount=amt, description=desc, date=dt
            )
            # Update account balance
            if tx_type == 'expense':
                acc.balance -= decimal.Decimal(amt)
            else:
                acc.balance += decimal.Decimal(amt)
            acc.save()
            return redirect('transactions_page')
            
    context = {
        'transactions': transactions,
        'accounts': accounts,
        'categories': categories,
        'period': period,
        'q': q
    }
    return render(request, 'expenses/transactions.html', context)

@login_required
def budgets_page_view(request):
    user = request.user
    categories = Category.objects.filter(user=user)
    budgets = Budget.objects.filter(user=user).select_related('category')
    savings_goals = SavingsGoal.objects.filter(user=user)
    
    context = {
        'categories': categories,
        'budgets': budgets,
        'savings_goals': savings_goals
    }
    return render(request, 'expenses/budgets.html', context)

@login_required
def gamification_page_view(request):
    user = request.user
    savings_goals = SavingsGoal.objects.filter(user=user)
    
    # Calculate gamified stats
    completed_goals = savings_goals.filter(is_completed=True).count()
    total_saved = Transaction.objects.filter(user=user, category__name='Savings').aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    # Simple badge calculations
    badges = []
    if completed_goals >= 1:
        badges.append({'name': 'First Saver', 'icon': 'bi-trophy-fill', 'color': '#fbbf24', 'desc': 'Completed your first savings goal!'})
    if completed_goals >= 3:
        badges.append({'name': 'Wealth Builder', 'icon': 'bi-award-fill', 'color': '#ec4899', 'desc': 'Completed 3 savings goals.'})
    if total_saved > 5000:
        badges.append({'name': 'Super Accumulator', 'icon': 'bi-shield-check', 'color': '#3b82f6', 'desc': 'Saved more than $5,000 overall.'})
        
    context = {
        'savings_goals': savings_goals,
        'completed_goals': completed_goals,
        'total_saved': total_saved,
        'badges': badges
    }
    return render(request, 'expenses/gamification.html', context)


# =====================================================================
# REST API VIEWSETS (JSON Interfaces for Interactive Frontend)
# =====================================================================

class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(Q(user=self.request.user) | Q(user__isnull=True))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.filter(user=user)
        
        # Filtering parameters
        period = self.request.query_params.get('period', None)
        account_id = self.request.query_params.get('account', None)
        category_id = self.request.query_params.get('category', None)
        tx_type = self.request.query_params.get('type', None)
        
        today = date.today()
        if period == 'daily':
            queryset = queryset.filter(date=today)
        elif period == 'weekly':
            start_of_week = today - timedelta(days=today.weekday())
            queryset = queryset.filter(date__gte=start_of_week)
        elif period == 'monthly':
            queryset = queryset.filter(date__gte=date(today.year, today.month, 1))
            
        if account_id:
            queryset = queryset.filter(account_id=account_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if tx_type:
            queryset = queryset.filter(type=tx_type)
            
        return queryset

    def perform_create(self, serializer):
        # Update Account Balance on transaction creation
        tx = serializer.save(user=self.request.user)
        acc = tx.account
        if tx.type == 'expense':
            acc.balance -= tx.amount
        else:
            acc.balance += tx.amount
        acc.save()

    def perform_destroy(self, instance):
        # Reverse Account Balance on transaction deletion
        acc = instance.account
        if instance.type == 'expense':
            acc.balance += instance.amount
        else:
            acc.balance -= instance.amount
        acc.save()
        instance.delete()

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SavingsGoalViewSet(viewsets.ModelViewSet):
    serializer_class = SavingsGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_funds(self, request, pk=None):
        goal = self.get_object()
        amount = float(request.data.get('amount', 0))
        if amount <= 0:
            return Response({'error': 'Amount must be greater than zero'}, status=400)
        
        goal.current_amount += decimal.Decimal(amount)
        if goal.current_amount >= goal.target_amount:
            goal.is_completed = True
            # Create a completed badge notifications
            Notification.objects.create(
                user=self.request.user,
                title=f"Goal Achieved: {goal.name}!",
                message=f"Outstanding work! You saved the complete {goal.target_amount} for your goal {goal.name}.",
                type='savings_reminder'
            )
        goal.save()
        return Response(SavingsGoalSerializer(goal).data)

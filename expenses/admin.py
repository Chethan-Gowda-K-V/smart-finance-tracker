from django.contrib import admin
from .models import Account, Category, Transaction, Budget, SavingsGoal

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'account_type', 'balance', 'created_at')
    list_filter = ('account_type', 'user')
    search_fields = ('name', 'user__username')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'type', 'icon', 'color')
    list_filter = ('type', 'user')
    search_fields = ('name', 'user__username')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'account', 'category', 'type', 'amount')
    list_filter = ('type', 'date', 'category', 'user')
    search_fields = ('description', 'user__username')

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date', 'user')

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'target_amount', 'current_amount', 'deadline', 'is_completed')
    list_filter = ('is_completed', 'deadline', 'user')
    search_fields = ('name', 'user__username')

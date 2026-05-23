from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Smart Finance Settings', {'fields': ('avatar', 'currency', 'monthly_income_goal', 'is_verified')}),
    )
    list_display = ('username', 'email', 'currency', 'monthly_income_goal', 'is_verified', 'is_staff')
    list_filter = ('is_verified', 'is_staff', 'is_superuser')

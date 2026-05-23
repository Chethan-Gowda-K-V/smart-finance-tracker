from django.db import models
from django.conf import settings

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('bank', 'Bank Account'),
        ('cash', 'Cash Wallet'),
        ('credit', 'Credit Card'),
        ('savings', 'Savings'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default='bank')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()}) - {self.balance}"

class Category(models.Model):
    CATEGORY_TYPES = (
        ('expense', 'Expense'),
        ('income', 'Income'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default='expense')
    icon = models.CharField(max_length=50, default='bi-tag') # Bootstrap icon name
    color = models.CharField(max_length=20, default='#6366f1') # CSS color code

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ('user', 'name', 'type')

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('expense', 'Expense'),
        ('income', 'Income'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField()
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    voice_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.type.capitalize()} - {self.amount} ({self.category.name})"

class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets', null=True, blank=True) # None = global budget
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        cat_name = self.category.name if self.category else "Global"
        return f"{cat_name} Budget: {self.amount} ({self.start_date} to {self.end_date})"

class SavingsGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.current_amount}/{self.target_amount}"

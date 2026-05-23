from rest_framework import serializers
from .models import Account, Category, Transaction, Budget, SavingsGoal

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ('user',)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('user',)

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    category_color = serializers.ReadOnlyField(source='category.color')
    category_icon = serializers.ReadOnlyField(source='category.icon')
    account_name = serializers.ReadOnlyField(source='account.name')

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('user',)

class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ('user',)

class SavingsGoalSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = SavingsGoal
        fields = '__all__'
        read_only_fields = ('user',)

    def get_progress_percentage(self, obj):
        if obj.target_amount > 0:
            pct = (obj.current_amount / obj.target_amount) * 100
            return min(round(pct, 2), 100.0)
        return 0.0

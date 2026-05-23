from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet, basename='account')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'budgets', views.BudgetViewSet, basename='budget')
router.register(r'savings-goals', views.SavingsGoalViewSet, basename='savings-goal')

urlpatterns = [
    # Template Page Views
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('transactions/', views.transactions_page_view, name='transactions_page'),
    path('budgets/', views.budgets_page_view, name='budgets_page'),
    path('gamification/', views.gamification_page_view, name='gamification_page'),
    
    # REST API views
    path('api/', include(router.urls)),
]

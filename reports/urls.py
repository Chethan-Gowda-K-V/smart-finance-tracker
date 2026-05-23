from django.urls import path
from . import views

urlpatterns = [
    path('reports/pdf/', views.export_pdf_view, name='export_pdf'),
    path('reports/excel/', views.export_excel_view, name='export_excel'),
]

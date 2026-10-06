from django.urls import path
from members import views

app_name = 'members'

urlpatterns = [
    path('', views.proforma_form_view, name='form'),
    path('success/', views.success_view, name='success'),
    path('member/<str:token>/', views.member_token_view, name='member_detail'),
    path('member/<str:token>/pdf/', views.pdf_download_view, name='pdf_download'),
    
    # Admin / Staff Dashboard & Actions
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/regenerate-pdf/<str:member_id>/', views.regenerate_pdf_view, name='regenerate_pdf'),
    path('dashboard/export-csv/', views.export_csv_view, name='export_csv'),
    path('dashboard/export-zip/', views.export_bulk_pdfs_zip_view, name='export_zip'),
]

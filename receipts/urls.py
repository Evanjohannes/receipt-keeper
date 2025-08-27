from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import custom_logout
urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('login/', LoginView.as_view(template_name='receipts/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('logout-page/', views.logout_page, name='logout_page'),
    path('upload/', views.upload_receipt, name='upload'),
    path('reports/', views.reports, name='reports'),
    path('export/', views.export_data, name='export_data'),
    path('export/', views.export_reports, name='export_reports'),
    path('delete/<int:id>/', views.delete_receipt, name='delete_receipt'),
    path('receipt/<int:receipt_id>/', views.receipt_detail, name='receipt_detail'),
]
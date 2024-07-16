from django.urls import path
from . import views

urlpatterns = [
    path('', views.AccountListView.as_view()),
    path('<str:accountId>', views.AccountDetailView.as_view()),
    path('transfer/', views.TransferFundsView.as_view()),
    path('import/', views.ImportAccountsView.as_view()),
]
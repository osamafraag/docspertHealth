from django.urls import path, include
from . import views

urlpatterns = [
    path('/', views.AccountListView.as_view()),
    # path('/<str:account_id>/', views.AccountDetailView.as_view()),
    # path('transfer/', views.TransferFundsView.as_view()),
]
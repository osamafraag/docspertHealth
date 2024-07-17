from rest_framework import serializers
from .models import Account, TransactionHistory

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'  
        
class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = '__all__'  
        
class TransferFundsSerializer(serializers.Serializer):
    fromAccountId = serializers.CharField(max_length=100)
    toAccountId = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
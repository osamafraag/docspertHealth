from rest_framework import serializers
from .models import Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'  
        
class TransferFundsSerializer(serializers.Serializer):
    from_account_id = serializers.CharField(max_length=100)
    to_account_id = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
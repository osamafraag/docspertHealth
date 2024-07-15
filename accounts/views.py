from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Account
from .serializers import AccountSerializer, TransferFundsSerializer

class AccountListView(APIView):
    def get(self, request):
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountDetailView(APIView):
    def get_object(self, account_id):
        try:
            return Account.objects.get(account_id=account_id)
        except Account.DoesNotExist:
            return None

    def get(self, request, account_id):
        account = self.get_object(account_id)
        if account is not None:
            serializer = AccountSerializer(account)
            return Response(serializer.data)
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, account_id):
        account = self.get_object(account_id)
        if account is not None:
            serializer = AccountSerializer(account, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, account_id):
        account = self.get_object(account_id)
        if account is not None:
            account.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

class TransferFundsView(APIView):
    def post(self, request):
        serializer = TransferFundsSerializer(data=request.data)
        if serializer.is_valid():
            from_account_id = serializer.validated_data['from_account_id']
            to_account_id = serializer.validated_data['to_account_id']
            amount = serializer.validated_data['amount']

            from_account = Account.objects.get(account_id=from_account_id)
            to_account = Account.objects.get(account_id=to_account_id)

            if from_account.balance >= amount:
                from_account.balance -= amount
                to_account.balance += amount
                from_account.save()
                to_account.save()
                return Response({"message": "Transfer successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

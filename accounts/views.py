from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Account
import csv
import io
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
    def get(self, request, accountId):
        account =Account.getObject(accountId)
        if account is not None:
            serializer = AccountSerializer(account)
            return Response(serializer.data)
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, accountId):
        account = Account.getObject(accountId)
        if account is not None:
            serializer = AccountSerializer(account, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, accountId):
        account = Account.getObject(accountId)
        if account is not None:
            account.delete()
            return Response({"message": "Account successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

class TransferFundsView(APIView):
    def post(self, request):
        serializer = TransferFundsSerializer(data=request.data)
        if serializer.is_valid():
            fromAccountId = serializer.validated_data['fromAccountId']
            toAccountId = serializer.validated_data['toAccountId']
            amount = serializer.validated_data['amount']

            fromAccount = Account.getObject(fromAccountId)
            toAccount = Account.getObject(toAccountId)
            if fromAccount and toAccount:
                if fromAccount.getBalance() >= amount:
                    fromAccount.updateBalance(amount)  
                    toAccount.updateBalance(amount, isDebit=False) 
                    return Response({"message": "Transfer successful"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
class ImportAccountsView(APIView):
    def post(self, request):
        csvFile = request.FILES['file']
        decodedFile = csvFile.read().decode('utf-8')
        ioString = io.StringIO(decodedFile)
        reader = csv.reader(ioString)
        next(reader)
        for row in reader:
            ID, Name, Balance = row
            Account.objects.create(accountId=ID, name=Name, balance=Balance)
        return Response({'message': 'Accounts imported successfully'})
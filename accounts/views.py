from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Account, TransactionHistory
from django.core.paginator import Paginator
import csv
import io
from django.db.models import Q
from .serializers import AccountSerializer, TransferFundsSerializer, TransactionHistorySerializer


class AccountListView(APIView):
    def get(self, request):
        searchQuery = request.GET.get('search')
        if searchQuery:
            accounts = Account.objects.filter(
                Q(accountId__icontains=searchQuery) | 
                Q(name__icontains=searchQuery)
            )
        else:
            accounts = Account.objects.all()
        paginator = Paginator(accounts, 10)
        page = request.GET.get('page', 1)
        pageData = paginator.get_page(page)
        serializer =  AccountSerializer(pageData, many=True) 
        return Response({
            'data': serializer.data,
            'meta': {
                'page': pageData.number,
                'perPage': 10,
                'totalPages': paginator.num_pages,
                'totalItems': paginator.count
            }
        })

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
            data = serializer.data
            fromHistory = TransactionHistory.objects.filter(fromAccount=account)
            toHistory = TransactionHistory.objects.filter(toAccount=account)
            
            fromSerializer = TransactionHistorySerializer(fromHistory, many=True)
            toSerializer = TransactionHistorySerializer(toHistory, many=True)
            
            data['fromHistory'] = fromSerializer.data
            data['toHistory'] = toSerializer.data
            return Response(data)
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
                    transactionHistory = TransactionHistory(
                        fromAccount=fromAccount,
                        toAccount=toAccount,
                        amount=amount
                    )
                    transactionHistory.save()
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
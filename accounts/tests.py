# tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from.models import Account
from .serializers import AccountSerializer, TransferFundsSerializer

class AccountSerializerTestCase(TestCase):
    def testSerializeAccount(self):
        account = Account.objects.create(accountId=1, name='Account 1', balance=1000)
        serializer = AccountSerializer(account)
        self.assertEqual(serializer.data, {'accountId': '1', 'name': 'Account 1', 'balance': '1000'})

class AccountListViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        Account.objects.create(accountId=1, name='Account 1', balance=1000)
        Account.objects.create(accountId=2, name='Account 2', balance=500)

    def testListAccounts(self):
        response = self.client.get('/accounts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

class AccountDetailViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.account = Account.objects.create(accountId=1, name='Account 1', balance=1000)

    def testGetAccount(self):
        response = self.client.get('/accounts/1/')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['accountId'], '1')
        self.assertEqual(data['name'], 'Account 1')
        self.assertEqual(data['balance'], '1000')
        self.assertIn('fromHistory', data)
        self.assertIn('toHistory', data)

    def testDetAccountNotFound(self):
        response = self.client.get('/accounts/3/')
        self.assertEqual(response.status_code, 404)

class TransferViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.account1 = Account.objects.create(accountId=1, name='Account 1', balance=1000)
        self.account2 = Account.objects.create(accountId=2, name='Account 2', balance=500)

    def testTransferFunds(self):
        data = {'fromAccountId': 1, 'toAccountId': 2, 'amount': 200}
        response = self.client.post('/accounts/transfer/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Account.objects.get(pk=1).balance, '800.00')
        self.assertEqual(Account.objects.get(pk=2).balance, '700.00')

    def testTransferInsufficientBalance(self):
        data = {'fromAccountId': 1, 'toAccountId': 2, 'amount': 1500}
        response = self.client.post('/accounts/transfer/', data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'error': 'Insufficient funds'})

class ImportAccountsViewTestCase(TestCase):
    def testImportAccounts(self):
        with open('testAccounts.csv', 'rb') as f:
            response = self.client.post('/accounts/import/', {'file': f})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'message': 'Accounts imported successfully'})
        self.assertEqual(Account.objects.count(), 4)
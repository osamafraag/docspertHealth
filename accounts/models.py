from django.db import models
from decimal import Decimal

class Account(models.Model):
    accountId = models.CharField(max_length=100, primary_key=True) 
    name = models.CharField(max_length=255)
    balance = models.CharField(max_length=20)
    

    @classmethod
    def getObject(cls, accountId):
        try:
            return cls.objects.get(accountId=accountId)
        except cls.DoesNotExist:
            return None
     
    def getBalance(self):
        return Decimal(self.balance)   
        
    def updateBalance(self, amount, isDebit=True):
        currentBalance =self.getBalance()
        if isDebit:
            currentBalance -= amount
        else:
            currentBalance += amount
        self.balance = str(currentBalance)  
        self.save()
        
        
    def __str__(self):
        return f"{self.name} ({self.accountId})"

class TransactionHistory(models.Model):
    fromAccount = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='from_account')
    toAccount = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='to_account')
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction from {self.fromAccount} to {self.toAccount} for {self.amount} on {self.date}"
from django.db import models

class Account(models.Model):
    accountId = models.CharField(max_length=100, primary_key=True) 
    name = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} ({self.accountId})"

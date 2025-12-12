from django.db import models

class Payment(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20)  # khalti, stripe, manual
    transaction_id = models.CharField(max_length=200, blank=True)
    is_verified = models.BooleanField(default=False)
    paid_at = models.DateTimeField(auto_now_add=True)

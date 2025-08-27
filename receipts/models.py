from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Receipt(models.Model):
    CATEGORY_CHOICES = [  
        ('food', 'Food & Dining'),
        ('transport', 'Transportation'),
        ('shopping', 'Shopping'),
        ('housing', 'Housing'),
        ('entertainment', 'Entertainment'),
        ('utilities', 'Utilities'),
        ('health', 'Health'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='receipts/')
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES,  
        default='other'
    )
    vendor = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor} - {self.amount} ({self.date})"
    
    def get_category_display(self):
        """Returns the human-readable category label"""
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)
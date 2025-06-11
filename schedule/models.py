from django.db import models
from django.utils import timezone
from destination.models import Destination

class DestinationRate(models.Model):
    destination = models.OneToOneField(Destination, on_delete=models.CASCADE, related_name='rates')
    adult_rate = models.DecimalField(max_digits=10, decimal_places=2)
    child_rate = models.DecimalField(max_digits=10, decimal_places=2)
    kid_rate = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rates for {self.destination.name}"

class Tour(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='tours')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    current_participants = models.PositiveIntegerField(default=0)
    adults = models.PositiveIntegerField(default=0)
    children = models.PositiveIntegerField(default=0)
    kids = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_price(self):
        try:
            rates = self.destination.rates
            total_price = (
                self.adults * rates.adult_rate +
                self.children * rates.child_rate +
                self.kids * rates.kid_rate
            )
            return total_price
        except DestinationRate.DoesNotExist:
            return 0

    def save(self, *args, **kwargs):
        self.price = self.calculate_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start_date']

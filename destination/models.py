from django.db import models
from django.utils.text import slugify
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('institutions', 'Institutions'),
        ('national_park', 'National Park'),
        ('camping', 'Camping'),
        ('rock_climbing', 'Rock Climbing'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    custom_name = models.CharField(max_length=100, blank=True, null=True, help_text="Enter custom category name if 'Other' is selected")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.custom_name if self.name == 'other' and self.custom_name else self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.custom_name if self.name == 'other' and self.custom_name else self.get_name_display()

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

class Destination(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='destinations')
    city = models.CharField(max_length=100, default='Lahore')
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_coordinates(self):
        """Fetch coordinates using OpenStreetMap's Nominatim service"""
        geolocator = Nominatim(user_agent="nomadic_travel")
        try:
            # Add a small delay to respect Nominatim's usage policy
            time.sleep(1)
            location = geolocator.geocode(self.address)
            if location:
                return location.latitude, location.longitude
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Geocoding error: {e}")
        return None, None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Only fetch coordinates if they're not already set
        if not self.latitude or not self.longitude:
            lat, lon = self.get_coordinates()
            if lat and lon:
                self.latitude = lat
                self.longitude = lon
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class DestinationImage(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='destinations/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.destination.name}"

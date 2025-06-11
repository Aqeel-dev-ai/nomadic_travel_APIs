from django.contrib import admin
from .models import Tour, DestinationRate

@admin.register(DestinationRate)
class DestinationRateAdmin(admin.ModelAdmin):
    list_display = ('destination', 'adult_rate', 'child_rate', 'kid_rate', 'updated_at')
    search_fields = ('destination__name',)
    list_filter = ('destination',)

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'start_date', 'end_date', 'price', 'current_participants')
    list_filter = ('destination', 'start_date')
    search_fields = ('title', 'description', 'destination')

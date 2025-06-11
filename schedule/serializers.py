from rest_framework import serializers
from .models import Tour, DestinationRate
from destination.serializers import DestinationSerializer
from destination.models import Destination
from django.utils import timezone

class DestinationRateSerializer(serializers.ModelSerializer):
    destination_name = serializers.CharField(source='destination.name', read_only=True)

    class Meta:
        model = DestinationRate
        fields = ['id', 'destination', 'destination_name', 'adult_rate', 'child_rate', 'kid_rate', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class TourSerializer(serializers.ModelSerializer):
    destination_details = DestinationSerializer(source='destination', read_only=True)
    destination_name = serializers.CharField(write_only=True, required=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Tour
        fields = [
            'id', 'title', 'description', 'destination_name', 'destination', 'destination_details',
            'start_date', 'end_date', 'price', 'current_participants',
            'adults', 'children', 'kids',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['current_participants', 'destination', 'price']

    def validate(self, data):
        # Validate dates
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            if start_date < timezone.now():
                raise serializers.ValidationError({
                    "start_date": "Start date cannot be in the past"
                })
            
            if end_date <= start_date:
                raise serializers.ValidationError({
                    "end_date": "End date must be after start date"
                })

        return data

    def validate_destination_name(self, value):
        try:
            # Try to find destination by name
            destination = Destination.objects.get(name__iexact=value)
            # Check if rates exist for this destination
            if not hasattr(destination, 'rates'):
                raise serializers.ValidationError(f"Rates not set for destination '{value}'. Please contact administrator.")
            return value
        except Destination.DoesNotExist:
            raise serializers.ValidationError(f"Destination '{value}' not found")

    def create(self, validated_data):
        # Get the destination name and remove it from validated_data
        destination_name = validated_data.pop('destination_name')
        
        # Find the destination by name
        try:
            destination = Destination.objects.get(name__iexact=destination_name)
        except Destination.DoesNotExist:
            raise serializers.ValidationError(f"Destination '{destination_name}' not found")
        
        # Create the tour with the found destination
        tour = Tour.objects.create(destination=destination, **validated_data)
        return tour

    def update(self, instance, validated_data):
        # Handle destination name if provided
        if 'destination_name' in validated_data:
            destination_name = validated_data.pop('destination_name')
            try:
                destination = Destination.objects.get(name__iexact=destination_name)
                instance.destination = destination
            except Destination.DoesNotExist:
                raise serializers.ValidationError(f"Destination '{destination_name}' not found")

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty")
        return value
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

class DestinationField(serializers.Field):
    def to_representation(self, value):
        return value.id

    def to_internal_value(self, data):
        if isinstance(data, int):
            try:
                return Destination.objects.get(id=data)
            except Destination.DoesNotExist:
                raise serializers.ValidationError(f"Destination with ID {data} not found")
        elif isinstance(data, str):
            try:
                return Destination.objects.get(name__iexact=data)
            except Destination.DoesNotExist:
                raise serializers.ValidationError(f"Destination '{data}' not found")
        else:
            raise serializers.ValidationError("Destination must be either an ID (integer) or name (string)")

class TourSerializer(serializers.ModelSerializer):
    destination_details = DestinationSerializer(source='destination', read_only=True)
    destination = DestinationField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_participants = serializers.SerializerMethodField()
    children = serializers.IntegerField(default=0, required=False)
    kids = serializers.IntegerField(default=0, required=False)

    class Meta:
        model = Tour
        fields = [
            'id', 'title', 'description', 'destination', 'destination_details',
            'start_date', 'end_date', 'price', 'total_participants',
            'adults', 'children', 'kids',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['price', 'total_participants']

    def get_total_participants(self, obj):
        return obj.adults + obj.children + obj.kids

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

        # Validate destination has rates
        destination = data.get('destination')
        if destination and not hasattr(destination, 'rates'):
            raise serializers.ValidationError({
                "destination": f"Rates not set for destination '{destination.name}'. Please contact administrator."
            })

        # Ensure children and kids are not negative
        if data.get('children', 0) < 0:
            raise serializers.ValidationError({
                "children": "Children count cannot be negative"
            })
        if data.get('kids', 0) < 0:
            raise serializers.ValidationError({
                "kids": "Kids count cannot be negative"
            })

        return data

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
        return super().create(validated_data)
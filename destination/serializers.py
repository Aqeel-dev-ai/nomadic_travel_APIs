from rest_framework import serializers
from .models import Category, Destination, DestinationImage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at']

class DestinationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DestinationImage
        fields = ['id', 'image', 'caption', 'is_primary', 'created_at']

class DestinationSerializer(serializers.ModelSerializer):
    images = DestinationImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Destination
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'category_name',
            'city', 'address', 'latitude', 'longitude', 'images', 'created_at', 'updated_at'
        ] 
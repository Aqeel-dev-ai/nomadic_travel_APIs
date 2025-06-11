from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Category, Destination, DestinationImage
from .serializers import CategorySerializer, DestinationSerializer, DestinationImageSerializer

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        """
        Allow public access for viewing destinations
        Require authentication for creating, updating, and deleting
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Destination.objects.all()
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by city
        city = self.request.query_params.get('city', None)
        if city is not None:
            queryset = queryset.filter(city__iexact=city)
        
        # Filter by search term
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(
                name__icontains=search
            ) | queryset.filter(
                description__icontains=search
            ) | queryset.filter(
                address__icontains=search
            ) | queryset.filter(
                city__icontains=search
            )
        
        # Order by created_at by default
        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def upload_images(self, request, slug=None):
        destination = self.get_object()
        images = request.FILES.getlist('images')
        captions = request.data.getlist('captions', [])
        is_primary = request.data.getlist('is_primary', [])

        for i, image in enumerate(images):
            caption = captions[i] if i < len(captions) else ''
            primary = is_primary[i] if i < len(is_primary) else False
            
            # If this image is marked as primary, unset any existing primary images
            if primary:
                DestinationImage.objects.filter(destination=destination, is_primary=True).update(is_primary=False)
            
            DestinationImage.objects.create(
                destination=destination,
                image=image,
                caption=caption,
                is_primary=primary
            )

        return Response({'status': 'images uploaded'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete_image(self, request, slug=None):
        destination = self.get_object()
        image_id = request.data.get('image_id')
        
        if not image_id:
            return Response({'error': 'image_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        image = get_object_or_404(DestinationImage, id=image_id, destination=destination)
        image.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

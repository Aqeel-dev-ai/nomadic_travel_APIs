from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
import logging
from .models import Tour
from .serializers import TourSerializer

logger = logging.getLogger(__name__)

# Create your views here.

class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        # Log the request data
        logger.info(f"Tour creation request data: {request.data}")
        
        # Validate required fields
        required_fields = ['title', 'description', 'destination_name', 'start_date', 'end_date', 'price', 'max_participants']
        missing_fields = [field for field in required_fields if field not in request.data]
        
        if missing_fields:
            return Response(
                {"detail": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate dates
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if start_date and end_date:
            try:
                start = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                if start < timezone.now():
                    return Response(
                        {"detail": "Start date cannot be in the past"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if end <= start:
                    return Response(
                        {"detail": "End date must be after start date"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"detail": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Validate price
        price = request.data.get('price')
        if price is not None:
            try:
                price = float(price)
                if price < 0:
                    return Response(
                        {"detail": "Price cannot be negative"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"detail": "Invalid price format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Validate participants
        max_participants = request.data.get('max_participants')
        if max_participants is not None:
            try:
                max_participants = int(max_participants)
                if max_participants <= 0:
                    return Response(
                        {"detail": "Maximum participants must be greater than 0"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"detail": "Invalid maximum participants format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

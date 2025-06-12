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
    serializer_class = TourSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-start_date']  # Ensure latest tours appear first

    def get_queryset(self):
        return Tour.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Log the request data
        logger.info(f"Tour creation request data: {request.data}")
        
        # Set default values for children and kids if not provided
        if 'children' not in request.data:
            request.data['children'] = 0
        if 'kids' not in request.data:
            request.data['kids'] = 0
        
        # Validate required fields
        required_fields = ['title', 'description', 'destination', 'start_date', 'end_date', 'adults']
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
                # Parse the dates and ensure they are timezone-aware
                start = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                # If no time is provided, set it to current time
                if start.hour == 0 and start.minute == 0 and start.second == 0:
                    current_time = timezone.now()
                    start = start.replace(
                        hour=current_time.hour,
                        minute=current_time.minute,
                        second=current_time.second
                    )
                
                if end.hour == 0 and end.minute == 0 and end.second == 0:
                    current_time = timezone.now()
                    end = end.replace(
                        hour=current_time.hour,
                        minute=current_time.minute,
                        second=current_time.second
                    )
                
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
                
                # Update the request data with timezone-aware dates
                request.data['start_date'] = start.isoformat()
                request.data['end_date'] = end.isoformat()
                
            except ValueError:
                return Response(
                    {"detail": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Validate participant numbers
        try:
            request.data['adults'] = int(request.data['adults'])
            request.data['children'] = int(request.data['children'])
            request.data['kids'] = int(request.data['kids'])
            
            if request.data['adults'] < 0:
                return Response(
                    {"detail": "Adults count cannot be negative"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if request.data['children'] < 0:
                return Response(
                    {"detail": "Children count cannot be negative"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if request.data['kids'] < 0:
                return Response(
                    {"detail": "Kids count cannot be negative"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid participant count format. All counts must be numbers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

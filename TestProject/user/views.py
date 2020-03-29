from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Profile
from .serializers import UserSerializer


class Signup(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'you signed up successfully'})
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
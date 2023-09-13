from django.shortcuts import render
from rest_framework import viewsets , status
from rest_framework.decorators import action
from rest_framework.response import Response
from decouple import config

from .models import *
from .serializers import *
from Useable.generatetoken import *
# Create your views here.

class AdminViewset(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

    @action(detail=False, methods=['POST'])
    def CreateAdmin(self, request):
        try:
            requireFeilds = ["first_name", "last_name", "email", "phone", "password"]
            ser = AdminSerializer(data= request.data, context = {"reqData": request.data, "requireFeilds": requireFeilds})
            if ser.is_valid():
                ser.save()
                return Response ({"status": True, "message" : "User created !!!" }, status=status.HTTP_201_CREATED)
            return Response({"status": False, "message": ser.errors }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response ({"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['POST'])
    def LoginAdmin(self, request):
        try:
            ser = AdminLoginSerializer(data=request.data)
            if ser.is_valid():
                fetchuser = ser.validated_data['fetch_user']
                admin_token = adminGenerateToken(fetchuser)
                if admin_token['status']:
                    fetchuser.no_of_wrong_attempts = 0
                    fetchuser.account_status = True
                    fetchuser.save()
                    return Response({"msg": "Login Successfully", "token": admin_token['token'], "payload": admin_token['payload']})
                return Response ({"status": False, "message": f"Invalid Credentials {admin_token['message']}" })
            
            return Response({"status": False, "msg" : ser.errors})
        except Exception as e:
            return Response ({"status": False, "error": str(e)})
    
    
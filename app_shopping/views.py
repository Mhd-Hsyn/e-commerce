from django.shortcuts import render
from rest_framework import viewsets , status
from rest_framework.decorators import action
from rest_framework.response import Response
from decouple import config
from operator import itemgetter
from passlib.hash import django_bcrypt_sha256 as handler
from django.core.mail import send_mail
from smtplib import SMTPException

import random

from .models import *
from .serializers import *
from Useable.token import *
from Useable.permissions import *
# Create your views here.

class AdminAuthViewset(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    
    # define serializer for diff apis
    def get_serializer_class(self):
        if self.action == 'adminSignup':
            return AdminSerializer
        elif self.action == 'adminLogin':
            return AdminLoginSerializer
        elif self.action == "adminForgotPassSendMail":
            return AdminForgotPassSerializer
    
    # Admin SignUp 
    @action(detail=False, methods=['POST'])
    def adminSignup(self, request):
        try:
            requireFeilds = ["first_name", "last_name", "email", "phone", "password"]
            ser = AdminSerializer(data= request.data, context = {"reqData": request.data, "requireFeilds": requireFeilds})
            if ser.is_valid():
                ser.save()
                return Response ({"status": True, "message" : "User created !!!" }, status=status.HTTP_201_CREATED)
            return Response({"status": False, "message": ser.errors }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response ({"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # Admin Login
    @action(detail=False, methods=['POST'])
    def adminLogin(self, request):
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
    
    @action(detail=False, methods=['POST'])
    def adminForgotPassSendMail(self, request):
        try:
            requireFeild = ["email"]
            requirefeild_status = uc.requireFeildValidation(request.data , requireFeild)
            if requirefeild_status['status']:
                fetchuser = Admin.objects.filter(email = request.data['email']).first()
                if fetchuser:
                    otpCode = random.randint(1000, 9999)
                    fetchuser.Otp = otpCode
                    fetchuser.OtpStatus = True
                    fetchuser.OtpCount = 0
                    fetchuser.save()
                    subject = "OTP for Reset Password E-commerce App"
                    message = f"Your OTP code for Password Reset is  {otpCode}"
                    email_from = config('EMAIL_HOST_USER')
                    email_to = request.data['email']
                    send_mail(subject= subject, message= message,from_email= email_from, recipient_list= [email_to], fail_silently= True)
                    return Response ({"status": True, "message": f"OTP send Successfully check your email {email_to}", "id": str(fetchuser.id)}, status= 200)
                return Response ({"status": False, "error": "No User found in this email"}, status= status.HTTP_404_NOT_FOUND)    
            return Response({"status": False, "error" : "email required"})    
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status= 400)
        
        
    # @action (detail=False, methods=['POST'])
    # def checkOtpToken(self,request):
    #     try:
    #         requireFeild = ["otp", "id"]
    #         feild_status = uc.requireFeildValidation(request.data, requireFeild)
    #         if not feild_status['status']:
    #             return Response({"status": False, "error": feild_status["message"]})  
    #         otp = request.data['otp']
    #         uid = request.data['id']
    #         fetchuser = Admin.objects.filter(id = uid).first()
    #         if not fetchuser :
    #             return Response({"status": False, "error": "User not exist"}, status= 404)
    #         if not fetchuser.OtpStatus:
    #             return Response({"status": False, "error": "No OTP , Otp Status False"}, status= 404)
    #         if fetchuser.OtpStatus and fetchuser.Otp == int(otp):
    #             fetchuser.Otp = 0
    #             fetchuser.OtpCount = 0
    #             fetchuser.OtpStatus = False
    #             fetchuser.save()
    #             return Response({"status": True, "message": "Otp verified . . . "}, status= 200)
    #         fetchuser.OtpCount += 1
    #         if fetchuser.OtpCount >= 3:
    #             fetchuser.Otp = 0
    #             fetchuser.OtpCount = 0
    #             fetchuser.OtpStatus = False
    #             fetchuser.save()
    #             return Response({"status": False, "message": f"Your OTP is expired . . . Kindly get OTP again "})
    #         fetchuser.save()
    #         return Response({"status": False, "message": f"Your OTP is wrong . You have only {3- fetchuser.OtpCount} attempts left "})
                    
    #     except Exception as e:
    #         return Response({"status": False, "message": str(e)}, status= 400)        
        
    @action (detail=False, methods=['POST'])
    def checkOtpToken(self,request):
        try:
            requireFeild = ["otp", "id"]
            feild_status = uc.requireFeildValidation(request.data, requireFeild)
            if feild_status["status"]:
                otp = request.data['otp']
                uid = request.data['id']
                fetchuser = Admin.objects.filter(id = uid).first()
                if fetchuser :
                    if fetchuser.OtpStatus and fetchuser.OtpCount < 3 :
                        if fetchuser.Otp == int(otp):
                            fetchuser.Otp = 0
                            fetchuser.save()
                            return Response({"status": True, "message": "Otp verified . . . ", "id": str(fetchuser.id)}, status= 200)
                        else:
                            fetchuser.OtpCount += 1
                            fetchuser.save()
                            if fetchuser.OtpCount >= 3:
                                fetchuser.Otp = 0
                                fetchuser.OtpCount = 0
                                fetchuser.OtpStatus = False
                                fetchuser.save()
                                return Response({"status": False, "message": f"Your OTP is expired . . . Kindly get OTP again "})
                            return Response({"status": False, "message": f"Your OTP is wrong . You have only {3- fetchuser.OtpCount} attempts left "})
                    return Response({"status": False, "error": "No OTP , Otp Status False"}, status= 404)
                return Response({"status": False, "error": "User not exist"}, status= 404)
            return Response({"status": False, "error": feild_status["message"]})
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status= 400)
        
        
    @action(detail=False, methods=['POST'])
    def resetPassword(self ,request):
        try:
            requireFeild = ["id", "newpassword"]
            requiredFeild_status = uc.requireFeildValidation(request.data, requireFeild)
            if requiredFeild_status["status"]:
                uid = request.data["id"]
                newpassword = request.data["newpassword"]
                if not uc.checkpasslen(password=newpassword):
                    return Response({"status": False, "error": "Password length must be greater than 8"})
                fetchuser = Admin.objects.filter(id =uid).first()
                if fetchuser:
                    if fetchuser.OtpStatus and fetchuser.Otp == 0:
                        fetchuser.password = handler.hash(newpassword)
                        fetchuser.OtpStatus = False
                        fetchuser.OtpCount = 0
                        fetchuser.save()
                        logout_all = AdminWhitelistToken.objects.filter(admin = fetchuser)
                        logout_all.delete()
                        return Response({"status": True, "message": "Password Reset Successfully Go to Login", "id": str(fetchuser.id)}, status= 200)
                    return Response({"status": False, "error": "Token not verified !!!!" })
                return Response({"status": False, "error": "User Not Exist !!!" })
            return Response({"status": False, "error": requiredFeild_status["message"] })
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status= 400)
        
            
        
# New Class use permission_classes    Admin Profile / change password / Logout 
class AdminViewset(viewsets.ModelViewSet):
    permission_classes = [AdminPermission]
    # queryset = Admin.objects.all()
    
    @action(detail=False, methods= ["GET"])
    def adminLogout(self, request):
        try:
            token = request.auth
            fetchuser = Admin.objects.filter(id = token["id"]).first()
            adminDeleteToken(fetchuser, request)
            return Response ({"status": False, "message": "Logout Successfully"}, status= 200)
        except Exception as e:
            return Response({"status": False, "error": f"Something wrong {str(e)}"}, status= 400)
    
    
    @action(detail=False, methods=['GET', "PUT"])
    def adminProfile(self, request):
        try:
            email = request.auth['email']
            fetchuser = Admin.objects.filter(email = email).first()
            
            if request.method == "GET":
                payload = {
                    "id" : str(fetchuser.id),
                    "first_name": fetchuser.first_name,
                    "last_name": fetchuser.last_name,
                    "email": fetchuser.email,
                    "phone": fetchuser.phone,
                    "image": fetchuser.image.url,   
                }
                return Response({"status": True , "data": payload })
            
            if request.method == "PUT":
                requirefeilds = ["first_name","last_name", "phone"]
                requireFeilds_status = uc.requireFeildValidation( request.data, requirefeilds)
                if requireFeilds_status['status']:
                    fetchuser.first_name, fetchuser.last_name, fetchuser.phone = itemgetter("first_name", "last_name", "phone")(request.data)
                    if request.FILES.get("image"):
                        fetchuser.image = request.FILES['image']
                    fetchuser.save()
                    payload = {
                    "id" : str(fetchuser.id),
                    "first_name": fetchuser.first_name,
                    "last_name": fetchuser.last_name,
                    "email": fetchuser.email,
                    "phone": fetchuser.phone,
                    "image": fetchuser.image.url,   
                    }
                    return Response({"status": True ,"message": "Updated Successfully" ,"data": payload })   
                return Response({"status": False, "error": requireFeilds_status['message']})    
        except Exception as e :
            return Response({"status": False , "error": str(e)}, status= 400)
    
    
    @action(detail= False, methods= ['POST'])
    def adminChangePass(self, request):
        try:
            requireFeilds = ["oldpassword", "newpassword"]
            feild_status = uc.requireFeildValidation(request.data, requireFeilds)
            if feild_status['status']:
                token = request.auth
                fetchuser = Admin.objects.filter(id = token['id']).first()
                if handler.verify(request.data['oldpassword'],fetchuser.password):
                    if uc.checkpasslen(request.data['newpassword']):
                        fetchuser.password = handler.hash(request.data["newpassword"])
                        # delete old token
                        adminDeleteToken(fetchuser, request)
                        # generate new token
                        token = adminGenerateToken(fetchuser) 
                        fetchuser.save()
                        return Response({"status": True, "message": "Password Successfully Changed", "token" : token["token"]})
                    return Response({"status":False, "error":"New Password Length must be graterthan 8"}, status= 400)
                return Response({"status":False, "error":"Old Password not verified"}, status= 400)
            return Response({"status":False, "error": feild_status['message']}, status= 400)
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status= 400)  
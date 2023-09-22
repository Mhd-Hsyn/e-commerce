from django.shortcuts import render
from rest_framework import viewsets , status
from rest_framework.decorators import action
from rest_framework.response import Response
from decouple import config
from operator import itemgetter
from passlib.hash import django_pbkdf2_sha256 as handler
from django.core.mail import send_mail

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
            requireFeilds_status = uc.requireFeildValidation(request.data, requireFeilds)
            if requireFeilds_status['status']:
                ser = AdminSerializer(data= request.data)
                if ser.is_valid():
                    ser.save()
                    return Response ({"status": True, "message" : "User created !!!" }, status=status.HTTP_201_CREATED)
                return Response({"status": False, "message": ser.errors }, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": False, "message": requireFeilds_status['message'] }, status=status.HTTP_400_BAD_REQUEST)
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
                    return Response({"status": True, "msg": "Login Successfully", "token": admin_token['token'], "payload": admin_token['payload']}, status= 200)
                return Response ({"status": False, "message": f"Invalid Credentials {admin_token['message']}"}, status= 400)
            
            return Response({"status": False, "msg" : ser.errors}, status= 400)
        except Exception as e:
            return Response ({"status": False, "error": str(e)}, status= 400)
    
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
                    return Response ({"status": True, "message": f"OTP send Successfully check your email {email_to}", "id": str(fetchuser.id)}, status= status.HTTP_200_OK)
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
                            return Response({"status": True, "message": "Otp verified . . . ", "id": str(fetchuser.id)}, status= status.HTTP_200_OK)
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
            token = request.auth  # access from permission class after decode
            fetchuser = Admin.objects.filter(id = token["id"]).first()
            adminLogout_DeleteToken(fetchuser, request)
            return Response ({"status": True, "message": "Logout Successfully"}, status= 200)
        except Exception as e:
            return Response({"status": False, "error": f"Something wrong {str(e)}"}, status= 400)
    
    
    @action(detail=False, methods=['GET', "PUT"])
    def adminProfile(self, request):
        try:
            decoded_token = request.auth  # get decoded token from permission class
            email = decoded_token['email']
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
                    return Response({"status": True ,"message": "Updated Successfully" ,"data": payload }, status= status.HTTP_200_OK)   
                return Response({"status": False, "error": requireFeilds_status['message']}, status= status.HTTP_400_BAD_REQUEST)    
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
                        adminLogout_DeleteToken(fetchuser, request)
                        # generate new token
                        token = adminGenerateToken(fetchuser) 
                        fetchuser.save()
                        return Response({"status": True, "message": "Password Successfully Changed", "token" : token["token"]}, status = 200)
                    return Response({"status":False, "error":"New Password Length must be graterthan 8"}, status= 400)
                return Response({"status":False, "error":"Old Password not verified"}, status= 400)
            return Response({"status":False, "error": feild_status['message']}, status= 400)
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status= 400)
        
        
    @action(detail= False, methods=['POST','GET','PUT','DELETE'])
    def ProductCategoryApi(self, request):
        try:
            # Get Product category
            if request.method == "GET":
                category = ProductCategory.objects.all()
                ser = ProductCategorySerializer(category, many = True)
                return Response({"status": True, "data": ser.data}, status= 200)
            # Add Product Category
            elif request.method == "POST":
                requiredFeilds = ["name", "description"]
                validator = uc.requireFeildValidation(request.data, requiredFeilds)
                if validator['status']:
                    ser = ProductCategorySerializer(data= request.data)
                    if ser.is_valid():
                        ser.save()
                        return Response({"status": True, "message": f"Successfully Added {request.data['name']} Category "}, status= 200)
                    return Response({"status": False, "error" : str(ser.errors)}, status= 400)
                return Response({"status": False, "error": validator['message']}, status= 400)
            #  edit Product Category
            elif request.method == "PUT":
                requiredFeilds = ['id','name','description']
                validator = uc.requireFeildValidation(reqData= request.data, requireFeilds= requiredFeilds)
                if validator['status']:
                    fetch_category = ProductCategory.objects.get(id = request.data['id'])
                    if fetch_category:
                        fetch_category.name = request.data['name']
                        fetch_category.description = request.data["description"]
                        fetch_category.save()
                        ser = ProductCategorySerializer(fetch_category)
                        return Response({"status": True, "message": f"{fetch_category.name} Category Updated Successfully", "data" : ser.data}, status= 200)
                    return Response({"status": False, "message": "Category not exists"})
                return Response({"status": False, "message": f"{validator['message']}"}, status= 400)
            # delete product category
            elif request.method == 'DELETE':
                requiredFeilds = ["id"]
                validator = uc.requireFeildValidation(request.data, requiredFeilds)
                if validator["status"]:
                    fetch_category = ProductCategory.objects.get(id = request.data["id"])
                    if fetch_category:
                        fetch_category.delete()
                        return Response ({"status": True, "message": f"{request.data['id']} Category Deleted !!!"}, status=status.HTTP_200_OK)
                    return Response({"status": False, "message": "Category not exists"})
                return Response({"status": False, "message": f"{validator['message']}"}, status= 400)
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status=400)
        
        #  Produuct Sub Category
    @action(detail=True, methods=["GET", "POST", "PUT", "DELETE"])
    def ProductSubCategoryApi(self, request, pk = None):
        try:
            # Get Product Sub category needs pk id of main Product category to get all sub-category  
            if request.method == "GET":
                category = ProductCategory.objects.filter(id = pk).first()
                if category is not None:
                    sub_category = Product_SubCategory.objects.filter(category = category)
                    ser = AddProductSubCategorySerializer(sub_category, many = True)
                    return Response ({"status": True, "category": category.name ,"data": ser.data}, status= 200)
                return Response({"status": False, "error": "Main Category not exist"}, status= 404)
                
            # Post / Add Product Sub Category  needs pk id of main Product category to add in sub-category
            elif request.method == "POST":
                requiredFeilds = ["name", "description"]
                validator = uc.requireFeildValidation(request.data, requiredFeilds)
                if validator["status"]:
                    ser = AddProductSubCategorySerializer(data = request.data, context = {"category_id": pk})
                    if ser.is_valid():
                        sub_category = ser.save()
                        return Response({"status": True, "message": f"{sub_category.name} Successfully added to {sub_category.category.name} Category", "category": sub_category.category.name, "sub_category": sub_category.name}, status=200)
                    return Response({"status": False, "error": str(ser.errors)}, status= 400)
                return Response({"status": False, "error": validator["message"]}, status=400)
            # Put / Edit product Sub Category
            # needs pk id of sub category to update the sub category
            elif request.method == "PUT":
                requiredFeilds = ["category_id","name", "description"]
                validator = uc.requireFeildValidation(request.data, requiredFeilds)
                if validator["status"]:
                    fetch_category = ProductCategory.objects.filter(id = request.data["category_id"]).first()
                    fetch_sub_category = Product_SubCategory.objects.filter(id = pk).first()
                    if fetch_category:
                        if fetch_sub_category:
                            fetch_sub_category.category = fetch_category
                            fetch_sub_category.name = request.data["name"]
                            fetch_sub_category.description = request.data["description"]
                            fetch_sub_category.save()
                            return Response ({"status": True, "message": f"{fetch_sub_category.name} Successfully changed in {fetch_sub_category.category.name} Category"}, status= 200)
                        return Response({"status": False, "error": f"Sub Category id not exist"}, status= 404)
                    return Response({"status": False, "error": f"Main Category id not exist"}, status= 404)
                return Response ({"status": False, "error": f"{validator['message']}"}, status= 400)
            # Delete Product Sub Category
            # needs pk id of sub category to delete
            elif request.method == "DELETE":
                fetch_sub_category = Product_SubCategory.objects.filter(id = pk).first()
                if fetch_sub_category:
                    fetch_sub_category.delete()
                    return Response ({"status": True, "message": f"{fetch_sub_category.name} Deleted Successfully from {fetch_sub_category.category.name} Category !!!"}, status= 200)
                return Response({"status": False, "error": f"Sub Category id not exist"}, status= 404)
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status= 400)
    
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from app_shopping.models import *
from passlib.hash import django_pbkdf2_sha256 as handler


class AdminAuthViewSet_TestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_adminSignup(self):
        url = reverse("adminauth-adminSignup")
        data = {
            "first_name": "Muhammad",
            "last_name": "Hussain",
            "email": "innocentsmsa92@hotmail.com",
            "phone": "12345678",
            "password": "hussain123",
        }
        response = self.client.post(url, data, format="json")
        # print(response.content)
        res_data = response.json()
        # print(res_data)
        self.assertEqual(res_data['status'], True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Admin.objects.count(), 1)
        self.assertEqual(Admin.objects.get().first_name, "Muhammad")
    
    def test_adminlogin(self):
        url = reverse("adminauth-adminLogin")
        _password = handler.hash("hussain123")
        admin = Admin.objects.create(
            first_name = "Mohd",
            last_name = "Hsyn",
            email = "syd.mhd.hsyn@gmail.com",
            phone = "12345678",
            password = _password,
        )
        data = {
            "email": "syd.mhd.hsyn@gmail.com",
            "password": "hussain123",
        }
        response = self.client.post(url, data, format= "json")
        res_data = response.json()
        self.assertEqual(res_data['status'], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_adminForgotPassSendMail(self):
        url = reverse("adminauth-adminForgotPassSendMail")
        _password = handler.hash("hussain123")
        admin = Admin.objects.create(
            first_name = "Mohd",
            last_name = "Hsyn",
            email = "syd.mhd.hsyn@gmail.com",
            phone = "12345678",
            password = _password,
        )
        data = {"email": "syd.mhd.hsyn@gmail.com"}
        response = self.client.post(url, data, format = "json")
        res_data = response.json()
        self.assertEqual(res_data['status'], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_admin = Admin.objects.get(email = "syd.mhd.hsyn@gmail.com")
        self.assertEqual(updated_admin.OtpStatus, True)
        self.assertNotEqual(updated_admin.Otp, 0)
        
    
    def test_checkOtpToken(self):
        url = reverse("adminauth-checkOtpToken")
        _password = handler.hash("hussain123")
        admin = Admin.objects.create(
           first_name = "Mohd",
            last_name = "Hsyn",
            email = "syd.mhd.hsyn@gmail.com",
            phone = "12345678",
            password = _password,
        )
        fetch_admin = Admin.objects.get(email = "syd.mhd.hsyn@gmail.com")
        fetch_admin.OtpStatus = True
        fetch_admin.Otp = 1010
        fetch_admin.save()
        uid = fetch_admin.id
        data = {"id": uid, "otp": "1010"}
        response = self.client.post(url, data, format= "json")
        res_data = response.json()
        self.assertEqual(res_data['status'], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_admin = Admin.objects.get(email = "syd.mhd.hsyn@gmail.com")
        self.assertEqual(updated_admin.Otp, 0)
    
    def test_resetPassword(self):
        url = reverse("adminauth-resetPassword")
        _password = handler.hash("hussain")
        admin = Admin.objects.create(
            first_name = "Mohd",
            last_name = "Hussain",
            email = "syd.mhd.hsyn@gmail.com",
            phone = "12345678",
            password = _password
        )
        fetch_admin = Admin.objects.get(email = "syd.mhd.hsyn@gmail.com")
        fetch_admin.OtpStatus = True
        fetch_admin.Otp = 0
        fetch_admin.save()
        uid = fetch_admin.id
        data = {"id": uid, "newpassword": "abcd12345"}
        response = self.client.post(url, data, format = "json")
        res_data= response.json()
        self.assertEqual(res_data['status'], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check updation in DB
        updated_admin = Admin.objects.get(email = "syd.mhd.hsyn@gmail.com")
        self.assertEqual(updated_admin.OtpStatus, False)
        # Verify the password after changing 
        self.assertTrue(handler.verify("abcd12345", updated_admin.password))
        # login after reset password 
        login_url = reverse("adminauth-adminLogin")
        login_data = {"email": "syd.mhd.hsyn@gmail.com", "password": "abcd12345"}
        login_response = self.client.post(login_url, login_data, format = "json")
        login_responsedata = login_response.json()
        self.assertEqual(login_responsedata['status'], True)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
    
    # Admin Need Authentication Class
    # Admin can't access without permission
class AdminViewSet_TestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        password = handler.hash("abcd12345")
        email = "syd.mhd.hsyn@gmail.com"
        create_admin = Admin.objects.create(
            first_name = "Mohd",
            last_name = "Hsyn",
            email = email,
            phone = "12345678",
            password = password,
        )
        # first login to save the admin login credentials and token in db
        login_url = reverse("adminauth-adminLogin")
        login_data = {"email": email, "password": "abcd12345"}
        # self.client.login(email = self.email, password = self.password)
        login_response = self.client.post(login_url, login_data)
        self.token = login_response.data['token']
        # check token sav in DB 
        self.fetch_admin = Admin.objects.get(email = email)
        fetch_token = AdminWhitelistToken.objects.get(admin= self.fetch_admin, token = self.token)
        self.assertEqual(fetch_token.token, self.token)
        
    def test_adminLogout(self):
        url = reverse("admin-adminLogout")
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.token}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_adminProfile(self):
        url = reverse("admin-adminProfile")
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.token}")
        response = self.client.get(url)
        print(response.content)
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from app_shopping.models import *


class AdminAuthViewSet_TestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_adminSignup(self):
        url = reverse("adminauth-adminSignup")
        data = {
            "first_name": "Shahzaib",
            "last_name": "Ali",
            "email": "innocentsmsa92@hotmail.com",
            "phone": "12345678",
            "password": "shahzaib",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Admin.objects.count(), 1)
        self.assertEqual(Admin.objects.get().first_name, "Shahzaib")

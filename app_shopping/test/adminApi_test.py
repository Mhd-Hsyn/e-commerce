from passlib.hash import django_pbkdf2_sha256 as handler
from django.core.files.uploadedfile import SimpleUploadedFile
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
        self.assertEqual(res_data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Admin.objects.count(), 1)
        self.assertEqual(Admin.objects.get().first_name, "Muhammad")

    def test_adminlogin(self):
        url = reverse("adminauth-adminLogin")
        _password = handler.hash("hussain123")
        admin = Admin.objects.create(
            first_name="Mohd",
            last_name="Hsyn",
            email="syd.mhd.hsyn@gmail.com",
            phone="12345678",
            password=_password,
        )
        data = {
            "email": "syd.mhd.hsyn@gmail.com",
            "password": "hussain123",
        }
        response = self.client.post(url, data, format="json")
        res_data = response.json()
        self.assertEqual(res_data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_adminForgotPassSendMail(self):
        url = reverse("adminauth-adminForgotPassSendMail")
        _password = handler.hash("hussain123")
        admin = Admin.objects.create(
            first_name="Mohd",
            last_name="Hsyn",
            email="syd.mhd.hsyn@gmail.com",
            phone="12345678",
            password=_password,
        )
        data = {"email": "syd.mhd.hsyn@gmail.com"}
        response = self.client.post(url, data, format="json")
        res_data = response.json()
        self.assertEqual(res_data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_admin = Admin.objects.get(email="syd.mhd.hsyn@gmail.com")
        self.assertEqual(updated_admin.OtpStatus, True)
        self.assertNotEqual(updated_admin.Otp, 0)

    def test_checkOtpToken(self):
        url = reverse("adminauth-checkOtpToken")
        _password = handler.hash("hussain123")
        admin = Admin.objects.create(
            first_name="Mohd",
            last_name="Hsyn",
            email="syd.mhd.hsyn@gmail.com",
            phone="12345678",
            password=_password,
        )
        fetch_admin = Admin.objects.get(email="syd.mhd.hsyn@gmail.com")
        fetch_admin.OtpStatus = True
        fetch_admin.Otp = 1010
        fetch_admin.save()
        uid = fetch_admin.id
        data = {"id": uid, "otp": "1010"}
        response = self.client.post(url, data, format="json")
        res_data = response.json()
        self.assertEqual(res_data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_admin = Admin.objects.get(email="syd.mhd.hsyn@gmail.com")
        self.assertEqual(updated_admin.Otp, 0)

    def test_resetPassword(self):
        url = reverse("adminauth-resetPassword")
        _password = handler.hash("hussain")
        admin = Admin.objects.create(
            first_name="Mohd",
            last_name="Hussain",
            email="syd.mhd.hsyn@gmail.com",
            phone="12345678",
            password=_password,
        )
        fetch_admin = Admin.objects.get(email="syd.mhd.hsyn@gmail.com")
        fetch_admin.OtpStatus = True
        fetch_admin.Otp = 0
        fetch_admin.save()
        uid = fetch_admin.id
        data = {"id": uid, "newpassword": "abcd12345"}
        response = self.client.post(url, data, format="json")
        res_data = response.json()
        self.assertEqual(res_data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check updation in DB
        updated_admin = Admin.objects.get(email="syd.mhd.hsyn@gmail.com")
        self.assertEqual(updated_admin.OtpStatus, False)
        # Verify the password after changing
        self.assertTrue(handler.verify("abcd12345", updated_admin.password))
        # login after reset password
        login_url = reverse("adminauth-adminLogin")
        login_data = {"email": "syd.mhd.hsyn@gmail.com", "password": "abcd12345"}
        login_response = self.client.post(login_url, login_data, format="json")
        login_responsedata = login_response.json()
        self.assertEqual(login_responsedata["status"], True)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    # Admin Need Authentication Class
    # Admin can't access without permission


class AdminViewSet_TestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.password = handler.hash("abcd12345")
        self.email = "syd.mhd.hsyn@gmail.com"
        create_admin = Admin.objects.create(
            first_name="Mohd",
            last_name="Hsyn",
            email=self.email,
            phone="12345678",
            password=self.password,
        )
        # first login to save the admin login credentials and token in db
        login_url = reverse("adminauth-adminLogin")
        login_data = {"email": self.email, "password": "abcd12345"}
        # self.client.login(email = self.email, password = self.password)
        login_response = self.client.post(login_url, login_data)
        self.token = login_response.data["token"]
        # check token sav in DB
        self.fetch_admin = Admin.objects.get(email=self.email)
        fetch_token = AdminWhitelistToken.objects.get(
            admin=self.fetch_admin, token=self.token
        )
        self.assertEqual(fetch_token.token, self.token)

    def test_adminLogout(self):
        url = reverse("admin-adminLogout")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_adminProfile(self):
        url = reverse("admin-adminProfile")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        # Get Admin
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_data = response.json()
        self.assertEqual(res_data["status"], True)
        self.assertEqual(res_data["data"]["email"], self.email)
        self.assertEqual(res_data["data"]["image"], "/media/AdminImage/dummyadmin.png")
        # PUT   Update-Admin
        # open the image
        with open(
            r"/media/hussain/Data/Python/Django/2_practice/_4_Ecomerce_shopping_app/ecomerce/media/CustomerImage/dummycustomer.png",
            "rb",
        ) as img:
            image_content = img.read()

        image = SimpleUploadedFile(
            "new_profileimage.png", image_content, content_type="image/png"
        )
        data = {
            "first_name": "SYED M",
            "last_name": "Hussain",
            "phone": "99999999",
            "image": image,
        }
        update_admin_response = self.client.put(
            url, data, format="multipart", HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(update_admin_response.status_code, status.HTTP_200_OK)
        update_res_data = update_admin_response.json()
        self.assertEqual(update_res_data["data"]["first_name"], "SYED M")

        # Check database Updated or not
        fetch_admin = Admin.objects.get(id=self.fetch_admin.id)
        self.assertEqual(fetch_admin.first_name, "SYED M")
        self.assertEqual(fetch_admin.last_name, "Hussain")
        self.assertEqual(fetch_admin.phone, "99999999")
        self.assertNotEqual(fetch_admin.image, "/media/AdminImage/dummyadmin.png")

    def test_adminChangePass(self):
        url = reverse("admin-adminChangePass")
        data = {"oldpassword": "abcd12345", "newpassword": "12345678"}
        response = self.client.post(
            url, data, HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        res_data = response.json()
        self.assertEqual(res_data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check in db
        fetch_admin = Admin.objects.get(id=self.fetch_admin.id)
        self.assertTrue(handler.verify("12345678", fetch_admin.password))
        self.assertFalse(handler.verify("abcd12345", fetch_admin.password))


class AdminProductCategory_TestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "syd.mhd,hsyn@gmail.com"
        admin = Admin.objects.create(
            first_name="Mohd",
            last_name="Hsyn",
            email=self.email,
            phone="12345678",
            password=handler.hash("abcd12345"),
        )
        login_data = {"email": self.email, "password": "abcd12345"}
        login_url = reverse("adminauth-adminLogin")
        login_response = self.client.post(path=login_url, data=login_data)
        self.token = login_response.json()["token"]

    # POST
    def test_ProductCategoryAdd(self):
        url = reverse("admin-ProductCategoryApi")
        data = {
            "name": "Mens",
            "description": "All Branded Mens category with high Quality",
        }
        response = self.client.post(
            path=url,
            data=data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        res_data = response.json()
        self.assertEqual(res_data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check DB
        fetch_category = ProductCategory.objects.get(name="Mens")
        self.assertEqual(fetch_category.name, "Mens")
        self.assertEqual(
            fetch_category.description, "All Branded Mens category with high Quality"
        )

    # Get all product
    def test_ProductCategoryGET(self):
        url = reverse("admin-ProductCategoryApi")
        # Add min 2 categories
        category = ProductCategory.objects.create(
            name="Mens", description="Branded Mens category with high Quality"
        )
        self.client.post(
            path=reverse("admin-ProductCategoryApi"),
            data={"name": "Womens", "description": "All womens category"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )

        response = self.client.get(path=url, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        # print(response.content)
        res_data = response.json()
        self.assertEqual(res_data["status"], True)
        self.assertEqual(len(res_data["data"]), 2)

    # Update the category
    def test_CategoryUpdate(self):
        url = reverse("admin-ProductCategoryApi")
        # firstly Add 2 category
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.client.post(
            path=reverse("admin-ProductCategoryApi"),
            data={"name": "Mens", "description": "All MENS Category"},
        )
        self.client.post(
            path=reverse("admin-ProductCategoryApi"),
            data={"name": "Womens", "description": "All womens category"},
        )
        #  Secondly fetch id of category
        get_response = self.client.get(path=url)
        get_res_data = get_response.json()
        # print(get_res_data)
        categories = get_res_data["data"]  # get data from response / remove status
        categories_id = []
        for category in categories:
            categories_id.append(category["id"])

        # Update these categories hit API
        response = self.client.put(
            path=url,
            data={
                "id": categories_id[0],
                "name": "Updated Mens Category",
                "description": "I update MEN cateogory",
            },
            format="json",
        )
        res_data = response.json()
        self.assertEqual(res_data["status"], True)
        self.assertEqual(res_data["data"]["name"], "Updated Mens Category")
        # check DB
        fetch_category = ProductCategory.objects.get(id=categories_id[0])
        self.assertEqual(fetch_category.name, "Updated Mens Category")
        self.assertEquals(fetch_category.description, "I update MEN cateogory")

    def test_deleteCategory(self):
        url = reverse("admin-ProductCategoryApi")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        # first post category
        self.client.post(
            path=url,
            data={"name": "Mens", "description": "Mens All Category"},
            format="json",
        )
        self.client.post(
            path=url,
            data={"name": "Womens", "description": "Womens Category"},
            format="json",
        )
        # second   =>  get all category and id
        categories_response = self.client.get(path=url)
        json_response = categories_response.json()
        data = json_response["data"]
        category_id = []
        for category in data:
            category_id.append(category["id"])

        # Delete the category
        response = self.client.delete(path=url, data={"id": category_id[0]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fetch_category = ProductCategory.objects.all()
        self.assertEqual(fetch_category.count(), 1)
        self.assertFalse(
            ProductCategory.objects.filter(
                name="Mens", description="Mens All Category"
            ).first()
        )


class AdminProductSubCat_TestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        admin_resp = self.client.post(
            path=reverse("adminauth-adminSignup"),
            data={
                "first_name": "S Mhd",
                "last_name": "Hsyn",
                "phone": "03242145",
                "email": "syd.mhd.hsyn@gmail.com",
                "password": "abcd1234",
            },
            format="json",
        )
        admin_login_response = self.client.post(
            path=reverse("adminauth-adminLogin"),
            data={"email": "syd.mhd.hsyn@gmail.com", "password": "abcd1234"},
            format="json",
        )
        json_data = admin_login_response.json()
        self.token = json_data["token"]

        categories = [
            {"name": "Mens", "description": "Mens all categppry"},
            {"name": "Women", "description": "Women all category"},
            {"name": "others", "description": "others category"},
        ]
        for category in categories:
            self.client.post(
                path=reverse("admin-ProductCategoryApi"),
                data={"name": category["name"], "description": category["description"]},
                HTTP_AUTHORIZATION=f"Bearer {self.token}",
            )
        get_category_resp = self.client.get(
            path=reverse("admin-ProductCategoryApi"),
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.get_category = get_category_resp.json()["data"]
        self.categoryList_id = []
        for category in self.get_category:
            self.categoryList_id.append(category["id"])

    def test_AddSubCategory(self):
        url = reverse(
            "admin-ProductSubCategoryApi", kwargs={"pk": self.categoryList_id[1]}
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.post(
            path=url,
            data={"name": "Jewlery", "description": "All branded womens jewlerry"},
        )
        res_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["status"], True)
        self.assertEqual(res_data["category"], "Women")
        self.assertEqual(res_data["sub_category"], "Jewlery")

    def test_GetsubCategory(self):
        url = reverse(
            "admin-ProductSubCategoryApi", kwargs={"pk": self.categoryList_id[1]}
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.client.post(
            path=url,
            data={"name": "Jewlery", "description": "All branded womens jewlerry"},
        )
        response = self.client.get(url)
        res_data = response.json()
        self.assertEqual(res_data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["category"], "Women")

    def test_UpdateSubCategory(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.client.post(
            path=reverse(
                "admin-ProductSubCategoryApi", kwargs={"pk": self.categoryList_id[1]}
            ),
            data={"name": "Jewlery", "description": "All branded womens jewlerry"},
        )
        get_subcategory = self.client.get(
            path=reverse(
                "admin-ProductSubCategoryApi", kwargs={"pk": self.categoryList_id[1]}
            )
        )
        # print(get_subcategory.content)
        res_data_getSubCat = get_subcategory.json()["data"]
        sub_cat_id = ""
        cat_id = ""
        for data in res_data_getSubCat:
            sub_cat_id = data["id"]
            cat_id = data["category"]

        update_response = self.client.put(
            path=reverse("admin-ProductSubCategoryApi", kwargs={"pk": sub_cat_id}),
            data={
                "name": "Updated_Jewlery",
                "description": "I update the jewlery",
                "category_id": cat_id,
            },
        )
        res_data_updated = update_response.json()
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data_updated["status"], True)
        # check DB
        fetch_sub_cat = Product_SubCategory.objects.filter(id=sub_cat_id).first()
        self.assertEqual(fetch_sub_cat.name, "Updated_Jewlery")
        self.assertEqual(fetch_sub_cat.description, "I update the jewlery")

    def test_deleteSubCategory(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.client.post(
            path=reverse(
                "admin-ProductSubCategoryApi", kwargs={"pk": self.categoryList_id[1]}
            ),
            data={"name": "Jewlery", "description": "All branded womens jewlerry"},
        )
        get_subcategory = self.client.get(
            path=reverse(
                "admin-ProductSubCategoryApi", kwargs={"pk": self.categoryList_id[1]}
            )
        )
        # print(get_subcategory.content)
        res_data_getSubCat = get_subcategory.json()["data"]
        sub_cat_id = ""
        for data in res_data_getSubCat:
            sub_cat_id = data["id"]

        response = self.client.delete(
            path=reverse("admin-ProductSubCategoryApi", kwargs={"pk": sub_cat_id})
        )
        res_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["status"], True)
        self.assertFalse(Product_SubCategory.objects.filter(id=sub_cat_id).first())

from django.test import TestCase
from app_shopping.models import *


class AdminModel_TestCase(TestCase):
    def setUp(self):
        self.admin = Admin(
            first_name="Shahzaib",
            last_name="Ali",
            email="innocentsmsa92@hotmail.com",
            phone="12345678",
            password="shahzaib",
        )

    def test_admin_create(self):
        self.admin.save()
        fetch_admin = Admin.objects.get(email="innocentsmsa92@hotmail.com")
        self.assertEqual(fetch_admin.first_name, "Shahzaib")
        self.assertEqual(fetch_admin.last_name, "Ali")
        self.assertEqual(fetch_admin.email, "innocentsmsa92@hotmail.com")
        self.assertEqual(fetch_admin.password, "shahzaib")

    def test_admin_str(self):
        self.assertEqual(str(self.admin), "Shahzaib Ali")


class AdminWhiteListToken_TestCase(TestCase):
    def setUp(self) -> None:
        self.admin = Admin.objects.create(
            first_name="Shahzaib",
            last_name="Ali",
            email="innocentsmsa92@hotmail.com",
            phone="12345678",
            password="shahzaib",
        )
        self.whiteListToken = AdminWhitelistToken(admin=self.admin, token="abcd@123")

    def test_AdminWhitelist(self):
        self.whiteListToken.save()
        fetch_token = AdminWhitelistToken.objects.get(token="abcd@123")
        self.assertEqual(fetch_token.token, "abcd@123")
        self.assertEqual(fetch_token.admin, self.admin)

    def test_str(self):
        self.assertEqual(str(self.admin), "Shahzaib Ali")


class ProductCategoryModel_TestCase(TestCase):
    def setUp(self) -> None:
        self.p_category = ProductCategory(
            name="Mens", description="Mens Design and Category"
        )

    def testCategory(self):
        self.p_category.save()
        fetch_category = ProductCategory.objects.get(name="Mens")
        self.assertEqual(fetch_category.name, "Mens")
        self.assertEqual(fetch_category.description, "Mens Design and Category")

    def testCategory_str_(self):
        self.assertEqual(str(self.p_category), "Mens")


class ProductSubCategory_TestCase(TestCase):
    def setUp(self) -> None:
        self.p_category = ProductCategory.objects.create(name="Mens")
        self.p_subcategory = Product_SubCategory(
            category=self.p_category, name="Shoes", description="Best Mens Shoes"
        )

    def testSubCategory(self):
        self.p_subcategory.save()
        fetch_subcategory = Product_SubCategory.objects.get(name="Shoes")
        self.assertEqual(fetch_subcategory.category, self.p_category)
        self.assertEqual(fetch_subcategory.name, "Shoes")
        self.assertEqual(fetch_subcategory.description, "Best Mens Shoes")

    def testSubCateory_str(self):
        self.assertEqual(str(self.p_subcategory), "Shoes - Mens")
